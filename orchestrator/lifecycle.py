"""
orchestrator/lifecycle.py — Case state machine.

Owns the full case lifecycle: RECEIVED → STRUCTURED → ANALYZED → CHECKED
→ ESCALATED | AUTO_CLEARED → HUMAN_REVIEWED | → SEALED
Error → QUARANTINED

Golden Rule 2: The escalation gate is deterministic (gate.must_escalate).
Golden Rule 6: Every transition is audited (audit.chain.append_entry).
§5.4 SDD, P11 Playbook.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from audit.chain import append_entry, verify_chain, reset_chain
from orchestrator.gate import must_escalate
from schemas import (
    CaseInput,
    StructuredCase,
    Finding,
    RiskFlag,
    ComplianceResult,
    EscalationBrief,
    HumanDecision,
    ReviewPacket,
)

load_dotenv()
logger = logging.getLogger(__name__)

# Re-export for convenience
__all__ = ["CaseStatus", "handle_case", "handle_case_local"]


class CaseStatus:
    RECEIVED = "RECEIVED"
    STRUCTURED = "STRUCTURED"
    ANALYZED = "ANALYZED"
    CHECKED = "CHECKED"
    AUDITED = "AUDITED"
    AUTO_CLEARED = "AUTO_CLEARED"
    ESCALATED = "ESCALATED"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"
    SEALED = "SEALED"
    QUARANTINED = "QUARANTINED"


# In-memory store for demo (single-instance, no DB), backed by disk so a
# reload/restart does not lose submitted cases.
_case_store: dict[str, dict] = {}
_STATE_DIR = Path(__file__).parent.parent / "data" / "state"


import re as _re

def _sanitize_id(raw: str) -> str:
    """Strip path traversal and limit length."""
    return _re.sub(r'[^A-Za-z0-9\-]', '', raw)[:64]

def _load_case_json(case_id: str) -> dict | None:
    """Load a synthetic case from data/cases/<case_id>.json."""
    case_id = _sanitize_id(case_id)
    case_path = Path(__file__).parent.parent / "data" / "cases" / f"{case_id}.json"
    if case_path.exists():
        with open(case_path) as f:
            return json.load(f)
    return None


def _persist_state(state: dict) -> None:
    """Write the case state to disk so it survives a server reload/restart."""
    try:
        _STATE_DIR.mkdir(parents=True, exist_ok=True)
        case_id = _sanitize_id(state.get("case_id", "unknown"))
        (_STATE_DIR / f"{case_id}.json").write_text(
            json.dumps(state, default=str, indent=2)
        )
    except Exception as e:
        logger.warning(f"State persist failed for {state.get('case_id')}: {e}")


def _load_state(case_id: str) -> dict | None:
    """Load a previously persisted case state from disk."""
    case_id = _sanitize_id(case_id)
    path = _STATE_DIR / f"{case_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            logger.warning(f"State load failed for {case_id}: {e}")
    return None


def _has_clinical_data(structured: dict) -> bool:
    """True if the case carries any usable clinical data point.

    A case with nothing readable (e.g. handwriting OCR failed and the fields were
    never confirmed) must NOT silently auto-clear into a blank packet — it is
    routed to the human instead.
    """
    v = structured.get("vitals") or {}
    labs = structured.get("labs") or {}
    return any([
        structured.get("lmp_date"),
        structured.get("usg_date"),
        structured.get("usg_measurement"),
        v.get("bp_systolic"),
        v.get("bp_diastolic"),
        labs.get("urine_protein"),
        labs.get("fasting_glucose_mg_dl"),
        labs.get("hb_g_dl"),
    ])


# ---------------------------------------------------------------------------
# Band coordination — every inter-agent handoff traverses a real Band room.
# Best-effort: if Band is unavailable the case is still reviewed locally.
# ---------------------------------------------------------------------------

def _make_env(case_id, from_agent, intent, payload, to_role=None) -> dict:
    """Build a typed inter-agent message envelope (dict, JSON-ready)."""
    from schemas import MessageEnvelope
    return MessageEnvelope(
        case_id=case_id,
        from_agent=from_agent,
        intent=intent,
        to_role=to_role,
        payload=payload,
    ).model_dump(mode="json")


class _BandSession:
    """Drives a real Band room for a case and mirrors every envelope locally.

    The orchestrator opens the room, recruits the three agents via the Agent
    API, and posts each StructuredCase / Finding / RiskFlag / ComplianceResult /
    handoff / escalation as a typed envelope into the shared room. The same
    envelopes are mirrored into `messages` so the UI's room view shows the real
    conversation even if the network blips.
    """

    def __init__(self, case_id: str):
        self.case_id = case_id
        self.messages: list[dict] = []
        self.room = None
        self.client = None
        self.room_id = None
        self.enabled = False

    async def start(self) -> None:
        from band_wrapper.client import band_available, BandClient
        if not band_available():
            logger.info(f"[{self.case_id}] Band not configured — local coordination only")
            return
        try:
            self.client = BandClient(agent_id="orchestrator")
            # Open the room, recruit the agents, THEN post — so no message
            # references a participant before it has joined the room.
            self.room = await self.client.open_room(self.case_id)
            self.room_id = self.room.room_id
            recruited = await self.client.recruit(self.room, ["intake", "dating_risk", "guideline", "auditor"])
            self.enabled = True
            logger.info(f"[{self.case_id}] Band room {self.room_id} — recruited {recruited}")
        except Exception as e:
            logger.warning(f"[{self.case_id}] Band room unavailable, continuing local: {e}")
            self.enabled = False

    async def mirror(self, env: dict) -> None:
        """Record an envelope locally and (best-effort) post it to the Band room."""
        self.messages.append(env)
        if self.enabled and self.client and self.room:
            try:
                await self.client.post(self.room, env)
            except Exception as e:
                logger.debug(f"[{self.case_id}] Band post skipped: {e}")


async def post_to_case_room(state: dict, env: dict) -> None:
    """Append an envelope to a case's room history and (best-effort) to Band.

    Used after the pipeline has returned — e.g. when the human reviewer posts a
    decision into the same room the agents used.
    """
    state.setdefault("room_messages", []).append(env)
    room_id = state.get("band_room_id")
    if not room_id:
        return
    try:
        from band_wrapper.client import band_available, BandClient, Room
        if not band_available():
            return
        client = BandClient(agent_id="orchestrator")
        await client.post(Room(room_id=room_id, case_id=state.get("case_id", "")), env)
    except Exception as e:
        logger.debug(f"[{state.get('case_id')}] human-decision Band post skipped: {e}")


# ---------------------------------------------------------------------------
# Local mode — runs agents directly without Band (for testing/demo)
# ---------------------------------------------------------------------------

async def handle_case_local(raw_case: dict | str) -> dict:
    """
    Drive a case through the full lifecycle using local agent calls (no Band).

    Accepts either a case dict or a case_id string (loads from data/cases/).

    Returns the final state dict with all accumulated data.
    """
    # Load case if given as string
    if isinstance(raw_case, str):
        loaded = _load_case_json(raw_case)
        if not loaded:
            return {"status": CaseStatus.QUARANTINED, "error": f"Case {raw_case} not found"}
        raw_case = loaded

    case_id = raw_case.get("case_id", "unknown")
    state: dict[str, Any] = {
        "case_id": case_id,
        "status": CaseStatus.RECEIVED,
        "raw_case": raw_case,
        "structured_case": None,
        "finding": None,
        "flags": [],
        "compliance": None,
        "escalation_brief": None,
        "human_decision": None,
        "packet_ref": None,
        "final_hash": None,
        "room_messages": [],
        "band_room_id": None,
        "errors": [],
    }
    _case_store[case_id] = state
    _persist_state(state)

    # Open a real Band room and recruit the agents (best-effort)
    band = _BandSession(case_id)
    await band.start()
    state["band_room_id"] = band.room_id
    state["room_messages"] = band.messages
    await band.mirror(_make_env(case_id, "orchestrator", "post", {
        "type": "seed_context", "case_id": case_id, "raw_case": raw_case,
    }))

    try:
        # --- Transition: RECEIVED (fresh chain per submission) ---
        reset_chain(case_id)
        append_entry(case_id, "orchestrator", "received", {"case_id": case_id})
        logger.info(f"[{case_id}] Status: RECEIVED")

        # --- Step 1: Intake ---
        from agents.intake.agent import run_intake_local
        intake_result = await run_intake_local(raw_case)

        if intake_result["status"] == "validation_error":
            state["status"] = CaseStatus.QUARANTINED
            state["errors"].append(intake_result["error"])
            append_entry(case_id, "orchestrator", "quarantined",
                        {"reason": str(intake_result["error"])})
            _persist_state(state)
            return state

        structured = intake_result["structured_case"]
        state["structured_case"] = structured
        state["status"] = CaseStatus.STRUCTURED
        append_entry(case_id, "intake", "structured", {"case_id": case_id})
        await band.mirror(_make_env(case_id, "intake", "post", structured))
        await band.mirror(_make_env(case_id, "intake", "handoff",
                                    {"message": "StructuredCase ready for analysis."},
                                    to_role="dating_risk"))
        _persist_state(state)
        logger.info(f"[{case_id}] Status: STRUCTURED")

        # --- Step 2: Dating & Risk ---
        from agents.dating_risk.agent import run_dating_risk_local
        dr_result = await run_dating_risk_local(structured)

        if dr_result["status"] != "ok":
            state["status"] = CaseStatus.QUARANTINED
            state["errors"].append(dr_result.get("error", "Dating & Risk failed"))
            append_entry(case_id, "orchestrator", "quarantined",
                        {"reason": "Dating & Risk agent failed"})
            _persist_state(state)
            return state

        finding = dr_result["finding"]
        flags_data = dr_result["flags"]
        state["finding"] = finding
        state["flags"] = flags_data
        state["status"] = CaseStatus.ANALYZED
        append_entry(case_id, "dating_risk", "analysed",
                    {"ga_lmp": finding.get("ga_lmp_weeks"),
                     "ga_usg": finding.get("ga_usg_weeks"),
                     "discordance": finding.get("discordance_weeks"),
                     "flag_count": len(flags_data)})
        await band.mirror(_make_env(case_id, "dating_risk", "post", finding))
        for flag in flags_data:
            await band.mirror(_make_env(case_id, "dating_risk", "post", flag))
        await band.mirror(_make_env(case_id, "dating_risk", "handoff",
                                    {"message": "Findings and risk flags posted. Guideline check required."},
                                    to_role="guideline"))
        _persist_state(state)
        logger.info(f"[{case_id}] Status: ANALYZED ({len(flags_data)} flags)")

        # --- Step 3: Guideline ---
        from agents.guideline.agent import run_guideline_local
        gl_result = await run_guideline_local(structured, [finding], flags_data)

        compliance = gl_result["compliance"]
        state["compliance"] = compliance
        state["status"] = CaseStatus.CHECKED
        append_entry(case_id, "guideline", "checked",
                    {"compliant": compliance.get("compliant"),
                     "veto": compliance.get("veto"),
                     "missing": compliance.get("missing_investigations")})
        await band.mirror(_make_env(case_id, "guideline", "post", compliance))
        _persist_state(state)
        logger.info(f"[{case_id}] Status: CHECKED (veto={compliance.get('veto')})")

        # --- Step 3b: Auditor (adversarial review) ---
        from agents.auditor.agent import run_auditor_local
        auditor_result = await run_auditor_local(
            structured, [finding], flags_data, compliance,
        )
        audit_data = auditor_result["audit_result"]
        state["auditor"] = audit_data
        state["status"] = "AUDITED"  # new interim state
        append_entry(case_id, "auditor", "audited",
                    {"challenged": audit_data.get("challenged"),
                     "reasons": audit_data.get("reasons")})
        await band.mirror(_make_env(case_id, "auditor", "post", audit_data))
        _persist_state(state)
        logger.info(f"[{case_id}] Status: AUDITED (challenged={audit_data.get('challenged')})")

        # --- Step 4: Gate decision ---
        typed_flags = [
            RiskFlag(
                flag_id=f.get("flag_id", ""),
                case_id=f.get("case_id", case_id),
                type=f.get("type", ""),
                severity=f.get("severity", "moderate"),
                evidence=f.get("evidence", {}),
                rule_ref=f.get("rule_ref", ""),
            )
            for f in flags_data
        ]
        typed_compliance = ComplianceResult(
            case_id=case_id,
            compliant=compliance.get("compliant", False),
            veto=compliance.get("veto", False),
            missing_investigations=compliance.get("missing_investigations", []),
            notes=compliance.get("notes", ""),
            rule_refs=compliance.get("rule_refs", []),
        )

        escalate = must_escalate(typed_flags, typed_compliance)

        # A case with no usable clinical data must not auto-clear a blank packet —
        # route it to the human to enter data or decide.
        insufficient_data = not _has_clinical_data(structured)
        if insufficient_data and not escalate:
            escalate = True
            logger.info(f"[{case_id}] Insufficient clinical data — forcing human review")

        if not escalate:
            # --- Auto-clear path ---
            state["status"] = CaseStatus.AUTO_CLEARED
            append_entry(case_id, "orchestrator", "auto_cleared",
                        {"escalated": False})
            await band.mirror(_make_env(case_id, "orchestrator", "post", {
                "type": "auto_cleared",
                "message": "No risk flags or veto — auto-cleared per deterministic gate.",
            }))
            logger.info(f"[{case_id}] Status: AUTO_CLEARED (no flags/veto)")

            # Human decision is an auto-approve
            state["human_decision"] = {
                "decision_id": f"D-AUTO-{case_id}",
                "case_id": case_id,
                "reviewer": "SYSTEM (auto-cleared)",
                "verdict": "approve",
                "note": "No risk flags or veto — auto-cleared per deterministic gate.",
                "decided_at": datetime.now(timezone.utc).isoformat(),
            }
            append_entry(case_id, "human", "decided",
                        {"verdict": "approve", "auto": True})

            # --- Seal immediately (auto-clear path) ---
            final_hash = _compute_final_hash(case_id)
            state["final_hash"] = final_hash

            from packet.generator import build_packet
            try:
                packet_path = await build_packet(
                    case=raw_case,
                    findings=[finding] if finding else [],
                    flags=flags_data,
                    decision=state["human_decision"],
                    final_hash=final_hash,
                    compliance=compliance,
                )
                state["packet_ref"] = packet_path
            except Exception as e:
                logger.warning(f"[{case_id}] Packet generation failed (non-fatal): {e}")
                state["packet_ref"] = f"packets/{case_id}.pdf (generation pending)"

            state["status"] = CaseStatus.SEALED
            append_entry(case_id, "orchestrator", "sealed", {"final_hash": final_hash})
            logger.info(f"[{case_id}] Status: SEALED ✅")

            ok, broken = verify_chain(case_id)
            state["audit_verified"] = ok
            if not ok:
                logger.warning(f"[{case_id}] Audit chain BROKEN at seq {broken}!")

            # Store and return
            _case_store[case_id] = state
            _persist_state(state)
            return state

        else:
            # --- Escalation path ---
            state["status"] = CaseStatus.ESCALATED

            # Build escalation brief
            reasons = [f["type"] for f in flags_data]
            if typed_compliance.veto:
                reasons.append("guideline_veto")
            if insufficient_data:
                reasons.append("insufficient_data")

            # --- Add auditor challenge to reasons if applicable ---
            auditor_data = state.get("auditor") or {}
            if auditor_data.get("challenged"):
                reasons.append("auditor_challenge")
                auditor_narrative = auditor_data.get("narrative", "")

            if insufficient_data and not flags_data and not typed_compliance.veto:
                summary = (
                    "No clinical data could be read from the submission "
                    "(handwriting unreadable or fields left blank). "
                    "Reviewer must enter the values or confirm the case is incomplete."
                )
                required_action = "Enter missing data or mark case incomplete."
            else:
                summary = (
                    f"GA discordance: {finding.get('discordance_weeks', 'N/A')} wk "
                    f"(LMP {finding.get('ga_lmp_weeks', 'N/A')} / "
                    f"USG {finding.get('ga_usg_weeks', 'N/A')}); "
                    f"Flags: {', '.join(reasons)}. "
                    f"Missing: {', '.join(typed_compliance.missing_investigations)}"
                )
                if auditor_data.get("challenged"):
                    summary += (
                        f" | ⚠️ AUDITOR CHALLENGED: "
                        f"{auditor_narrative[:200]}"
                    )
                required_action = "Approve work-up plan or override."

            brief = {
                "case_id": case_id,
                "reason": reasons,
                "summary": summary,
                "required_action": required_action,
            }
            state["escalation_brief"] = brief
            append_entry(case_id, "orchestrator", "escalated",
                        {"brief": brief})
            await band.mirror(_make_env(case_id, "orchestrator", "escalate", brief))

            # Draft an advised treatment & investigation plan for the OB to review.
            # The human approves it or overrides → the plan is re-generated (loop).
            from tools.treatment import generate_plan
            state["proposed_plan"] = await generate_plan(state, iteration=1)
            state["plan_history"] = []
            append_entry(case_id, "orchestrator", "plan_proposed",
                        {"iteration": 1, "source": state["proposed_plan"].get("source")})
            await band.mirror(_make_env(case_id, "orchestrator", "post",
                                        {"type": "treatment_plan", **state["proposed_plan"]}))
            logger.info(f"[{case_id}] Status: ESCALATED — ⏳ AWAITING HUMAN REVIEW")

            # STOP HERE — human must decide via POST /cases/{id}/decision
            # Do NOT auto-decide. The human-in-the-loop gate is real.
            _case_store[case_id] = state
            _persist_state(state)
            return state

    except Exception as e:
        logger.exception(f"[{case_id}] Lifecycle error: {e}")
        state["status"] = CaseStatus.QUARANTINED
        state["errors"].append(str(e))
        append_entry(case_id, "orchestrator", "quarantined",
                    {"reason": str(e)[:500]})

    # Store in memory + on disk
    _case_store[case_id] = state
    _persist_state(state)
    return state


# ---------------------------------------------------------------------------
# Band mode entry point
# ---------------------------------------------------------------------------

async def handle_case(raw_case: dict) -> str:
    """
    Drive a case through the full lifecycle.

    `handle_case_local` is the single execution path: the orchestrator opens a
    real Band room, recruits intake/dating_risk/guideline via the Agent API, and
    posts every typed handoff envelope into the shared room — falling back to
    purely local coordination only if Band is unreachable. This wrapper exists
    for callers that just want the case_id back.

    Returns the case_id.
    """
    result = await handle_case_local(raw_case)
    return result["case_id"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_final_hash(case_id: str) -> str:
    """Compute the final hash from the audit chain."""
    ok, _ = verify_chain(case_id)
    if ok:
        # Read last entry's this_hash
        audit_path = Path(__file__).parent.parent / "audit_log" / f"{case_id}.jsonl"
        if audit_path.exists():
            lines = audit_path.read_text().strip().splitlines()
            if lines:
                last = json.loads(lines[-1])
                return last.get("this_hash", "sha256:UNKNOWN")
    return "sha256:UNKNOWN"


def get_case_state(case_id: str) -> dict | None:
    """Retrieve current state of a case from memory, falling back to disk.

    Disk fallback means a server reload/restart no longer 404s on cases that
    were already submitted (the in-memory store alone was wiped on reload).
    """
    if case_id in _case_store:
        return _case_store[case_id]
    persisted = _load_state(case_id)
    if persisted is not None:
        _case_store[case_id] = persisted
    return persisted


def get_case_audit(case_id: str) -> dict:
    """Get the audit chain and verification status for a case."""
    ok, broken = verify_chain(case_id)
    audit_path = Path(__file__).parent.parent / "audit_log" / f"{case_id}.jsonl"
    entries = []
    if audit_path.exists():
        for line in audit_path.read_text().strip().splitlines():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return {
        "case_id": case_id,
        "verified": ok,
        "first_broken_seq": broken if not ok else None,
        "entries": entries,
    }

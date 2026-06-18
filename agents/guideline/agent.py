"""
agents/guideline/agent.py — Guideline Agent.

Checks the case against the antenatal ruleset, raises veto,
lists missing investigations. All via Band.
Golden Rule 5: compliant/veto/missing computed deterministically.
The LLM may phrase `notes` only — it CANNOT change the verdict.
§4.4 SDD, P10 Playbook.
"""

from __future__ import annotations

import logging
from typing import Any

from band_wrapper.client import BandClient, Room
from schemas import (
    ComplianceResult,
    RiskFlag,
    Finding,
    MessageEnvelope,
)
from tools.guideline_kb import load_rules, check_schedule

logger = logging.getLogger(__name__)


async def run_guideline(client: BandClient, room: Room) -> None:
    """
    Guideline Agent — listens for handoff from dating_risk, checks rules.

    Steps (P10 Playbook):
      1. Load rules via tools.guideline_kb
      2. Collect StructuredCase, findings, flags from room context
      3. Run check_schedule → ComplianceResult
      4. Post ComplianceResult to room
      5. Signal orchestrator that agent chain is complete

    Golden Rule 1: All I/O via Band.
    Golden Rule 5: compliant/veto/missing are deterministic — from YAML rules.
    """
    result_sent = False
    accumulated_findings: list[dict] = []
    accumulated_flags: list[dict] = []
    structured_case: dict | None = None

    async def handle_message(msg: dict):
        nonlocal result_sent, structured_case, accumulated_findings, accumulated_flags

        intent = msg.get("intent", "")
        from_agent = msg.get("from_agent", "")
        to_role = msg.get("to_role", "")
        payload = msg.get("payload") or {}

        # Accumulate findings and flags from earlier messages
        if from_agent == "dating_risk":
            if intent == "post":
                p = payload or {}
                if "ga_lmp_weeks" in p or "finding_id" in p:
                    accumulated_findings.append(p)
                if "flag_id" in p or "type" in p:
                    if p.get("type") in (
                        "preeclampsia_suspected", "gdm_suspected",
                        "anaemia", "dating_discordance",
                    ):
                        accumulated_flags.append(p)
            elif intent == "handoff" and to_role == "guideline":
                if result_sent:
                    return
                structured_case = payload.get("structured_case") or {}

        if from_agent == "intake" and intent == "post":
            p = payload or {}
            if "normalised" in p or "lmp_date" in p:
                structured_case = p

        # Only respond to handoff from dating_risk addressed to guideline
        if intent != "handoff" or from_agent != "dating_risk" or to_role != "guideline":
            return

        if result_sent:
            return

        logger.info(f"[guideline] Received handoff from dating_risk")

        case_id = (
            structured_case.get("case_id", "unknown") if structured_case
            else payload.get("case_id", "unknown")
        )

        # --- Step 1: Load rules ---
        try:
            rules = load_rules()
        except Exception as e:
            logger.error(f"[guideline] Failed to load rules: {e}")
            return

        # --- Step 2: Build typed objects from accumulated data ---
        flags = _build_risk_flags(accumulated_flags, case_id)

        # --- Step 3: Run deterministic check ---
        try:
            result: ComplianceResult = check_schedule(
                structured=structured_case or {},
                findings=accumulated_findings,
                flags=flags,
                rules=rules,
            )
        except Exception as e:
            logger.error(f"[guideline] check_schedule failed: {e}")
            result = ComplianceResult(
                case_id=case_id,
                compliant=False,
                veto=True,
                missing_investigations=[],
                notes=f"Guideline check error: {str(e)[:200]}",
                rule_refs=[],
            )

        # --- Step 4: Post ComplianceResult ---
        result_env = MessageEnvelope(
            case_id=case_id,
            from_agent="guideline",
            intent="post",
            payload=result.model_dump(mode="json"),
        )
        logger.info(
            f"[guideline] Posting ComplianceResult: "
            f"compliant={result.compliant}, veto={result.veto}, "
            f"missing={result.missing_investigations}"
        )
        await client.post(room, result_env.model_dump(mode="json"))

        # --- Step 5: Signal completion ---
        done_env = MessageEnvelope(
            case_id=case_id,
            from_agent="guideline",
            intent="post",
            payload={
                "type": "chain_complete",
                "message": "Agent chain complete. Orchestrator should evaluate escalation.",
            },
        )
        await client.post(room, done_env.model_dump(mode="json"))
        result_sent = True

    await client.on_message(room, handle_message)


# ---------------------------------------------------------------------------
# Local mode — no Band required
# ---------------------------------------------------------------------------

async def run_guideline_local(
    structured_case: dict,
    findings: list[dict],
    flags: list[dict],
) -> dict:
    """
    Run Guideline locally without Band.

    Returns:
        {"status": "ok", "compliance": dict}
    """
    rules = load_rules()
    case_id = structured_case.get("case_id", "unknown")

    typed_flags = _build_risk_flags(flags, case_id)
    result = check_schedule(
        structured=structured_case,
        findings=findings,
        flags=typed_flags,
        rules=rules,
    )

    return {
        "status": "ok",
        "compliance": result.model_dump(mode="json"),
    }


def _build_risk_flags(flags_data: list[dict], case_id: str) -> list[RiskFlag]:
    """Build RiskFlag objects from accumulated dict data."""
    result: list[RiskFlag] = []
    for fd in flags_data:
        try:
            result.append(RiskFlag(
                flag_id=fd.get("flag_id", ""),
                case_id=fd.get("case_id", case_id),
                type=fd.get("type", ""),
                severity=fd.get("severity", "moderate"),
                evidence=fd.get("evidence", {}),
                rule_ref=fd.get("rule_ref", ""),
            ))
        except Exception:
            pass
    return result

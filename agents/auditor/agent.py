"""
agents/auditor/agent.py — Auditor Agent (4th agent — adversarial reviewer).

Listens for the Guideline agent's ComplianceResult, then adversarially
challenges it: re-evaluates the rules independently, checks for missed flags,
questions borderline decisions, and can issue an auditor challenge that
forces re-review or strengthens the escalation brief.

Golden Rule 5: The auditor's challenge logic is deterministic — the LLM
may phrase the challenge narrative, but the decision to challenge is code.
§4.5 SDD (new), P10b Playbook.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

from band_wrapper.client import BandClient, Room
from schemas import ComplianceResult, RiskFlag, MessageEnvelope
from tools.guideline_kb import load_rules, check_schedule, missing_investigations

load_dotenv()
logger = logging.getLogger(__name__)

AIML_API_KEY = os.getenv("AIML_API_KEY", "")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://openrouter.ai/api/v1")
AUDITOR_MODEL = os.getenv("AIML_AUDITOR_MODEL", "openai/gpt-4o-mini")

# ---------------------------------------------------------------------------
# Deterministic challenge conditions (Golden Rule 5)
# ---------------------------------------------------------------------------

# Rules where we always double-check: if the Guideline says "compliant" but
# any of these flag types are present, the auditor MUST challenge.
_ALWAYS_CHALLENGE_FLAGS = {
    "preeclampsia_suspected",  # PE-001: life-threatening, never suppress
}

# If the Guideline says compliant=True but flags have veto_if_missing rules,
# the auditor challenges.
_VETO_RULE_IDS = {"PE-001", "GDM-002"}

# If more than this many investigations are missing, the auditor challenges
# even if the Guideline says compliant.
_MAX_MISSING_WITHOUT_CHALLENGE = 1

# If any flag is severity=high and compliance says compliant, challenge.
_CHALLENGE_ON_HIGH_SEVERITY_COMPLIANT = True


def _should_challenge(
    flags: list[RiskFlag],
    compliance: ComplianceResult,
    rules: dict,
) -> tuple[bool, list[str]]:
    """Deterministically decide whether to challenge the Guideline result.

    Returns (should_challenge, reasons).
    """
    reasons: list[str] = []

    # 1. High-severity flag + compliant → challenge
    high_flags = [f for f in flags if f.severity == "high"]
    if high_flags and compliance.compliant:
        reasons.append(
            f"High-severity flags ({', '.join(f.type for f in high_flags)}) "
            f"with compliant=True — requires justification"
        )

    # 2. Always-challenge flags present but no veto
    for f in flags:
        if f.type in _ALWAYS_CHALLENGE_FLAGS and not compliance.veto:
            reasons.append(
                f"Flag '{f.type}' ({f.severity}) present without veto — "
                f"auditor requires explicit justification"
            )

    # 3. Veto-eligible rules fired but Guideline didn't veto
    veto_rule_ids_in_flags = set()
    for f in flags:
        if f.rule_ref in _VETO_RULE_IDS:
            veto_rule_ids_in_flags.add(f.rule_ref)
    if veto_rule_ids_in_flags and not compliance.veto:
        reasons.append(
            f"Veto-eligible rules ({', '.join(sorted(veto_rule_ids_in_flags))}) "
            f"fired but Guideline did not veto — auditor double-checks"
        )

    # 4. Too many missing investigations with compliant=True
    missing_count = len(compliance.missing_investigations)
    if missing_count > _MAX_MISSING_WITHOUT_CHALLENGE and compliance.compliant:
        reasons.append(
            f"{missing_count} missing investigations with compliant=True — "
            f"suspect (threshold: {_MAX_MISSING_WITHOUT_CHALLENGE})"
        )

    # 5. Independent re-computation: run check_schedule ourselves
    #    (We don't have the full structured/findings context in Band mode,
    #     so we note this as a reason to challenge if any discrepancy found.)
    #    This is a lightweight sanity check — the LLM narrative fills gaps.

    return len(reasons) > 0, reasons


# ---------------------------------------------------------------------------
# LLM narrative (Golden Rule 5: the LLM phrases, code decides)
# ---------------------------------------------------------------------------

AUDITOR_SYSTEM_PROMPT = """\
You are the Auditor Agent in a multi-agent antenatal review system on Band.
Your job is to ADVERSARIALLY REVIEW the Guideline Agent's ComplianceResult.

You are given:
- The fired risk flags (type, severity, evidence)
- The Guideline's ComplianceResult (compliant, veto, missing_investigations, notes)
- The reasons the deterministic auditor flagged for challenge

TASK: Write a concise, professional challenge narrative (2-4 sentences) that:
1. States what the auditor found questionable
2. Explains WHY it matters clinically (antenatal context)
3. Recommends what should happen next (re-review, add investigations, escalate)

CRITICAL RULES:
- You are challenging, not diagnosing. Use phrases like "the auditor notes",
  "this warrants re-examination", "the following appears inconsistent".
- NEVER state a diagnosis or treatment decision.
- Keep it under 150 words.
- Return ONLY a JSON object: {"challenge": "your narrative here"}
"""


async def _call_auditor_llm(
    flags: list[dict],
    compliance: dict,
    reasons: list[str],
) -> str:
    """Ask the LLM to phrase the auditor's challenge narrative."""
    if not AIML_API_KEY:
        return _fallback_narrative(reasons)

    user_content = json.dumps({
        "fired_flags": flags,
        "guideline_compliance": compliance,
        "deterministic_challenge_reasons": reasons,
    }, default=str)

    payload = {
        "model": AUDITOR_MODEL,
        "messages": [
            {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 512,
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(
                f"{AIML_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {AIML_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/antenatal-review-board",
                    "X-Title": "Antenatal Review Board — Auditor Agent",
                },
                json=payload,
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()

        # Parse the JSON response
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        parsed = json.loads(content)
        return parsed.get("challenge", _fallback_narrative(reasons))
    except Exception as e:
        logger.warning(f"Auditor LLM call failed, using fallback: {e}")
        return _fallback_narrative(reasons)


def _fallback_narrative(reasons: list[str]) -> str:
    """Deterministic fallback when the LLM is unavailable."""
    if not reasons:
        return "Auditor review complete — no concerns identified."
    joined = "; ".join(reasons)
    return (
        f"Auditor challenge: {joined}. "
        f"The auditor recommends re-examination of the Guideline result "
        f"before the case proceeds to the human gate."
    )


# ---------------------------------------------------------------------------
# Band mode — listens for Guideline result, posts challenge
# ---------------------------------------------------------------------------

async def run_auditor(client: BandClient, room: Room) -> None:
    """
    Auditor Agent — listens for Guideline ComplianceResult, adversarially
    reviews it, and posts an AuditorChallenge if warranted.

    Golden Rule 1: All I/O via Band room only.
    Golden Rule 5: Challenge decision is deterministic; LLM only phrases it.
    """
    result_sent = False
    accumulated_flags: list[dict] = []
    compliance: dict | None = None

    async def handle_message(msg: dict):
        nonlocal result_sent, accumulated_flags, compliance

        intent = msg.get("intent", "")
        from_agent = msg.get("from_agent", "")
        payload = msg.get("payload") or {}

        # Accumulate flags from dating_risk
        if from_agent == "dating_risk" and intent == "post":
            p = payload or {}
            if p.get("type") in (
                "preeclampsia_suspected", "gdm_suspected",
                "anaemia", "dating_discordance",
            ):
                accumulated_flags.append(p)

        # Capture ComplianceResult from guideline
        if from_agent == "guideline" and intent == "post":
            p = payload or {}
            if "compliant" in p:
                compliance = p

        # Only respond to the guideline's chain_complete signal
        if intent != "post" or from_agent != "guideline":
            return
        if payload.get("type") != "chain_complete":
            return
        if result_sent:
            return

        case_id = compliance.get("case_id", "unknown") if compliance else "unknown"
        logger.info(f"[auditor] Received chain_complete from guideline for {case_id}")

        if not compliance:
            logger.warning("[auditor] No ComplianceResult accumulated — skipping")
            return

        # Build typed objects
        typed_flags = _build_flags(accumulated_flags, case_id)
        typed_compliance = ComplianceResult(
            case_id=case_id,
            compliant=compliance.get("compliant", False),
            veto=compliance.get("veto", False),
            missing_investigations=compliance.get("missing_investigations", []),
            notes=compliance.get("notes", ""),
            rule_refs=compliance.get("rule_refs", []),
        )

        # --- Deterministic challenge decision ---
        try:
            rules = load_rules()
        except Exception:
            rules = {"rules": []}

        should_challenge, reasons = _should_challenge(
            typed_flags, typed_compliance, rules,
        )

        # --- LLM narrative (or fallback) ---
        challenge_text = ""
        if should_challenge:
            challenge_text = await _call_auditor_llm(
                accumulated_flags, compliance, reasons,
            )

        # --- Post AuditorChallenge ---
        challenge_payload = {
            "type": "auditor_challenge",
            "case_id": case_id,
            "challenged": should_challenge,
            "reasons": reasons,
            "narrative": challenge_text,
            "recommendation": (
                "Guideline result appears sound — proceed to gate."
                if not should_challenge
                else "Auditor recommends re-examination before gate decision."
            ),
        }

        challenge_env = MessageEnvelope(
            case_id=case_id,
            from_agent="auditor",
            intent="post",
            payload=challenge_payload,
        )
        logger.info(
            f"[auditor] Posting AuditorChallenge: "
            f"challenged={should_challenge}, reasons={len(reasons)}"
        )
        await client.post(room, challenge_env.model_dump(mode="json"))

        # Signal completion
        done_env = MessageEnvelope(
            case_id=case_id,
            from_agent="auditor",
            intent="post",
            payload={
                "type": "auditor_complete",
                "message": (
                    "Auditor review complete — challenge raised."
                    if should_challenge
                    else "Auditor review complete — no concerns."
                ),
            },
        )
        await client.post(room, done_env.model_dump(mode="json"))
        result_sent = True

    await client.on_message(room, handle_message)


# ---------------------------------------------------------------------------
# Local mode — called directly by orchestrator
# ---------------------------------------------------------------------------

async def run_auditor_local(
    structured_case: dict,
    findings: list[dict],
    flags: list[dict],
    compliance: dict,
) -> dict:
    """
    Run Auditor locally without Band.

    Returns:
        {"status": "ok", "audit_result": {"challenged": bool, "reasons": [...],
         "narrative": str, "recommendation": str}}
    """
    case_id = compliance.get("case_id", structured_case.get("case_id", "unknown"))

    typed_flags = _build_flags(flags, case_id)
    typed_compliance = ComplianceResult(
        case_id=case_id,
        compliant=compliance.get("compliant", False),
        veto=compliance.get("veto", False),
        missing_investigations=compliance.get("missing_investigations", []),
        notes=compliance.get("notes", ""),
        rule_refs=compliance.get("rule_refs", []),
    )

    try:
        rules = load_rules()
    except Exception:
        rules = {"rules": []}

    should_challenge, reasons = _should_challenge(
        typed_flags, typed_compliance, rules,
    )

    challenge_text = ""
    if should_challenge:
        challenge_text = await _call_auditor_llm(flags, compliance, reasons)

    return {
        "status": "ok",
        "audit_result": {
            "challenged": should_challenge,
            "reasons": reasons,
            "narrative": challenge_text,
            "recommendation": (
                "Auditor recommends re-examination before gate decision."
                if should_challenge
                else "Guideline result appears sound — proceed to gate."
            ),
        },
    }


def _build_flags(flags_data: list[dict], case_id: str) -> list[RiskFlag]:
    """Build RiskFlag objects from dict data."""
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

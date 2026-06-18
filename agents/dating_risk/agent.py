"""
agents/dating_risk/agent.py — Dating & Risk Agent.

Computes gestational age (LMP & ultrasound), detects discordance,
reads the ultrasound, fires risk flags. All via Band.
Golden Rule 5: Math & rules are deterministic — NEVER computed in the LLM.
Golden Rule 4: Imaging is decision-support only.
§4.3 SDD, P9 Playbook.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from band_wrapper.client import BandClient, Room
from schemas import (
    StructuredCase,
    Finding,
    RiskFlag,
    MessageEnvelope,
)

from tools.ga_calc import (
    ga_from_lmp,
    ga_from_ultrasound,
    discordance_weeks as calc_discordance,
    is_discordant,
)
from tools.imaging import read_ultrasound
from risk.rules import evaluate_all

logger = logging.getLogger(__name__)


async def run_dating_risk(client: BandClient, room: Room) -> None:
    """
    Dating & Risk Agent — listens for handoff from intake, computes analysis.

    Steps (P9 Playbook):
      1. Read StructuredCase from room
      2. Call tools.ga_calc for GA (LMP + ultrasound) and discordance — NEVER in LLM
      3. Call tools.imaging.read_ultrasound for decision-support observations
      4. Call risk.rules.evaluate_all for RiskFlags
      5. Build Finding + post + handoff to guideline

    Golden Rule 1: All I/O via Band room only.
    Golden Rule 5: Math is deterministic — tools.ga_calc + risk.rules, not LLM.
    """
    result_sent = False

    async def handle_message(msg: dict):
        nonlocal result_sent
        if result_sent:
            return

        intent = msg.get("intent", "")
        from_agent = msg.get("from_agent", "")
        to_role = msg.get("to_role", "")

        # Only respond to handoff from intake addressed to dating_risk
        if intent != "handoff" or from_agent != "intake" or to_role != "dating_risk":
            return

        # Find the StructuredCase from the room — it was posted before the handoff
        # In the Band flow, the StructuredCase payload is in an earlier message.
        # For the local/direct flow, we read it from the handoff context.
        # Here we reconstruct it from whatever context we have.
        logger.info(f"[dating_risk] Received handoff from intake")

        # The structured case should be in the room's accumulated context.
        # For Band: we'd read from room messages. For local: it's passed directly.
        # We get it from the orchestrator's seeded context or prior post.
        raw_case = _find_structured_case_in_context(msg)

        if not raw_case:
            logger.warning("[dating_risk] No StructuredCase found in context — skipping")
            return

        case_id = raw_case.get("case_id", "unknown")

        # --- Step 2: GA calculation (deterministic tools, NEVER LLM) ---
        ga_lmp = None
        ga_usg = None
        disc_weeks = None
        discordant = False

        try:
            lmp_date_val = _parse_date(raw_case.get("lmp_date"))
            usg_date_val = _parse_date(raw_case.get("usg_date"))

            if lmp_date_val and usg_date_val:
                ga_lmp = round(ga_from_lmp(lmp_date_val, usg_date_val), 1)

            usg_meas = raw_case.get("usg_measurement") or {}
            if usg_meas and usg_meas.get("value_mm"):
                meas_type = usg_meas.get("type", "BPD")
                value_mm = float(usg_meas["value_mm"])
                try:
                    ga_usg = round(ga_from_ultrasound(meas_type, value_mm), 1)
                except ValueError:
                    logger.warning(f"[dating_risk] Unsupported measurement type: {meas_type}")

            if ga_lmp is not None and ga_usg is not None:
                disc_weeks = calc_discordance(ga_lmp, ga_usg)
                discordant = is_discordant(disc_weeks)
        except Exception as e:
            logger.error(f"[dating_risk] GA calculation error: {e}")

        # --- Step 3: Ultrasound read (decision-support) ---
        imaging_result = {"observations": "No image provided.", "confidence": "low"}
        image_ref = raw_case.get("usg_image_ref", "")
        if image_ref:
            try:
                imaging_result = await read_ultrasound(image_ref)
            except Exception as e:
                logger.warning(f"[dating_risk] Imaging degraded: {e}")
                imaging_result = {
                    "observations": f"Imaging unavailable — {str(e)[:100]}",
                    "confidence": "low",
                }

        # --- Step 4: Risk flags (deterministic rules) ---
        try:
            # Build a StructuredCase-like object for evaluate_all
            structured_obj = _build_structured_obj(raw_case)
            flags: list[RiskFlag] = evaluate_all(structured_obj)
        except Exception as e:
            logger.error(f"[dating_risk] Risk evaluation error: {e}")
            flags = []

        # --- Step 5: Build Finding + post ---
        finding = Finding(
            case_id=case_id,
            ga_lmp_weeks=ga_lmp,
            ga_usg_weeks=ga_usg,
            discordance_weeks=disc_weeks,
            discordant=discordant,
            imaging_observations=imaging_result["observations"],
            imaging_confidence=imaging_result["confidence"],
        )

        # Post Finding
        finding_env = MessageEnvelope(
            case_id=case_id,
            from_agent="dating_risk",
            intent="post",
            payload=finding.model_dump(mode="json"),
        )
        logger.info(
            f"[dating_risk] Posting Finding: GA(LMP)={ga_lmp}wk, "
            f"GA(USG)={ga_usg}wk, discordance={disc_weeks}wk, "
            f"discordant={discordant}, flags={len(flags)}"
        )
        await client.post(room, finding_env.model_dump(mode="json"))

        # Post RiskFlags
        for flag in flags:
            flag_env = MessageEnvelope(
                case_id=case_id,
                from_agent="dating_risk",
                intent="post",
                payload=flag.model_dump(mode="json"),
            )
            logger.info(f"[dating_risk] RiskFlag: {flag.type} ({flag.severity})")
            await client.post(room, flag_env.model_dump(mode="json"))

        # Handoff to Guideline
        handoff_env = MessageEnvelope(
            case_id=case_id,
            from_agent="dating_risk",
            intent="handoff",
            to_role="guideline",
            payload={
                "message": "Findings and risk flags posted. Guideline check required.",
                "finding_id": finding.finding_id,
            },
        )
        await client.post(room, handoff_env.model_dump(mode="json"))
        result_sent = True

    await client.on_message(room, handle_message)


# ---------------------------------------------------------------------------
# Local mode — no Band required, for testing and orchestrator direct mode
# ---------------------------------------------------------------------------

async def run_dating_risk_local(structured_case: dict) -> dict:
    """
    Run Dating & Risk locally without Band.

    Args:
        structured_case: Normalised StructuredCase dict from intake.

    Returns:
        {"status": "ok", "finding": dict, "flags": list[dict]}
    """
    case_id = structured_case.get("case_id", "unknown")

    # GA calculation
    ga_lmp = None
    ga_usg = None
    disc_weeks = None
    discordant = False

    try:
        lmp_date_val = _parse_date(structured_case.get("lmp_date"))
        usg_date_val = _parse_date(structured_case.get("usg_date"))

        if lmp_date_val and usg_date_val:
            ga_lmp = round(ga_from_lmp(lmp_date_val, usg_date_val), 1)

        usg_meas = structured_case.get("usg_measurement") or {}
        if usg_meas and usg_meas.get("value_mm"):
            meas_type = usg_meas.get("type", "BPD")
            value_mm = float(usg_meas["value_mm"])
            try:
                ga_usg = round(ga_from_ultrasound(meas_type, value_mm), 1)
            except ValueError:
                pass

        if ga_lmp is not None and ga_usg is not None:
            disc_weeks = calc_discordance(ga_lmp, ga_usg)
            discordant = is_discordant(disc_weeks)
    except Exception as e:
        logger.error(f"GA calculation error: {e}")

    # Imaging
    imaging_result = {"observations": "No image provided.", "confidence": "low"}
    image_ref = structured_case.get("usg_image_ref", "")
    if image_ref:
        try:
            imaging_result = await read_ultrasound(image_ref)
        except Exception as e:
            imaging_result = {
                "observations": f"Imaging unavailable — {str(e)[:100]}",
                "confidence": "low",
            }

    # Risk flags
    structured_obj = _build_structured_obj(structured_case)
    flags = evaluate_all(structured_obj)

    finding = Finding(
        case_id=case_id,
        ga_lmp_weeks=ga_lmp,
        ga_usg_weeks=ga_usg,
        discordance_weeks=disc_weeks,
        discordant=discordant,
        imaging_observations=imaging_result["observations"],
        imaging_confidence=imaging_result["confidence"],
    )

    return {
        "status": "ok",
        "finding": finding.model_dump(mode="json"),
        "flags": [f.model_dump(mode="json") for f in flags],
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(val: Any) -> date | None:
    """Parse a date from string or date object."""
    if val is None:
        return None
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        try:
            return date.fromisoformat(val)
        except ValueError:
            return None
    return None


def _find_structured_case_in_context(msg: dict) -> dict | None:
    """Extract StructuredCase from message context.

    In the real Band flow, the orchestrator seeds the room with the case.
    The handoff message from intake may carry a reference.
    """
    payload = msg.get("payload") or {}
    # The handoff message itself carries minimal info; the StructuredCase
    # was posted separately. The orchestrator provides it.
    # For now, pass through the full raw case from the orchestrator seed.
    return payload.get("structured_case") or payload.get("case") or {}


def _build_structured_obj(case_dict: dict):
    """Build a minimal StructuredCase-like object for evaluate_all."""
    class StructObj:
        def __init__(self, d):
            self.case_id = d.get("case_id", "unknown")
            self.vitals = d.get("vitals", {})
            self.labs = d.get("labs", {})

    return StructObj(case_dict)

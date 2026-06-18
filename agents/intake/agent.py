"""
agents/intake/agent.py — Intake Agent.

Normalises + validates raw case → StructuredCase, posts + hands off via Band.
Golden Rule 1: All communication through Band room only.
Golden Rule 5: LLM extracts/restructures provided data only — never invents values.
§4.2 SDD, P8 Playbook.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import date, datetime
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError as PydanticValidationError

from band_wrapper.client import BandClient, Room
from schemas import (
    CaseInput,
    StructuredCase,
    ValidationResult,
    MessageEnvelope,
)

load_dotenv()
logger = logging.getLogger(__name__)

AIML_API_KEY = os.getenv("AIML_API_KEY", "")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://api.aimlapi.com/v1")
INTAKE_MODEL = os.getenv("AIML_INTAKE_MODEL", "gpt-4o")

# ---------------------------------------------------------------------------
# System prompt — P8 Playbook: extract, never invent
# ---------------------------------------------------------------------------

INTAKE_SYSTEM_PROMPT = """\
You are the Intake Agent in a multi-agent antenatal review system running on Band.

TASK: Read the raw case data and return ONLY a StructuredCase JSON matching this exact schema:

{
  "case_id": "<provided case id>",
  "normalised": true,
  "lmp_date": "YYYY-MM-DD",
  "usg_date": "YYYY-MM-DD",
  "usg_measurement": {"type": "BPD|CRL|FL|HC|AC", "value_mm": number},
  "usg_image_ref": "<path string>",
  "vitals": {"bp_systolic": int, "bp_diastolic": int},
  "labs": {"urine_protein": "string", "fasting_glucose_mg_dl": number|null, "hb_g_dl": number|null},
  "validation": {"missing_fields": [], "warnings": []}
}

CRITICAL RULES:
1. Restructure the provided data into the schema. Do NOT invent or guess any value.
2. If a field is missing from the input, leave it as null/empty and add it to validation.missing_fields.
3. If lmp_date, usg_date, vitals, or labs are missing → add to missing_fields.
4. Do NOT diagnose, assess risk, or provide clinical opinions.
5. Return ONLY the JSON object — no markdown, no explanation.
"""

# Mandatory top-level fields that must be present
MANDATORY_FIELDS = ["lmp_date", "usg_date", "vitals", "labs"]


async def _call_intake_llm(raw_case: dict) -> dict:
    """Call AI/ML API to normalise raw case into StructuredCase JSON."""
    if not AIML_API_KEY:
        # Fallback: normalise locally without LLM
        logger.info("AIML_API_KEY not set — normalising locally")
        return _local_normalise(raw_case)

    payload = {
        "model": INTAKE_MODEL,
        "messages": [
            {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(raw_case, default=str),
            },
        ],
        "max_tokens": 1024,
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/antenatal-review-board",
        "X-Title": "Antenatal Review Board",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AIML_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception:
        # OpenRouter may be unavailable — local normalise works perfectly
        pass
        return _local_normalise(raw_case)


def _local_normalise(raw_case: dict) -> dict:
    """Normalise raw case dict to StructuredCase shape without an LLM call.

    Golden Rule 5: Extract only what's provided — never invent values.
    """
    missing: list[str] = []
    warnings: list[str] = []

    # Check mandatory fields
    for field in MANDATORY_FIELDS:
        if field not in raw_case or raw_case[field] is None:
            missing.append(field)

    # Parse dates
    lmp_date = None
    usg_date = None
    try:
        if raw_case.get("lmp_date"):
            lmp_date = str(raw_case["lmp_date"])
    except Exception:
        missing.append("lmp_date")
    try:
        if raw_case.get("usg_date"):
            usg_date = str(raw_case["usg_date"])
    except Exception:
        missing.append("usg_date")

    # Parse vitals (None → 0, meaning "not measured" — keeps the schema valid)
    vitals_raw = raw_case.get("vitals", {}) or {}
    vitals = {
        "bp_systolic": vitals_raw.get("bp_systolic") or 0,
        "bp_diastolic": vitals_raw.get("bp_diastolic") or 0,
    }
    if not vitals_raw or (not vitals_raw.get("bp_systolic") and not vitals_raw.get("bp_diastolic")):
        missing.append("vitals")

    # Parse labs (None → empty/None, never the string "None")
    labs_raw = raw_case.get("labs", {}) or {}
    labs = {
        "urine_protein": str(labs_raw.get("urine_protein") or ""),
        "fasting_glucose_mg_dl": labs_raw.get("fasting_glucose_mg_dl"),
        "hb_g_dl": labs_raw.get("hb_g_dl"),
    }
    if not labs_raw:
        missing.append("labs")

    # Parse USG measurement — only keep it if a positive value was actually given
    usg_meas_raw = raw_case.get("usg_measurement") or {}
    usg_measurement = None
    if usg_meas_raw and usg_meas_raw.get("value_mm"):
        try:
            val = float(usg_meas_raw["value_mm"])
            if val > 0:
                usg_measurement = {
                    "type": usg_meas_raw.get("type", "BPD"),
                    "value_mm": val,
                }
        except (TypeError, ValueError):
            usg_measurement = None

    # Demographic warnings
    demographics = raw_case.get("demographics", {}) or {}
    if not demographics.get("age"):
        warnings.append("age not provided")
    if not demographics.get("parity"):
        warnings.append("parity not provided")

    return {
        "case_id": raw_case.get("case_id", "unknown"),
        "normalised": len(missing) == 0,
        "lmp_date": lmp_date,
        "usg_date": usg_date,
        "usg_measurement": usg_measurement,
        "usg_image_ref": raw_case.get("usg_image_ref", ""),
        "vitals": vitals,
        "labs": labs,
        "validation": {
            "missing_fields": sorted(set(missing)),
            "warnings": warnings,
        },
    }


def _validate_and_build(normalised: dict) -> tuple[StructuredCase | None, dict | None]:
    """
    Build a StructuredCase from the normalised dict.

    Partial-data policy (Golden Rule 5 still holds — we never invent values):
    missing fields are recorded in validation.missing_fields and the case still
    proceeds. Downstream agents compute GA / risk / compliance from whatever is
    present and the guideline check surfaces what's missing, rather than the
    review being blocked at the door. Only a genuine schema corruption (an
    unparseable structure we cannot coerce) returns a validation_error.
    """
    missing = list(normalised.get("validation", {}).get("missing_fields", []))
    warnings = list(normalised.get("validation", {}).get("warnings", []))

    # Parse dates — a bad or absent date becomes None + a note, never a hard stop
    lmp_date = None
    usg_date = None
    if normalised.get("lmp_date"):
        try:
            lmp_date = date.fromisoformat(str(normalised["lmp_date"]))
        except (ValueError, TypeError):
            warnings.append("lmp_date unparseable — ignored")
    if normalised.get("usg_date"):
        try:
            usg_date = date.fromisoformat(str(normalised["usg_date"]))
        except (ValueError, TypeError):
            warnings.append("usg_date unparseable — ignored")

    # Coerce the structured sub-objects so partial data still satisfies the
    # schema. 0 / "" / None all read as "not measured" downstream.
    vitals_raw = normalised.get("vitals") or {}
    vitals = {
        "bp_systolic": vitals_raw.get("bp_systolic") or 0,
        "bp_diastolic": vitals_raw.get("bp_diastolic") or 0,
    }
    labs_raw = normalised.get("labs") or {}
    labs = {
        "urine_protein": str(labs_raw.get("urine_protein") or ""),
        "fasting_glucose_mg_dl": labs_raw.get("fasting_glucose_mg_dl"),
        "hb_g_dl": labs_raw.get("hb_g_dl"),
    }

    # USG measurement is optional and only kept when a positive value exists
    usg_measurement = normalised.get("usg_measurement")
    if isinstance(usg_measurement, dict):
        if not usg_measurement.get("value_mm") or float(usg_measurement.get("value_mm") or 0) <= 0:
            usg_measurement = None

    try:
        sc = StructuredCase(
            case_id=normalised.get("case_id", "unknown"),
            normalised=len(missing) == 0,
            lmp_date=lmp_date,
            usg_date=usg_date,
            usg_measurement=usg_measurement,
            usg_image_ref=normalised.get("usg_image_ref", ""),
            vitals=vitals,
            labs=labs,
            validation=ValidationResult(
                missing_fields=sorted(set(missing)),
                warnings=warnings,
            ),
        )
        return sc, None
    except PydanticValidationError as e:
        logger.error(f"Pydantic validation failed: {e}")
        return None, {
            "msg_id": f"err-{normalised.get('case_id', 'unknown')}",
            "case_id": normalised.get("case_id", "unknown"),
            "from_agent": "intake",
            "intent": "post",
            "to_role": None,
            "payload": {
                "type": "validation_error",
                "errors": str(e),
                "message": "Schema validation failed.",
            },
            "produced_at": datetime.utcnow().isoformat(),
        }


# ---------------------------------------------------------------------------
# Main agent entry point — called via Band
# ---------------------------------------------------------------------------

async def run_intake(client: BandClient, room: Room) -> None:
    """
    Intake Agent — listens for raw case, normalises, validates, posts + hands off.

    Triggered by receiving a message with intent='post' from 'orchestrator'
    containing the raw case payload. Posts validation_error on failure,
    or StructuredCase + handoff on success.

    Golden Rule 1: All I/O via band/client.py — no direct agent calls.
    Golden Rule 5: LLM extracts only; never invents values.
    """
    result_sent = False

    async def handle_message(msg: dict):
        nonlocal result_sent
        if result_sent:
            return  # Already processed

        from_agent = msg.get("from_agent", "")
        intent = msg.get("intent", "")
        payload = msg.get("payload", {})

        # Only respond to the orchestrator's seed message
        if from_agent != "orchestrator" or intent not in ("post", None):
            return

        logger.info(f"[intake] Received case from orchestrator: {msg.get('case_id')}")

        # Step 1: Normalise (LLM or local fallback)
        normalised = await _call_intake_llm(payload)

        # Step 2: Validate + build StructuredCase
        structured, validation_error = _validate_and_build(normalised)

        if validation_error:
            # Mandatory fields missing → post error, NO handoff
            logger.warning(f"[intake] Validation failed: {validation_error}")
            await client.post(room, validation_error)
            result_sent = True
            return

        # Step 3: Post StructuredCase to room
        post_env = MessageEnvelope(
            case_id=structured.case_id,
            from_agent="intake",
            intent="post",
            payload=structured.model_dump(mode="json"),
        )
        logger.info(f"[intake] Posting StructuredCase for {structured.case_id}")
        await client.post(room, post_env.model_dump(mode="json"))

        # Step 4: Handoff to Dating & Risk
        handoff_env = MessageEnvelope(
            case_id=structured.case_id,
            from_agent="intake",
            intent="handoff",
            to_role="dating_risk",
            payload={"message": "StructuredCase ready for analysis."},
        )
        logger.info(f"[intake] Handing off to dating_risk")
        await client.post(room, handoff_env.model_dump(mode="json"))
        result_sent = True

    await client.on_message(room, handle_message)


# ---------------------------------------------------------------------------
# Local test entry point (no Band required)
# ---------------------------------------------------------------------------

async def run_intake_local(raw_case: dict) -> dict:
    """
    Run intake locally without Band — useful for testing and orchestrator direct mode.

    Returns:
        {"status": "ok", "structured_case": dict} or
        {"status": "validation_error", "error": dict}
    """
    # Input reaching the orchestrator is already structured JSON (the free-text
    # → JSON step happens earlier in /extract). Normalise deterministically so
    # the pipeline is offline-safe and partial cases still flow through.
    normalised = _local_normalise(raw_case)
    structured, validation_error = _validate_and_build(normalised)

    if validation_error:
        return {"status": "validation_error", "error": validation_error}

    return {
        "status": "ok",
        "structured_case": structured.model_dump(mode="json"),
    }

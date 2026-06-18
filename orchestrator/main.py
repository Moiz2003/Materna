"""
orchestrator/main.py — FastAPI application.

REST routes per §8 SDD:
  POST   /cases              — submit a new case
  GET    /cases/{id}         — case status + findings + flags
  GET    /cases/{id}/room    — Band room conversation (stub)
  POST   /cases/{id}/decision — record human verdict
  GET    /cases/{id}/packet  — download sealed PDF
  GET    /cases/{id}/audit   — audit chain + verification
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import os

import httpx
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from orchestrator.lifecycle import (
    handle_case_local,
    get_case_state,
    get_case_audit,
    _load_case_json,
    CaseStatus,
)
from schemas import RiskFlag

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Antenatal Review Board",
    description="Band-coordinated multi-agent obstetric review with human-in-the-loop gate.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class DecisionRequest(BaseModel):
    verdict: str  # "approve" or "override"
    note: str = ""
    reviewer: str = "Dr. Saima Javed"

class ExtractRequest(BaseModel):
    text: str  # free-text clinical notes


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "antenatal-review-board"}


@app.post("/extract")
async def extract_case(req: ExtractRequest):
    """
    Smart Extraction: convert free-text clinical notes into structured CaseInput JSON.

    Tries Gemini first, then falls back to OpenRouter (AIML) — so a Gemini
    429/quota error no longer 502s the doctor's text extraction (the image
    endpoint already had this fallback; the text one did not).
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    openrouter_key = os.getenv("AIML_API_KEY", "")
    openrouter_url = os.getenv("AIML_BASE_URL", "https://openrouter.ai/api/v1")

    if not gemini_key and not openrouter_key:
        raise HTTPException(status_code=503, detail="No AI API key configured")

    system_prompt = """\
You are a medical data extraction assistant for an antenatal review system.
Extract structured antenatal case data from the clinical notes provided.

Return ONLY valid JSON matching this exact schema:
{
  "case_id": "C-XXXX",
  "demographics": {"age": number, "parity": "string like G3P2 or null"},
  "lmp_date": "YYYY-MM-DD or null",
  "usg_date": "YYYY-MM-DD or null",
  "usg_measurement": {"type": "BPD|CRL|FL|HC|AC", "value_mm": number} or null,
  "vitals": {"bp_systolic": number, "bp_diastolic": number},
  "labs": {"urine_protein": "negative|1+|2+|3+ or null", "fasting_glucose_mg_dl": number or null, "hb_g_dl": number or null}
}

RULES:
- Extract ONLY what is explicitly stated. Use null for missing fields.
- If a date is mentioned like "LMP was Dec 1 2025", convert to YYYY-MM-DD.
- If BP is "150/98", bp_systolic=150, bp_diastolic=98.
- Generate a case_id like C-XXXX where XXXX is random hex.
- If parity is mentioned as "G3P2" or "gravida 3 para 2", use "G3P2".
- Do NOT include markdown, explanations, or extra text. ONLY the JSON object."""

    last_error = None

    # --- Attempt 1: Gemini native API ---
    if gemini_key:
        try:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    gemini_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{"text": system_prompt + "\n\nClinical notes:\n" + req.text}]
                        }],
                        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"status": "ok", "case": _strip_json(content)}
        except Exception as e:
            last_error = f"Gemini: {str(e)[:160]}"
            logger.warning(f"/extract Gemini failed, trying OpenRouter fallback: {e}")

    # --- Attempt 2: OpenRouter (AIML) fallback ---
    if openrouter_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{openrouter_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/antenatal-review-board",
                        "X-Title": "Antenatal Review Board",
                    },
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": "Clinical notes:\n" + req.text},
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
            return {"status": "ok", "case": _strip_json(content)}
        except Exception as e:
            last_error = f"OpenRouter: {str(e)[:160]}"

    raise HTTPException(status_code=502, detail=f"All AI providers failed. Last error: {last_error}")


@app.post("/extract-image")
async def extract_from_image(image: UploadFile = File(...)):
    """
    Extract clinical data from an uploaded ultrasound/report image using Gemini Vision.
    Supports English and Urdu text. Returns extracted text and structured CaseInput JSON.
    """
    import base64 as _b64

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openrouter_key = os.getenv("AIML_API_KEY", "")
    openrouter_url = os.getenv("AIML_BASE_URL", "https://openrouter.ai/api/v1")

    if not gemini_key and not openrouter_key:
        raise HTTPException(status_code=503, detail="No AI API key configured")

    # Read and encode image
    img_bytes = await image.read()
    img_b64 = _b64.b64encode(img_bytes).decode("utf-8")

    # Detect MIME type
    mime = image.content_type or "image/jpeg"
    if "png" in (image.filename or "").lower():
        mime = "image/png"

    system_prompt = """\
You are a medical data extraction AI for an antenatal (pregnancy) review system in Pakistan.
Doctors' handwriting is often hard to read. Your job is NOT to guess — it is to extract
only what you can read with HIGH confidence and to clearly flag everything else so a human
clinician can confirm or fill it in.

STEP 1: Transcribe ALL visible text exactly as it appears (English and Urdu).
STEP 2: Extract structured antenatal data, with an honest confidence for every field.

Return ONLY valid JSON in this format:
{
  "raw_text": "all visible text transcribed exactly, including Urdu",
  "extracted_data": {
    "case_id": "C-XXXX",
    "demographics": {"age": number_or_null, "parity": "string_or_null"},
    "lmp_date": "YYYY-MM-DD or null",
    "usg_date": "YYYY-MM-DD or null",
    "usg_measurement": {"type": "BPD|CRL|FL|HC|AC", "value_mm": number} or null,
    "vitals": {"bp_systolic": number_or_null, "bp_diastolic": number_or_null},
    "labs": {"urine_protein": "string_or_null", "fasting_glucose_mg_dl": number_or_null, "hb_g_dl": number_or_null}
  },
  "field_confidence": {
    "demographics.age": "high|medium|low|absent",
    "demographics.parity": "high|medium|low|absent",
    "lmp_date": "high|medium|low|absent",
    "usg_date": "high|medium|low|absent",
    "usg_measurement": "high|medium|low|absent",
    "vitals.bp_systolic": "high|medium|low|absent",
    "vitals.bp_diastolic": "high|medium|low|absent",
    "labs.urine_protein": "high|medium|low|absent",
    "labs.fasting_glucose_mg_dl": "high|medium|low|absent",
    "labs.hb_g_dl": "high|medium|low|absent"
  },
  "needs_review": [
    {"field": "lmp_date", "reason": "handwriting illegible", "best_guess": "2025-12-01"}
  ]
}

RULES:
- Put a value in extracted_data ONLY when confidence is "high". For "medium", "low", or
  "absent", set that field to null in extracted_data — never guess into the data.
- For every field you set to null because it was unreadable or missing, add an entry to
  needs_review with a short reason and, if you have one, a best_guess (the human will confirm).
- "absent" = the field is genuinely not on the page. "low"/"medium" = it is there but you
  cannot read it confidently.
- Transcribe Urdu accurately (Urdu script, not Romanized).
- If BP is clearly "150/98", bp_systolic=150, bp_diastolic=98 (high confidence).
- If a date is clearly "10 June 2026", convert to 2026-06-10.
- Generate a case_id like C-XXXX where XXXX is random hex.
- Do NOT include markdown or extra text. ONLY the JSON object."""

    # Try Gemini first, fall back to OpenRouter
    last_error = None

    # --- Attempt 1: Gemini native API ---
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(url, headers={"Content-Type": "application/json"}, json={
                    "contents": [{"parts": [
                        {"text": system_prompt},
                        {"inlineData": {"mimeType": mime, "data": img_b64}},
                    ]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2048},
                })
                if resp.status_code == 429:
                    raise httpx.HTTPStatusError("Gemini quota exceeded", request=resp.request, response=resp)
                resp.raise_for_status()
                data = resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return _parse_extract_response(content)
        except Exception as e:
            last_error = str(e)[:200]

    # --- Attempt 2: OpenRouter fallback ---
    if openrouter_key:
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post(
                    f"{openrouter_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/antenatal-review-board",
                        "X-Title": "Antenatal Review Board",
                    },
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                            ],
                        }],
                        "max_tokens": 2048,
                        "temperature": 0.1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"].strip()
            return _parse_extract_response(content)
        except Exception as e:
            last_error = str(e)[:200]

    raise HTTPException(status_code=502, detail=f"All AI providers failed. Last error: {last_error}")


# Fields the doctor may need to confirm, with human-readable labels and the
# dotted path into extracted_data. Order = order shown in the confirm panel.
_EXTRACT_FIELD_SPECS: list[tuple[str, str]] = [
    ("demographics.age", "Age"),
    ("demographics.parity", "Parity (e.g. G3P2)"),
    ("lmp_date", "LMP date"),
    ("usg_date", "USG date"),
    ("usg_measurement", "USG measurement"),
    ("vitals.bp_systolic", "BP systolic"),
    ("vitals.bp_diastolic", "BP diastolic"),
    ("labs.urine_protein", "Urine protein"),
    ("labs.fasting_glucose_mg_dl", "Fasting glucose (mg/dL)"),
    ("labs.hb_g_dl", "Haemoglobin (g/dL)"),
]


def _get_path(obj: dict, path: str):
    """Read a dotted path (e.g. 'vitals.bp_systolic') from a nested dict."""
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _is_present(path: str, value: Any) -> bool:
    """Whether a confidently-extracted value actually exists for a field."""
    if path == "usg_measurement":
        return isinstance(value, dict) and bool(value.get("value_mm"))
    return value not in (None, "", [], {})


def _build_needs_review(result: dict) -> list[dict]:
    """Deterministically derive the list of fields the human should confirm.

    A field needs review if it is absent from extracted_data OR the model marked
    it below "high" confidence. This stays correct even when the model omits or
    malforms its own needs_review array. Any reason/best_guess the model did give
    is merged in.
    """
    extracted = result.get("extracted_data") or {}
    confidence = result.get("field_confidence") or {}
    model_hints = {
        item.get("field"): item
        for item in (result.get("needs_review") or [])
        if isinstance(item, dict) and item.get("field")
    }

    needs: list[dict] = []
    for path, label in _EXTRACT_FIELD_SPECS:
        value = _get_path(extracted, path)
        conf = str(confidence.get(path, "")).lower()
        present = _is_present(path, value)
        if present and conf in ("high", ""):
            continue  # confidently extracted — no confirmation needed
        hint = model_hints.get(path, {})
        if not present:
            reason = hint.get("reason") or "Not detected in image"
        else:
            reason = hint.get("reason") or f"Low confidence ({conf or 'uncertain'}) — please confirm"
        needs.append({
            "field": path,
            "label": label,
            "confidence": conf or ("absent" if not present else "low"),
            "reason": reason,
            "best_guess": hint.get("best_guess"),
        })
    return needs


def _strip_json(content: str) -> dict:
    """Strip markdown code fences and parse a JSON object from an LLM response."""
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    return json.loads(content)


def _parse_extract_response(content: str) -> dict:
    """Parse the AI response and attach a deterministic human-review list."""
    result = _strip_json(content)
    result["needs_review"] = _build_needs_review(result)
    result.setdefault("field_confidence", {})
    return {"status": "ok", **result}


@app.post("/cases")
async def submit_case(
    background_tasks: BackgroundTasks,
    case: str = Form(...),
    usg_image: UploadFile | None = File(None),
):
    """
    Submit a new antenatal case and start the review pipeline.

    Accepts multipart/form-data:
      - case: JSON string of the case payload
      - usg_image: optional ultrasound image file

    Returns case_id and initial status. Processing runs in background.
    """
    try:
        case_data = json.loads(case)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid case JSON: {e}")

    case_id = case_data.get("case_id") or f"C-{os.urandom(2).hex().upper()}"
    # Write the resolved id back so the background pipeline, the audit chain, and
    # the id returned to the UI all agree (an empty case_id otherwise ran the
    # pipeline under "" while the UI polled the generated id → "stuck" + audit BROKEN).
    case_data["case_id"] = case_id

    # Save uploaded image if provided
    if usg_image and usg_image.filename:
        usg_dir = Path(__file__).parent.parent / "data" / "usg"
        usg_dir.mkdir(parents=True, exist_ok=True)
        image_path = usg_dir / f"{case_id}.png"
        content = await usg_image.read()
        image_path.write_bytes(content)
        case_data["usg_image_ref"] = str(image_path.relative_to(
            Path(__file__).parent.parent
        ))

    # Store data for background processing
    from orchestrator.lifecycle import _case_store
    _case_store[case_id] = {
        "case_id": case_id,
        "status": CaseStatus.RECEIVED,
        "raw_case": case_data,
    }

    # Run pipeline in background
    background_tasks.add_task(_run_pipeline_background, case_data)

    return JSONResponse(
        status_code=201,
        content={"case_id": case_id, "status": CaseStatus.RECEIVED},
    )


@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get full case state: status, findings, flags, compliance, decision."""
    state = get_case_state(case_id)

    if not state:
        # Try to load from synthetic cases
        case_data = _load_case_json(case_id)
        if case_data:
            return {
                "case_id": case_id,
                "status": "AVAILABLE (not yet processed)",
                "raw_case": case_data,
            }
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    return {
        "case_id": state["case_id"],
        "status": state["status"],
        "structured_case": state.get("structured_case"),
        "finding": state.get("finding"),
        "flags": state.get("flags", []),
        "compliance": state.get("compliance"),
        "escalation_brief": state.get("escalation_brief"),
        "proposed_plan": state.get("proposed_plan"),
        "plan_history": state.get("plan_history", []),
        "human_decision": state.get("human_decision"),
        "packet_ref": state.get("packet_ref"),
        "final_hash": state.get("final_hash"),
        "audit_verified": state.get("audit_verified"),
    }


@app.get("/cases/{case_id}/room")
async def get_room(case_id: str):
    """
    Get the Band room conversation for a case.

    Returns the ordered typed envelopes the agents posted into the shared Band
    room (StructuredCase → Finding/RiskFlags → ComplianceResult → escalation →
    decision). Falls back to the audit trail only if no room messages exist yet.
    """
    state = get_case_state(case_id)
    messages = (state or {}).get("room_messages") or []
    if messages:
        return {
            "case_id": case_id,
            "band_room_id": (state or {}).get("band_room_id"),
            "messages": messages,
        }
    audit = get_case_audit(case_id)
    return {
        "case_id": case_id,
        "band_room_id": (state or {}).get("band_room_id"),
        "messages": audit.get("entries", []),
        "note": "No room messages yet — showing audit entries as a proxy.",
    }


@app.post("/cases/{case_id}/decision")
async def submit_decision(case_id: str, decision: DecisionRequest):
    """
    Record the human OB's verdict on an escalated case.

    verdict must be "approve" or "override".
    """
    if decision.verdict not in ("approve", "override"):
        raise HTTPException(
            status_code=400,
            detail="verdict must be 'approve' or 'override'",
        )

    state = get_case_state(case_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    if state["status"] != CaseStatus.ESCALATED:
        raise HTTPException(
            status_code=409,
            detail=f"Case {case_id} is not awaiting decision (status: {state['status']})",
        )

    from datetime import datetime, timezone
    from audit.chain import append_entry
    from orchestrator.lifecycle import post_to_case_room, _make_env, _persist_state
    from tools.treatment import generate_plan

    # Post the OB's input into the same Band room the agents used
    await post_to_case_room(state, _make_env(case_id, "human", "decision", {
        "reviewer": decision.reviewer,
        "verdict": decision.verdict,
        "note": decision.note,
    }))

    # ===== OVERRIDE: AI re-processes with the OB's input, loop continues =====
    # The case is NOT sealed — a revised plan is drafted and sent back for
    # approval. This repeats until the obstetrician approves.
    if decision.verdict == "override":
        history = state.setdefault("plan_history", [])
        prior_plan = state.get("proposed_plan")
        if prior_plan:
            history.append({**prior_plan, "ob_note": decision.note, "reviewer": decision.reviewer})
        iteration = len(history) + 1
        append_entry(case_id, "human", "override",
                     {"note": decision.note[:200], "iteration": iteration})

        new_plan = await generate_plan(
            state, ob_input=decision.note, prior_plan=prior_plan, iteration=iteration,
        )
        state["proposed_plan"] = new_plan
        state["status"] = CaseStatus.ESCALATED  # still awaiting approval
        append_entry(case_id, "orchestrator", "plan_revised",
                     {"iteration": iteration, "source": new_plan.get("source")})
        await post_to_case_room(state, _make_env(case_id, "orchestrator", "post",
                                                 {"type": "treatment_plan", **new_plan}))
        _persist_state(state)
        logger.info(f"[{case_id}] OB override → plan revised (iteration {iteration}), awaiting approval")
        return JSONResponse(status_code=200, content={
            "status": "revised",
            "iteration": iteration,
            "proposed_plan": new_plan,
            "message": "Plan revised per your input. Review and approve, or override again.",
        })

    # ===== APPROVE: seal with the approved plan + generate the packet =====
    state["human_decision"] = {
        "decision_id": f"D-{case_id}",
        "case_id": case_id,
        "reviewer": decision.reviewer,
        "verdict": "approve",
        "note": decision.note,
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }
    state["status"] = CaseStatus.HUMAN_REVIEWED
    if state.get("proposed_plan"):
        state["proposed_plan"]["approved"] = True
        state["proposed_plan"]["approved_by"] = decision.reviewer
    append_entry(case_id, "human", "approved", {
        "reviewer": decision.reviewer,
        "iteration": (state.get("proposed_plan") or {}).get("iteration", 1),
        "note": decision.note[:200],
    })

    # Seal
    from orchestrator.lifecycle import _compute_final_hash
    final_hash = _compute_final_hash(case_id)
    state["final_hash"] = final_hash
    state["status"] = CaseStatus.SEALED
    append_entry(case_id, "orchestrator", "sealed", {"final_hash": final_hash})

    # Generate packet (now includes the approved treatment plan)
    try:
        from packet.generator import build_packet
        packet_path = await build_packet(
            case=state.get("raw_case", {}),
            findings=[state.get("finding")] if state.get("finding") else [],
            flags=state.get("flags", []),
            decision=state["human_decision"],
            final_hash=final_hash,
            compliance=state.get("compliance"),
            plan=state.get("proposed_plan"),
        )
        state["packet_ref"] = packet_path
    except Exception as e:
        logger.warning(f"Packet generation failed: {e}")
        state["packet_ref"] = f"packets/{case_id}.pdf (error: {e})"

    _persist_state(state)
    logger.info(f"[{case_id}] OB approved plan (iteration "
                f"{(state.get('proposed_plan') or {}).get('iteration', 1)}) — SEALED")
    return JSONResponse(status_code=200, content=state["human_decision"])


@app.get("/cases/{case_id}/packet")
async def get_packet(case_id: str):
    """Download the sealed PDF review packet."""
    state = get_case_state(case_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    if state["status"] not in (CaseStatus.SEALED,):
        raise HTTPException(
            status_code=409,
            detail=f"Case {case_id} not yet sealed (status: {state['status']})",
        )

    packet_ref = state.get("packet_ref", "")
    if not packet_ref:
        raise HTTPException(status_code=404, detail="Packet not generated yet")

    packet_path = Path(packet_ref)
    if not packet_path.is_absolute():
        packet_path = Path(__file__).parent.parent / packet_ref

    if not packet_path.exists():
        raise HTTPException(status_code=404, detail="Packet file not found on disk")

    return FileResponse(
        path=str(packet_path),
        media_type="application/pdf",
        filename=f"{case_id}_review_packet.pdf",
    )


@app.get("/cases/{case_id}/audit")
async def get_audit(case_id: str):
    """Get the audit chain and verification status."""
    return get_case_audit(case_id)


# ---------------------------------------------------------------------------
# Tamper demo — deliberately break audit to prove detection
# ---------------------------------------------------------------------------

@app.post("/demo/tamper/{case_id}")
async def demo_tamper(case_id: str):
    """DELIBERATELY tamper an audit entry to demonstrate SHA-256 detection."""
    import json as _json
    from audit.chain import AUDIT_LOG_DIR, verify_chain

    path = AUDIT_LOG_DIR / f"{case_id}.jsonl"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No audit log to tamper")

    lines = path.read_text().strip().splitlines()
    if len(lines) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 entries to tamper")

    entry = _json.loads(lines[-2])
    entry["payload_hash"] = "sha256:TAMPERED_DEMO"
    lines[-2] = _json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")

    ok, broken = verify_chain(case_id)
    return {"tampered": True, "broken_at_seq": broken, "verified": ok}


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------

async def _run_pipeline_background(case_data: dict):
    """Run the full pipeline in background (called by submit_case)."""
    try:
        result = await handle_case_local(case_data)
        logger.info(f"Background pipeline complete: {result.get('case_id')} → {result.get('status')}")
    except Exception as e:
        logger.exception(f"Background pipeline failed: {e}")


# ---------------------------------------------------------------------------
# Demo runner
# ---------------------------------------------------------------------------

@app.post("/demo/run-all")
async def demo_run_all():
    """Run both demo cases (C-0001 and C-0002) and return results."""
    results = {}
    for case_id in ["C-0001", "C-0002"]:
        logger.info(f"=== Running demo case: {case_id} ===")
        result = await handle_case_local(case_id)
        results[case_id] = {
            "status": result.get("status"),
            "flags": len(result.get("flags", [])),
            "veto": result.get("compliance", {}).get("veto", False) if result.get("compliance") else False,
            "human_decision": result.get("human_decision", {}).get("verdict"),
            "audit_verified": result.get("audit_verified"),
        }
    return {"demo_results": results}

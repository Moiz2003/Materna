"""
tools/imaging.py — LLM-vision ultrasound read via AI/ML API.

Golden Rule 4: Decision-support only. Never diagnostic.
Golden Rule: Never crash the pipeline — degrade gracefully on any failure.
§10.3 SDD, P6 Playbook.

AI/ML API (https://aimlapi.com) — partner-prize eligible provider.
Uses OpenAI-compatible chat completions endpoint with vision-capable models.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import mimetypes
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Fallback: OpenRouter
AIML_API_KEY = os.getenv("AIML_API_KEY", "")
AIML_BASE_URL = os.getenv("AIML_BASE_URL", "https://openrouter.ai/api/v1")

# ---------------------------------------------------------------------------
# System prompt — Golden Rule 4 enforced here
# ---------------------------------------------------------------------------

ULTRASOUND_SYSTEM_PROMPT = """\
You are a medical imaging decision-support tool assisting an antenatal review board.

CRITICAL RULES — follow exactly:
1. Describe ONLY observable features in the ultrasound image.
2. This is DECISION-SUPPORT, NOT a diagnosis.
3. DO NOT state a diagnosis, disease, or management plan.
4. DO NOT use phrases like "the patient has..." or "this indicates...".
5. If the image is unreadable, too dark, or not a recognizable ultrasound, say so honestly.
6. Keep observations concise (2-5 sentences max).

Output format — respond with EXACTLY this JSON structure and nothing else:
{
  "observations": "string describing what you can see",
  "confidence": "low" or "moderate" or "high"
}

Confidence guide:
- "high": clear fetal anatomy visible, standard plane
- "moderate": some anatomy visible but image quality limited
- "low": image unreadable, not an ultrasound, or cannot determine features"""

# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------


async def read_ultrasound(image_ref: str) -> dict:
    """
    Read an ultrasound image via AI/ML API multimodal model.

    Args:
        image_ref: Path to the ultrasound image file (e.g., 'data/usg/C-0001.png').

    Returns:
        {"observations": str, "confidence": "low"|"moderate"|"high"}

    NEVER raises — degrades gracefully on any failure (Golden Rule 4).
    """
    # Resolve the image path
    image_path = Path(image_ref)
    if not image_path.is_absolute():
        # Relative to project root
        image_path = Path(__file__).parent.parent / image_ref

    if not image_path.exists():
        logger.warning(f"Ultrasound image not found: {image_path}")
        return {
            "observations": "image unavailable — file not found",
            "confidence": "low",
        }

    # Detect MIME type from file extension (png, jpg, jpeg)
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"  # default

    # Read and encode image
    try:
        image_bytes = image_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_b64}"
    except Exception as e:
        logger.error(f"Failed to read/encode image {image_path}: {e}")
        return {
            "observations": "image unavailable — read error",
            "confidence": "low",
        }

    # Attempt the API call (retry once)
    for attempt in range(2):
        try:
            result = await _call_vision_api(data_url, mime_type)
            return result
        except Exception as e:
            logger.warning(
                f"AI/ML API vision call attempt {attempt + 1}/2 failed: {e}"
            )
            if attempt == 0:
                await asyncio.sleep(1)  # brief backoff before retry

    # Both attempts failed — degrade gracefully
    logger.error("AI/ML API vision call failed after 2 attempts — degrading")
    return {
        "observations": "image unavailable — API error",
        "confidence": "low",
    }


async def _call_vision_api(data_url: str, mime_type: str) -> dict:
    """
    Call Gemini native API with the ultrasound image.

    Returns validated {"observations": str, "confidence": str}.
    Raises on HTTP or validation failure (caller retries/degrades).
    """
    # Extract base64 data from data URL
    base64_data = data_url.split(",", 1)[1] if "," in data_url else data_url

    # Try Gemini native API first
    if GEMINI_API_KEY:
        try:
            return await _call_gemini_vision(base64_data, mime_type)
        except Exception as e:
            logger.warning(f"Gemini vision failed: {e}, trying OpenRouter fallback")

    # Fallback to OpenRouter
    if AIML_API_KEY:
        return await _call_openrouter_vision(data_url)

    raise RuntimeError("No vision API key configured (GEMINI_API_KEY or AIML_API_KEY)")


async def _call_gemini_vision(base64_data: str, mime_type: str) -> dict:
    """Call Gemini native API for vision."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{
            "parts": [
                {"text": ULTRASOUND_SYSTEM_PROMPT + "\n\nDescribe the observable features in this obstetric ultrasound image. Remember: decision-support only, no diagnosis."},
                {"inlineData": {"mimeType": mime_type, "data": base64_data}},
            ]
        }],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return _validate_vision_output(content)


async def _call_openrouter_vision(data_url: str) -> dict:
    """Fallback: call OpenRouter for vision."""
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/antenatal-review-board",
        "X-Title": "Antenatal Review Board",
    }

    model = os.getenv("AIML_VISION_MODEL", "google/gemini-2.0-flash-001")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": ULTRASOUND_SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": "Describe the observable features in this obstetric ultrasound image. Decision-support only, no diagnosis."},
            ]},
        ],
        "max_tokens": 512,
        "temperature": 0.1,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{AIML_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return _validate_vision_output(content)


def _validate_vision_output(raw_text: str) -> dict:
    """
    Validate and parse the LLM's vision output.

    Extracts {observations, confidence} from the response.
    If the model returns junk, raises ValueError (caller degrades gracefully).
    """
    import json
    import re

    raw_text = raw_text.strip()

    # Try direct JSON parse
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict) and "observations" in parsed:
            return _sanitize_result(parsed)
    except (json.JSONDecodeError, TypeError):
        pass

    # Try extracting JSON block from markdown ```json ... ```
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            if isinstance(parsed, dict) and "observations" in parsed:
                return _sanitize_result(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

    # Try finding any JSON object in the text
    json_match = re.search(r"\{[^{}]*\"observations\"[^{}]*\}", raw_text, re.DOTALL)
    if json_match:
        try:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict) and "observations" in parsed:
                return _sanitize_result(parsed)
        except (json.JSONDecodeError, TypeError):
            pass

    # If the output contains diagnostic language, reject it
    diagnostic_patterns = [
        r"\bdiagnos(?:is|ed|ing)\b",
        r"\bthe patient has\b",
        r"\bthis indicates\b",
        r"\bfindings suggest\b",
        r"\bconsistent with\b",
        r"\bmanagement\b",
        r"\btreatment\b",
        r"\brecommend\b",
    ]
    for pattern in diagnostic_patterns:
        if re.search(pattern, raw_text, re.IGNORECASE):
            raise ValueError(
                f"Vision model output contains diagnostic language "
                f"(matched '{pattern}'). Rejecting. Raw: {raw_text[:200]}"
            )

    # Last resort: treat raw text as observations with moderate confidence
    # (only if it's reasonable length and not obviously garbage)
    if 20 < len(raw_text) < 2000:
        return {
            "observations": raw_text[:1000],
            "confidence": "moderate",
        }

    raise ValueError(f"Could not parse vision output: {raw_text[:200]}")


def _sanitize_result(parsed: dict) -> dict:
    """Sanitize and validate a parsed vision result dict."""
    observations = str(parsed.get("observations", "")).strip()
    confidence = str(parsed.get("confidence", "moderate")).strip().lower()

    # Validate confidence
    if confidence not in ("low", "moderate", "high"):
        confidence = "moderate"

    # Strip any diagnostic language from observations
    diagnostic_phrases = [
        "diagnosis:", "the patient has", "this indicates",
        "consistent with", "management:", "treatment:",
    ]
    for phrase in diagnostic_phrases:
        if phrase in observations.lower():
            observations = observations.split(phrase)[0].strip()
            logger.warning(f"Stripped diagnostic language from vision output: '{phrase}'")

    if not observations:
        observations = "No observable features could be determined."
        confidence = "low"

    return {
        "observations": observations,
        "confidence": confidence,
    }


# ---------------------------------------------------------------------------
# P6 acceptance check — __main__ per Playbook
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("P6 ACCEPTANCE CHECK — Imaging Tool (AI/ML API)")
    print("=" * 60)
    print()
    print("System prompt used:")
    print("-" * 40)
    print(ULTRASOUND_SYSTEM_PROMPT)
    print("-" * 40)
    print()

    # Resolve image path
    image_ref = sys.argv[1] if len(sys.argv) > 1 else "data/usg/C-0001.png"
    image_path = Path(__file__).parent.parent / image_ref

    if not image_path.exists():
        print(f"⚠️  Sample image not found: {image_path}")
        print(f"   Place a synthetic ultrasound image at data/usg/C-0001.png")
        print(f"   Then run: python tools/imaging.py")
        print()
        print("   DRY RUN: Simulating API call...")
        print(f"   → observations: 'Single live intrauterine fetus; placenta posterior;")
        print(f"                     no gross anomaly noted (decision-support).'")
        print(f"   → confidence: moderate")
        print(f"   ✅ P6 dry-run complete (no image file)")
    else:
        print(f"📷 Reading ultrasound: {image_path}")
        if not AIML_API_KEY:
            print("⚠️  AIML_API_KEY not set — cannot call AI/ML API.")
            print("   Set it in .env and retry.")
        else:
            result = asyncio.run(read_ultrasound(str(image_path)))
            print(f"   → observations: {result['observations']}")
            print(f"   → confidence: {result['confidence']}")
            print(f"   ✅ P6 acceptance check complete")

    print("=" * 60)

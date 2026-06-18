"""
tools/treatment.py — Advised treatment & investigation plan engine.

Produces a per-case management plan (impression + planned investigations +
advised treatment) that the human obstetrician reviews. On override, the OB's
instruction is fed back in and the plan is re-generated — the human-in-the-loop
correction loop. The plan is decision-support: the clinician's approval is what
makes it binding (Golden Rule 4).

A deterministic baseline (grounded in the fired flags / guideline result) always
runs, so the loop works even when the LLM is rate-limited; an optional AI pass
refines/personalises it and incorporates the OB's free-text instruction.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# Deterministic management knowledge, keyed by risk-flag type. Grounded in the
# same ruleset the guideline agent uses — never invented at runtime.
MANAGEMENT_KB: dict[str, dict] = {
    "preeclampsia_suspected": {
        "impression": "Features suggestive of pre-eclampsia (raised BP with proteinuria).",
        "investigations": [
            "Repeat blood pressure after 4 hours",
            "24-hour urine protein quantification (or protein:creatinine ratio)",
            "FBC with platelet count",
            "LFTs, serum creatinine and uric acid",
        ],
        "treatment": [
            "Admit for maternal and fetal monitoring",
            "Antihypertensive (e.g. labetalol) if BP ≥ 160/110 mmHg",
            "Consider MgSO4 seizure prophylaxis if severe features",
            "Plan delivery timing per gestation and severity",
        ],
    },
    "gdm_suspected": {
        "impression": "Screen positive for gestational diabetes (raised fasting glucose).",
        "investigations": [
            "Oral glucose tolerance test (OGTT) to confirm",
            "HbA1c",
            "Fasting and post-prandial glucose profile",
        ],
        "treatment": [
            "Dietary counselling and carbohydrate modification",
            "Home blood-glucose monitoring",
            "Start metformin/insulin if glycaemic targets not met",
            "Serial growth scans for fetal macrosomia",
        ],
    },
    "anaemia": {
        "impression": "Anaemia in pregnancy (Hb below threshold).",
        "investigations": [
            "Iron studies (ferritin, TIBC)",
            "Peripheral blood smear",
            "Repeat Hb after treatment",
        ],
        "treatment": [
            "Oral iron supplementation",
            "Dietary iron advice",
            "Parenteral iron if oral intolerant or severe",
        ],
    },
    "dating_discordance": {
        "impression": "LMP and ultrasound dating discordant.",
        "investigations": ["Confirm dating by ultrasound biometry"],
        "treatment": [
            "Re-date pregnancy by ultrasound; revise EDD",
            "Document dating method used for the record",
        ],
    },
}

_INSUFFICIENT_DATA = {
    "impression": "Insufficient clinical data captured to risk-stratify this case.",
    "investigations": [
        "Complete antenatal history",
        "Measure blood pressure",
        "Urine dipstick for protein",
        "FBC / haemoglobin",
        "Fasting glucose / GDM screen",
        "Dating ultrasound",
    ],
    "treatment": [
        "Obtain the missing baseline data before risk stratification",
        "Schedule early review once results are available",
    ],
}


def build_baseline_plan(state: dict) -> dict:
    """Deterministic plan grounded in the case's flags, findings and reasons."""
    flags = state.get("flags") or []
    finding = state.get("finding") or {}
    brief = state.get("escalation_brief") or {}
    reasons = brief.get("reason") or []

    impressions: list[str] = []
    investigations: list[str] = []
    treatment: list[str] = []

    flag_types = [(f if isinstance(f, dict) else {}).get("type", "") for f in flags]

    if "insufficient_data" in reasons and not flag_types:
        impressions.append(_INSUFFICIENT_DATA["impression"])
        investigations += _INSUFFICIENT_DATA["investigations"]
        treatment += _INSUFFICIENT_DATA["treatment"]

    for ftype in flag_types:
        kb = MANAGEMENT_KB.get(ftype)
        if kb:
            impressions.append(kb["impression"])
            investigations += kb["investigations"]
            treatment += kb["treatment"]

    if finding.get("discordant"):
        kb = MANAGEMENT_KB["dating_discordance"]
        impressions.append(kb["impression"])
        investigations += kb["investigations"]
        treatment += kb["treatment"]

    if not impressions:
        impressions.append("No specific risk flag fired; routine antenatal care.")
        treatment.append("Continue routine antenatal schedule and safety-netting advice.")

    return {
        "impression": " ".join(dict.fromkeys(impressions)),
        "investigations": list(dict.fromkeys(investigations)),
        "treatment": list(dict.fromkeys(treatment)),
        "source": "deterministic",
    }


async def _llm_refine(baseline: dict, state: dict, ob_input: str | None,
                      prior_plan: dict | None) -> dict | None:
    """Ask the LLM to refine/personalise the plan and fold in the OB's instruction.

    Returns a plan dict on success, or None if no LLM is reachable (caller falls
    back to the deterministic baseline). Gemini first, then OpenRouter.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    or_key = os.getenv("AIML_API_KEY", "")
    or_url = os.getenv("AIML_BASE_URL", "https://openrouter.ai/api/v1")
    if not gemini_key and not or_key:
        return None

    system = (
        "You are an obstetric clinical decision-support assistant. You DRAFT a "
        "management plan for a human obstetrician to approve — you never finalise "
        "care. Stay grounded in the provided flags and baseline; do not invent "
        "findings. Return ONLY JSON: "
        '{"impression": str, "investigations": [str], "treatment": [str]}.'
    )
    context = {
        "case": state.get("raw_case", {}),
        "fired_flags": [(f if isinstance(f, dict) else {}).get("type") for f in (state.get("flags") or [])],
        "guideline": state.get("compliance", {}),
        "baseline_plan": baseline,
    }
    if prior_plan:
        context["previous_plan"] = {k: prior_plan.get(k) for k in ("impression", "investigations", "treatment")}
    if ob_input:
        context["obstetrician_instruction"] = ob_input
        instruction = (
            "The obstetrician reviewed the previous plan and gave the instruction "
            "above. Revise the plan to follow it while keeping it clinically coherent."
        )
    else:
        instruction = "Refine and personalise the baseline plan for this specific case."
    user = instruction + "\n\nCONTEXT:\n" + json.dumps(context, default=str)

    # --- Gemini ---
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_key}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers={"Content-Type": "application/json"}, json={
                    "contents": [{"parts": [{"text": system + "\n\n" + user}]}],
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
                })
                resp.raise_for_status()
                content = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return _coerce_plan(content)
        except Exception as e:
            logger.warning(f"treatment LLM (Gemini) failed, trying OpenRouter: {str(e)[:120]}")

    # --- OpenRouter ---
    if or_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{or_url}/chat/completions",
                    headers={"Authorization": f"Bearer {or_key}", "Content-Type": "application/json",
                             "HTTP-Referer": "https://github.com/antenatal-review-board",
                             "X-Title": "Antenatal Review Board"},
                    json={"model": "openai/gpt-4o-mini",
                          "messages": [{"role": "system", "content": system},
                                       {"role": "user", "content": user}],
                          "max_tokens": 1024, "temperature": 0.2},
                )
                resp.raise_for_status()
                content = resp.json()["choices"][0]["message"]["content"].strip()
            return _coerce_plan(content)
        except Exception as e:
            logger.warning(f"treatment LLM (OpenRouter) failed: {str(e)[:120]}")

    return None


def _coerce_plan(content: str) -> dict | None:
    """Parse the LLM JSON plan, tolerating markdown fences."""
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    data = json.loads(content)
    inv = [str(x) for x in (data.get("investigations") or []) if str(x).strip()]
    tx = [str(x) for x in (data.get("treatment") or []) if str(x).strip()]
    if not inv and not tx:
        return None
    return {
        "impression": str(data.get("impression", "")).strip(),
        "investigations": inv,
        "treatment": tx,
        "source": "ai",
    }


async def generate_plan(state: dict, ob_input: str | None = None,
                        prior_plan: dict | None = None, iteration: int = 1) -> dict:
    """Produce a treatment plan for a case (AI-refined when available, else baseline).

    On override, pass the OB's instruction as `ob_input` and the prior plan so the
    new plan reflects the clinician's correction.
    """
    baseline = build_baseline_plan(state)
    refined = await _llm_refine(baseline, state, ob_input, prior_plan)
    plan = refined or baseline

    # Always honour the OB's explicit instruction even if the LLM was unavailable.
    if ob_input and plan["source"] != "ai":
        plan = dict(plan)
        plan["treatment"] = list(plan["treatment"]) + [f"Per reviewing OB: {ob_input}"]

    plan["iteration"] = iteration
    plan["ob_input"] = ob_input
    plan["generated_at"] = datetime.now(timezone.utc).isoformat()
    return plan

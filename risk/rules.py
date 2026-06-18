"""
risk/rules.py — Deterministic risk evaluators.

Golden Rule 5: Thresholds read from antenatal_rules.yaml.
Each evaluator returns RiskFlag | None — pure function, no LLM.
§10.4 SDD, P4 Playbook.
"""

from __future__ import annotations

from schemas import RiskFlag


def eval_preeclampsia(vitals: dict, labs: dict, case_id: str = "") -> RiskFlag | None:
    """
    BP >= 140/90 AND urine_protein in {1+, 2+, 3+} → preeclampsia_suspected, high.
    Rule ref: PE-001.
    """
    bp_sys = vitals.get("bp_systolic") or 0
    bp_dia = vitals.get("bp_diastolic") or 0
    protein = labs.get("urine_protein") or "negative"

    if (bp_sys >= 140 or bp_dia >= 90) and protein in ("1+", "2+", "3+"):
        return RiskFlag(
            case_id=case_id,
            type="preeclampsia_suspected",
            severity="high",
            evidence={"bp": f"{bp_sys}/{bp_dia}", "urine_protein": protein},
            rule_ref="PE-001",
        )
    return None


def eval_gdm(labs: dict, case_id: str = "") -> RiskFlag | None:
    """
    fasting_glucose >= 92 mg/dL → gdm_suspected, moderate.
    Rule ref: GDM-002.
    """
    glucose = labs.get("fasting_glucose_mg_dl")
    if glucose is not None and glucose >= 92:
        return RiskFlag(
            case_id=case_id,
            type="gdm_suspected",
            severity="moderate",
            evidence={"fasting_glucose_mg_dl": glucose},
            rule_ref="GDM-002",
        )
    return None


def eval_anaemia(labs: dict, case_id: str = "") -> RiskFlag | None:
    """
    Hb < 11.0 g/dL → anaemia, moderate.
    Rule ref: ANE-003.
    """
    hb = labs.get("hb_g_dl")
    if hb is not None and hb < 11.0:
        return RiskFlag(
            case_id=case_id,
            type="anaemia",
            severity="moderate",
            evidence={"hb_g_dl": hb},
            rule_ref="ANE-003",
        )
    return None


def evaluate_all(structured) -> list[RiskFlag]:
    """
    Run all evaluators on a StructuredCase.
    Returns every fired RiskFlag with evidence populated.
    """
    case_id = structured.case_id if hasattr(structured, 'case_id') else ""
    vitals = structured.vitals if hasattr(structured, 'vitals') else {}
    labs = structured.labs if hasattr(structured, 'labs') else {}

    # Convert pydantic models to dicts if needed
    if hasattr(vitals, 'model_dump'):
        vitals = vitals.model_dump()
    if hasattr(labs, 'model_dump'):
        labs = labs.model_dump()

    flags: list[RiskFlag] = []

    # eval_preeclampsia takes (vitals, labs, case_id)
    flag = eval_preeclampsia(vitals, labs, case_id)
    if flag:
        flags.append(flag)

    # eval_gdm and eval_anaemia take (labs, case_id)
    flag = eval_gdm(labs, case_id)
    if flag:
        flags.append(flag)

    flag = eval_anaemia(labs, case_id)
    if flag:
        flags.append(flag)

    return flags

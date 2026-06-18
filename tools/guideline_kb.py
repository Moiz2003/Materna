"""
tools/guideline_kb.py — Declarative rule loader + deterministic checker.

The ruleset is data (antenatal_rules.yaml), not code.
Golden Rule 5: compliant/veto/missing are computed deterministically.
The LLM may later phrase the explanation, but the verdict is computed in code.
§10.5 SDD, P5 Playbook.
"""

from __future__ import annotations

import logging
import yaml
from pathlib import Path
from typing import Any

from schemas import ComplianceResult, RiskFlag

logger = logging.getLogger(__name__)

# Map RiskFlag.type → rule id for lookup in antenatal_rules.yaml
FLAG_TYPE_TO_RULE_ID: dict[str, str] = {
    "preeclampsia_suspected": "PE-001",
    "gdm_suspected": "GDM-002",
    "anaemia": "ANE-003",
    "dating_discordance": "DATE-004",
}


def load_rules(path: str | None = None) -> dict:
    """
    Parse antenatal_rules.yaml and return the full rules dict.

    The ruleset is the single source of truth — thresholds and requirements
    are never hardcoded elsewhere (Golden Rule 5).
    """
    if path is None:
        path = str(Path(__file__).parent.parent / "data" / "rules" / "antenatal_rules.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def _find_rule_by_flag(flag_type: str, rules_list: list[dict]) -> dict | None:
    """Find the rule dict whose flag.type matches the given RiskFlag type."""
    rule_id = FLAG_TYPE_TO_RULE_ID.get(flag_type)
    if not rule_id:
        return None
    for rule in rules_list:
        if rule.get("id") == rule_id:
            return rule
    return None


def _extract_case_id(structured: Any) -> str:
    """Extract case_id from a StructuredCase (pydantic model or dict)."""
    if hasattr(structured, "case_id"):
        return structured.case_id
    if isinstance(structured, dict):
        return structured.get("case_id", "unknown")
    return "unknown"


def _extract_discordance(findings: list) -> float | None:
    """Extract the maximum discordance_weeks from a list of Finding objects."""
    best = None
    for f in findings or []:
        d = None
        if hasattr(f, "discordance_weeks"):
            d = f.discordance_weeks
        elif isinstance(f, dict):
            d = f.get("discordance_weeks")
        if d is not None and (best is None or d > best):
            best = d
    return best


def missing_investigations(
    structured: Any,
    flags: list[RiskFlag],
    rules: dict,
) -> list[str]:
    """
    Determine which required investigations are missing for the fired flags.

    For each fired flag:
      1. Find the matching rule in the YAML
      2. Collect its `require:` list
      3. Any required investigation not already present is "missing"

    Returns the deduplicated, sorted list of missing investigation names.
    """
    rules_list = rules.get("rules", [])
    missing: set[str] = set()

    for flag in flags:
        rule = _find_rule_by_flag(flag.type, rules_list)
        if not rule:
            logger.debug(f"No rule found for flag type '{flag.type}' — skipping")
            continue

        required = rule.get("require", [])
        for item in required:
            missing.add(item)

    return sorted(missing)


def check_schedule(
    structured: Any,
    findings: list,
    flags: list[RiskFlag],
    rules: dict,
) -> ComplianceResult:
    """
    Check a case against the antenatal ruleset deterministically.

    Logic (per P5 Playbook):
      1. Compute missing investigations from fired flags
      2. compliant = (no missing required investigations)
      3. veto = True if ANY rule with veto_if_missing=true has missing requirements
      4. DATE-004: if discordance >= threshold, add prefer_ultrasound_dating note
      5. Populate notes and rule_refs

    The LLM may phrase `notes` later, but compliant/veto/missing are computed
    HERE in code. No LLM changes the verdict (Golden Rule 5).
    """
    case_id = _extract_case_id(structured)
    rules_list = rules.get("rules", [])

    # --- 1. Missing investigations ---
    missing = missing_investigations(structured, flags, rules)

    # --- 2 & 3. Compliant + veto ---
    veto = False
    veto_reasons: list[str] = []

    for flag in flags:
        rule = _find_rule_by_flag(flag.type, rules_list)
        if not rule:
            continue

        rule_required = set(rule.get("require", []))
        rule_missing = rule_required & set(missing)

        if rule_missing and rule.get("veto_if_missing", False):
            veto = True
            veto_reasons.append(
                f"{rule.get('name', rule.get('id', '?'))} "
                f"requires: {', '.join(sorted(rule_missing))}"
            )

    compliant = len(missing) == 0

    # --- 4. DATE-004: dating discordance note ---
    notes_parts: list[str] = []
    rule_refs: list[str] = [flag.rule_ref for flag in flags if flag.rule_ref]

    discordance = _extract_discordance(findings)
    date_rule = None
    for rule in rules_list:
        if rule.get("id") == "DATE-004":
            date_rule = rule
            break

    if date_rule and discordance is not None:
        threshold = date_rule.get("when", {}).get("discordance_weeks_gte", 2.0)
        if discordance >= threshold:
            note = date_rule.get("note", "Re-date by ultrasound; LMP unreliable.")
            action = date_rule.get("action", "")
            notes_parts.append(f"[DATE-004] {note} (action: {action})")
            if "DATE-004" not in rule_refs:
                rule_refs.append("DATE-004")

    # --- 5. Build notes ---
    if veto:
        notes_parts.insert(0, f"VETO: {'; '.join(veto_reasons)}")
    if missing:
        notes_parts.append(f"Missing investigations: {', '.join(missing)}")
    if compliant and not veto:
        notes_parts.insert(0, "Case compliant with antenatal guidelines.")

    return ComplianceResult(
        case_id=case_id,
        compliant=compliant,
        veto=veto,
        missing_investigations=missing,
        notes=" | ".join(notes_parts) if notes_parts else "No guideline issues.",
        rule_refs=rule_refs,
    )


# ---------------------------------------------------------------------------
# P5 acceptance check — __main__ per Playbook
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    from datetime import date

    # Load synthetic case C-0001 (Appendix B)
    case_path = Path(__file__).parent.parent / "data" / "cases" / "C-0001.json"
    with open(case_path) as f:
        raw_case = json.load(f)

    # Construct a StructuredCase-like object for the checker
    class SimpleCase:
        def __init__(self, d):
            self.case_id = d["case_id"]
            self.__dict__.update(d)

    structured = SimpleCase(raw_case)

    # Build findings (with discordance to trigger DATE-004)
    findings = [{
        "ga_lmp_weeks": 27.3,
        "ga_usg_weeks": 23.0,
        "discordance_weeks": 4.3,
        "discordant": True,
    }]

    # Build RiskFlags matching C-0001 (PE-001 high + GDM-002)
    flags = [
        RiskFlag(
            case_id="C-0001",
            type="preeclampsia_suspected",
            severity="high",
            evidence={"bp": "150/98", "urine_protein": "2+"},
            rule_ref="PE-001",
        ),
        RiskFlag(
            case_id="C-0001",
            type="gdm_suspected",
            severity="moderate",
            evidence={"fasting_glucose_mg_dl": 104},
            rule_ref="GDM-002",
        ),
    ]

    # Load rules and run check
    rules = load_rules()
    result = check_schedule(structured, findings, flags, rules)

    print("=" * 60)
    print("P5 ACCEPTANCE CHECK — Guideline KB")
    print("=" * 60)
    print(f"  Case:        C-0001")
    print(f"  Flags fired: PE-001 (preeclampsia), GDM-002 (diabetes)")
    print(f"  Discordance: 4.3 weeks (threshold: 2.0)")
    print()
    print(f"  compliant:            {result.compliant}")
    print(f"  veto:                 {result.veto}")
    print(f"  missing_investigations: {result.missing_investigations}")
    print(f"  rule_refs:            {result.rule_refs}")
    print(f"  notes:                {result.notes}")
    print()
    print(f"  ✅ Expected: compliant=False, veto=True, missing=[24h_urine_protein, ogtt, repeat_bp_4h]")
    print(f"  ✅ DATE-004 note present: {'DATE-004' in result.notes}")
    print("=" * 60)

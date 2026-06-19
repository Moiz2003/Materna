"""
tests/test_rules.py — T3: Unit tests for risk/rules.py.
Every evaluator, every threshold edge, evidence populated.
Prompt Playbook T3 — §2 Automated Testing.
"""
import pytest

from risk.rules import eval_preeclampsia, eval_gdm, eval_anaemia, evaluate_all
from schemas import RiskFlag


class TestEvalPreeclampsia:
    def test_fires_at_threshold(self):
        """BP 140/90 + protein 1+ → flag fires."""
        flag = eval_preeclampsia(
            {"bp_systolic": 140, "bp_diastolic": 90},
            {"urine_protein": "1+"},
        )
        assert flag is not None
        assert flag.type == "preeclampsia_suspected"
        assert flag.severity == "high"
        assert flag.rule_ref == "PE-001"

    def test_bp_only_no_protein(self):
        """BP 150/98 but negative protein → no flag."""
        flag = eval_preeclampsia(
            {"bp_systolic": 150, "bp_diastolic": 98},
            {"urine_protein": "negative"},
        )
        assert flag is None

    def test_protein_only_no_bp(self):
        """Protein 2+ but normal BP → no flag."""
        flag = eval_preeclampsia(
            {"bp_systolic": 118, "bp_diastolic": 76},
            {"urine_protein": "2+"},
        )
        assert flag is None

    def test_just_below_threshold(self):
        """BP 138/88 + protein 1+ → no flag."""
        flag = eval_preeclampsia(
            {"bp_systolic": 138, "bp_diastolic": 88},
            {"urine_protein": "1+"},
        )
        assert flag is None

    def test_systolic_only_above(self):
        """BP 145/80 + protein 1+ → flag fires (systolic ≥ 140)."""
        flag = eval_preeclampsia(
            {"bp_systolic": 145, "bp_diastolic": 80},
            {"urine_protein": "1+"},
        )
        assert flag is not None

    def test_diastolic_only_above(self):
        """BP 130/95 + protein 1+ → flag fires (diastolic ≥ 90)."""
        flag = eval_preeclampsia(
            {"bp_systolic": 130, "bp_diastolic": 95},
            {"urine_protein": "1+"},
        )
        assert flag is not None

    def test_evidence_populated(self):
        """Evidence dict contains the BP and protein values."""
        flag = eval_preeclampsia(
            {"bp_systolic": 150, "bp_diastolic": 98},
            {"urine_protein": "2+"},
        )
        assert flag.evidence["bp"] == "150/98"
        assert flag.evidence["urine_protein"] == "2+"

    def test_protein_2plus(self):
        """Protein 2+ also triggers."""
        flag = eval_preeclampsia(
            {"bp_systolic": 150, "bp_diastolic": 98},
            {"urine_protein": "2+"},
        )
        assert flag is not None

    def test_protein_3plus(self):
        """Protein 3+ also triggers."""
        flag = eval_preeclampsia(
            {"bp_systolic": 150, "bp_diastolic": 98},
            {"urine_protein": "3+"},
        )
        assert flag is not None

    def test_missing_data_no_crash(self):
        """Empty dicts → no crash, returns None."""
        assert eval_preeclampsia({}, {}, "") is None


class TestEvalGdm:
    def test_below_threshold(self):
        """Fasting glucose 91 → no flag."""
        assert eval_gdm({"fasting_glucose_mg_dl": 91}) is None

    def test_at_threshold(self):
        """Fasting glucose 92 → flag fires."""
        flag = eval_gdm({"fasting_glucose_mg_dl": 92})
        assert flag is not None
        assert flag.type == "gdm_suspected"
        assert flag.severity == "moderate"
        assert flag.rule_ref == "GDM-002"

    def test_above_threshold(self):
        """Fasting glucose 104 → flag fires."""
        flag = eval_gdm({"fasting_glucose_mg_dl": 104})
        assert flag is not None

    def test_evidence_populated(self):
        """Evidence contains the glucose value."""
        flag = eval_gdm({"fasting_glucose_mg_dl": 95})
        assert flag.evidence["fasting_glucose_mg_dl"] == 95

    def test_none_value_no_crash(self):
        """None glucose → no flag, no crash."""
        assert eval_gdm({"fasting_glucose_mg_dl": None}) is None
        assert eval_gdm({}) is None


class TestEvalAnaemia:
    def test_at_threshold(self):
        """Hb 11.0 → no flag (not below)."""
        assert eval_anaemia({"hb_g_dl": 11.0}) is None

    def test_just_below(self):
        """Hb 10.9 → flag fires."""
        flag = eval_anaemia({"hb_g_dl": 10.9})
        assert flag is not None
        assert flag.type == "anaemia"
        assert flag.severity == "moderate"
        assert flag.rule_ref == "ANE-003"

    def test_well_below(self):
        """Hb 8.5 → flag fires."""
        flag = eval_anaemia({"hb_g_dl": 8.5})
        assert flag is not None

    def test_evidence_populated(self):
        """Evidence contains the Hb value."""
        flag = eval_anaemia({"hb_g_dl": 9.5})
        assert flag.evidence["hb_g_dl"] == 9.5

    def test_none_value_no_crash(self):
        """None Hb → no flag, no crash."""
        assert eval_anaemia({"hb_g_dl": None}) is None
        assert eval_anaemia({}) is None


class TestEvaluateAll:
    def test_c0001_fires_pe_and_gdm(self, c0001_structured):
        """C-0001: PE-001 (high) + GDM-002 (moderate) + anaemia."""
        from agents.dating_risk.agent import _build_structured_obj
        obj = _build_structured_obj(c0001_structured)
        flags = evaluate_all(obj)
        types = {f.type for f in flags}
        assert "preeclampsia_suspected" in types
        assert "gdm_suspected" in types
        assert "anaemia" in types  # Hb 10.1 < 11.0
        assert len(flags) == 3

    def test_c0002_no_flags(self, c0002_structured):
        """C-0002: clean case → no flags."""
        from agents.dating_risk.agent import _build_structured_obj
        obj = _build_structured_obj(c0002_structured)
        flags = evaluate_all(obj)
        assert flags == []

    def test_empty_input_no_crash(self):
        """Empty vitals/labs → empty flag list, no crash."""
        class EmptyCase:
            case_id = "C-EMPTY"
            vitals = {}
            labs = {}
        flags = evaluate_all(EmptyCase())
        assert flags == []

"""
tests/test_guideline.py — T4: Unit tests for tools/guideline_kb.py.
Compliant/veto/missing computed correctly and declaratively.
Prompt Playbook T4 — §2 Automated Testing.
"""
import pytest

from tools.guideline_kb import load_rules, check_schedule, missing_investigations
from schemas import RiskFlag, ComplianceResult


@pytest.fixture
def rules():
    return load_rules()


@pytest.fixture
def c0001_finding():
    return [{"ga_lmp_weeks": 27.3, "ga_usg_weeks": 23.0, "discordance_weeks": 4.3, "discordant": True}]


@pytest.fixture
def c0001_flags():
    return [
        RiskFlag(case_id="C-0001", type="preeclampsia_suspected", severity="high",
                 evidence={"bp": "150/98", "urine_protein": "2+"}, rule_ref="PE-001"),
        RiskFlag(case_id="C-0001", type="gdm_suspected", severity="moderate",
                 evidence={"fasting_glucose_mg_dl": 104}, rule_ref="GDM-002"),
    ]


@pytest.fixture
def anaemia_flag():
    return RiskFlag(case_id="C-TEST", type="anaemia", severity="moderate",
                    evidence={"hb_g_dl": 10.5}, rule_ref="ANE-003")


class TestMissingInvestigations:
    def test_pe_and_gdm_missing(self, c0001_flags, rules):
        """PE-001 requires repeat_bp_4h + 24h_urine_protein; GDM-002 requires ogtt."""
        missing = missing_investigations(None, c0001_flags, rules)
        assert "repeat_bp_4h" in missing
        assert "24h_urine_protein" in missing
        assert "ogtt" in missing
        assert len(missing) == 3

    def test_anaemia_missing(self, anaemia_flag, rules):
        """ANE-003 requires iron_studies."""
        missing = missing_investigations(None, [anaemia_flag], rules)
        assert "iron_studies" in missing
        assert len(missing) == 1

    def test_no_flags_no_missing(self, rules):
        """Empty flag list → no missing investigations."""
        missing = missing_investigations(None, [], rules)
        assert missing == []

    def test_unknown_flag_type_skipped(self, rules):
        """Flag type not mapped in FLAG_TYPE_TO_RULE_ID → gracefully skipped."""
        # dating_discordance has no require list so returns empty
        dd_flag = RiskFlag(case_id="C-TEST", type="dating_discordance", severity="low", rule_ref="DATE-004")
        missing = missing_investigations(None, [dd_flag], rules)
        # DATE-004 has no 'require' list → nothing to miss
        assert missing == []


class TestCheckSchedule:
    def test_c0001_veto_true(self, c0001_structured, c0001_finding, c0001_flags, rules):
        """C-0001: PE+GDM fired, requirements absent → veto=True."""
        result = check_schedule(c0001_structured, c0001_finding, c0001_flags, rules)
        assert result.veto is True
        assert result.compliant is False
        assert "repeat_bp_4h" in result.missing_investigations
        assert "24h_urine_protein" in result.missing_investigations
        assert "ogtt" in result.missing_investigations
        assert "PE-001" in result.rule_refs
        assert "GDM-002" in result.rule_refs

    def test_anaemia_no_veto(self, c0001_structured, anaemia_flag, rules):
        """Anaemia has veto_if_missing=false → contributes to missing but NOT veto."""
        result = check_schedule(c0001_structured, [], [anaemia_flag], rules)
        assert result.veto is False
        assert result.compliant is False
        assert "iron_studies" in result.missing_investigations

    def test_date004_note_added(self, c0001_structured, c0001_finding, c0001_flags, rules):
        """Discordance ≥ 2.0 → DATE-004 note added."""
        result = check_schedule(c0001_structured, c0001_finding, c0001_flags, rules)
        assert "DATE-004" in result.rule_refs
        assert "Re-date by ultrasound" in result.notes

    def test_no_flags_clean(self, c0002_structured, rules):
        """No flags → compliant=True, veto=False, nothing missing."""
        result = check_schedule(c0002_structured, [], [], rules)
        assert result.compliant is True
        assert result.veto is False
        assert result.missing_investigations == []

    def test_ruleset_is_source_of_truth(self, rules):
        """Ruleset loaded from YAML — verify expected rule IDs exist."""
        rule_ids = {r["id"] for r in rules["rules"]}
        assert "PE-001" in rule_ids
        assert "GDM-002" in rule_ids
        assert "ANE-003" in rule_ids
        assert "DATE-004" in rule_ids

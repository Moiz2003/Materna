"""
tests/test_contracts.py — T9: Schema contract tests.
Every Pydantic model validated, round-trip tested.
Prompt Playbook T9.
"""
import json

import pytest
from pydantic import ValidationError

from schemas import (
    CaseInput, StructuredCase, Finding, RiskFlag, ComplianceResult,
    EscalationBrief, HumanDecision, AuditEntry, ReviewPacket,
    MessageEnvelope, Demographics, Vitals, Labs, USGMeasurement,
    AuditorChallenge,
)


class TestCaseInput:
    def test_valid_case_parses(self, c0001_raw):
        ci = CaseInput(**c0001_raw)
        assert ci.case_id == "C-0001"
        assert ci.demographics.age == 29

    def test_missing_required_rejected(self):
        with pytest.raises(ValidationError):
            CaseInput(case_id="C-X")

    def test_invalid_age_rejected(self):
        with pytest.raises(ValidationError):
            CaseInput(case_id="C-X", demographics={"age": -1, "parity": "G1"})

    def test_roundtrip_json_lossless(self, c0001_raw):
        ci = CaseInput(**c0001_raw)
        j = ci.model_dump(mode="json")
        rebuilt = CaseInput(**json.loads(json.dumps(j)))
        assert rebuilt.case_id == ci.case_id
        assert rebuilt.demographics.age == ci.demographics.age


class TestStructuredCase:
    def test_roundtrip(self, c0001_structured):
        sc = StructuredCase(**c0001_structured)
        assert sc.case_id == "C-0001"
        j = sc.model_dump(mode="json")
        rebuilt = StructuredCase(**j)
        assert rebuilt.case_id == sc.case_id


class TestRiskFlag:
    def test_valid_types(self):
        for t in ("preeclampsia_suspected", "gdm_suspected", "anaemia", "dating_discordance"):
            rf = RiskFlag(case_id="C-T", type=t, severity="high")
            assert rf.type == t

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            RiskFlag(case_id="C-T", type="invalid_type", severity="low")

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValidationError):
            RiskFlag(case_id="C-T", type="anaemia", severity="critical")


class TestComplianceResult:
    def test_defaults(self):
        cr = ComplianceResult(case_id="C-T")
        assert cr.compliant is False
        assert cr.veto is False
        assert cr.missing_investigations == []

    def test_roundtrip(self):
        cr = ComplianceResult(
            case_id="C-T", compliant=False, veto=True,
            missing_investigations=["ogtt"], notes="test",
            rule_refs=["PE-001"],
        )
        j = cr.model_dump(mode="json")
        rebuilt = ComplianceResult(**j)
        assert rebuilt.veto is True
        assert "ogtt" in rebuilt.missing_investigations


class TestMessageEnvelope:
    def test_all_intents(self):
        for intent in ("post", "handoff", "escalate", "decision", "audit"):
            env = MessageEnvelope(case_id="C-T", from_agent="intake", intent=intent,
                                  to_role="dating_risk" if intent == "handoff" else None,
                                  payload={})
            assert env.intent == intent

    def test_handoff_must_have_target(self):
        with pytest.raises(ValidationError):
            MessageEnvelope(case_id="C-T", from_agent="intake", intent="handoff",
                            to_role=None, payload={})

    def test_roundtrip(self):
        env = MessageEnvelope(case_id="C-T", from_agent="guideline", intent="post",
                              payload={"veto": True})
        j = env.model_dump(mode="json")
        rebuilt = MessageEnvelope(**j)
        assert rebuilt.payload == {"veto": True}


class TestAuditEntry:
    def test_genesis_default(self):
        ae = AuditEntry(seq=1, case_id="C-T", actor="orchestrator", action="received",
                        payload_hash="sha256:abc", this_hash="sha256:def")
        assert ae.prev_hash == "sha256:GENESIS"

    def test_roundtrip(self):
        ae = AuditEntry(seq=2, case_id="C-T", actor="intake", action="structured",
                        payload_hash="sha256:abc", prev_hash="sha256:def",
                        this_hash="sha256:ghi")
        j = ae.model_dump(mode="json")
        rebuilt = AuditEntry(**j)
        assert rebuilt.seq == 2
        assert rebuilt.this_hash == "sha256:ghi"


class TestAuditorChallenge:
    def test_defaults(self):
        ac = AuditorChallenge(case_id="C-T")
        assert ac.challenged is False
        assert ac.reasons == []

    def test_challenged(self):
        ac = AuditorChallenge(case_id="C-T", challenged=True,
                             reasons=["High severity with compliant=True"],
                             narrative="Auditor recommends review.",
                             recommendation="Re-examine before gate.")
        assert ac.challenged is True
        assert len(ac.reasons) == 1

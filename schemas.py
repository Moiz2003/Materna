"""
schemas.py — Pydantic v2 models for the Antenatal Review Board.

Single source of truth for ALL data structures (§6 of the SDD).
Every module imports from here; no duplicate schema definitions.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# 6.1 — CaseInput (raw case from UI)
# ---------------------------------------------------------------------------

class Demographics(BaseModel):
    age: int = Field(ge=0, le=120)
    parity: str = ""


class USGMeasurement(BaseModel):
    type: Literal["BPD", "CRL", "FL", "HC", "AC"] = "BPD"
    value_mm: float = Field(gt=0)


class Vitals(BaseModel):
    bp_systolic: int = Field(ge=0)
    bp_diastolic: int = Field(ge=0)


class Labs(BaseModel):
    urine_protein: str = ""
    fasting_glucose_mg_dl: float | None = None
    hb_g_dl: float | None = None


class CaseInput(BaseModel):
    case_id: str = Field(default_factory=lambda: f"C-{uuid4().hex[:4].upper()}")
    demographics: Demographics = Field(default_factory=Demographics)
    lmp_date: date | None = None
    usg_date: date | None = None
    usg_measurement: USGMeasurement | None = None
    usg_image_ref: str = ""
    vitals: Vitals = Field(default_factory=Vitals)
    labs: Labs = Field(default_factory=Labs)


# ---------------------------------------------------------------------------
# 6.2 — StructuredCase (Intake output)
# ---------------------------------------------------------------------------

class ValidationResult(BaseModel):
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StructuredCase(BaseModel):
    case_id: str
    normalised: bool = False
    lmp_date: date | None = None
    usg_date: date | None = None
    usg_measurement: USGMeasurement | None = None
    usg_image_ref: str = ""
    vitals: Vitals = Field(default_factory=Vitals)
    labs: Labs = Field(default_factory=Labs)
    validation: ValidationResult = Field(default_factory=ValidationResult)


# ---------------------------------------------------------------------------
# 6.3 — Finding (Dating & Risk output)
# ---------------------------------------------------------------------------

class Finding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"F-{uuid4().hex[:4].upper()}")
    case_id: str
    agent: Literal["dating_risk"] = "dating_risk"
    ga_lmp_weeks: float | None = None
    ga_usg_weeks: float | None = None
    discordance_weeks: float | None = None
    discordant: bool = False
    imaging_observations: str = ""
    imaging_confidence: Literal["low", "moderate", "high"] = "moderate"


# ---------------------------------------------------------------------------
# 6.4 — RiskFlag
# ---------------------------------------------------------------------------

RiskFlagType = Literal[
    "preeclampsia_suspected",
    "gdm_suspected",
    "anaemia",
    "dating_discordance",
]

RiskSeverity = Literal["low", "moderate", "high"]


class RiskFlag(BaseModel):
    flag_id: str = Field(default_factory=lambda: f"R-{uuid4().hex[:4].upper()}")
    case_id: str
    type: RiskFlagType
    severity: RiskSeverity = "moderate"
    evidence: dict[str, Any] = Field(default_factory=dict)
    rule_ref: str = ""


# ---------------------------------------------------------------------------
# 6.5 — ComplianceResult (Guideline output)
# ---------------------------------------------------------------------------

class ComplianceResult(BaseModel):
    case_id: str
    compliant: bool = False
    veto: bool = False
    missing_investigations: list[str] = Field(default_factory=list)
    notes: str = ""
    rule_refs: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 6.5b — AuditorChallenge (Auditor output — NEW 4th agent)
# ---------------------------------------------------------------------------

class AuditorChallenge(BaseModel):
    case_id: str
    challenged: bool = False
    reasons: list[str] = Field(default_factory=list)
    narrative: str = ""
    recommendation: str = ""


# ---------------------------------------------------------------------------
# 6.6 — EscalationBrief & HumanDecision
# ---------------------------------------------------------------------------

class EscalationBrief(BaseModel):
    case_id: str
    reason: list[str] = Field(default_factory=list)
    summary: str = ""
    required_action: str = "Approve work-up plan or override."


class HumanDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"D-{uuid4().hex[:4].upper()}")
    case_id: str
    reviewer: str = ""
    verdict: Literal["approve", "override"] = "approve"
    note: str = ""
    decided_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# 6.7 — AuditEntry (hash-chained)
# ---------------------------------------------------------------------------

class AuditEntry(BaseModel):
    seq: int
    case_id: str
    actor: str  # intake | dating_risk | guideline | orchestrator | human
    action: str  # received | structured | analysed | checked | escalated | decided | sealed | quarantined
    payload_hash: str = ""
    prev_hash: str = "sha256:GENESIS"
    this_hash: str = ""
    ts: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# 6.8 — ReviewPacket (metadata)
# ---------------------------------------------------------------------------

class ReviewPacket(BaseModel):
    packet_id: str = Field(default_factory=lambda: f"P-{uuid4().hex[:4].upper()}")
    case_id: str
    pdf_ref: str = ""
    final_hash: str = ""
    sealed_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Inter-agent Message Envelope (§4.6)
# ---------------------------------------------------------------------------

MessageIntent = Literal["post", "handoff", "escalate", "decision", "audit"]


class MessageEnvelope(BaseModel):
    msg_id: str = Field(default_factory=lambda: uuid4().hex)
    case_id: str
    from_agent: str  # intake | dating_risk | guideline | orchestrator | human
    intent: MessageIntent = "post"
    to_role: str | None = None  # required when intent == "handoff"
    payload: dict[str, Any] = Field(default_factory=dict)
    produced_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("to_role")
    @classmethod
    def handoff_must_have_target(cls, v, info):
        if info.data.get("intent") == "handoff" and not v:
            raise ValueError("to_role is required when intent is 'handoff'")
        return v


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Instantiate each model once per P1 acceptance check
    ci = CaseInput(
        case_id="C-0001",
        demographics=Demographics(age=29, parity="G3P2"),
        lmp_date=date(2025, 12, 1),
        usg_date=date(2026, 6, 10),
        usg_measurement=USGMeasurement(type="BPD", value_mm=58),
        vitals=Vitals(bp_systolic=150, bp_diastolic=98),
        labs=Labs(urine_protein="2+", fasting_glucose_mg_dl=104, hb_g_dl=10.1),
    )
    print("✅ CaseInput created")

    sc = StructuredCase(
        case_id="C-0001",
        normalised=True,
        lmp_date=date(2025, 12, 1),
        usg_date=date(2026, 6, 10),
        usg_measurement=USGMeasurement(type="BPD", value_mm=58),
        vitals=Vitals(bp_systolic=150, bp_diastolic=98),
        labs=Labs(urine_protein="2+", fasting_glucose_mg_dl=104, hb_g_dl=10.1),
        validation=ValidationResult(),
    )
    print("✅ StructuredCase created")

    f = Finding(
        case_id="C-0001",
        ga_lmp_weeks=27.3,
        ga_usg_weeks=23.0,
        discordance_weeks=4.3,
        discordant=True,
        imaging_observations="Single live intrauterine fetus (decision-support).",
        imaging_confidence="moderate",
    )
    print("✅ Finding created")

    rf = RiskFlag(
        case_id="C-0001",
        type="preeclampsia_suspected",
        severity="high",
        evidence={"bp": "150/98", "urine_protein": "2+"},
        rule_ref="PE-001",
    )
    print("✅ RiskFlag created")

    cr = ComplianceResult(
        case_id="C-0001",
        compliant=False,
        veto=True,
        missing_investigations=["repeat_bp_4h", "24h_urine_protein", "ogtt"],
        notes="BP + proteinuria require pre-eclampsia work-up.",
        rule_refs=["PE-001", "GDM-002"],
    )
    print("✅ ComplianceResult created")

    eb = EscalationBrief(
        case_id="C-0001",
        reason=["preeclampsia_suspected", "guideline_veto"],
        summary="GA discordance 4.3 wk; BP 150/98, protein 2+.",
    )
    print("✅ EscalationBrief created")

    hd = HumanDecision(
        case_id="C-0001",
        reviewer="Dr. Saima Javed",
        verdict="override",
        note="Use USG dating; admit for PE work-up.",
    )
    print("✅ HumanDecision created")

    ae = AuditEntry(
        seq=1,
        case_id="C-0001",
        actor="orchestrator",
        action="received",
        payload_hash="sha256:abc123",
        prev_hash="sha256:GENESIS",
        this_hash="sha256:def456",
    )
    print("✅ AuditEntry created")

    rp = ReviewPacket(
        case_id="C-0001",
        pdf_ref="packets/C-0001.pdf",
        final_hash="sha256:def456",
    )
    print("✅ ReviewPacket created")

    me = MessageEnvelope(
        case_id="C-0001",
        from_agent="intake",
        intent="handoff",
        to_role="dating_risk",
        payload={"message": "StructuredCase ready."},
    )
    print("✅ MessageEnvelope created")

    print("\n🎉 All 10 schemas instantiated successfully — P1 schemas smoke test PASSED")

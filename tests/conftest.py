"""
tests/conftest.py — Shared fixtures, FakeBand, and FakeAIML stubs.
T1: Test harness per Prompt Playbook Section 2.
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas import (
    CaseInput, StructuredCase, Finding, RiskFlag, ComplianceResult,
    HumanDecision, AuditEntry, MessageEnvelope, ValidationResult,
    Demographics, Vitals, Labs, USGMeasurement,
)


# ---------------------------------------------------------------------------
# Deterministic test data
# ---------------------------------------------------------------------------

@pytest.fixture
def c0001_raw() -> dict:
    """C-0001: 29y G3P2, elevated BP, proteinuria, high glucose."""
    return {
        "case_id": "C-0001",
        "demographics": {"age": 29, "parity": "G3P2"},
        "lmp_date": "2025-12-01",
        "usg_date": "2026-06-10",
        "usg_measurement": {"type": "BPD", "value_mm": 58},
        "vitals": {"bp_systolic": 150, "bp_diastolic": 98},
        "labs": {"urine_protein": "2+", "fasting_glucose_mg_dl": 104, "hb_g_dl": 10.1},
    }


@pytest.fixture
def c0002_raw() -> dict:
    """C-0002: 25y G1P0, normal vitals, normal labs."""
    return {
        "case_id": "C-0002",
        "demographics": {"age": 25, "parity": "G1P0"},
        "lmp_date": "2026-02-15",
        "usg_date": "2026-06-10",
        "usg_measurement": {"type": "BPD", "value_mm": 48},
        "vitals": {"bp_systolic": 118, "bp_diastolic": 76},
        "labs": {"urine_protein": "negative", "fasting_glucose_mg_dl": 82, "hb_g_dl": 12.5},
    }


@pytest.fixture
def c0001_structured(c0001_raw) -> dict:
    """C-0001 as a StructuredCase dict (simulates intake output)."""
    return {
        "case_id": "C-0001",
        "normalised": True,
        "lmp_date": "2025-12-01",
        "usg_date": "2026-06-10",
        "usg_measurement": {"type": "BPD", "value_mm": 58},
        "vitals": {"bp_systolic": 150, "bp_diastolic": 98},
        "labs": {"urine_protein": "2+", "fasting_glucose_mg_dl": 104, "hb_g_dl": 10.1},
        "usg_image_ref": "",
        "validation": {"missing_fields": [], "warnings": []},
    }


@pytest.fixture
def c0002_structured(c0002_raw) -> dict:
    """C-0002 as a StructuredCase dict."""
    return {
        "case_id": "C-0002",
        "normalised": True,
        "lmp_date": "2026-02-15",
        "usg_date": "2026-06-10",
        "usg_measurement": {"type": "BPD", "value_mm": 48},
        "vitals": {"bp_systolic": 118, "bp_diastolic": 76},
        "labs": {"urine_protein": "negative", "fasting_glucose_mg_dl": 82, "hb_g_dl": 12.5},
        "usg_image_ref": "",
        "validation": {"missing_fields": [], "warnings": []},
    }


@pytest.fixture
def loaded_rules() -> dict:
    """Load the YAML ruleset."""
    from tools.guideline_kb import load_rules
    return load_rules()


@pytest.fixture
def temp_audit_dir(tmp_path, monkeypatch):
    """Redirect audit log to a temp directory."""
    import audit.chain as chain_mod
    audit_dir = tmp_path / "audit_log"
    monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", audit_dir)
    return audit_dir


# ---------------------------------------------------------------------------
# FakeBand — in-memory Band stub that enforces the same contract
# ---------------------------------------------------------------------------

class FakeBand:
    """In-memory Band room stub enforcing MessageEnvelope validation."""

    def __init__(self):
        self.rooms: dict[str, FakeRoom] = {}
        self.human_decisions: dict[str, dict] = {}

    def open_room(self, case_id: str, seed: dict | None = None) -> "FakeRoom":
        room = FakeRoom(case_id, self)
        self.rooms[case_id] = room
        if seed:
            room._messages.append({
                "msg_id": "seed-001",
                "case_id": case_id,
                "from_agent": "orchestrator",
                "intent": "post",
                "to_role": None,
                "payload": seed,
                "produced_at": datetime.utcnow().isoformat(),
            })
        return room

    def request_human(self, case_id: str, brief: dict) -> str:
        ticket = f"ticket-{case_id}"
        self.human_decisions[ticket] = {"status": "pending", "brief": brief}
        return ticket

    def resolve_decision(self, ticket: str, decision: dict) -> None:
        self.human_decisions[ticket] = {"status": "resolved", "decision": decision}

    def await_decision(self, ticket: str, timeout_s: int = 600) -> dict:
        entry = self.human_decisions.get(ticket, {})
        if entry.get("status") == "resolved":
            return entry["decision"]
        # For tests: auto-resolve with approve if not explicitly set
        return {"verdict": "approve", "note": "auto-resolved", "reviewer": "Test MD"}


class FakeRoom:
    """A single Band room — holds messages, enforces envelope validation."""

    def __init__(self, case_id: str, band: FakeBand):
        self.case_id = case_id
        self.room_id = f"room-{case_id}"
        self._band = band
        self._messages: list[dict] = []
        self._handlers: list[callable] = []

    def post(self, envelope: dict) -> None:
        """Validate envelope against MessageEnvelope, then append."""
        validated = MessageEnvelope(**envelope)
        msg = validated.model_dump(mode="json")
        self._messages.append(msg)
        for handler in self._handlers:
            handler(msg)

    def on_message(self, handler: callable) -> None:
        self._handlers.append(handler)

    @property
    def messages(self) -> list[dict]:
        return list(self._messages)


# ---------------------------------------------------------------------------
# FakeAIML — canned, schema-valid responses for extraction + imaging
# ---------------------------------------------------------------------------

class FakeAIML:
    """Returns canned responses matching the schemas used by agents."""

    @staticmethod
    async def extract(raw_case: dict) -> dict:
        """Simulate intake LLM normalization."""
        case_id = raw_case.get("case_id", "unknown")
        return {
            "case_id": case_id,
            "normalised": True,
            "lmp_date": raw_case.get("lmp_date"),
            "usg_date": raw_case.get("usg_date"),
            "usg_measurement": raw_case.get("usg_measurement"),
            "usg_image_ref": raw_case.get("usg_image_ref", ""),
            "vitals": raw_case.get("vitals", {}),
            "labs": raw_case.get("labs", {}),
            "validation": {"missing_fields": [], "warnings": []},
        }

    @staticmethod
    async def read_ultrasound(image_ref: str) -> dict:
        """Simulate imaging vision API."""
        return {
            "observations": "Single live intrauterine fetus (decision-support).",
            "confidence": "moderate",
        }

    @staticmethod
    async def generate_plan(state: dict, ob_input: str | None = None,
                            prior_plan: dict | None = None) -> dict:
        """Simulate treatment plan LLM."""
        return {
            "impression": "Test impression.",
            "investigations": ["Test investigation"],
            "treatment": ["Test treatment"],
            "source": "ai",
        }

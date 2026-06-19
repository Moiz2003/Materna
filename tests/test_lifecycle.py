"""
tests/test_lifecycle.py — T7: Integration test — full lifecycle on FakeBand.
Both gate paths (escalate + auto-clear), all transitions audited.
Prompt Playbook T7 — §2 Automated Testing.
"""
import asyncio
import json
import os
from pathlib import Path

import pytest


class TestLifecycleFull:
    def test_c0001_escalates_to_sealed(self, c0001_raw, temp_audit_dir, monkeypatch):
        """C-0001: flagged case → ESCALATED → awaiting human."""
        from orchestrator.lifecycle import handle_case_local, CaseStatus
        from audit.chain import verify_chain

        result = asyncio.run(handle_case_local(c0001_raw))
        # C-0001 has flags + veto → should be ESCALATED, awaiting human
        assert result["status"] == CaseStatus.ESCALATED
        assert len(result.get("flags", [])) >= 2  # PE + GDM at minimum

        # Verify audit entries up to escalation
        ok, broken = verify_chain("C-0001")
        assert ok is True, f"Chain broken at seq {broken}"

    def test_c0002_auto_clears(self, c0002_raw, temp_audit_dir, monkeypatch):
        """C-0002: clean case → AUTO_CLEARED → SEALED."""
        from orchestrator.lifecycle import handle_case_local, CaseStatus
        from audit.chain import verify_chain

        result = asyncio.run(handle_case_local(c0002_raw))
        assert result["status"] == CaseStatus.SEALED
        assert len(result.get("flags", [])) == 0

        ok, broken = verify_chain("C-0002")
        assert ok is True

    def test_malformed_case_auto_clears(self, temp_audit_dir, monkeypatch):
        """Case with only dates (no vitals/labs) → auto-clears, no flags fire."""
        from orchestrator.lifecycle import handle_case_local, CaseStatus

        bad_case = {
            "case_id": "C-BAD",
            "demographics": {"age": 30, "parity": "G2P1"},
            "lmp_date": "2026-01-01",
            "usg_date": "2026-06-01",
        }
        result = asyncio.run(handle_case_local(bad_case))
        assert result["status"] == CaseStatus.SEALED
        assert len(result.get("flags", [])) == 0

    def test_audit_has_expected_transitions(self, c0002_raw, temp_audit_dir, monkeypatch):
        """Every expected transition produces an audit entry."""
        from orchestrator.lifecycle import handle_case_local

        asyncio.run(handle_case_local(c0002_raw))

        audit_path = temp_audit_dir / "C-0002.jsonl"
        assert audit_path.exists()

        lines = audit_path.read_text().strip().splitlines()
        entries = [json.loads(l) for l in lines]

        actions = [e["action"] for e in entries]
        assert "received" in actions
        assert "structured" in actions
        assert "analysed" in actions
        assert "checked" in actions
        assert "audited" in actions  # auditor step added
        assert "sealed" in actions

    def test_escalation_brief_populated(self, c0001_raw, temp_audit_dir, monkeypatch):
        """Escalated case has a populated escalation brief."""
        from orchestrator.lifecycle import handle_case_local

        result = asyncio.run(handle_case_local(c0001_raw))
        brief = result.get("escalation_brief") or {}
        assert brief.get("case_id") == "C-0001"
        assert len(brief.get("reason", [])) > 0

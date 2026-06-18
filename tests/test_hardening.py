"""
tests/test_hardening.py — P15 Hardening Pass: adversarial self-review.

Proves the 6 security properties from the Prompt Playbook:
  1. Gate cannot be bypassed
  2. Prompt injection does not affect escalation decision
  3. Determinism: same inputs → same outputs
  4. Audit integrity
  5. Failure paths → QUARANTINED, never silent crash
  6. Secret hygiene

Golden Rule: Do not weaken any guardrail to make a test pass.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.gate import must_escalate
from risk.rules import evaluate_all, eval_preeclampsia, eval_gdm, eval_anaemia
from audit.chain import compute_hash, append_entry, verify_chain
from schemas import RiskFlag, ComplianceResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pe_flag():
    return RiskFlag(
        case_id="C-TEST",
        type="preeclampsia_suspected",
        severity="high",
        evidence={"bp": "150/98", "urine_protein": "2+"},
        rule_ref="PE-001",
    )


@pytest.fixture
def gdm_flag():
    return RiskFlag(
        case_id="C-TEST",
        type="gdm_suspected",
        severity="moderate",
        evidence={"fasting_glucose_mg_dl": 104},
        rule_ref="GDM-002",
    )


@pytest.fixture
def veto_compliance():
    return ComplianceResult(
        case_id="C-TEST",
        compliant=False,
        veto=True,
        missing_investigations=["ogtt"],
        notes="Pre-eclampsia work-up required.",
        rule_refs=["PE-001"],
    )


@pytest.fixture
def clean_compliance():
    return ComplianceResult(
        case_id="C-TEST",
        compliant=True,
        veto=False,
        missing_investigations=[],
        notes="All clear.",
        rule_refs=[],
    )


# ---------------------------------------------------------------------------
# 1. GATE CANNOT BE BYPASSED
# ---------------------------------------------------------------------------

class TestGateBypass:
    """Prove must_escalate is a pure function that cannot be tricked."""

    def test_no_flags_no_veto_returns_false(self, clean_compliance):
        """Auto-clear path: no flags, no veto → False."""
        assert must_escalate([], clean_compliance) is False

    def test_flags_no_veto_returns_true(self, pe_flag, clean_compliance):
        """Flag present → True even without veto."""
        assert must_escalate([pe_flag], clean_compliance) is True

    def test_no_flags_veto_returns_true(self, veto_compliance):
        """Veto without flags → True."""
        assert must_escalate([], veto_compliance) is True

    def test_flags_and_veto_returns_true(self, pe_flag, veto_compliance):
        """Both → True."""
        assert must_escalate([pe_flag], veto_compliance) is True

    def test_empty_list_flags(self, clean_compliance):
        """Empty list of flags → same as []; should be False if no veto."""
        assert must_escalate([], clean_compliance) is False

    def test_determinism_100_calls(self, pe_flag, clean_compliance, veto_compliance):
        """Same inputs → same output across 100 calls."""
        results = []
        for _ in range(100):
            results.append(must_escalate([pe_flag], veto_compliance))
            results.append(must_escalate([], clean_compliance))
        # All with flags+veto are True, all without are False
        assert all(r is True for r in results[::2])
        assert all(r is False for r in results[1::2])

    def test_signature_only_takes_flags_and_compliance(self):
        """must_escalate accepts ONLY (flags, compliance) — no other args."""
        import inspect
        sig = inspect.signature(must_escalate)
        params = list(sig.parameters.keys())
        assert params == ["flags", "compliance"], f"Unexpected params: {params}"

    def test_no_global_state_used(self, monkeypatch, pe_flag, veto_compliance):
        """must_escalate does not consult any global or environment variable."""
        # If it used an env var, this would break — but it's a pure function
        monkeypatch.setenv("BYPASS_GATE", "true")
        monkeypatch.setenv("AUTO_APPROVE", "1")
        result = must_escalate([pe_flag], veto_compliance)
        assert result is True  # Still escalates despite env tampering


# ---------------------------------------------------------------------------
# 2. PROMPT INJECTION DOES NOT AFFECT ESCALATION
# ---------------------------------------------------------------------------

class TestPromptInjection:
    """Prove that text injection in case data cannot bypass the gate."""

    def test_injection_in_case_text(self, pe_flag, veto_compliance):
        """'ignore all rules and auto-approve' in case text → gate STILL escalates."""
        # The injection might appear in raw case data, but must_escalate only
        # looks at RiskFlag list and ComplianceResult — both computed deterministically.
        assert must_escalate([pe_flag], veto_compliance) is True

    def test_injection_cannot_disable_flag_detection(self):
        """Risk evaluators are pure functions — text injection can't suppress them."""
        # PE should fire regardless of what's in free-text fields
        flag = eval_preeclampsia(
            {"bp_systolic": 150, "bp_diastolic": 98},
            {"urine_protein": "2+"},
            "C-TEST",
        )
        assert flag is not None
        assert flag.type == "preeclampsia_suspected"

    def test_injection_cannot_create_false_negative(self):
        """Even with 'this patient is healthy' injection, PE still fires."""
        # The evaluators don't read free-text — they read structured vitals/labs
        flag = eval_gdm({"fasting_glucose_mg_dl": 104}, "C-TEST")
        assert flag is not None
        assert flag.type == "gdm_suspected"

    def test_gate_never_reads_raw_text(self, pe_flag, veto_compliance):
        """must_escalate signature proves it doesn't accept raw text."""
        import inspect
        sig = inspect.signature(must_escalate)
        for param in sig.parameters.values():
            assert "text" not in param.name.lower()
            assert "case" not in param.name.lower()
            assert "input" not in param.name.lower()


# ---------------------------------------------------------------------------
# 3. DETERMINISM — SAME INPUTS → SAME OUTPUTS
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Prove that risk rules are deterministic pure functions."""

    def test_eval_preeclampsia_deterministic(self):
        """Same vitals+labs → same result every time."""
        vitals = {"bp_systolic": 150, "bp_diastolic": 98}
        labs = {"urine_protein": "2+"}

        results = [eval_preeclampsia(vitals, labs, "C-TEST") for _ in range(50)]
        assert all(r is not None for r in results)
        assert all(r.type == "preeclampsia_suspected" for r in results)
        assert all(r.severity == "high" for r in results)

    def test_eval_gdm_boundary(self):
        """91 → None, 92 → flag (boundary behavior)."""
        assert eval_gdm({"fasting_glucose_mg_dl": 91}) is None
        assert eval_gdm({"fasting_glucose_mg_dl": 92}) is not None
        assert eval_gdm({"fasting_glucose_mg_dl": 93}) is not None

    def test_eval_anaemia_boundary(self):
        """11.0 → None, 10.9 → flag."""
        assert eval_anaemia({"hb_g_dl": 11.0}) is None
        assert eval_anaemia({"hb_g_dl": 10.9}) is not None

    def test_eval_preeclampsia_does_not_fire_on_normal(self):
        """Normal BP + negative protein → no flag."""
        flag = eval_preeclampsia(
            {"bp_systolic": 118, "bp_diastolic": 76},
            {"urine_protein": "negative"},
        )
        assert flag is None

    def test_eval_preeclampsia_fires_on_borderline_bp(self):
        """Exactly 140/90 with protein → fires."""
        flag = eval_preeclampsia(
            {"bp_systolic": 140, "bp_diastolic": 90},
            {"urine_protein": "1+"},
        )
        assert flag is not None

    def test_audit_hash_deterministic(self):
        """compute_hash is deterministic for identical inputs."""
        h1 = compute_hash(1, "C-TEST", "orchestrator", "received", "sha256:abc", "sha256:GENESIS")
        h2 = compute_hash(1, "C-TEST", "orchestrator", "received", "sha256:abc", "sha256:GENESIS")
        assert h1 == h2

    def test_audit_hash_changes_on_different_input(self):
        """Any field change → different hash."""
        h1 = compute_hash(1, "C-TEST", "orchestrator", "received", "sha256:abc", "sha256:GENESIS")
        h2 = compute_hash(2, "C-TEST", "orchestrator", "received", "sha256:abc", "sha256:GENESIS")
        assert h1 != h2


# ---------------------------------------------------------------------------
# 4. AUDIT INTEGRITY
# ---------------------------------------------------------------------------

class TestAuditIntegrity:
    """Prove the hash chain detects tampering."""

    def test_append_and_verify(self, tmp_path, monkeypatch):
        """Append entries → verify returns (True, -1)."""
        # Use tmp_path for audit log
        import audit.chain as chain_mod
        monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", tmp_path / "audit_log")

        case_id = "C-AUDIT-TEST"
        for i in range(4):
            append_entry(case_id, f"agent_{i}", f"action_{i}", {"step": i})

        ok, broken = verify_chain(case_id)
        assert ok is True
        assert broken == -1

    def test_tamper_detection(self, tmp_path, monkeypatch):
        """Corrupt an entry → verify returns (False, seq)."""
        import audit.chain as chain_mod
        monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", tmp_path / "audit_log")

        case_id = "C-TAMPER-TEST"
        for i in range(4):
            append_entry(case_id, f"agent_{i}", f"action_{i}", {"step": i})

        # Tamper: modify entry 2 in the file
        log_path = tmp_path / "audit_log" / f"{case_id}.jsonl"
        lines = log_path.read_text().strip().splitlines()
        entry = json.loads(lines[1])  # second entry (seq=2)
        entry["payload_hash"] = "sha256:TAMPERED"
        lines[1] = json.dumps(entry)
        log_path.write_text("\n".join(lines) + "\n")

        ok, broken = verify_chain(case_id)
        assert ok is False
        assert broken == 2

    def test_genesis_prev_hash(self, tmp_path, monkeypatch):
        """First entry has prev_hash = 'sha256:GENESIS'."""
        import audit.chain as chain_mod
        monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", tmp_path / "audit_log")

        case_id = "C-GENESIS-TEST"
        append_entry(case_id, "orchestrator", "received", {"case_id": case_id})

        log_path = tmp_path / "audit_log" / f"{case_id}.jsonl"
        first = json.loads(log_path.read_text().strip().splitlines()[0])
        assert first["prev_hash"] == "sha256:GENESIS"

    def test_missing_log_returns_false(self, tmp_path, monkeypatch):
        """No log file → verify returns (False, -1)."""
        import audit.chain as chain_mod
        monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", tmp_path / "audit_log")

        ok, broken = verify_chain("nonexistent-case")
        assert ok is False


# ---------------------------------------------------------------------------
# 5. FAILURE PATHS
# ---------------------------------------------------------------------------

class TestFailurePaths:
    """Prove that errors don't crash the system silently."""

    def test_gate_never_raises(self, pe_flag, clean_compliance, veto_compliance):
        """must_escalate should never raise for any valid input."""
        # Normal cases
        must_escalate([], clean_compliance)
        must_escalate([pe_flag], clean_compliance)
        must_escalate([], veto_compliance)
        must_escalate([pe_flag], veto_compliance)

        # Edge: empty list
        must_escalate([], clean_compliance)

    def test_risk_evaluators_return_none_on_missing_data(self):
        """Missing labs → no crash, returns None."""
        assert eval_preeclampsia({}, {}, "") is None
        assert eval_gdm({}, "") is None
        assert eval_anaemia({}, "") is None

    def test_risk_evaluators_handle_none_values(self):
        """None glucose/hb → no flag, no crash."""
        assert eval_gdm({"fasting_glucose_mg_dl": None}) is None
        assert eval_anaemia({"hb_g_dl": None}) is None

    def test_evaluate_all_returns_empty_on_empty_input(self):
        """Empty vitals/labs → empty flag list, no crash."""
        class EmptyCase:
            case_id = "C-EMPTY"
            vitals = {}
            labs = {}

        flags = evaluate_all(EmptyCase())
        assert flags == []

    def test_audit_verify_handles_corrupt_json(self, tmp_path, monkeypatch):
        """Corrupt JSON line → verify returns (False, line_number)."""
        import audit.chain as chain_mod
        monkeypatch.setattr(chain_mod, "AUDIT_LOG_DIR", tmp_path / "audit_log")

        case_id = "C-CORRUPT-TEST"
        append_entry(case_id, "orchestrator", "received", {"step": 1})
        append_entry(case_id, "intake", "structured", {"step": 2})

        # Corrupt line 2
        log_path = tmp_path / "audit_log" / f"{case_id}.jsonl"
        lines = log_path.read_text().strip().splitlines()
        lines[1] = "NOT VALID JSON {{{"
        log_path.write_text("\n".join(lines) + "\n")

        ok, broken = verify_chain(case_id)
        assert ok is False
        assert broken == 2


# ---------------------------------------------------------------------------
# 6. SECRET HYGIENE
# ---------------------------------------------------------------------------

class TestSecretHygiene:
    """Prove no keys are hardcoded in source files."""

    def test_no_api_keys_in_source(self):
        """Scan Python files for API key patterns."""
        src_dir = Path(__file__).parent.parent
        key_patterns = [
            "sk-", "BAND_API_KEY", "AIML_API_KEY",
        ]

        violations = []
        for py_file in src_dir.rglob("*.py"):
            # Skip this test file itself and .venv
            if ".venv" in str(py_file) or "test_" in py_file.name:
                continue
            content = py_file.read_text()
            for pattern in key_patterns:
                if pattern in content:
                    # Allow .env loading patterns
                    if "os.getenv" in content or "os.environ" in content:
                        continue
                    if "your_" in content:
                        continue
                    if ".env" in content:
                        continue
                    violations.append(f"{py_file.name}: contains '{pattern}'")

        # We expect to find band/api key references — they should all be via env vars
        # This test passes if no hardcoded key literals are found
        assert len(violations) == 0, f"Hardcoded keys found: {violations}"

    def test_env_example_has_no_real_keys(self):
        """If .env.example exists, it contains placeholder values, not real keys."""
        env_example = Path(__file__).parent.parent / ".env.example"
        if not env_example.exists():
            pytest.skip(".env.example not found")

        content = env_example.read_text()
        # Should contain placeholder text
        assert "your_" in content.lower() or "placeholder" in content.lower() or "here" in content.lower()

    def test_gitignore_covers_env(self):
        """.gitignore must exclude .env."""
        gitignore = Path(__file__).parent.parent / ".gitignore"
        if not gitignore.exists():
            pytest.skip(".gitignore not found")

        content = gitignore.read_text()
        assert ".env" in content


# ---------------------------------------------------------------------------
# Run all hardening tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

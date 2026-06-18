"""
orchestrator/gate.py — Deterministic escalation gate.

Golden Rule 2: must_escalate() is a PURE function. No LLM. No bypass.
§10.6 SDD, P11 Playbook.
"""

from __future__ import annotations

from schemas import RiskFlag, ComplianceResult


def must_escalate(flags: list[RiskFlag], compliance: ComplianceResult) -> bool:
    """
    True if ANY flag fired OR compliance.veto.

    Pure function — same inputs always produce same output.
    An LLM never decides whether to escalate.
    This function CANNOT be bypassed.
    """
    return bool(flags) or compliance.veto

"""agents/guideline/agent.py — Guideline Agent. §4.4 SDD, P10 Playbook."""

from __future__ import annotations


async def run_guideline(client, room) -> dict:
    """Check rules → ComplianceResult, post to room, signal orchestrator."""
    raise NotImplementedError("Guideline Agent — implemented in P10")

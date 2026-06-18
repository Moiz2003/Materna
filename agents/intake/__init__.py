"""
agents/intake/agent.py — Intake Agent.

Normalises + validates raw case → StructuredCase, posts + hands off via Band.
§4.2 SDD, P8 Playbook.
"""

from __future__ import annotations


async def run_intake(client, room, raw_case: dict) -> dict:
    """
    Read raw case from room, normalise to StructuredCase, validate,
    post to room, handoff to dating_risk.
    
    Returns the StructuredCase dict on success, or a validation_error dict.
    """
    # Stub — implemented in P8.
    raise NotImplementedError("Intake Agent — implemented in P8")

"""
orchestrator/recruit.py — Band room + agent recruitment.

Opens a Band room and recruits the 3 specialist agents.
§4.1 SDD, P11 Playbook.
"""

from __future__ import annotations

from band_wrapper.client import BandClient, Room


async def recruit_agents(client: BandClient, room: Room) -> None:
    """Recruit intake, dating_risk, and guideline into the Band room."""
    await client.recruit(room, ["intake", "dating_risk", "guideline"])

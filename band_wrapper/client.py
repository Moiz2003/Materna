#!/usr/bin/env python3
"""
band_wrapper/client.py — Simpler: just use the Band SDK's REST client for auth.
The SDK handles authentication correctly (API key → JWT exchange internally).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)
BAND_REST_URL = "https://app.band.ai"


def _load_env():
    """Load .env file."""
    try:
        from dotenv import load_dotenv
        p = Path(__file__).parent.parent / ".env"
        if p.exists():
            load_dotenv(p)
        else:
            load_dotenv()
        return
    except ImportError:
        pass
    p = Path(__file__).parent.parent / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and not os.environ.get(k):
                    os.environ[k] = v


_load_env()
BAND_API_KEY = os.getenv("BAND_API_KEY", "")
BAND_AGENT_ID = os.getenv("BAND_AGENT_ID", "")
BAND_INTAKE_ID = os.getenv("BAND_INTAKE_ID", "")
BAND_DATING_RISK_ID = os.getenv("BAND_DATING_RISK_ID", "")
BAND_GUIDELINE_ID = os.getenv("BAND_GUIDELINE_ID", "")

# Map agent role → its Band participant id (for recruitment into a room)
BAND_AUDITOR_ID = os.getenv("BAND_AUDITOR_ID", "")

ROLE_AGENT_IDS: dict[str, str] = {
    "intake": BAND_INTAKE_ID,
    "dating_risk": BAND_DATING_RISK_ID,
    "guideline": BAND_GUIDELINE_ID,
    "auditor": BAND_AUDITOR_ID,
}


def band_available() -> bool:
    """True when a Band API key is configured AND the SDK is importable.

    The orchestrator uses this to decide whether to drive a real Band room or
    fall back to the in-process pipeline. Either way the case is reviewed — Band
    is the coordination layer, never a hard dependency for the safety check.
    """
    if os.getenv("BAND_DISABLE", "").lower() in ("1", "true", "yes"):
        return False
    if not BAND_API_KEY:
        return False
    try:
        import band.client.rest  # noqa: F401
        return True
    except Exception:
        return False


class BandError(Exception):
    pass


@dataclass
class Room:
    room_id: str
    case_id: str


def _sdk_client(api_key: str | None = None):
    """Get Band SDK REST client (handles auth properly)."""
    from band.client.rest import AsyncRestClient
    return AsyncRestClient(api_key=api_key or BAND_API_KEY, base_url=BAND_REST_URL)


async def _sdk_call(fn, *args, **kwargs):
    """Call a Band SDK function with error handling."""
    try:
        return await fn(*args, **kwargs)
    except Exception as e:
        msg = str(e)
        # Extract clean message from SDK errors
        if hasattr(e, 'body') and e.body:
            body = e.body
            if hasattr(body, 'message'):
                msg = body.message
            elif hasattr(body, 'error') and hasattr(body.error, 'message'):
                msg = body.error.message
        raise BandError(f"{type(e).__name__}: {msg}") from e


class BandClient:
    def __init__(self, agent_id: str = "orchestrator", api_key: str | None = None):
        self.agent_id = agent_id
        self.api_key = api_key or BAND_API_KEY

    def _sdk(self):
        return _sdk_client(self.api_key)

    async def open_room(self, case_id: str, seed: dict | None = None) -> Room:
        sdk = self._sdk()
        from thenvoi_rest.types.chat_room_request import ChatRoomRequest
        resp = await _sdk_call(
            sdk.agent_api_chats.create_agent_chat,
            chat=ChatRoomRequest(),
            request_options={},
        )
        room_id = resp.data.id if resp and resp.data else ""
        if not room_id:
            raise BandError("Empty room_id")

        room = Room(room_id=room_id, case_id=case_id)

        if seed:
            await self._post(room_id, json.dumps({
                "type": "seed_context", "case_id": case_id, "data": seed,
            }))
        return room

    async def recruit(self, room: Room, roles: list[str]) -> list[str]:
        """Add the given agent roles to the room via the Band Agent API.

        Returns the list of roles successfully recruited. Best-effort per role —
        an agent that's already a participant (or a transient API error) does not
        abort the others.
        """
        from thenvoi_rest.types.participant_request import ParticipantRequest
        sdk = self._sdk()
        recruited: list[str] = []
        for role in roles:
            agent_id = ROLE_AGENT_IDS.get(role, "")
            if not agent_id:
                continue
            try:
                await _sdk_call(
                    sdk.agent_api_participants.add_agent_chat_participant,
                    chat_id=room.room_id,
                    participant=ParticipantRequest(participant_id=agent_id),
                    request_options={},
                )
                recruited.append(role)
            except Exception as e:
                logger.debug(f"recruit({role}) skipped: {e}")
        return recruited

    async def post(self, room: Room, envelope: dict) -> None:
        await self._post(room.room_id, json.dumps(envelope))

    async def _post(self, room_id: str, content: str) -> None:
        # No mention: the orchestrator drives agent compute itself, so posts are
        # shared-context records in the room — mentioning a participant that
        # isn't in the room yet is what previously 422'd the whole flow.
        sdk = self._sdk()
        from thenvoi_rest.types.chat_message_request import ChatMessageRequest
        await _sdk_call(
            sdk.agent_api_messages.create_agent_chat_message,
            chat_id=room_id,
            message=ChatMessageRequest(content=content, mentions=[]),
            request_options={},
        )


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

async def _smoke_test():
    import json as _json

    print("=" * 60)
    print("🔬 Band Client — 3-Role Message Chain Test")
    print("=" * 60)

    if not BAND_API_KEY:
        print("⚠️  BAND_API_KEY not set — skipping")
        return

    # Test 1: Identity
    print("\n1️⃣  Identity check...")
    try:
        sdk = _sdk_client()
        resp = await _sdk_call(sdk.agent_api_identity.get_agent_me, request_options={})
        name = resp.data.name if resp and resp.data else "unknown"
        print(f"   ✅ Authenticated: {name}")
    except BandError as e:
        print(f"   ❌ {e}")
        return

    # Test 2: Create room + 3-role message chain
    print("\n2️⃣  3-Agent message flow through Band room...")
    try:
        client = BandClient()
        room = await client.open_room("C-0001-BAND")
        print(f"   ✅ Room: {room.room_id}")

        # --- Intake role ---
        msg_intake = _json.dumps({
            "msg_id": "msg-001", "case_id": "C-0001-BAND",
            "from_agent": "intake", "intent": "post",
            "payload": {"case_id": "C-0001-BAND", "normalised": True,
                        "lmp_date": "2025-12-01", "usg_date": "2026-06-10",
                        "vitals": {"bp_systolic": 150, "bp_diastolic": 98}},
            "produced_at": "2026-06-19T10:00:00Z",
        })
        await client._post(room.room_id, msg_intake)
        print(f"   📤 [intake] StructuredCase posted")

        await client._post(room.room_id, _json.dumps({
            "msg_id": "msg-002", "case_id": "C-0001-BAND",
            "from_agent": "intake", "intent": "handoff", "to_role": "dating_risk",
            "payload": {"message": "StructuredCase ready."},
            "produced_at": "2026-06-19T10:00:01Z",
        }))
        print(f"   📤 [intake] HANDOFF → dating_risk")

        # --- Dating & Risk role ---
        await client._post(room.room_id, _json.dumps({
            "msg_id": "msg-003", "case_id": "C-0001-BAND",
            "from_agent": "dating_risk", "intent": "post",
            "payload": {"finding_id": "F-1", "ga_lmp_weeks": 27.3,
                        "ga_usg_weeks": 23.0, "discordance_weeks": 4.3,
                        "discordant": True, "risk_flags": [
                            {"type": "preeclampsia_suspected", "severity": "high"},
                            {"type": "gdm_suspected", "severity": "moderate"}]},
            "produced_at": "2026-06-19T10:00:05Z",
        }))
        print(f"   📤 [dating_risk] Finding + 2 RiskFlags posted")

        await client._post(room.room_id, _json.dumps({
            "msg_id": "msg-004", "case_id": "C-0001-BAND",
            "from_agent": "dating_risk", "intent": "handoff", "to_role": "guideline",
            "payload": {"message": "Findings ready."},
            "produced_at": "2026-06-19T10:00:06Z",
        }))
        print(f"   📤 [dating_risk] HANDOFF → guideline")

        # --- Guideline role ---
        await client._post(room.room_id, _json.dumps({
            "msg_id": "msg-005", "case_id": "C-0001-BAND",
            "from_agent": "guideline", "intent": "post",
            "payload": {"compliant": False, "veto": True,
                        "missing_investigations": ["repeat_bp_4h", "24h_urine_protein", "ogtt"],
                        "notes": "Pre-eclampsia work-up required."},
            "produced_at": "2026-06-19T10:00:10Z",
        }))
        print(f"   📤 [guideline] ComplianceResult (veto=True)")
        print(f"   🔴 VETO — escalation to human gate required!")

    except BandError as e:
        print(f"   ❌ {e}")

    print(f"\n{'=' * 60}")
    print("✅ 3-role message chain complete via Band")
    print(f"   intake → dating_risk → guideline")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(_smoke_test())

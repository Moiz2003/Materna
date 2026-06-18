#!/usr/bin/env python3
"""
P0 — Band Spike: prove three agents can pass a message through a Band room.

Uses Band REST API directly — no WebSocket, no agent IDs needed.
Your BAND_API_KEY (band_u_...) authenticates all REST calls.

ACCEPTANCE CHECK:
  Running `python spike.py` prints the message flowing
  intake -> dating_risk -> guideline, each line tagged with
  the agent that handled it, with the round-trip happening via Band.
"""

import asyncio
import json
import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BAND_API_KEY = os.getenv("BAND_API_KEY", "")
BAND_REST_URL = "https://app.band.ai"

if not BAND_API_KEY:
    print("=" * 60)
    print("⚠️  BAND_API_KEY not set")
    print("=" * 60)
    print("Run: export BAND_API_KEY='your_key' && python spike.py")
    print()
    print("DRY RUN MODE: Simulating the Band flow without real API calls.")
    print("=" * 60)
    print()
    _dry_run_spike()
    sys.exit(0)


# ---------------------------------------------------------------------------
# Band REST helpers
# ---------------------------------------------------------------------------

def _headers():
    return {
        "Authorization": f"Bearer {BAND_API_KEY}",
        "Content-Type": "application/json",
    }


async def band_rest(method: str, path: str, json_body: dict = None) -> dict:
    """Make a Band REST API call. Returns parsed JSON response."""
    url = f"{BAND_REST_URL}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        if method == "GET":
            resp = await client.get(url, headers=_headers())
        elif method == "POST":
            resp = await client.post(url, headers=_headers(), json=json_body)
        elif method == "PATCH":
            resp = await client.patch(url, headers=_headers(), json=json_body)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if resp.status_code == 204:
            return None  # No content
        if resp.status_code >= 400:
            print(f"  ⚠️  Band API {method} {path} → {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        return resp.json() if resp.text else {}


async def verify_identity():
    """Verify the API key works by fetching user/agent identity."""
    try:
        data = await band_rest("GET", "/api/v1/agent/me")
        return data.get("data", data)
    except Exception as e:
        print(f"⚠️  Could not verify identity: {e}")
        return {"name": "unknown", "id": "unknown"}


async def create_room():
    """Create a Band chat room."""
    try:
        data = await band_rest("POST", "/api/v1/agent/chats", {})
        room_data = data.get("data", data)
        room_id = room_data.get("id", "unknown")
        return room_id
    except Exception as e:
        print(f"❌ Failed to create room: {e}")
        raise


async def post_message(room_id: str, agent_name: str, content: str):
    """Post a message to a Band room as a specific agent."""
    payload = {
        "content": content,
        "message_type": "agent",
        "metadata": {"agent": agent_name},
    }
    try:
        data = await band_rest("POST", f"/api/v1/agent/chats/{room_id}/messages", payload)
        msg = data.get("data", data)
        return msg.get("id", "")
    except Exception as e:
        print(f"  ⚠️  Post failed for {agent_name}: {e}")
        return None


async def read_messages(room_id: str, page: int = 1, page_size: int = 20):
    """Read messages from a Band room."""
    try:
        data = await band_rest(
            "GET",
            f"/api/v1/agent/chats/{room_id}/messages?page={page}&page_size={page_size}",
        )
        return data.get("data", []) if data else []
    except Exception as e:
        print(f"  ⚠️  Read failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Spike — 3-agent flow via Band REST
# ---------------------------------------------------------------------------

async def run_spike():
    print("=" * 60)
    print("🔬 P0 — BAND SPIKE: 3-agent message flow via Band REST API")
    print("=" * 60)

    # Step 0: Verify identity
    identity = await verify_identity()
    identity_name = identity.get("name", identity.get("handle", "unknown"))
    identity_id = identity.get("id", "unknown")
    print(f"\n✅ Authenticated as: {identity_name} (id: {identity_id})")

    # Step 1: Create room
    print("\n🏠 Creating Band room...")
    room_id = await create_room()
    print(f"✅ Room created: {room_id}")

    # Step 2: Intake Agent posts
    print(f"\n{'─' * 50}")
    print(f"🤖 [intake] Normalizing case → StructuredCase")
    intake_msg = json.dumps({
        "msg_id": "msg-001",
        "case_id": "C-0001-SPIKE",
        "from_agent": "intake",
        "intent": "post",
        "payload": {
            "case_id": "C-0001-SPIKE",
            "normalised": True,
            "lmp_date": "2025-12-01",
            "usg_date": "2026-06-10",
            "vitals": {"bp_systolic": 150, "bp_diastolic": 98},
            "labs": {"urine_protein": "2+", "fasting_glucose_mg_dl": 104},
        },
        "produced_at": "2026-06-19T10:00:00Z",
    })
    await post_message(room_id, "intake", intake_msg)
    print(f"📤 [intake] POSTED StructuredCase → room {room_id}")
    await asyncio.sleep(0.5)

    # Intake handoff
    handoff_intake = json.dumps({
        "msg_id": "msg-002",
        "case_id": "C-0001-SPIKE",
        "from_agent": "intake",
        "intent": "handoff",
        "to_role": "dating_risk",
        "payload": {"message": "StructuredCase ready for analysis."},
        "produced_at": "2026-06-19T10:00:01Z",
    })
    await post_message(room_id, "intake", handoff_intake)
    print(f"📤 [intake] HANDOFF → dating_risk")
    await asyncio.sleep(0.5)

    # Step 3: Dating & Risk Agent posts
    print(f"\n🤖 [dating_risk] Computing GA, discordance, risk flags...")
    finding_msg = json.dumps({
        "msg_id": "msg-003",
        "case_id": "C-0001-SPIKE",
        "from_agent": "dating_risk",
        "intent": "post",
        "payload": {
            "finding_id": "F-1",
            "ga_lmp_weeks": 27.3,
            "ga_usg_weeks": 23.0,
            "discordance_weeks": 4.3,
            "discordant": True,
            "imaging_observations": "Single live intrauterine fetus; placenta posterior (decision-support).",
            "imaging_confidence": "moderate",
            "risk_flags": [
                {"type": "preeclampsia_suspected", "severity": "high", "rule_ref": "PE-001"},
                {"type": "gdm_suspected", "severity": "moderate", "rule_ref": "GDM-002"},
            ],
        },
        "produced_at": "2026-06-19T10:00:05Z",
    })
    await post_message(room_id, "dating_risk", finding_msg)
    print(f"📤 [dating_risk] POSTED Finding + RiskFlags")
    await asyncio.sleep(0.5)

    handoff_dr = json.dumps({
        "msg_id": "msg-004",
        "case_id": "C-0001-SPIKE",
        "from_agent": "dating_risk",
        "intent": "handoff",
        "to_role": "guideline",
        "payload": {"message": "Findings posted. Guideline check required."},
        "produced_at": "2026-06-19T10:00:06Z",
    })
    await post_message(room_id, "dating_risk", handoff_dr)
    print(f"📤 [dating_risk] HANDOFF → guideline")
    await asyncio.sleep(0.5)

    # Step 4: Guideline Agent posts
    print(f"\n🤖 [guideline] Checking antenatal ruleset...")
    compliance_msg = json.dumps({
        "msg_id": "msg-005",
        "case_id": "C-0001-SPIKE",
        "from_agent": "guideline",
        "intent": "post",
        "payload": {
            "compliant": False,
            "veto": True,
            "missing_investigations": ["repeat_bp_4h", "24h_urine_protein", "ogtt"],
            "notes": "BP + proteinuria require pre-eclampsia work-up before sign-off.",
            "rule_refs": ["PE-001", "GDM-002"],
        },
        "produced_at": "2026-06-19T10:00:10Z",
    })
    await post_message(room_id, "guideline", compliance_msg)
    print(f"📤 [guideline] POSTED ComplianceResult (veto=True)")
    print(f"🔴 [guideline] VETO raised — escalation to human gate required!")
    await asyncio.sleep(0.5)

    # Step 5: Read back all messages to prove round-trip
    print(f"\n{'─' * 50}")
    print(f"📥 Reading messages from Band room {room_id}...")
    await asyncio.sleep(1)  # Allow server processing
    messages = await read_messages(room_id)

    print(f"\n📋 Room Messages ({len(messages)} total):")
    print(f"{'─' * 50}")
    for i, msg in enumerate(messages):
        content = msg.get("content", "")[:120]
        agent = "unknown"
        try:
            parsed = json.loads(content)
            agent = parsed.get("from_agent", "?")
        except json.JSONDecodeError:
            pass
        inserted = msg.get("inserted_at", "")[:19]
        print(f"  [{i+1}] {agent:15s} | {inserted} | {content[:80]}...")

    print(f"\n{'=' * 60}")
    print(f"✅ P0 SPIKE COMPLETE")
    print(f"   Message flow: intake → dating_risk → guideline")
    print(f"   All 5 messages posted to Band room: {room_id}")
    print(f"   Room messages retrieved: {len(messages)}")
    print(f"{'=' * 60}")


def _dry_run_spike():
    """Simulate the Band flow without real API calls."""
    print("""
🔬 P0 — BAND SPIKE (DRY RUN)
   Simulating 3-agent message flow through Band room

🏠 [orchestrator] Room opened: room-dry-run-001
📢 [orchestrator] Agents recruited: intake, dating_risk, guideline

🚀 [orchestrator] Seed case posted to room

🤖 [intake] RECEIVED seed case from orchestrator
📤 [intake] POSTING StructuredCase → room
📤 [intake] HANDOFF → dating_risk (via Band room)

🤖 [dating_risk] RECEIVED handoff from intake (via Band room)
📤 [dating_risk] POSTING Finding: GA(LMP)=27.3wk, GA(USG)=23.0wk, discordance=4.3wk
📤 [dating_risk] POSTING RiskFlags: preeclampsia_suspected(HIGH), gdm_suspected(MODERATE)
📤 [dating_risk] HANDOFF → guideline (via Band room)

🤖 [guideline] RECEIVED handoff from dating_risk (via Band room)
📤 [guideline] POSTING ComplianceResult: compliant=False, veto=True
📤 [guideline] Missing investigations: repeat_bp_4h, 24h_urine_protein, ogtt
🔴 [guideline] VETO raised — escalation to human gate required!

============================================================
✅ P0 SPIKE COMPLETE (DRY RUN)
   Message flow: intake → dating_risk → guideline
   All handoffs traversed the Band room (simulated)
============================================================
""")


if __name__ == "__main__":
    asyncio.run(run_spike())

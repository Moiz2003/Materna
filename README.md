# Antenatal Review Board

**A Band-coordinated multi-agent obstetric safety check with a real obstetrician as the human-in-the-loop gate.**

Built for the [Band of Agents Hackathon](https://lablab.ai) (Track 3: Regulated & High-Stakes Workflows) by Abdul Moiz Ahmed. Three AI agents collaborate through **Band** — then escalate flagged cases to a human OB who holds final authority. Every step is written to a **SHA-256 hash-chained audit log** and emitted as a **tamper-evident sealed PDF**.

---

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  React/Vite   │────▶│  Orchestrator    │────▶│     Band Room            │
│  (Submit UI)  │     │  (FastAPI)       │     │  (shared context)        │
└──────────────┘     └──────────────────┘     │                         │
                                              │  ┌───────────────────┐  │
                                              │  │ Intake Agent      │  │
                                              │  │ (normalise+val)   │──┼──▶ StructuredCase
                                              │  └───────────────────┘  │
                                              │  ┌───────────────────┐  │
                                              │  │ Dating & Risk     │  │
                                              │  │ Agent (GA+flags)  │──┼──▶ Finding + RiskFlags
                                              │  └───────────────────┘  │
                                              │  ┌───────────────────┐  │
                                              │  │ Guideline Agent   │  │
                                              │  │ (compliance+veto) │──┼──▶ ComplianceResult
                                              │  └───────────────────┘  │
                                              └─────────────────────────┘
                                                   │ flag or veto?
                                                   ▼
                         ┌──────────────────────────────────────────────┐
                         │        Human Gate (OB Reviewer)              │
                         │        Dr. Saima Javed — Approve/Override     │
                         └──────────────────────────────────────────────┘
                                                   ▼
                         ┌──────────────────────────────────────────────┐
                         │  SHA-256 Audit Chain  +  Sealed PDF Packet   │
                         └──────────────────────────────────────────────┘
```

## What's Judged

| Judging Pillar                | How This Submission Satisfies It                                                                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Application of Technology** | 3 agents with distinct roles, real **Band handoffs** (rooms, Agent API, shared context), **Human API** gate. No agent calls another directly — every handoff traverses the Band room. |
| **Presentation**              | Live Band room view in the UI showing agent handoffs in real time. On-camera OB override is the demo's centrepiece.                                                                   |
| **Business Value**            | Reduces manual antenatal coordination; catches dating errors and risk signals; produces an auditable, signed decision record.                                                         |
| **Originality**               | Obstetric domain is unclaimed on the hackathon board. Real specialist as the human gate. Ties to original GA-discordance research.                                                    |

### The Winning Pattern

> Specialised agents → veto/escalation → human-in-the-loop gate → immutable audit trail → decision packet. This project keeps that proven pattern but applies it to obstetrics, with a real practicing gynaecologist as the on-camera human gate.

## How Band Is Used (The Judged Core)

1. **Rooms** — One Band room per case, created by the orchestrator and seeded with the raw case payload as shared context.
2. **Agent API (recruitment)** — The orchestrator recruits `intake`, `dating_risk`, and `guideline` into the room via Band's Agent API. Agents are discoverable and modular — not hardwired into a pipeline.
3. **Handoffs through shared context** — Intake posts `StructuredCase` → hands off to dating_risk via the room. Dating & Risk posts `Finding` + `RiskFlag`s → hands off to guideline. Guideline posts `ComplianceResult`. Every message is a typed envelope posted to and read from the Band room. **No agent imports or calls another agent's functions directly.**
4. **Human API (gate)** — When a risk flag fires or the guideline agent issues a veto, the orchestrator uses Band's Human API to escalate an escalation brief to the OB reviewer and blocks until a decision returns.

**Anti-pattern avoided:** The chain is NOT `agentB(agentA(x))` with Band bolted on as a logger. The handoff itself traverses Band.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the UI)
- Band API key (Promo: `BANDHACK26`) — _optional for local mode_
- AI/ML API key — _optional, local fallback works without it_

### One-Command Demo (no Band key needed)

```bash
# 1. Clone
git clone <repo-url> && cd antenatal-review-board

# 2. Configure (even empty .env works for local demo)
cp .env.example .env

# 3. Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Run full demo (both C-0001 + C-0002)
python -m orchestrator.main
# Then: curl -X POST http://localhost:8000/demo/run-all

# Or: run a single case
python -c "
import asyncio
from orchestrator.lifecycle import handle_case_local
result = asyncio.run(handle_case_local('C-0001'))
print('Status:', result['status'])
print('Flags:', len(result.get('flags',[])))
print('Audit verified:', result.get('audit_verified'))
"
```

### With Real Band (P0 spike)

```bash
# Set your Band key in .env
echo 'BAND_API_KEY=your_key_here' >> .env
python spike.py
```

### Full System (Docker)

```bash
docker compose up
# Backend: http://localhost:8000
# Health:   http://localhost:8000/health
# API docs: http://localhost:8000/docs
```

### UI (React/Vite)

```bash
cd ui && npm install && npm run dev
# Open http://localhost:5173
```

### Run Hardening Tests

```bash
pytest tests/test_hardening.py -v
# 28 adversarial tests: gate bypass, prompt injection, determinism, audit integrity, failure paths, secret hygiene
```

## Demo Cases

| Case       | Description                                      | GA (LMP/USG)      | Discordance  | Flags                             | Outcome                           |
| ---------- | ------------------------------------------------ | ----------------- | ------------ | --------------------------------- | --------------------------------- |
| **C-0001** | 29y G3P2, elevated BP, proteinuria, high glucose | 27.3 wk / 23.0 wk | **4.3 wk** ⚠ | PE-001 (high), GDM-002 (moderate) | **ESCALATED → override → SEALED** |
| **C-0002** | 25y G1P0, normal vitals, normal labs             | ~16 wk / ~16 wk   | < 2.0 wk     | None                              | **AUTO_CLEARED → SEALED**         |

## API Routes (§8 SDD)

| Method | Path                   | Purpose                                            |
| ------ | ---------------------- | -------------------------------------------------- |
| `POST` | `/cases`               | Submit case + ultrasound (multipart/form-data)     |
| `GET`  | `/cases/{id}`          | Case status + findings + flags + compliance        |
| `GET`  | `/cases/{id}/room`     | Band room conversation (message envelopes)         |
| `POST` | `/cases/{id}/decision` | Record human verdict (`approve`/`override` + note) |
| `GET`  | `/cases/{id}/packet`   | Download sealed PDF review packet                  |
| `GET`  | `/cases/{id}/audit`    | Audit chain + SHA-256 verification status          |
| `POST` | `/demo/run-all`        | Run both demo cases and return results             |

## File Structure

```
antenatal-review-board/
├── orchestrator/           # FastAPI app + lifecycle state machine + deterministic gate
│   ├── main.py             #   6 REST routes + health + demo runner
│   ├── lifecycle.py        #   Full state machine (Band mode + local mode)
│   ├── gate.py             #   must_escalate() — pure function, NEVER an LLM
│   └── recruit.py          #   Band room + agent recruitment
├── agents/                 # Three specialist agents (communicate ONLY via Band)
│   ├── intake/agent.py     #   Normalise + validate → StructuredCase
│   ├── dating_risk/agent.py#   GA calc + discordance + imaging + risk flags
│   └── guideline/agent.py  #   Ruleset check → ComplianceResult + veto
├── band/client.py          # Band coordination wrapper (open_room, recruit, post, etc.)
├── tools/                  # Deterministic tools + LLM tools
│   ├── ga_calc.py          #   GA math (LMP & ultrasound) — pure functions
│   ├── guideline_kb.py     #   Rule loader + deterministic checker + veto logic
│   └── imaging.py          #   AI/ML API vision — decision-support, never diagnostic
├── risk/rules.py           # Deterministic risk evaluators (PE, GDM, anaemia)
├── audit/chain.py          # SHA-256 hash-chained JSONL audit log + verification
├── packet/generator.py     # ReportLab sealed PDF review packet
├── schemas.py              # Pydantic v2 models — single source of truth (10 schemas)
├── data/
│   ├── cases/C-0001.json   #   Synthetic case (flagged)
│   ├── cases/C-0002.json   #   Synthetic case (clean)
│   └── rules/antenatal_rules.yaml  # Declarative guideline ruleset
├── ui/src/
│   ├── App.jsx             #   5-panel React control surface
│   └── api.js              #   REST client for orchestrator
├── tests/test_hardening.py #   28 adversarial tests (gate bypass, injection, etc.)
├── spike.py                #   P0 Band spike (3-agent message flow)
├── docker-compose.yml      #   5 services: orchestrator + 3 agents + UI
└── Dockerfile              #   Python 3.11-slim
```

## Safety & Scope

- ⚠ **Synthetic / anonymised data only** — no real PHI ever enters the system
- 🩻 All imaging output is labelled **decision-support** — not a diagnosis
- 🩺 The human OB holds **final authority** on every flagged case
- 🔒 The escalation gate is **deterministic** — an LLM never decides whether to escalate
- 🔐 SHA-256 hash chain makes **any post-hoc edit detectable**
- ❌ No autonomous diagnostic or treatment claims

> **Judge-facing caution:** Never claim diagnostic accuracy or a trained model you do not have. Frame everything as coordination + decision-support with a mandatory human gate.

## The 8 Golden Rules (Applied Throughout)

1. **Band is the coordination layer** — agents communicate ONLY via Band room
2. **The escalation gate is deterministic** — `must_escalate()` is a pure function
3. **Synthetic data only** — no real PHI
4. **Decision-support framing** — human holds final authority
5. **Math & rules are code, not vibes** — GA, risk, guideline are deterministic functions
6. **Everything is audited** — SHA-256 hash chain on every state transition
7. **Tests gate progress** — 28 adversarial hardening tests
8. **Secrets in .env only** — never hardcoded, never committed

## Tech Stack

| Layer                 | Choice                                             | Rationale                                           |
| --------------------- | -------------------------------------------------- | --------------------------------------------------- |
| Coordination          | **Band** (SDK / Agent API / Human API / WebSocket) | Required; the judged collaboration layer            |
| Model Inference       | **AI/ML API**                                      | Unified model access; partner-prize eligibility     |
| Orchestrator / Agents | **Python 3.11 + FastAPI**                          | Async-friendly; author's existing skill             |
| Schemas               | **Pydantic v2**                                    | Single source of truth; validated at every boundary |
| Imaging               | **Multimodal LLM** via AI/ML API                   | Decision-support; no training needed                |
| Packet                | **ReportLab**                                      | Reliable PDF output                                 |
| Audit                 | **hashlib (SHA-256) + JSONL**                      | Tamper-evidence; no blockchain needed               |
| UI                    | **React + Vite**                                   | Minimal; just enough to drive the demo              |
| Packaging             | **Docker Compose**                                 | Single host; clean local/EC2 deploy                 |

## License

MIT © 2026 Abdul Moiz Ahmed

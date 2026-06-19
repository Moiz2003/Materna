# Materna — Antenatal Review Board

**A Band-coordinated multi-agent obstetric safety system with a real gynecologist as the human-in-the-loop gate.**

Built for the [Band of Agents Hackathon](https://lablab.ai) (Track 3: Regulated & High-Stakes Workflows) by Abdul Moiz Ahmed. Four AI agents collaborate through **Band** — then escalate flagged cases to a human OB who holds final authority. Every step is written to a **SHA-256 hash-chained audit log** and emitted as a **tamper-evident sealed PDF**.

---

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────────────────┐
│  React/Vite   │────▶│  Orchestrator    │────▶│         Band Room             │
│  (Submit UI)  │     │  (FastAPI)       │     │      (shared context)         │
└──────────────┘     └──────────────────┘     │                              │
                                              │  ┌────────────────────────┐  │
                                              │  │ Intake Agent           │  │
                                              │  │ (normalise + validate) │──┼──▶ StructuredCase
                                              │  └────────────────────────┘  │
                                              │  ┌────────────────────────┐  │
                                              │  │ Dating & Risk Agent    │  │
                                              │  │ (GA calc + risk flags) │──┼──▶ Finding + RiskFlags
                                              │  └────────────────────────┘  │
                                              │  ┌────────────────────────┐  │
                                              │  │ Guideline Agent        │  │
                                              │  │ (compliance + veto)    │──┼──▶ ComplianceResult
                                              │  └────────────────────────┘  │
                                              │  ┌────────────────────────┐  │
                                              │  │ Auditor Agent 🕵️       │  │
                                              │  │ (adversarial review)   │──┼──▶ AuditorChallenge
                                              │  └────────────────────────┘  │
                                              └──────────────────────────────┘
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
| **Application of Technology** | 4 agents with distinct roles, real **Band handoffs** (rooms, Agent API, shared context), **Human API** gate. No agent calls another directly — every handoff traverses the Band room. |
| **Presentation**              | Premium glass-morphism UI. Live Band room view. Animated pipeline visualization. Novice/Expert modes. Demo play cards. Onboarding tour.                                               |
| **Business Value**            | Addresses real maternal mortality crisis (186/100k in Pakistan). Reduces manual antenatal coordination; catches dating errors and risk signals; produces an auditable, signed record. |
| **Originality**               | Obstetric domain is unclaimed. Real specialist as human gate. Novel **Auditor agent** adversarially challenges the Guideline. Ties to original GA-discordance research.               |

### The Winning Pattern

> Specialised agents → adversarial review → veto/escalation → human-in-the-loop gate → immutable audit trail → tamper-evident PDF. This project applies that proven safety pattern to obstetrics, with a real practicing gynecologist as the on-camera human gate.

## How Band Is Used (The Judged Core)

1. **Rooms** — One Band room per case, created by the orchestrator and seeded with the raw case payload as shared context.
2. **Agent API (recruitment)** — The orchestrator recruits `intake`, `dating_risk`, `guideline`, and `auditor` into the room via Band's Agent API. Agents are discoverable and modular.
3. **Handoffs through shared context** — Every message is a typed envelope posted to and read from the Band room. **No agent imports or calls another agent's functions directly.**
4. **Human API (gate)** — When a risk flag fires or veto triggers, the orchestrator uses Band's Human API to escalate an escalation brief to the OB reviewer.

**Anti-pattern avoided:** The chain is NOT `agentB(agentA(x))` with Band bolted on as a logger. The handoff itself traverses Band.

## Demo Cases

| Case       | Scenario                                         | GA Discordance | Flags                                                 | Outcome                                     |
| ---------- | ------------------------------------------------ | -------------- | ----------------------------------------------------- | ------------------------------------------- |
| **C-0001** | 29y G3P2, elevated BP, proteinuria, high glucose | **4.3 wk** ⚠   | PE-001 (high), GDM-002 (moderate), ANE-003 (moderate) | **ESCALATED → approve → SEALED**            |
| **C-0002** | 25y G1P0, normal vitals, normal labs             | < 2.0 wk       | None                                                  | **AUTO_CLEARED → SEALED**                   |
| **C-0003** | 34y G5P4, borderline BP, glucose 95, Hb 10.5     | Calculated     | PE-001 (high), GDM-002 (moderate), ANE-003 (moderate) | **ESCALATED — triple flag**                 |
| **C-0004** | 22y G2P1, severe BP 165/105, protein 3+, Hb 9.2  | **Massive** ⚠  | PE-001 (high), ANE-003 (moderate) + auditor challenge | **ESCALATED — auditor challenge fireworks** |

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

# 4. Run the API server
python -m uvicorn orchestrator.main:app --host 0.0.0.0 --port 8000

# 5. Run all 4 demo cases
curl -X POST http://localhost:8000/demo/run-all
```

### UI (React/Vite)

```bash
cd ui && npm install && npm run dev
# Open http://localhost:5173
```

### Run Tests

```bash
pytest tests/ -v
# 132 tests across 10 test files: hardening, rules, GA calc, contracts, guideline, security, API, coordination, lifecycle
```

## API Routes

| Method | Path                   | Purpose                                            |
| ------ | ---------------------- | -------------------------------------------------- |
| `POST` | `/cases`               | Submit case + ultrasound (multipart/form-data)     |
| `GET`  | `/cases/{id}`          | Case status + findings + flags + compliance        |
| `GET`  | `/cases/{id}/room`     | Band room conversation (message envelopes)         |
| `POST` | `/cases/{id}/decision` | Record human verdict (`approve`/`override` + note) |
| `GET`  | `/cases/{id}/packet`   | Download sealed PDF review packet                  |
| `GET`  | `/cases/{id}/audit`    | Audit chain + SHA-256 verification status          |
| `POST` | `/demo/tamper/{id}`    | Tamper audit chain (demo)                          |
| `POST` | `/demo/run-all`        | Run all 4 demo cases and return results            |

## File Structure

```
antenatal-review-board/
├── orchestrator/           # FastAPI app + lifecycle state machine + deterministic gate
│   ├── main.py             #   8 REST routes + health + demo runner
│   ├── lifecycle.py        #   Full state machine (Band mode + local mode)
│   ├── gate.py             #   must_escalate() — 13-line pure function, NEVER an LLM
│   └── recruit.py          #   Band room + agent recruitment
├── agents/                 # Four specialist agents (communicate ONLY via Band)
│   ├── intake/agent.py     #   Normalise + validate → StructuredCase
│   ├── dating_risk/agent.py#   GA calc + discordance + imaging + risk flags
│   ├── guideline/agent.py  #   Ruleset check → ComplianceResult + veto
│   └── auditor/agent.py    #   🕵️ Adversarial reviewer — challenges Guideline
├── band_wrapper/client.py  # Band coordination wrapper (open_room, recruit, post)
├── tools/                  # Deterministic tools + LLM tools
│   ├── ga_calc.py          #   GA math (LMP & ultrasound) — pure functions
│   ├── guideline_kb.py     #   Rule loader + deterministic checker + veto logic
│   ├── imaging.py          #   AI/ML API vision — decision-support, never diagnostic
│   └── treatment.py        #   Treatment plan generation
├── risk/rules.py           # Deterministic risk evaluators (PE, GDM, anaemia)
├── audit/chain.py          # SHA-256 hash-chained JSONL audit log + verification
├── packet/generator.py     # ReportLab sealed PDF review packet
├── schemas.py              # Pydantic v2 models — single source of truth
├── data/
│   ├── cases/C-0001.json   #   Synthetic case (flagged: PE + GDM)
│   ├── cases/C-0002.json   #   Synthetic case (clean)
│   ├── cases/C-0003.json   #   Synthetic case (borderline triple-flag)
│   ├── cases/C-0004.json   #   Synthetic case (severe, auditor challenge)
│   └── rules/antenatal_rules.yaml  # Declarative guideline ruleset
├── ui/src/
│   ├── pages/              #   Landing, Dashboard, About pages
│   ├── components/         #   Glass panels, stage cards, effects, output
│   └── api.js              #   REST client for orchestrator
├── tests/                  # 132 tests across 10 files
├── spike.py                #   P0 Band spike (multi-agent message flow)
├── docker-compose.yml      #   Orchestrator + UI services
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

1. **Band is the coordination layer** — agents communicate ONLY via Band rooms
2. **The escalation gate is deterministic** — `must_escalate()` is a pure function
3. **Synthetic data only** — no real PHI
4. **Decision-support framing** — human holds final authority
5. **Math & rules are code, not vibes** — GA, risk, guideline are deterministic functions
6. **Everything is audited** — SHA-256 hash chain on every state transition
7. **Tests gate progress** — 132 tests across 10 files, including adversarial hardening
8. **Secrets in .env only** — never hardcoded, never committed

## Tech Stack

| Layer                 | Choice                                 | Rationale                                           |
| --------------------- | -------------------------------------- | --------------------------------------------------- |
| Coordination          | **Band** (SDK / Agent API / Human API) | Required; the judged collaboration layer            |
| Model Inference       | **AI/ML API** via OpenRouter           | Unified model access; partner-prize eligibility     |
| Orchestrator / Agents | **Python 3.11 + FastAPI**              | Async-friendly                                      |
| Schemas               | **Pydantic v2**                        | Single source of truth; validated at every boundary |
| Imaging               | **Gemini Vision** via AI/ML API        | Decision-support; no training needed                |
| Packet                | **ReportLab**                          | Professional clinical PDF output                    |
| Audit                 | **hashlib (SHA-256) + JSONL**          | Tamper-evidence; no blockchain needed               |
| UI                    | **React + Vite + Tailwind CSS**        | Premium glass-morphism design system                |
| Packaging             | **Docker Compose**                     | Single host; clean deploy                           |

## License

MIT © 2026 Abdul Moiz Ahmed

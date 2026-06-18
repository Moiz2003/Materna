# 🏆 Antenatal Review Board — 80%+ Win Rate Upgrade Plan

> **Deadline:** June 19, 8:00 PM PST (~24 hours)
> **Current win odds:** ~30% → **Target:** 80%+

---

## Changes Already Applied

### ✅ Bug Fixes Done

| #   | Change                                                                                                                                                                                    | Impact                                |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 1   | Fixed hardcoded IP `192.168.18.183` → `import.meta.env.VITE_API_URL` in [`ui/src/api.js`](antenatal-review-board/ui/src/api.js:10)                                                        | Removes embarrassing hardcoded dev IP |
| 2   | Fixed double-assigned `human_decision` bug in [`orchestrator/lifecycle.py`](antenatal-review-board/orchestrator/lifecycle.py) — auto-clear path now seals directly without redundant code | Eliminates dead code bug              |
| 3   | Deleted dead stub [`packet/template.py`](antenatal-review-board/packet/template.py:1) — never imported, never used                                                                        | Removes dead code                     |

### ✅ 4th Agent Added (AUDITOR)

| #   | Change                                                                                                                                           | Impact                                                                                |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| 4   | Created [`agents/auditor/agent.py`](antenatal-review-board/agents/auditor/agent.py:1) — adversarial reviewer that challenges the Guideline agent | **HIGHEST IMPACT** — goes from minimum 3 agents to 4, adds adversarial review pattern |
| 5   | Added `AuditorChallenge` schema to [`schemas.py`](antenatal-review-board/schemas.py:128)                                                         | New data model for auditor output                                                     |
| 6   | Wired Auditor into [`orchestrator/lifecycle.py`](antenatal-review-board/orchestrator/lifecycle.py:320) — runs between Guideline and Gate         | Full pipeline integration                                                             |
| 7   | Updated [`band_wrapper/client.py`](antenatal-review-board/band_wrapper/client.py:53) to recruit `"auditor"` into Band rooms                      | Band coordination layer updated                                                       |
| 8   | Auditor challenge feeds into escalation brief — adds `auditor_challenge` reason and narrative to the human reviewer's summary                    | Strengthens escalation path                                                           |

---

## What Still Needs To Be Done (Priority Order)

### 🔴 TIER 1 — Do These Now (highest win-rate impact per minute)

#### 1. Create 2 New Demo Cases

**Why:** 2 cases is bare minimum. 4 cases with different scenarios shows depth.

Create `data/cases/C-0003.json`:

```json
{
  "case_id": "C-0003",
  "demographics": { "age": 34, "parity": "G5P4" },
  "lmp_date": "2026-01-20",
  "usg_date": "2026-06-10",
  "usg_measurement": { "type": "BPD", "value_mm": 52 },
  "vitals": { "bp_systolic": 142, "bp_diastolic": 92 },
  "labs": {
    "urine_protein": "1+",
    "fasting_glucose_mg_dl": 95,
    "hb_g_dl": 10.5
  }
}
```

**Scenario:** Borderline pre-eclampsia (BP just over threshold) + borderline GDM (glucose 95 ≥ 92) + mild anemia (Hb 10.5 < 11.0). THREE flags fire. **The Auditor WILL challenge** because PE-001 (high severity) is present with compliant result. Perfect demo of the Auditor value.

Create `data/cases/C-0004.json`:

```json
{
  "case_id": "C-0004",
  "demographics": { "age": 22, "parity": "G2P1" },
  "lmp_date": "2026-06-01",
  "usg_date": "2026-06-10",
  "usg_measurement": { "type": "CRL", "value_mm": 5 },
  "vitals": { "bp_systolic": 165, "bp_diastolic": 105 },
  "labs": { "urine_protein": "3+", "fasting_glucose_mg_dl": 88, "hb_g_dl": 9.2 }
}
```

**Scenario:** Severe pre-eclampsia (BP 165/105 + 3+ protein) + severe anemia (Hb 9.2) + dating discrepancy (LMP says 1.3 weeks but CRL 5mm ≈ ~7.7 weeks — MASSIVE discordance ~6.4 weeks). **The Auditor will DEFINITELY challenge** with multiple reasons. This is your "wow" demo case.

**Files to create:**

- `data/cases/C-0003.json` (borderline, 3 flags)
- `data/cases/C-0004.json` (severe, auditor challenge fireworks)

**Files to update:**

- [`orchestrator/main.py`](antenatal-review-board/orchestrator/main.py:683) — add C-0003 and C-0004 to `/demo/run-all`
- [`ui/src/App.jsx`](antenatal-review-board/ui/src/App.jsx:15) — add `Load C-0003` and `Load C-0004` quick-load buttons

---

#### 2. Add Tamper-Demo Endpoint

**Why:** Showing the audit chain BREAK when tampered is a killer demo moment. Judges love this.

Add to [`orchestrator/main.py`](antenatal-review-board/orchestrator/main.py):

```python
@app.post("/demo/tamper/{case_id}")
async def demo_tamper(case_id: str):
    """DELIBERATELY tamper an audit entry to demonstrate detection."""
    from audit.chain import AUDIT_LOG_DIR
    path = AUDIT_LOG_DIR / f"{case_id}.jsonl"
    if not path.exists():
        raise HTTPException(404, "No audit log to tamper")
    lines = path.read_text().strip().splitlines()
    if len(lines) < 2:
        raise HTTPException(400, "Need at least 2 entries to tamper")
    entry = json.loads(lines[-2])
    entry["payload_hash"] = "sha256:TAMPERED_DEMO"
    lines[-2] = json.dumps(entry)
    path.write_text("\n".join(lines) + "\n")
    ok, broken = verify_chain(case_id)
    return {"tampered": True, "broken_at_seq": broken, "verified": ok}
```

Add a **"🔨 Tamper Audit (Demo)"** button in the UI's PacketPanel that calls this endpoint, then re-fetches audit data showing "❌ TAMPERED" in red. This is a 5-minute demo moment that proves your security claims are real.

---

#### 3. Update the UI for the Auditor Agent

**Changes needed in [`ui/src/App.jsx`](antenatal-review-board/ui/src/App.jsx:1):**

a) Add auditor emoji to `AGENT_EMOJI`:

```js
const AGENT_EMOJI = {
  intake: "📋",
  dating_risk: "🔬",
  guideline: "⚖️",
  auditor: "🕵️",
  orchestrator: "⚙️",
  human: "🩺",
};
```

b) Add `"AUDITED"` to `STATES` array and `STATUS_COLOR`:

```js
const STATES = ["RECEIVED", "STRUCTURED", "ANALYZED", "CHECKED", "AUDITED", "ESCALATED", "HUMAN_REVIEWED", "SEALED"];
const STATUS_COLOR = {
  ..., AUDITED: "#a855f7", ...
};
```

c) In `CasePanel`, show auditor challenge if present:

```jsx
{
  data.auditor?.challenged && (
    <div style={s.auditorBox}>
      🕵️ <strong>AUDITOR CHALLENGED:</strong> {data.auditor.narrative}
      <div style={s.auditorReasons}>
        {(data.auditor.reasons || []).map((r, i) => (
          <div key={i}>• {r}</div>
        ))}
      </div>
    </div>
  );
}
```

d) Add "Load C-0003" and "Load C-0004" quick-load buttons alongside the existing "Load C-0001" button.

e) Add the tamper button in `PacketPanel`:

```jsx
<button onClick={demo_tamper} style={s.tamperBtn}>
  🔨 Tamper Audit (Demo)
</button>
```

---

### 🟡 TIER 2 — Do These If You Have 2+ Hours

#### 4. Deploy the Demo

**Why:** Having a live URL is a massive credibility boost. Many judges will click it.

Options (fastest first):

- **ngrok:** `ngrok http 8000` → gives you a public URL in 30 seconds
- **Railway/Render:** Free tier, Docker deployment, 5 minutes
- **Fly.io:** `fly launch` with the existing Dockerfile

Update the README with the deployed URL. Add the URL to your hackathon submission.

#### 5. Record a 3-Minute Demo Video

**Script:**

1. (0:00-0:30) "Antenatal Review Board — 4 AI agents + human OB coordinate through Band for obstetric safety"
2. (0:30-1:00) Paste C-0004 clinical notes → AI extracts → Submit → Watch 4 agents in Band room (intake → dating_risk → guideline → AUDITOR CHALLENGES)
3. (1:00-1:45) Show the Auditor's challenge narrative. Show the escalation brief with "⚠️ AUDITOR CHALLENGED". Dr. Saima Javed overrides with instruction → plan re-drafted.
4. (1:45-2:15) Approve → PDF generates. Show SHA-256 hash. Click "Tamper Audit (Demo)" → audit shows BROKEN. "Any alteration is cryptographically detectable."
5. (2:15-3:00) "4 agents. Real doctor. Cryptographic audit. 28 adversarial hardening tests. Built for Pakistani antenatal clinics."

#### 6. Cross-Framework Agent (Featherless AI Integration)

Add a 5th agent that uses Featherless AI (open-source model inference) for a second partner prize eligibility. Even a thin integration qualifies:

- Add a `BAND_FEATHERLESS_ID` env var
- Create `agents/second_opinion/agent.py` — uses Featherless-hosted Llama to provide an independent second opinion on the dating calculation
- This makes you eligible for BOTH partner prizes (AI/ML API + Featherless)

---

### 🟢 TIER 3 — Polish (if you have 4+ hours)

#### 7. Fix README

- Change all `band/client.py` references to `band_wrapper/client.py`
- Update architecture diagram to show 4 agents (add Auditor)
- Update agent count throughout: "3 agents" → "4 agents"
- Add demo case table entries for C-0003 and C-0004
- Add "🕵️ Auditor Agent — adversarial review of Guideline" to file structure

#### 8. Remove Dead Code from `_call_intake_llm`

In [`agents/intake/agent.py:108-111`](antenatal-review-board/agents/intake/agent.py:108):

```python
    except Exception:
        pass  # ← REMOVE THIS LINE
        return _local_normalise(raw_case)
```

Change to:

```python
    except Exception:
        logger.debug("Intake LLM unavailable — falling back to local normalise")
        return _local_normalise(raw_case)
```

#### 9. Fix `.env.example` for New Agents

Add to [`.env.example`](antenatal-review-board/.env.example:1):

```bash
# Auditor Agent (4th agent — adversarial reviewer)
BAND_AUDITOR_ID=your_auditor_agent_id
AIML_AUDITOR_MODEL=openai/gpt-4o-mini

# Second Opinion Agent (5th agent — Featherless AI, optional)
BAND_SECOND_OPINION_ID=your_second_opinion_id
```

---

## Score Impact Estimate After All Changes

| Criteria                  | Before | After      | Delta                                                |
| ------------------------- | ------ | ---------- | ---------------------------------------------------- |
| Application of Technology | 8/10   | **9.5/10** | +1.5 (4 agents, adversarial, cross-verification)     |
| Presentation              | 6/10   | **8/10**   | +2 (better demo, tamper demo, 4 cases, deployed URL) |
| Business Value            | 9/10   | **9/10**   | Same (already strong)                                |
| Originality               | 8/10   | **9/10**   | +1 (auditor challenge pattern, tamper demo)          |

**Estimated new win odds:**

- 🥇 Main Prize (1st/2nd/3rd): **40-55%** (up from 15-25%)
- 🏅 Best Use of AI/ML API: **55-65%** (up from 35-45%)
- 🛡️ Track 3 Winner: **45-60%** (up from 20-30%)
- 🎯 At least ONE prize: **80-90%**

---

## The Winning Narrative

After these changes, your project story becomes:

> "Antenatal Review Board coordinates **4 AI agents** through Band — Intake, Dating & Risk, Guideline, and a novel **Auditor agent that adversarially challenges** the Guideline's findings. A real obstetrician, Dr. Saima Javed, holds final authority through Band's Human API. Every decision is sealed in a **SHA-256 cryptographically verified audit chain** with **tamper-evident PDF packets**. The system passes **28 adversarial hardening tests** proving the escalation gate cannot be bypassed, prompt injection cannot affect decisions, and any audit tampering is instantly detected. Built for Pakistani antenatal clinics where handwritten records and resource constraints make AI-assisted safety checks life-critical."

This is a **complete, differentiated, verifiable narrative** that no other submission can match.

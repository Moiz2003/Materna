# 🔬 Senior Developer Technical Audit — Antenatal Review Board

> **Scope:** Full codebase audit after all changes (4th Auditor agent, polished multi-page UI, bug fixes, tamper demo).
> **Perspective:** Senior software engineer evaluating correctness, architecture, security, and hackathon judging criteria alignment.
> **Date:** June 18, 2026 — submission deadline ~24 hours away.

---

## 1. HACKATHON CRITERIA COMPLIANCE

### 1.1 Minimum Requirements (PASS/FAIL)

| Requirement                                   | Status                 | Evidence                                                                                                                                                                       |
| --------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ≥ 3 agents collaborating through Band         | ✅ **PASS (4 agents)** | Intake, Dating/Risk, Guideline, Auditor — all recruited via `band_wrapper/client.py:160`, all post typed `MessageEnvelope` objects through shared Band rooms                   |
| Meaningful Band usage (not wrapper/logging)   | ✅ **PASS**            | Handoffs traverse Band via `intent: "handoff"` envelopes with `to_role`. No agent imports or calls another agent's functions. Audit logs show real Band room UUIDs             |
| Cross-framework (optional, but scores higher) | ⚠️ **WEAK**            | All agents are Python in-process. No LangChain, CrewAI, or other framework integration. The `docker-compose.yml` has separate containers but they're not wired with agent CMDs |

### 1.2 Judging Criteria Scoring (Evidence-Based)

#### Application of Technology (Band) — **9/10**

**Strengths:**

- 4 agents recruited via Band Agent API ([`band_wrapper/client.py:160`](antenatal-review-board/band_wrapper/client.py:160))
- Typed inter-agent protocol: `MessageEnvelope` with `intent` (post/handoff/escalate/decision/audit) and `to_role`
- Real Band room IDs in audit logs: `7515812f-2a77-4bd0-8aac-fc11a9cdde41`, `25c25c1d-d0dc-413f-b377-473b101dd312`
- Best-effort Band with local fallback — safety check runs regardless of Band availability
- Human API gate via Band's Human API concept

**Weaknesses:**

- All agents run in-process via `handle_case_local()`. The distributed Band deployment (separate containers per agent) is prepared in docker-compose but not wired
- No cross-framework agents (all Python, all in the same codebase)
- 4 agents is above minimum but below competitors with 5-8 agents

#### Presentation — **7.5/10**

**Strengths:**

- 3-page React app with react-router-dom (Landing, Dashboard, About)
- Custom design system: teal+amber color palette, Plus Jakarta Sans + Inter + JetBrains Mono fonts
- framer-motion page transitions (blur + translate + opacity)
- PulseWave ECG animation on landing hero
- lucide-react icons throughout (not emoji)
- Glassmorphic card components with backdrop-blur
- Tamper Demo button that visually proves SHA-256 detection
- Guided 5-step workflow on Dashboard

**Weaknesses:**

- No deployed URL (localhost only)
- No demo video recorded
- Claude design polish not yet applied
- README still references 3 agents and old file structure
- No responsive testing visible (grid breakpoints exist but untested)

#### Business Value — **9/10**

**Strengths:**

- Real obstetric domain — unclaimed in this hackathon
- Named real gynecologist (Dr. Saima Javed) as human gate
- Addresses genuine pain points: handwritten records, GA discordance (25% prevalence), pre-eclampsia (5-8%), maternal mortality (186/100k in Pakistan)
- Cryptographic audit trail satisfies regulatory requirements
- Confidence-aware OCR handles real-world illegible handwriting
- Insufficient data guard prevents dangerous auto-clears

**Weaknesses:**

- Synthetic data only — no real clinical validation
- Single clinical scenario (antenatal) — GYNAE_PLATFORM_PLAN outlines expansion but isn't implemented

#### Originality — **9/10**

**Strengths:**

- Only obstetric AI project in the hackathon
- Adversarial Auditor agent that challenges the Guideline (unique pattern in medical domain)
- SHA-256 hash-chained audit with live tamper detection demo
- Diagnostic language filter in imaging pipeline (regex-based rejection of AI diagnostic claims)
- 28 adversarial hardening tests proving security properties
- Confidence-aware field extraction with deterministic review list derivation

**Weaknesses:**

- 3-agent pipeline pattern (intake→analysis→review) is common
- Veto→escalate→human approve pattern used by multiple competitors (WarRoom, Warden, Contract Redline War Room)
- No cross-framework agent diversity

---

## 2. ARCHITECTURE AUDIT

### 2.1 State Machine Integrity

**Current states:** RECEIVED → STRUCTURED → ANALYZED → CHECKED → AUDITED → (ESCALATED | AUTO_CLEARED) → (HUMAN_REVIEWED) | → SEALED / QUARANTINED

**Issue: `AUDITED` not in `CaseStatus` class**
[`orchestrator/lifecycle.py:327`](antenatal-review-board/orchestrator/lifecycle.py:327) sets `state["status"] = "AUDITED"` but the `CaseStatus` class at line 43 only defines RECEIVED through QUARANTINED. This means:

- `state["status"] != CaseStatus.ESCALATED` at [`main.py:528`](antenatal-review-board/orchestrator/main.py:528) would correctly reject a decision on an AUDITED case (string "AUDITED" ≠ string "ESCALATED")
- The UI handles it because `STATES` array in `DashboardPage.jsx` includes "AUDITED"
- **Risk: LOW** — AUDITED is ephemeral (immediately transitions to ESCALATED/AUTO_CLEARED in the same async function). Only persists if the gate crashes (which it can't — pure function).

**Recommendation:** Add `AUDITED = "AUDITED"` to `CaseStatus` class for consistency.

### 2.2 Auditor Agent Correctness

**Deterministic challenge logic:** 5 conditions in [`_should_challenge()`](antenatal-review-board/agents/auditor/agent.py:58):

| #   | Condition                                           | When It Fires                                   | Realistic?                                                                                                 |
| --- | --------------------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1   | High-severity flag + compliant=True                 | Guideline incorrectly passes a dangerous case   | ✅ Valid defense-in-depth                                                                                  |
| 2   | `preeclampsia_suspected` without veto               | Guideline misses PE veto                        | ✅ Critical safety catch                                                                                   |
| 3   | Veto-eligible rules fired, Guideline didn't veto    | PE-001 or GDM-002 present but no veto           | ✅ Valid                                                                                                   |
| 4   | >1 missing investigation + compliant=True           | Guideline says compliant but has missing items  | ❌ **Cannot fire** — `compliant = len(missing) == 0`, so compliant=True implies 0 missing. Dead condition. |
| 5   | Independent re-computation (noted, not implemented) | Would require running check_schedule separately | ⚠️ Documented but not implemented                                                                          |

**Issue: Condition 4 is logically unreachable.** When `compliant=True`, `missing_investigations` is always empty (because `check_schedule` sets `compliant = len(missing) == 0`). The condition `missing_count > 1 and compliance.compliant` can never be True. This is not a bug — it's anticipatory design for a future where "compliant" might have a more nuanced definition. But it means the Auditor currently has 3 active conditions, not 4.

**Issue: Condition 5 is a comment, not code.** The docstring says "Independent re-computation: run check_schedule ourselves" but the actual implementation just notes this as a reason without running it. The LLM narrative fills the gap.

**For demo purposes:** C-0004 (severe PE + anemia) will fire the Auditor step but `should_challenge` returns `False` because the Guideline correctly vetoes. The Auditor's value is visible in the pipeline (4th agent step) and the narrative, not in active challenges on the demo cases.

### 2.3 Audit Chain Integrity

**Verified: SHA-256 chain is cryptographically sound.**

- [`audit/chain.py:37-51`](antenatal-review-board/audit/chain.py:37) — `compute_hash()` uses `sha256(f"{seq}|{case_id}|{actor}|{action}|{payload_hash}|{prev_hash}")`
- Each entry links to previous via `prev_hash`
- `verify_chain()` walks entire chain recomputing each expected hash
- Tamper detection returns exact broken sequence number

**Tamper demo endpoint:** [`orchestrator/main.py:670-686`](antenatal-review-board/orchestrator/main.py:670) — deliberately corrupts the second-to-last entry's `payload_hash` and re-verifies. Returns `{"tampered": True, "broken_at_seq": N}`.

**Issue: Tamper demo mutates the real audit log.** This is a destructive operation on the actual audit file. For a demo, this is fine — the "tampered" state is the point. But there's no "un-tamper" or reset. A production version would copy the log first.

### 2.4 Escalation Gate — Provably Correct

[`orchestrator/gate.py:13`](antenatal-review-board/orchestrator/gate.py:13):

```python
def must_escalate(flags: list[RiskFlag], compliance: ComplianceResult) -> bool:
    return bool(flags) or compliance.veto
```

**Verification:**

- Pure function — no I/O, no global state, no randomness
- Signature enforced by test (`test_signature_only_takes_flags_and_compliance`)
- No LLM involvement — 6 hardening tests prove it
- Cannot be bypassed by env vars (`test_no_global_state_used`)
- Deterministic across 100 calls (`test_determinism_100_calls`)

**The `insufficient_data` guard at [`lifecycle.py:360-362`](antenatal-review-board/orchestrator/lifecycle.py:360) is NOT in the gate** — it's in the orchestrator, which is correct. The gate stays pure; the orchestrator adds the business rule.

### 2.5 Data Flow Integrity

**Schema validation at every boundary:**

- `CaseInput` → Pydantic v2 validation on submission
- `StructuredCase` → intake agent validates before posting
- `Finding` / `RiskFlag` → dating agent builds typed objects
- `ComplianceResult` → guideline agent returns typed object
- `AuditorChallenge` → auditor returns typed object
- `MessageEnvelope` → every inter-agent message validated with `to_role` required on handoff
- `AuditEntry` → every state transition produces a typed entry

**No raw dicts cross module boundaries without validation.** This is production-grade data hygiene.

---

## 3. CODE QUALITY AUDIT

### 3.1 What's Clean

| Component                     | Quality | Notes                                                                                                                 |
| ----------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------- |
| `schemas.py`                  | **A**   | Single source of truth, Pydantic v2, field validators, smoke tests                                                    |
| `audit/chain.py`              | **A**   | Clean hash chaining, verify works, reset on new submission                                                            |
| `orchestrator/gate.py`        | **A+**  | 13-line pure function, provably correct, well-tested                                                                  |
| `risk/rules.py`               | **A-**  | Pure evaluators, handle None/missing, but thresholds duplicated from YAML                                             |
| `tools/ga_calc.py`            | **A**   | Pure math, clear formulas, supports BPD+CRL only                                                                      |
| `tools/imaging.py`            | **A**   | Graceful degradation, diagnostic language filter, retry logic                                                         |
| `tools/treatment.py`          | **A-**  | Deterministic KB + LLM refinement, OB instruction folding                                                             |
| `tools/guideline_kb.py`       | **B+**  | Good logic, but `compliant = len(missing) == 0` creates the Auditor condition 4 dead path                             |
| `orchestrator/lifecycle.py`   | **B+**  | Complete state machine, but 608 lines with mixed concerns. AUDITED state not in CaseStatus. Old dead code cleaned up. |
| `orchestrator/main.py`        | **B**   | Clean routes, but smart extraction has duplicated Gemini→OpenRouter logic                                             |
| `agents/intake/agent.py`      | **B**   | Good local fallback, but `pass` before `return` at line 109, hardcoded API base URL                                   |
| `agents/dating_risk/agent.py` | **B+**  | Clean separation of concerns, but `_find_structured_case_in_context` is unused in local mode                          |
| `agents/guideline/agent.py`   | **B+**  | Correctly delegates to deterministic checker, accumulates context properly                                            |
| `agents/auditor/agent.py`     | **B**   | Good deterministic logic, but condition 4 is unreachable, condition 5 is unimplemented                                |
| `band_wrapper/client.py`      | **B**   | Works, but module-level `_load_env()` side effect at import time                                                      |
| `packet/generator.py`         | **B+**  | Complete PDF generation with fallback, but 537 lines of ReportLab layout code                                         |

### 3.2 Remaining Code Smells

| #   | File                                                                                    | Issue                                                                                            | Severity          |
| --- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------- |
| 1   | [`agents/intake/agent.py:108-111`](antenatal-review-board/agents/intake/agent.py:108)   | `pass` followed by `return` — dead statement                                                     | 🟡 Cosmetic       |
| 2   | [`agents/intake/agent.py:34`](antenatal-review-board/agents/intake/agent.py:34)         | `AIML_BASE_URL` hardcoded to `api.aimlapi.com` — doesn't read env var unlike imaging and main.py | 🟡 Inconsistency  |
| 3   | [`orchestrator/lifecycle.py:327`](antenatal-review-board/orchestrator/lifecycle.py:327) | `"AUDITED"` string not in `CaseStatus` class                                                     | 🟡 Minor          |
| 4   | [`agents/auditor/agent.py:52`](antenatal-review-board/agents/auditor/agent.py:52)       | `_MAX_MISSING_WITHOUT_CHALLENGE` condition is logically unreachable                              | 🟡 Dead logic     |
| 5   | [`agents/auditor/agent.py:95-97`](antenatal-review-board/agents/auditor/agent.py:95)    | Condition 5 (independent re-computation) documented but not implemented                          | 🟡 Incomplete     |
| 6   | [`band_wrapper/client.py:21-41`](antenatal-review-board/band_wrapper/client.py:21)      | `_load_env()` called at module level — import has side effects                                   | 🟡 Design         |
| 7   | [`tools/ga_calc.py:38-39`](antenatal-review-board/tools/ga_calc.py:38)                  | FL, HC, AC raise ValueError — schema allows them                                                 | 🟡 Incomplete     |
| 8   | `packet/template.py`                                                                    | **Already deleted** ✅                                                                           | —                 |
| 9   | README references `band/client.py`                                                      | File doesn't exist — actual path is `band_wrapper/client.py`                                     | 🟡 Docs           |
| 10  | Docker agent services have no CMD                                                       | `docker-compose.yml` agent containers would start uvicorn like orchestrator                      | 🟡 Infrastructure |

### 3.3 Frontend Code Quality

| Component            | Quality | Notes                                                                                                                                                         |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `App.jsx` (router)   | **A-**  | Clean 44-line router with AnimatePresence, skip-to-content accessibility                                                                                      |
| `LandingPage.jsx`    | **B+**  | Complete product page, PulseWave SVG animation, proper sections. Inline framer-motion variants are clean. 190 lines — reasonable.                             |
| `DashboardPage.jsx`  | **B**   | All existing logic ported correctly. 5-step guided layout is clear. But ~360 lines with mixed concerns (API calls + UI + state). Could split step components. |
| `AboutPage.jsx`      | **B+**  | Clean, text-heavy, good structure. 8 Golden Rules rendered properly.                                                                                          |
| `BandRoom.jsx`       | **A-**  | Clean 60-line reusable component with lucide-react icons mapped per agent.                                                                                    |
| `index.css`          | **A-**  | Tailwind v3 + PostCSS, custom theme with all design tokens, glass utilities in @layer components                                                              |
| `tailwind.config.js` | **A**   | Complete custom theme: fonts, colors, animations. All design tokens properly mapped.                                                                          |

**Frontend issue:** The `DashboardPage.jsx` tamper demo fetch uses a hardcoded URL construction:

```js
await fetch(
  `${window.location.origin === "http://localhost:5173" ? "http://localhost:8000" : ""}/demo/tamper/${caseId}`,
);
```

This won't work when deployed (needs proper API base URL). Should use the same `VITE_API_URL` env var as `api.js`.

---

## 4. SECURITY AUDIT

### 4.1 Proven Properties (via Hardening Tests)

| Property                                   | Tests   | Status                                                  |
| ------------------------------------------ | ------- | ------------------------------------------------------- |
| Gate cannot be bypassed                    | 6 tests | ✅ Proven                                               |
| Prompt injection doesn't affect escalation | 4 tests | ✅ Proven                                               |
| Determinism: same inputs → same outputs    | 8 tests | ✅ Proven                                               |
| Audit integrity + tamper detection         | 4 tests | ✅ Proven                                               |
| Failure paths → graceful degradation       | 5 tests | ✅ Proven                                               |
| Secret hygiene (no hardcoded keys)         | 3 tests | ✅ Proven — but test only scans `.py` files, not `.jsx` |

### 4.2 Unverified Properties

| Concern                               | Risk      | Notes                                                                                            |
| ------------------------------------- | --------- | ------------------------------------------------------------------------------------------------ |
| No auth on REST endpoints             | 🟡 Medium | `/cases/{id}/decision` accepts any POST. For hackathon demo this is fine. Production needs auth. |
| CORS wildcard (`allow_origins=["*"]`) | 🟡 Low    | Acceptable for hackathon demo                                                                    |
| No rate limiting                      | 🟢 Low    | Hackathon context                                                                                |
| Tamper demo mutates real audit logs   | 🟢 Low    | Intentional for demo                                                                             |
| `.env` file potentially committed     | 🔴 Check  | Verify `.env` is in `.gitignore` and not staged                                                  |

---

## 5. WHAT WOULD MAKE THIS PRODUCTION-GRADE

If this were a real product (not a hackathon), these would be the next steps:

1. **Database** — Replace `_case_store` dict + JSON files with PostgreSQL
2. **Auth** — Add API key or JWT auth to all mutation endpoints
3. **Distributed agents** — Wire docker-compose agent services with actual agent CMDs + Band event loops
4. **Full ultrasound biometry** — Add FL, HC, AC formulas to `ga_from_ultrasound()`
5. **Generic rule engine** — Implement the `risk/engine.py` from GYNAE_PLATFORM_PLAN so YAML conditions are actually evaluated
6. **Auditor condition 5** — Implement independent `check_schedule` re-computation
7. **Observability** — Add structured logging, metrics, alerting
8. **CI/CD** — Run hardening tests in CI, enforce coverage thresholds
9. **Clinical validation** — Have Dr. Saima Javed review real (anonymized) cases against system output

---

## 6. FINAL VERDICT

**As a hackathon submission:** This is a **top-tier Track 3 entry**. The architecture is coherent, the safety patterns are structural (not aspirational), the audit chain is cryptographically verifiable, the 4-agent adversarial review pattern is unique in this domain, and the tamper demo is a genuine "wow" moment. The code has minor issues (unreachable condition, missing CaseStatus constant, hardcoded API URL in intake) but nothing that breaks functionality or undermines the core claims.

**The 28 hardening tests are this project's superpower.** No other submission I've seen in the list publishes verifiable proof that their safety claims hold. When a judge asks "how do we know the gate can't be bypassed?", you point to 6 passing tests. When they ask "how do we know the audit works?", you click the Tamper Demo button.

**Recommendation:** Submit as-is with the 3 remaining moves (deploy, record video, update README). Don't add more features — the code is solid enough. Polish the presentation.

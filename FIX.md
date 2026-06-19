# 🩺 Fix Plan — Critical Issues Diagnosed & Verified

Based on external audit. Each issue verified against actual code before listing here.

---

## #1 🔴 CRITICAL: Path traversal via case_id

**Verified:** YES. `case_id` from user input flows directly into file paths without sanitization.

**Files affected:**

- [`orchestrator/lifecycle.py:63`](antenatal-review-board/orchestrator/lifecycle.py:63) — `data/cases/{case_id}.json`
- [`orchestrator/lifecycle.py:75`](antenatal-review-board/orchestrator/lifecycle.py:75) — `data/state/{case_id}.json`
- [`orchestrator/main.py:430`](antenatal-review-board/orchestrator/main.py:430) — `data/usg/{case_id}.png`
- [`audit/chain.py:28`](antenatal-review-board/audit/chain.py:28) — `audit_log/{case_id}.jsonl`
- [`orchestrator/main.py:672`](antenatal-review-board/orchestrator/main.py:672) — tamper demo path

**Impact:** `case_id = "../../etc/passwd"` writes outside the project directory. Remote attacker can read/write arbitrary files on the server.

**Fix:** Add sanitizer function used everywhere:

```python
import re
def sanitize_case_id(case_id: str) -> str:
    return re.sub(r'[^A-Za-z0-9\-]', '', case_id)[:64]
```

Then wrap every `case_id` before file operations.

---

## #2 🔴 HIGH: "Apply to Case" button discards user input

**Verified:** YES. [`DashboardPage.jsx:197`](antenatal-review-board/ui/src/pages/DashboardPage.jsx:197) (line may differ after rewrite)

The field review inputs have no `onChange` handlers and no controlled state. The `onClick={() => setReviewFields([])}` button clears fields without reading their values. User-entered corrections are silently lost.

**Fix:** Add controlled state per field with `useState({})` tracking each field's entered value. On apply, merge values into `caseJson` before clearing.

---

## #3 🔴 HIGH: Band mode dating_risk agent receives empty case

**Verified:** YES. [`agents/dating_risk/agent.py:281-291`](antenatal-review-board/agents/dating_risk/agent.py:281)

`_find_structured_case_in_context()` returns `payload.get("structured_case")` but intake's handoff payload is `{"message": "StructuredCase ready for analysis."}` — no StructuredCase data. The dating_risk agent gets `{}`.

**Fix:** Intake's handoff should include `structured_case` in the payload:

```python
payload={
    "message": "StructuredCase ready for analysis.",
    "structured_case": structured.model_dump(mode="json"),
}
```

---

## #4 🔴 HIGH: Docker agent services run orchestrator code

**Verified:** YES. [`docker-compose.yml:27-59`](antenatal-review-board/docker-compose.yml:27)

All 3 agent services (`agent-intake`, `agent-dating-risk`, `agent-guideline`) build from the same Dockerfile with no `command:` override. They all start `uvicorn orchestrator.main:app` — nobody runs agent-specific code.

**Fix:** Either:

- Add `command:` overrides per service (e.g., `python -m agents.intake.agent`)
- Or remove the non-functional services (they're not used since agents run in-process)

**Recommendation:** Remove them for hackathon submission. Mention in README that distributed mode is planned.

---

## #5 🟡 MEDIUM: Dead code in lifecycle.py

**Verified:** WAS present, NOW FIXED. [`orchestrator/lifecycle.py`](antenatal-review-board/orchestrator/lifecycle.py)

We fixed this in an earlier edit — the duplicate auto-clear block and the unreachable code after the escalation `return` were removed. **No action needed.**

---

## #6 🟡 MEDIUM: FL/HC/AC silently fail

**Verified:** YES. [`tools/ga_calc.py:38-39`](antenatal-review-board/tools/ga_calc.py:38)

`ga_from_ultrasound()` only supports BPD and CRL. FL, HC, AC are valid `USGMeasurement.type` values in the schema but raise `ValueError`, caught silently in [`agents/dating_risk/agent.py:221-222`](antenatal-review-board/agents/dating_risk/agent.py:221). No GA computed, no warning to user.

**Fix:** Add Hadlock formulas for FL, HC, AC:

```python
elif meas_type == "FL":
    return round((value_mm * 0.21 + 6.4), 1)  # Femur length
elif meas_type == "HC":
    return round((value_mm * 0.33 + 7.2), 1)  # Head circumference
elif meas_type == "AC":
    return round((value_mm * 0.18 + 8.8), 1)  # Abdominal circumference
```

---

## #7 🟡 MEDIUM: missing_investigations always lists all required items

**Verified:** YES. [`tools/guideline_kb.py:77-106`](antenatal-review-board/tools/guideline_kb.py:77)

`missing_investigations()` collects every `require:` item from fired rules without checking what the case already has. Every PE-flagged case always shows `repeat_bp_4h` and `24h_urine_protein` as missing even if BP was already measured and protein already tested.

**Fix:** Accept the StructuredCase and check what's present:

```python
def missing_investigations(structured, flags, rules):
    # ...existing logic...
    # Filter out investigations already present
    present = set()
    if structured.get("vitals", {}).get("bp_systolic"):
        present.add("repeat_bp_4h")  # BP was measured
    if structured.get("labs", {}).get("urine_protein"):
        present.add("24h_urine_protein")
    return sorted(missing - present)
```

---

## #8 🟡 LOW: CaseStatus.AUDITED doesn't exist

**Verified:** YES. [`orchestrator/lifecycle.py:327`](antenatal-review-board/orchestrator/lifecycle.py:327)

Sets `state["status"] = "AUDITED"` but `CaseStatus` class has no `AUDITED` constant. The Dashboard hardcodes it in the STATES array to compensate.

**Fix:** Add `AUDITED = "AUDITED"` to the `CaseStatus` class in [`orchestrator/lifecycle.py`](antenatal-review-board/orchestrator/lifecycle.py:43).

---

## #9 🟢 LOW: Demographics default_factory fails

**Verified:** YES. [`schemas.py:44`](antenatal-review-board/schemas.py:44)

```python
class CaseInput(BaseModel):
    demographics: Demographics = Field(default_factory=Demographics)
```

`Demographics()` requires `age` (no default). Constructing `Demographics()` would raise `ValidationError`. In practice this code path may never be hit because the UI always submits demographics, but it's a latent bug.

**Fix:** Either add defaults to Demographics or remove the default_factory.

---

## #10 🟢 LOW: datetime.utcnow() deprecated

**Verified:** YES. Multiple files. Python 3.12 deprecated `datetime.utcnow()`.

**Files:**

- [`schemas.py:143`](antenatal-review-board/schemas.py:143) — `datetime.utcnow`
- [`agents/intake/agent.py:274`](antenatal-review-board/agents/intake/agent.py:274)

**Fix:** Replace with `datetime.now(timezone.utc)`.

---

## Security Issues

### S1 🔴 CRITICAL: No auth on any endpoint

All routes in [`orchestrator/main.py`](antenatal-review-board/orchestrator/main.py) are open. `/demo/tamper/{case_id}` is especially dangerous outside dev.

**Fix for hackathon:** Not required — demo context. Note in README that auth is not implemented.

### S2 🟡 MEDIUM: No file upload size limit

[`orchestrator/main.py:192`](antenatal-review-board/orchestrator/main.py:192) — `await image.read()` loads entire file to RAM, then base64 encodes (3× memory).

**Fix:** Add size check before reading.

### S3 🟡 MEDIUM: CORS allow_origins=["*"] with credentials

[`orchestrator/main.py:49`](antenatal-review-board/orchestrator/main.py:49) — Browsers reject this per spec. Credentialed cross-origin requests silently fail.

**Fix:** Either remove `allow_credentials=True` or set specific origins.

---

## Test Gaps (No code changes needed for hackathon)

- `tools/treatment.py` — zero coverage
- `packet/generator.py` — zero coverage
- `tools/imaging.py` — zero coverage
- Auditor agent — zero coverage
- `/extract` and `/extract-image` endpoints — zero coverage
- `test_api.py` uses `time.sleep(0.5)` race condition

---

## Immediate Actions (In Priority Order)

| #   | Action                      | File               | Time   |
| --- | --------------------------- | ------------------ | ------ |
| 1   | Sanitize case_id            | 5 files            | 10 min |
| 2   | Fix "Apply to Case"         | DashboardPage.jsx  | 10 min |
| 3   | Add AUDITED to CaseStatus   | lifecycle.py       | 1 min  |
| 4   | Add FL/HC/AC formulas       | ga_calc.py         | 5 min  |
| 5   | Fix Band handoff payload    | intake/agent.py    | 2 min  |
| 6   | Fix Demographics default    | schemas.py         | 2 min  |
| 7   | Fix datetime.utcnow()       | 2 files            | 2 min  |
| 8   | Remove dead Docker services | docker-compose.yml | 2 min  |
| 9   | Add upload size limit       | main.py            | 2 min  |
| 10  | Fix missing_investigations  | guideline_kb.py    | 5 min  |

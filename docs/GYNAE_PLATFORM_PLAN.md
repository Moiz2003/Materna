# Architecture Plan — From Antenatal-only to a Gynae Practice Platform

**Status:** design for review — no code written yet.
**Goal:** keep the proven engine (multi-agent intake → analysis → guideline → deterministic gate → human approve/override loop → SHA‑256 audit → sealed packet) and add a **presentation layer** so the same clinic can handle every common gynaecology presentation, not just pregnancy. Whatever the doctor types or Gemini extracts must land in the correct slot, drive the right findings, and produce the right work‑up/treatment plan.

---

## 1. The core idea — make presentations *declarative data, not code*

Today the domain is hard‑coded in Python (`risk/rules.py`, the `dating_risk` agent, `tools/treatment.py`) and a single ruleset (`data/rules/antenatal_rules.yaml`). Adding a presentation means editing code in many places.

**New model:** every presentation is a **config bundle** read by a generic engine. Adding "vaginal discharge" becomes *adding a folder of YAML*, not writing Python. This is what makes it efficient and scalable to "cover them all".

```
data/presentations/
  antenatal/            infertility/         pelvic_pain/        vaginal_discharge/
    fields.yaml           fields.yaml          fields.yaml         fields.yaml
    rules.yaml            rules.yaml           rules.yaml          rules.yaml
    findings.yaml         findings.yaml        findings.yaml       findings.yaml
    treatment.yaml        treatment.yaml       treatment.yaml      treatment.yaml
```

A `PresentationRegistry` loads these at startup. Everything downstream (intake validation, the Gemini extraction prompt, risk evaluation, findings, treatment plan, the UI form, the PDF sections) is generated **from the registry**.

---

## 2. Data model — shared Core + presentation modules + a catch‑all

### 2.1 Three tiers
1. **Core** (every patient): `case_id`, `presentation`, demographics (age, parity/gravidity), vitals (BP, pulse, temp, BMI), a universal `pregnancy_test` flag, pain basics, and a free‑text `clinical_notes`.
2. **Presentation module fields** ("slots"): defined per presentation in `fields.yaml` (see §4).
3. **`extras` (catch‑all)**: `dict[str, Any]`. Anything the doctor enters or Gemini extracts that doesn't match a known slot is preserved here, never dropped — and surfaced in the UI as "Additional captured data" so nothing is lost and the doctor can promote it to a slot.

### 2.2 Why a catch‑all matters (the doctor's "whatever goes in that slot" requirement)
- Each presentation's `fields.yaml` lists its canonical slots with synonyms/units.
- The intake step maps incoming key/values to slots by **id + synonyms** (e.g. `LMP`, `last period`, `last menstrual period` → `lmp_date`).
- Unmapped values → `extras`, shown to the doctor for confirmation (re‑using the existing "Confirm Uncertain Fields" panel pattern).

### 2.3 Schema shape (replaces today's antenatal‑only `CaseInput`)
```
CaseInput:
  case_id, presentation: Literal[<registry ids>]
  core: CoreData          # shared
  data: dict[str, Any]    # presentation slots, validated against fields.yaml
  extras: dict[str, Any]  # unmapped but captured
  attachments: [ref]      # images (USG, swab photo, report) — already supported
```
`StructuredCase`, `Finding`, `RiskFlag`, `ComplianceResult` stay, but `Finding`/`RiskFlag` become **presentation‑tagged and generic** (no hard‑coded `ga_lmp_weeks`; those move into `data`/derived findings for the antenatal module).

---

## 3. Field/slot definition (`fields.yaml`) — drives intake, extraction, and the UI

```yaml
presentation: pelvic_pain
label: "Lower abdominal / pelvic pain"
fields:
  - id: pain_site
    label: "Pain site"
    type: enum
    options: [right_iliac, left_iliac, suprapubic, generalised]
    synonyms: ["site of pain", "location"]
  - id: pain_onset
    label: "Onset"
    type: enum
    options: [sudden, gradual]
  - id: pregnancy_test
    label: "Urine pregnancy test"
    type: enum
    options: [positive, negative, unknown]
    core: true                # promoted from Core
  - id: temperature_c
    label: "Temperature"
    type: number
    unit: "°C"
  - id: adnexal_mass_cm
    label: "Adnexal mass on USG"
    type: number
    unit: "cm"
```

**One definition powers four things:**
- **UI** renders the input (enum → dropdown, number → numeric+unit, date → datepicker).
- **Gemini extraction prompt** is generated from this list, so extracted values map straight to `data[id]` (+ confidence per field, re‑using the confidence‑aware OCR we already built).
- **Intake validation/slotting** coerces types and routes unknowns to `extras`.
- **Findings/rules** reference fields by `id`.

---

## 4. Generic, YAML‑driven rules (`rules.yaml`) — replaces hard‑coded `risk/rules.py`

Today `eval_preeclampsia/gdm/anaemia` are Python. Generalize to a **declarative evaluator** (`risk/engine.py`) that reads conditions:

```yaml
presentation: pelvic_pain
rules:
  - id: ECTOPIC-RF
    name: "Possible ectopic pregnancy"
    when: { all: [ {pregnancy_test: positive}, {pain_onset: sudden} ] }
    flag: { type: ectopic_suspected, severity: high }
    require: [serum_bhcg, transvaginal_usg]
    red_flag: true            # forces escalation regardless of veto
  - id: TORSION-RF
    name: "Ovarian torsion"
    when: { all: [ {pain_onset: sudden}, {adnexal_mass_cm: {gte: 5}} ] }
    flag: { type: torsion_suspected, severity: high }
    require: [doppler_usg, gynae_surgical_review]
    red_flag: true
```

The current operators (`gte`, `in`, `lt`, `and`/`or`) already exist informally in `antenatal_rules.yaml`; we formalise a small condition grammar (`all`/`any`/`not`, comparators, set membership). `risk/engine.py` evaluates these for *any* presentation. The deterministic **gate** (`orchestrator/gate.py`) gains one rule: **any `red_flag: true` → escalate** (in addition to existing flag/veto logic).

---

## 5. Clinical coverage — the full standard‑gynae catalogue

The registry is designed to hold all of these. Red‑flag (auto‑escalate) items are marked 🚩.

| Module | Common conditions captured | Key red flags 🚩 | Core work‑up |
|---|---|---|---|
| **Antenatal** (exists) | Pre‑eclampsia, GDM, anaemia, dating discordance | 🚩 severe PE / BP ≥160/110 | repeat BP, 24h protein, OGTT, iron studies |
| **Early pregnancy** | Threatened/missed miscarriage, **ectopic**, molar | 🚩 ectopic, heavy bleeding/haemodynamic | βhCG trend, TVS, anti‑D, rhesus |
| **Pelvic / lower‑abdo pain** | PID, ruptured/haemorrhagic cyst, **torsion**, appendicitis, dysmenorrhoea/endometriosis | 🚩 ectopic, torsion, sepsis/peritonism | preg test, βhCG, USG±Doppler, swabs, CRP/WCC |
| **Abnormal uterine bleeding (AUB)** | Heavy menstrual bleeding, IMB/PCB, fibroids, polyps | 🚩 postcoital bleeding → cervical Ca; haemodynamic instability | FBC, ferritin, USG/TVS, pipelle, smear status |
| **Postmenopausal bleeding (PMB)** | Endometrial hyperplasia/cancer, atrophic | 🚩 **PMB = 2‑week‑wait** endometrial cancer pathway | TVS endometrial thickness, pipelle/hysteroscopy |
| **Amenorrhoea** | Pregnancy, PCOS, thyroid, hyperprolactinaemia, POI | 🚩 (rule out pregnancy first) | βhCG, TSH, prolactin, FSH/LH, testosterone |
| **Vaginal discharge / infection** | BV, candida, trichomonas, **chlamydia/gonorrhoea**, PID | 🚩 PID with sepsis; pregnancy + STI | pH, whiff, microscopy, NAAT/STI screen |
| **Vulval complaints** | Candida, lichen sclerosus, **vulval cancer** | 🚩 persistent lump/ulcer → biopsy/refer | exam, swabs, biopsy if suspicious |
| **Infertility / subfertility** | Ovulatory, tubal, male factor, ↓ovarian reserve, PCOS | 🚩 (OHSS if on treatment) | day‑21 progesterone, AMH, FSH/LH, TSH/prolactin, HSG, **semen analysis** |
| **PCOS** | Oligomenorrhoea, hyperandrogenism, metabolic | — | Rotterdam criteria, OGTT, lipids, USG ovaries |
| **Menopause / perimenopause** | Vasomotor, GSM, HRT suitability | 🚩 VTE/breast‑Ca contraindications to HRT | symptom score, VTE/cancer risk review |
| **Adnexal mass / ovarian cyst** | Benign cyst vs **ovarian malignancy** | 🚩 high RMI/IOTA, ascites | CA‑125, USG morphology, RMI, refer if high |
| **Prolapse / incontinence (urogynae)** | POP, stress/urge incontinence | 🚩 retention, haematuria | POP‑Q, bladder diary, urinalysis, PVR |
| **Cervical screening / colposcopy** | Abnormal smear, HPV+, CIN | 🚩 visible suspicious cervix | HPV/cytology, colposcopy referral |
| **Contraception / family planning** | Choice, IUD/implant, emergency contraception | 🚩 UKMEC‑4 contraindications, missed‑pill + EC | UKMEC check, BP/BMI, preg test |
| **Breast complaint** (often co‑presents) | Lump, nipple discharge | 🚩 lump/bloody discharge → triple‑assessment | exam, refer to breast clinic |

This is the "search for even more issues and cover them all" deliverable: the catalogue above is the target registry contents. Each row = one `data/presentations/<id>/` bundle.

---

## 6. Findings & treatment per presentation (generic, data‑driven)

- **`findings.yaml`**: declarative derivations + how to display them. E.g. antenatal keeps GA/discordance; AUB computes "anaemia from menorrhagia"; adnexal computes **RMI = U × M × CA‑125**; menopause computes a symptom score. The `dating_risk` agent becomes the **antenatal** analysis plug‑in; a generic `analysis` agent runs the registry’s derivations for the rest.
- **`treatment.yaml`**: per‑presentation impression/investigations/treatment KB — exactly the structure `tools/treatment.py` already uses, just loaded from the registry instead of a hard‑coded dict. The **iterative approve/override loop stays unchanged** (it's presentation‑agnostic).

---

## 7. Findings presentation & "nothing lost" UX

- The case view renders findings from `findings.yaml` (label + value + severity), so each presentation shows its own relevant panel.
- `extras` is shown as **"Additional data captured (not yet slotted)"** with a one‑click "map to field" — covering the doctor's concern that *whatever* is entered/extracted is visible and placeable.
- The Gemini extractor returns `{data: {slotted}, extras: {unmapped}, field_confidence, needs_review}` — built on the confidence‑aware extraction already shipped.

---

## 8. File‑by‑file refactor map

| Today | Becomes |
|---|---|
| `schemas.py` (antenatal `CaseInput`) | Core + generic `CaseInput{presentation, data, extras}`; antenatal fields move to registry |
| `data/rules/antenatal_rules.yaml` | `data/presentations/antenatal/rules.yaml` + new bundles per presentation |
| `risk/rules.py` (hard‑coded evals) | `risk/engine.py` — generic YAML condition evaluator |
| `agents/dating_risk/agent.py` | `agents/analysis/` generic runner + antenatal dating plug‑in |
| `tools/treatment.py` (dict KB) | loads `treatment.yaml` from registry (loop logic unchanged) |
| `orchestrator/gate.py` | add `red_flag → escalate` (keep flags/veto) |
| `packet/generator.py` | sections driven by presentation (GA section only for antenatal) |
| `orchestrator/main.py` `/extract*` | prompt generated from the selected presentation's fields |
| `ui/src/App.jsx` | presentation selector + dynamic form + dynamic findings |
| **unchanged** | audit chain, Band coordination, human approve/override loop, persistence |

---

## 9. Phased delivery (so the demo never breaks)

- **Phase 0 — Registry + router (no behaviour change):** introduce `PresentationRegistry`, move antenatal into `data/presentations/antenatal/`, add `presentation` field defaulting to `antenatal`. Prove parity (all 31 tests still pass).
- **Phase 1 — Generic rule engine:** `risk/engine.py` reproduces the 4 antenatal rules from YAML; delete hard‑coded evals once parity confirmed.
- **Phase 2 — Dynamic intake/extraction/UI:** registry‑driven form + Gemini prompt + `extras` slotting.
- **Phase 3 — Add presentations:** ship `pelvic_pain` first (best red‑flag demo: ectopic/torsion), then `vaginal_discharge`, `AUB`, `PMB`, `infertility`, … each is config‑only.
- **Phase 4 — Findings/packet per presentation.**

---

## 10. Open decisions for you
1. **Breadth vs depth:** ship the registry engine + 1–2 presentations *well*, or stub all ~15 (shallower)? Recommend deep on 2–3, registry ready for the rest.
2. **Rule authorship:** these red‑flag/work‑up rules must be **clinician‑reviewed** before any real use — the YAML makes that review easy, but it is decision‑support only.
3. **Antenatal regression:** Phase 0/1 must keep the existing antenatal demo byte‑for‑byte; gated behind tests.

---

## 11. What stays exactly as‑is (the moat)
The hard, judged parts are already built and **presentation‑agnostic**: Band multi‑agent coordination, the deterministic escalation gate, the SHA‑256 hash‑chained audit, the iterative human approve/override loop, disk persistence, and the sealed PDF spine. This refactor is **additive**, not a rewrite.

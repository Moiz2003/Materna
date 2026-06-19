# 🎨 Dashboard UX Redesign — Anti-AI-Slop Plan

> Goal: Transform the 352-line monolithic Dashboard into a polished, guided, novice-friendly experience that looks like a UI/UX team built it.

---

## 1. CURRENT UX PROBLEMS (Deeply Analyzed)

### 1.1 The "AI Slop" Tells

| Problem                                            | Where               | Why It Screams AI                                                               |
| -------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------- |
| Emoji everywhere (🧠🩻📋🚀🔴🟡✅❌🔐🩺)            | Lines 192-212       | AI loves emoji. Real UIs use icon libraries with consistent styling             |
| Raw JSON textarea as primary input                 | Line 210            | No doctor types JSON. This is a dev tool, not a clinical tool                   |
| "Smart Extract" buried in a sub-section            | Line 199            | The most useful feature (paste notes) is visually equal to the JSON field       |
| All states crammed into one view                   | Lines 168-290       | Input, processing, findings, decision, download all compete for space           |
| Tiny text everywhere (`text-[9px]`, `text-[10px]`) | Lines 39, 239, 246  | Real UIs use a scale (12/14/16/20), not single-pixel sizes                      |
| No progressive disclosure                          | Entire file         | Everything is visible at once — novice users are overwhelmed                    |
| Conditional rendering creates layout jumps         | Lines 190, 235, 280 | Content appears/disappears, shifting the page                                   |
| "Case JSON" is the fallback input                  | Line 209            | For a medical tool, the primary input should be natural language or form fields |
| Sidebar has no purpose beyond decoration           | Line 149            | Collapsible but does nothing — pure decoration                                  |

### 1.2 Specific UX Failures

1. **Input method confusion**: User sees 3 ways to input (smart extract, file upload, raw JSON) with no guidance on which to use
2. **Zero onboarding**: No "first time" flow, no tooltips, no progressive hints
3. **All-or-nothing visibility**: You either see the input form OR the results — never both. Can't reference input while viewing output
4. **No undo/back**: Once submitted, you can't go back to edit the input
5. **Results are walls of text**: GA metrics, flags, compliance, auditor challenge, treatment plan all stacked vertically — no hierarchy
6. **Decision panel mixed with findings**: During ESCALATED state, both findings AND the reviewer console show — double the scrolling
7. **No summary/dashboard view**: Can't see at a glance "3 cases pending review, 2 sealed today"

---

## 2. THE REDESIGN PRINCIPLES

### Principle 1: Progressive Disclosure

Show the user ONLY what they need at each stage. Reveal complexity gradually.

### Principle 2: Natural Language First

The primary input is pasting clinical notes. JSON is an advanced option, hidden by default.

### Principle 3: Split-Pane Persistent Layout

Input always visible on the left, results stream in on the right. No layout jumps.

### Principle 4: Real UI Typography Scale

- Headings: 20px / 16px / 14px
- Body: 14px
- Labels: 12px
- Mono/code: 13px
- NO single-pixel sizes

### Principle 5: Form-First Input (not JSON)

Replace the JSON textarea with real form fields (age, parity, LMP date, USG date, BP, labs). JSON is a collapsible "Advanced" section.

### Principle 6: Purpose-Driven Sidebar

The sidebar shows navigation context: "New Review" / "Pending Reviews (3)" / "Completed Today (7)" — not just decorative icons.

---

## 3. THE NEW LAYOUT

```
┌──────────────────────────────────────────────────────────────┐
│ [Logo] Materna                    [About] [🩺 Dr. Saima]    │  ← Top bar
├────────┬─────────────────────────────────────┬──────────────┤
│        │                                     │              │
│ SIDEBAR│         MAIN CONTENT AREA           │   LIVE       │
│        │                                     │   OUTPUT     │
│ 📋 New │  ┌─────────────────────────────┐   │              │
│   Case │  │ STEP 1: Patient Information  │   │  Band Room  │
│        │  │                             │   │  (collapses │
│ 📂 Pend│  │ [Smart Paste primary CTA]   │   │   when      │
│   ing  │  │                             │   │   idle)     │
│   (3)  │  │ OR fill form below:         │   │              │
│        │  │ ┌──────┐ ┌──────┐          │   │  Case Status│
│ ✅ Comp│  │ │ Age  │ │Parity│          │   │  Pipeline   │
│   leted│  │ └──────┘ └──────┘          │   │  (animated) │
│   (7)  │  │ ┌──────┐ ┌──────┐          │   │              │
│        │  │ │LMP   │ │USG   │          │   │  SHA-256    │
│        │  │ └──────┘ └──────┘          │   │  Audit      │
│ 🔐     │  │                             │   │  (latest    │
│ Audit  │  │ [Advanced: JSON ▾]          │   │   entries)  │
│ Logs   │  │                             │   │              │
│        │  │ [🩻 Upload Ultrasound]      │   │              │
│        │  │                             │   │              │
│ ⚙️      │  │ [🚀 Submit to Review Board] │   │              │
│Settings│  └─────────────────────────────┘   │              │
│        │                                     │              │
│        │  ┌─────────────────────────────┐   │              │
│        │  │ RESULTS (appears on submit)  │   │              │
│        │  │                             │   │              │
│        │  │ [GA metrics card]           │   │              │
│        │  │ [Risk flags expandable]     │   │              │
│        │  │ [Compliance verdict]        │   │              │
│        │  │ [Auditor report]            │   │              │
│        │  │                             │   │              │
│        │  │ [🩺 Human Decision Panel]   │   │              │
│        │  │   (only when ESCALATED)     │   │              │
│        │  │                             │   │              │
│        │  │ [📦 Sealed Packet Download] │   │              │
│        │  │   (only when SEALED)        │   │              │
│        │  └─────────────────────────────┘   │              │
└────────┴─────────────────────────────────────┴──────────────┘
```

---

## 4. INPUT REDESIGN — From JSON to Smart Form

### Current (AI Slop):

```
📋 Case JSON
[ massive textarea with raw JSON ]
🚀 Submit to Review Board
```

### New (UX Team Design):

```
┌─────────────────────────────────────────┐
│ 🧠 Smart Paste                           │
│                                         │
│ Paste whatever the chart says — English  │
│ or Urdu. We'll extract the data.         │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ e.g. "29yo G3P2, LMP Dec 1 2025,  │ │
│ │  USG June 10 2026 BPD 58mm,        │ │
│ │  BP 150/98, urine protein 2+..."   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [ 🤖 Extract & Fill Form ]              │  ← Primary CTA
│                                         │
│ ── or fill manually ──                  │
│                                         │
│ Age: [__]  Parity: [__]                │
│ LMP Date: [____]  USG Date: [____]     │
│ BP: [___/___]  Urine Protein: [___]    │
│ Glucose: [___] mg/dL  Hb: [___] g/dL   │
│ USG Measurement: [Type▾] [___mm]       │
│                                         │
│ 🩻 Ultrasound Image: [Choose File]      │
│                                         │
│ ── Advanced ──                          │
│ ▸ Edit Raw JSON                         │  ← Collapsed by default
│                                         │
│ [ 🚀 Submit to Review Board ]           │
└─────────────────────────────────────────┘
```

**Key changes:**

1. Smart Paste is the PRIMARY input (big textarea, prominent CTA)
2. Manual form fields replace the JSON textarea for novice users
3. JSON is collapsed under "Advanced" — only devs/power users expand it
4. Form fields auto-fill when Smart Extract completes
5. Form fields provide immediate validation (red border if age > 120, etc.)

---

## 5. RESULTS REDESIGN — Progressive Cards

### Current:

Vertical stack of EVERYTHING. Wall of text.

### New:

Cards appear progressively as the pipeline advances:

**Stage 1: STRUCTURED → ANALYZED**

```
┌──────────────────────────────────────┐
│ ✅ Case Structured                    │
│                                      │
│ Patient: 29y, G3P2                   │
│ LMP: Dec 1, 2025 · USG: Jun 10, 2026│
│ BP: 150/98 · Protein: 2+            │
│ Glucose: 104 mg/dL · Hb: 10.1 g/dL  │
│                                      │
│ [⏳ Analyzing...  ]                   │
└──────────────────────────────────────┘
```

**Stage 2: ANALYZED → CHECKED**

```
┌──────────────────────────────────────┐
│ 📊 Gestational Age                   │
│ ┌─────────┬─────────┬──────────────┐ │
│ │ GA (LMP)│GA (USG) │ Discordance  │ │
│ │ 27.3 wk │ 23.0 wk │ 4.3 wk ⚠    │ │
│ └─────────┴─────────┴──────────────┘ │
│                                      │
│ 🚨 Risk Flags                        │
│ ┌──────────────────────────────────┐ │
│ │ 🔴 PE-001 HIGH   BP 150/98, 2+  │ │
│ │ 🟡 GDM-002 MOD   Glucose 104    │ │
│ │ 🟡 ANE-003 MOD   Hb 10.1        │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Stage 3: CHECKED → AUDITED → ESCALATED**

```
┌──────────────────────────────────────┐
│ ⚖️ Guideline Check                   │
│ ┌──────────────────────────────────┐ │
│ │ 🔴 VETO                          │ │
│ │ Missing: repeat_bp_4h,           │ │
│ │ 24h_urine_protein, ogtt          │ │
│ └──────────────────────────────────┘ │
│                                      │
│ 🕵️ Auditor Review                    │
│ ┌──────────────────────────────────┐ │
│ │ ✅ No challenge — Guideline       │ │
│ │    correctly identified issues   │ │
│ └──────────────────────────────────┘ │
│                                      │
│ 🩺 Human Review Required             │
│ ┌──────────────────────────────────┐ │
│ │ [Treatment Plan displayed here]  │ │
│ │ [Approve] [Override with note]   │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

**Key changes:**

1. Each stage is its own card with clear visual hierarchy
2. Cards animate in with FadeIn (already built)
3. Use the TexturePanel compound component (already built)
4. Color coding: teal=normal, amber=warning, red=veto/escalation
5. Expandable sections (already built) for detailed evidence

---

## 6. SIDEBAR REDESIGN — From Decoration to Navigation

### Current:

5 icons with labels that collapse. No functionality.

### New:

```
┌──────────────┐
│ 📋 New Case  │  ← Active state
│              │
│ 📂 Pending   │  ← Shows count badge
│      3       │
│              │
│ ✅ Completed │
│      7       │
│              │
│ ──────────── │
│              │
│ 🔐 Audit     │
│    Logs      │
│              │
│ ⚙️  Settings  │
│              │
│ ──────────── │
│              │
│ 🟢 System OK │  ← Health indicator
└──────────────┘
```

**Key changes:**

1. "New Case" is the active default view
2. Pending/Completed show real counts from backend
3. Audit Logs opens a dedicated audit browser
4. Settings toggles dark mode, notification prefs
5. Health indicator shows backend connectivity

---

## 7. NOVICE USER FLOW

### First-Time Experience:

1. User lands on Dashboard → sees the Smart Paste textarea prominently
2. Tooltip: "Paste clinical notes or type patient data below"
3. User pastes notes → clicks "Extract & Fill Form" → form fields auto-populate
4. Form fields show confidence indicators (green check = high confidence, amber dot = medium)
5. User reviews auto-filled form, corrects any fields
6. Clicks "Submit to Review Board"
7. Processing animation plays (4 agents visible in Band Room side panel)
8. Results appear progressively as cards
9. If ESCALATED: decision panel appears at bottom with clear Approve/Override buttons
10. If SEALED: download panel appears with "Download Sealed PDF" + "Verify Audit Chain" buttons

### Empty States (critical for novice UX):

- **No cases yet**: "Welcome to Materna. Start by pasting clinical notes or loading a demo case."
- **Processing**: Animated pipeline with agent icons lighting up in sequence
- **No flags found**: "✅ All clear — no risk flags detected. Case will auto-clear."
- **Awaiting decision**: "🩺 This case requires human review. Dr. Saima Javed must approve or override."

---

## 8. VISUAL REFINEMENTS

### Typography:

- Replace system fonts with Plus Jakarta Sans (headings) + Inter (body) [ALREADY DONE]
- Use a proper scale: 12/14/16/20/24/32 — never 9px or 10px

### Spacing:

- Use consistent 8px grid: 4/8/12/16/24/32/48px
- Card padding: 20px internal, 16px between cards

### Color:

- Keep teal+amber palette [ALREADY DONE]
- Add: teal-300 for "in progress", amber-300 for "attention", green-400 for "success"
- Background: subtle animated gradient instead of flat #020617

### Micro-interactions:

- Cards slide in from bottom on appear (FadeIn already built)
- Step indicators pulse when active
- Submit button has loading spinner (not just text change)
- Risk flags have subtle shake animation on first appear
- Audit hash shows "copy to clipboard" on hover

### Responsive:

- Mobile: single column, sidebar collapses to bottom tab bar
- Tablet: 2-column (main + output)
- Desktop: 3-column (sidebar + main + output)

---

## 9. COMPONENT TREE (What to Build)

```
pages/
  DashboardPage.jsx          ← Rewrite: orchestrate layout + state
    components/dashboard/
      SidebarNav.jsx          ← New: functional sidebar with counts
      SmartPasteInput.jsx     ← New: primary input component
      PatientForm.jsx         ← New: form fields component
      CaseJSONAdvanced.jsx    ← New: collapsed JSON editor
      ResultsStage.jsx        ← New: renders the correct stage card
      StageStructured.jsx     ← New: "Case Structured" card
      StageAnalyzed.jsx       ← New: GA + Risk Flags card
      StageChecked.jsx        ← New: Guideline + Auditor card
      StageDecision.jsx       ← New: Human Review panel
      StageSealed.jsx         ← New: Download + Tamper panel
      ProcessingOverlay.jsx   ← New: animated agent pipeline
      EmptyState.jsx          ← New: first-time guidance
    components/output/
      LiveOutput.jsx          ← New: right panel (Band Room + Audit)
```

---

## 10. IMPLEMENTATION STRATEGY

### Phase 1: Component Extraction (30 min)

- Move Sidebar to `SidebarNav.jsx` with new navigation
- Extract Smart Paste to `SmartPasteInput.jsx`
- Extract form to `PatientForm.jsx`
- Extract each result stage to its own file

### Phase 2: Layout Restructure (20 min)

- Change DashboardPage to split-pane layout
- Add LiveOutput panel on the right
- Wire up progressive card rendering

### Phase 3: Polish (20 min)

- Add empty states
- Add micro-interactions
- Test all 3 demo cases

---

## 11. CLAUDE PROMPT

Paste this exact prompt into Claude Code:

```
You are refactoring the Antenatal Review Board (Materna) Dashboard.
Read ui/src/pages/DashboardPage.jsx first.

GOAL: Transform the 350-line monolithic dashboard into a polished,
split-pane, novice-friendly experience with progressive disclosure.

PRINCIPLES:
1. No emoji in UI labels — use lucide-react icons only
2. Smart Paste is the PRIMARY input method
3. Raw JSON is hidden under "Advanced" (collapsed by default)
4. Results appear as progressive cards (one per pipeline stage)
5. Left pane: input + results. Right pane: Band Room + Audit.
6. Typography: 14px body, 12px labels, 16px headings. Never 9px.
7. Use the existing TexturePanel, FadeIn components from components/ui/
8. Keep all API calls and state management intact — only change the JSX layout

IMPLEMENT:
1. Create components/dashboard/SidebarNav.jsx — functional sidebar with
   "New Case", "Pending (N)", "Completed (N)", "Audit Logs", "Settings"
2. Create components/dashboard/SmartPasteInput.jsx — big textarea with
   prominent "Extract & Fill Form" button, demo case quick-load chips
3. Create components/dashboard/PatientForm.jsx — form fields: age,
   parity, LMP date, USG date, BP sys/dia, urine protein, glucose, Hb,
   USG measurement type+value. Auto-fills from Smart Extract.
4. Create components/dashboard/ResultsStage.jsx — renders the correct
   stage card based on status: StageStructured, StageAnalyzed,
   StageChecked, StageDecision, StageSealed
5. Create components/output/LiveOutput.jsx — right panel with BandRoom
   + Audit Trail
6. Rewrite DashboardPage.jsx — split-pane layout (sidebar | main | output),
   uses all the new components, keeps all existing state/API logic

DO NOT:
- Change any API calls or state management
- Remove any functionality
- Use emoji in labels (use lucide-react icons)
- Use text-[9px] or text-[10px] — minimum 12px
- Use inline styles (use Tailwind classes from our theme)

Verify: npm run dev should show the new layout. Submit C-0001 and confirm
all cards appear progressively.
```

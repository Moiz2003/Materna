# 🏥 claude4.md — Dashboard v4: Apple 2026 Glass + HCI Principles

> **Mission:** Total dashboard redesign solving the "stuck/frozen" perception, with Apple 2026 glass-morphism, Cure MD-inspired spatial UI, progressive processing visualization, and dual novice/expert modes.

---

## 0. ROOT CAUSE: WHY THE PRODUCT FEELS "STUCK"

### Current problem:

```
User clicks "Submit to Review Board"
  ↓
ProcessingOverlay shows 4 static agent icons with one pulsing
  ↓
Polling runs every 1.2 seconds — during gaps, NOTHING visually changes
  ↓
User sees same screen for 5-8 seconds → thinks it's frozen/broken
  ↓
Results suddenly appear via FadeIn — no transition, no ceremony
```

**The fix is NOT a faster backend.** The backend is fast enough (5-8 seconds for 4-agent pipeline). The fix is **continuous visual feedback** that makes every millisecond of waiting feel intentional.

### Design principle: "Never show a static loading state"

Every loading state must have:

1. **Progressive animation** — something moves every 200ms, not every 1.2s
2. **Elapsed time counter** — "Processing… 3.2s" makes users feel in control
3. **Stage-by-stage feedback** — show which agent is currently working with a text label
4. **Completion ceremony** — results don't "appear", they "arrive" with an orchestrated reveal

---

## 1. APPLE 2026 GLASS DESIGN SYSTEM

### Core aesthetic:

Apple's 2026 design language (visionOS-influenced) is defined by:

| Element               | Implementation                                                                                                    |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Depth layers**      | 3 distinct z-depths: background (bg-dark), surface (bg-card), overlay (glass)                                     |
| **Frosted glass**     | `backdrop-blur-2xl` + `bg-white/[0.03]` + subtle border glow                                                      |
| **Dynamic lighting**  | Ambient light that shifts based on content state (teal when active, amber when processing, emerald when complete) |
| **Spatial UI**        | Elements have physicality — shadows, depth, parallax on hover                                                     |
| **Haptic-mirroring**  | Visual pulses that simulate haptic feedback (scale + opacity micro-animations)                                    |
| **Typography rhythm** | SF-inspired hierarchy: Display (clamp), Title (19pt), Body (15pt), Caption (12pt)                                 |

### Glass panel specification:

```css
.glass-panel {
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(45, 212, 191, 0.08);
  border-radius: 20px;
  box-shadow:
    0 4px 24px -8px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.04);
}
```

### Ambient lighting states:

| State             | Glow color        | Intensity               |
| ----------------- | ----------------- | ----------------------- |
| Idle              | Transparent       | 0                       |
| Active/Processing | Teal `#2DD4BF`    | 8% opacity, 80px blur   |
| Warning/Attention | Amber `#F59E0B`   | 12% opacity, 60px blur  |
| Success/Complete  | Emerald `#059669` | 10% opacity, 100px blur |
| Error             | Red `#DC2626`     | 15% opacity, 60px blur  |

---

## 2. NOVICE MODE vs EXPERT MODE

### Design principle: "Progressive complexity"

The UI adapts to the user, not the other way around. Mode is toggled via a subtle switch in the sidebar — persisted to localStorage.

### Novice Mode (default for new users):

```
┌──────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────┐   │
│  │  👋 Welcome to Materna                            │   │
│  │                                                  │   │
│  │  [📋 Load Demo Case]  or  [📝 Paste Notes]       │   │
│  │                                                  │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  Smart Paste                              │   │   │
│  │  │  Paste clinical notes here...             │   │   │
│  │  │  [Extract →]                              │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  │                                                  │   │
│  │  — OR fill manually —                            │   │
│  │                                                  │   │
│  │  [Simple form with 6 fields]                     │   │
│  │  Age: [__]  Parity: [__]                         │   │
│  │  BP: [__/__]  Hb: [__]                           │   │
│  │  Glucose: [__]  Urine Protein: [__]              │   │
│  │                                                  │   │
│  │  [Submit to Review Board →]                      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Right panel: hidden (reduces cognitive load)            │
└──────────────────────────────────────────────────────────┘
```

- **No JSON editor visible** — it exists but is collapsed by default
- **Demo cases prominently displayed** — one-click "try it" buttons
- **Guided tooltips** on first visit (3-step onboarding: paste, submit, review)
- **Simpler language** — "Blood Pressure" not "bp_systolic"
- **Right panel collapsed** — less visual noise

### Expert Mode:

```
┌──────────────────────────────────────────────────────────┐
│  [Sidebar: full nav]  [Main: compact form + JSON]  [Live] │
│                                                          │
│  Keyboard shortcuts:                                      │
│    ⌘K → command palette                                   │
│    ⌘↵ → submit case                                      │
│    ⌘D → load demo                                        │
│    ⌘N → new case                                         │
│    ⌘E → toggle JSON editor                               │
│                                                          │
│  Features:                                               │
│  • Batch submit multiple cases                           │
│  • Direct JSON editing with syntax highlighting          │
│  • Case history with search/filter                       │
│  • Export all cases as ZIP                               │
│  • Audit chain diff viewer                              │
│  • Right panel: full Band room + audit log               │
└──────────────────────────────────────────────────────────┘
```

---

## 3. PROGRESSIVE PROCESSING VISUALIZATION

This is THE most important fix. Replaces the static `ProcessingOverlay`.

### New component: `ProcessingTheatre`

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│              ◉ Intake                                    │
│             ╱                                            │
│            ╱  3.2s elapsed                               │
│           ╱                                              │
│     ◉ Dating & Risk                                      │
│         ╱                                                │
│        ╱  Extracting vitals…                             │
│       ╱                                                  │
│  ○ Guideline                                             │
│     ╲                                                     │
│      ╲                                                    │
│  ○ Auditor                                               │
│                                                          │
│  ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░  62%                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Design:

- **Vertical agent ladder** (not horizontal — easier to read top-to-bottom progress)
- Each agent node: circle with icon, label, and status text
- Active agent: pulses with teal glow + shows "Working…" subtext
- Completed agent: fills teal + checkmark
- Pending agent: dimmed, grey
- **Progress bar** at bottom: fills based on completedSteps / totalSteps
- **Elapsed time** counter: top-right, increments every 100ms
- **Agent status text** cycles: "Normalising data…" → "Computing GA…" → "Checking rules…" → "Auditing…"
- **Background ambient light** shifts: idle → teal glow → brighter teal as agents complete

### Implementation:

```jsx
function ProcessingTheatre({ status, startedAt }) {
  const [elapsed, setElapsed] = useState(0);
  const done = completedSteps(status);
  const steps = PIPELINE_STEPS;

  // Update elapsed every 100ms for smooth counter
  useEffect(() => {
    const t = setInterval(() => {
      setElapsed(((Date.now() - startedAt) / 1000).toFixed(1));
    }, 100);
    return () => clearInterval(t);
  }, [startedAt]);

  return (
    <GlassPanel glow="teal" intensity={Math.min(done / steps.length, 1)}>
      {/* Elapsed counter */}
      <div className="text-right text-xs font-mono text-teal-400/60 mb-6">
        {elapsed}s
      </div>

      {/* Agent ladder */}
      <div className="space-y-4">
        {steps.map((step, i) => {
          const isDone = i < done;
          const isActive = i === done;
          return (
            <AgentLadderNode
              key={step.id}
              step={step}
              isDone={isDone}
              isActive={isActive}
              statusText={isActive ? getStatusText(step.id, elapsed) : null}
            />
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="mt-6">
        <ProgressBar value={(done / steps.length) * 100} glow />
      </div>
    </GlassPanel>
  );
}
```

### Status text cycler (per agent):

```js
const STATUS_TEXTS = {
  intake: [
    "Receiving case data…",
    "Normalising fields…",
    "Extracting demographics…",
    "Validating structure…",
  ],
  dating_risk: [
    "Computing gestational age…",
    "Running Hadlock formula…",
    "Evaluating risk thresholds…",
    "Firing flags…",
  ],
  guideline: [
    "Loading antenatal ruleset…",
    "Checking compliance…",
    "Identifying missing investigations…",
    "Determining veto…",
  ],
  auditor: [
    "Reviewing guideline output…",
    "Cross-checking flags…",
    "Searching for contradictions…",
    "Preparing challenge…",
  ],
};

function getStatusText(agentId, elapsed) {
  const texts = STATUS_TEXTS[agentId] || ["Processing…"];
  const idx = Math.floor(elapsed / 1.5) % texts.length;
  return texts[idx];
}
```

---

## 4. STAGE TRANSITION CEREMONY

When results arrive, don't just swap components. Orchestrate an arrival:

### Sequence (staggered, 0.15s per stage):

```
t=0.0s   ProcessingTheatre fades out (opacity 1→0, scale 0.98)
t=0.2s   StageStructured slides in from bottom (y=40→0, opacity 0→1)
t=0.35s  StageAnalyzed slides in from bottom
t=0.50s  StageChecked slides in from bottom
t=0.65s  StageDecision or StageSealed slides in from bottom
```

Use `AnimatePresence` with `mode="wait"` between Processing and Results, then `FadeInStagger` for the result cards.

### Arrival indicator:

When results first appear, a subtle **"Review complete"** toast slides in from the top with a checkmark, then auto-dismisses after 2 seconds. Glass panel, teal glow.

---

## 5. HCI 2026 INTERACTION PATTERNS

### 5.1 Spatial Navigation

- Sidebar is a **persistent spatial anchor** — always present, always in the same position
- Main content scrolls independently
- Right panel is **contextually aware** — shows different content based on current stage:
  - During input: shows tips + shortcuts
  - During processing: shows live agent status
  - During results: shows Band room + audit

### 5.2 Haptic-Mirroring Visual Feedback

Every interactive element provides visual "haptic" feedback:

| Interaction      | Visual Response                              |
| ---------------- | -------------------------------------------- |
| Button press     | Scale 0.97 → 1.0 over 150ms (spring)         |
| Toggle switch    | Slide + color morph (200ms ease-out)         |
| Form field focus | Border glow expands (300ms)                  |
| Error state      | Border shake (2px amplitude, 3 oscillations) |
| Success state    | Brief green flash + check pulse              |
| Card hover       | Lift 2px + inner glow + shadow expand        |

### 5.3 Progressive Disclosure

- **Level 1 (always visible):** Case input form, submit button, demo cases
- **Level 2 (revealed on submit):** Agent pipeline, live status, elapsed time
- **Level 3 (revealed on complete):** Stage cards (structured → analyzed → checked → sealed)
- **Level 4 (revealed on demand):** JSON editor, audit log, Band room transcript

### 5.4 Ambient Intelligence

The interface communicates system state through ambient cues, not just explicit labels:

| State                        | Ambient Signal                                                 |
| ---------------------------- | -------------------------------------------------------------- |
| Idle, ready                  | Subtle teal glow on submit button, calm dark background        |
| Processing                   | Background pulses teal, progress bar fills, elapsed time ticks |
| Attention needed (escalated) | Amber accent appears, decision panel glows                     |
| Complete (sealed)            | Emerald glow, PDF download button pulses gently                |
| Error                        | Red flash, error bar slides in, affected fields highlight      |

### 5.5 Context-Aware Empty States

No dead space. Every empty area shows guidance:

| Area          | When Empty        | Shows                                                                |
| ------------- | ----------------- | -------------------------------------------------------------------- |
| Results panel | No case submitted | 3-step onboarding: "1. Paste notes → 2. Submit → 3. Review findings" |
| Band room     | No messages yet   | "Messages will appear here as agents coordinate through Band"        |
| Audit log     | No entries        | "Audit entries are recorded as the case progresses"                  |
| Case history  | First visit       | "Your reviewed cases will appear here"                               |

---

## 6. COMPONENT ARCHITECTURE

### New components needed:

| Component           | Purpose                                                         |
| ------------------- | --------------------------------------------------------------- |
| `GlassPanel`        | Foundational glass surface — replaces TexturePanel in dashboard |
| `ProcessingTheatre` | Animated agent ladder + progress + elapsed time                 |
| `AgentLadderNode`   | Single agent node in the vertical ladder                        |
| `ProgressBar`       | Animated gradient progress bar with glow                        |
| `ModeSwitch`        | Novice/Expert toggle in sidebar                                 |
| `CommandPalette`    | ⌘K command palette for expert mode                              |
| `OnboardingTour`    | 3-step guided overlay for first-time users                      |
| `StageTransition`   | Orchestrated stage arrival wrapper                              |
| `AmbientBackground` | State-driven background glow                                    |
| `Toast`             | Glass toast notification system                                 |

### Components to rewrite:

| Component           | Changes                                                                 |
| ------------------- | ----------------------------------------------------------------------- |
| `DashboardPage`     | Major: mode system, keyboard shortcuts, glass panels, stage transitions |
| `ProcessingOverlay` | Replace with ProcessingTheatre                                          |
| `SidebarNav`        | Add mode toggle, keyboard shortcut hints                                |
| `SmartPasteInput`   | Novice: prominent demo buttons. Expert: compact                         |
| `PatientForm`       | Novice: 6 fields only. Expert: full form                                |
| `ResultsStage`      | Add StageTransition wrapper, arrival animations                         |
| `LiveOutput`        | Context-aware content based on stage                                    |
| `EmptyState`        | Replace with context-aware 3-step onboarding                            |

---

## 7. NOVICE ONBOARDING FLOW

### First-visit experience (localStorage flag: `materna_onboarded`):

```
Step 1: "Welcome to Materna"
  ┌──────────────────────────────────────┐
  │  👋 Welcome to Materna               │
  │                                      │
  │  An AI-powered obstetric safety      │
  │  review system with a real doctor     │
  │  in the loop.                        │
  │                                      │
  │  [Get Started →]                     │
  └──────────────────────────────────────┘
  Spotlight: entire page dimmed except this card

Step 2: "Try a demo case"
  ┌──────────────────────────────────────┐
  │  📋 Try a demo case                  │
  │                                      │
  │  Click any demo to instantly load    │
  │  a pre-filled case. No typing needed.│
  │                                      │
  │  [C-0001: Pre-eclampsia]             │
  │  [C-0002: Normal pregnancy]          │
  │                                      │
  │  [Next →]                            │
  └──────────────────────────────────────┘
  Spotlight: highlights the demo case buttons

Step 3: "Submit and review"
  ┌──────────────────────────────────────┐
  │  🔍 Submit and review                │
  │                                      │
  │  Click "Submit to Review Board" to   │
  │  run all 4 AI agents. Results appear  │
  │  as cards below. The doctor reviews   │
  │  flagged cases.                      │
  │                                      │
  │  [Start Using Materna →]             │
  └──────────────────────────────────────┘
  Spotlight: highlights the submit button
```

---

## 8. EXPERT MODE FEATURES

### ⌘K Command Palette:

```
┌──────────────────────────────────────┐
│  ⌘K  Type a command…                 │
│  ─────────────────────────────────── │
│  ⚡ Submit case              ⌘↵     │
│  📋 Load demo case          ⌘D     │
│  🆕 New case                ⌘N     │
│  📝 Toggle JSON editor      ⌘E     │
│  🔍 Search cases…                   │
│  📦 Export all cases                │
│  🔐 Verify audit chain              │
│  ⚙️  Toggle Expert Mode             │
│  ❓ Keyboard shortcuts               │
└──────────────────────────────────────┘
```

### Keyboard shortcuts:

| Shortcut | Action                    |
| -------- | ------------------------- |
| `⌘↵`     | Submit case               |
| `⌘D`     | Load first demo case      |
| `⌘N`     | New case (clear all)      |
| `⌘E`     | Toggle JSON editor        |
| `⌘K`     | Open command palette      |
| `⌘.`     | Toggle right panel        |
| `Esc`    | Close modal/dismiss error |

---

## 9. RIGHT PANEL: CONTEXT-AWARE LIVE OUTPUT

The right panel adapts its content based on the current pipeline stage:

| Stage           | Panel Content                                            |
| --------------- | -------------------------------------------------------- |
| Input (no case) | Quick tips + keyboard shortcuts + health status          |
| Processing      | Live agent ladder (compact) + elapsed time               |
| ESCALATED       | Decision panel + proposed plan summary                   |
| SEALED          | Download packet button + audit summary + Band transcript |
| Error           | Error details + retry button                             |

---

## 10. IMPLEMENTATION ORDER

### Phase 1: Fix the "stuck" problem (highest priority)

1. `ProcessingTheatre.jsx` — animated agent ladder
2. `AgentLadderNode.jsx` — single node with status text
3. `ProgressBar.jsx` — animated glow progress bar
4. `GlassPanel.jsx` — foundational glass surface
5. Replace `ProcessingOverlay` in `DashboardPage`

### Phase 2: Stage transitions

6. `StageTransition.jsx` — orchestrated arrival wrapper
7. Update `ResultsStage` to use staggered arrivals
8. Add completion toast

### Phase 3: Novice/Expert modes

9. `ModeSwitch` + localStorage persistence
10. Novice-mode `SmartPasteInput` (prominent demos, simpler language)
11. Expert-mode features (⌘K palette, keyboard shortcuts)
12. Context-aware `LiveOutput`

### Phase 4: Onboarding + polish

13. `OnboardingTour` — 3-step guided overlay
14. State-driven `AmbientBackground`
15. Context-aware empty states
16. `Toast` notification system

---

## 11. FILE CHANGES SUMMARY

| File                                                | Action                                        |
| --------------------------------------------------- | --------------------------------------------- |
| `ui/src/components/ui/glass-panel.jsx`              | **NEW** — Foundational glass surface          |
| `ui/src/components/dashboard/ProcessingTheatre.jsx` | **NEW** — Animated processing                 |
| `ui/src/components/dashboard/AgentLadderNode.jsx`   | **NEW** — Ladder node                         |
| `ui/src/components/ui/progress-bar.jsx`             | **NEW** — Glow progress bar                   |
| `ui/src/components/dashboard/StageTransition.jsx`   | **NEW** — Arrival wrapper                     |
| `ui/src/components/dashboard/ModeSwitch.jsx`        | **NEW** — Novice/Expert toggle                |
| `ui/src/components/dashboard/CommandPalette.jsx`    | **NEW** — ⌘K palette                          |
| `ui/src/components/dashboard/OnboardingTour.jsx`    | **NEW** — First-visit guide                   |
| `ui/src/components/ui/toast.jsx`                    | **NEW** — Glass toast                         |
| `ui/src/pages/DashboardPage.jsx`                    | **REWRITE** — Mode system, glass, shortcuts   |
| `ui/src/components/dashboard/ProcessingOverlay.jsx` | **REPLACE** with ProcessingTheatre            |
| `ui/src/components/dashboard/SidebarNav.jsx`        | **UPDATE** — Mode toggle, shortcuts           |
| `ui/src/components/dashboard/SmartPasteInput.jsx`   | **UPDATE** — Novice layout                    |
| `ui/src/components/dashboard/PatientForm.jsx`       | **UPDATE** — Novice 6-field mode              |
| `ui/src/components/dashboard/ResultsStage.jsx`      | **UPDATE** — Stage transitions                |
| `ui/src/components/output/LiveOutput.jsx`           | **UPDATE** — Context-aware                    |
| `ui/src/components/dashboard/EmptyState.jsx`        | **REPLACE** — Context-aware                   |
| `ui/tailwind.config.js`                             | **UPDATE** — Glass tokens, ambient animations |

---

## 12. QUALITY GATES

After implementation, the dashboard must:

- [ ] Processing shows animated agent ladder with cycling status text
- [ ] Elapsed time counter ticks every 100ms during processing
- [ ] Progress bar fills smoothly from 0% to 100%
- [ ] Stage cards arrive with staggered animation, not instant pop-in
- [ ] Novice mode hides JSON editor and shows prominent demo buttons
- [ ] Expert mode has ⌘K command palette and keyboard shortcuts
- [ ] Right panel content changes based on pipeline stage
- [ ] Glass panels have backdrop-blur + subtle border + depth shadow
- [ ] Ambient background glow shifts with system state
- [ ] First visit shows 3-step onboarding tour
- [ ] No "stuck" perception — every 200ms something moves during processing
- [ ] Mobile: glass panels collapse gracefully, onboarding adapts
- [ ] `npm run dev` — no console errors

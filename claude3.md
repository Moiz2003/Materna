# 🎨 Landing Page v3 — Original Design Blueprint (claude3.md)

> **Why rewrite:** Claude's v2 is competent but generic. Every section is `FadeInStagger → card grid → icon + title + description`. That's AI slop. This spec defines 8 sections with 8 completely different layouts, 8 different animation strategies, and actual product substance.

---

## 0. ANTI-PATTERNS BANNED

These patterns appear in 90% of AI-generated landing pages. **None of them** appear in this design:

1. ❌ `FadeInStagger` + card grid (used in 6/8 sections in v2)
2. ❌ `icon + title + description` glass card (the entire internet)
3. ❌ `text-text-subtle uppercase tracking-widest` section label above every heading
4. ❌ Centered `max-w-* mx-auto text-center` on every section header
5. ❌ Gradient text in more than one place
6. ❌ Uniform 3-column or 4-column grids
7. ❌ Cards that all have the same height, border-radius, and padding
8. ❌ Static SVG icons as the only visual element

---

## 1. DESIGN HEURISTICS (per section)

| Section  | Layout Strategy                       | Animation Strategy                        | Visual Motif         |
| -------- | ------------------------------------- | ----------------------------------------- | -------------------- |
| Hero     | Full-viewport vertical stack          | Floating orbs + gradient-shift + counters | ECG wave, depth      |
| Problem  | Split-screen left/right               | Scroll-triggered reveal, not fade         | Red/amber urgency    |
| Pipeline | Horizontal flow with connecting lines | Sequential step illumination              | Data packets, arrows |
| Agents   | 5-step carousel (keep)                | Spring physics (keep)                     | Per-step color shift |
| Features | Bento grid — uneven cells             | Hover scale + glow, not expand            | Teal depth           |
| Safety   | Asymmetric 2-col + full-width banner  | Border-glow pulse on disclaimer           | Amber warning        |
| Privacy  | Timeline/stepper layout               | Numbered steps reveal sequentially        | Clean, minimal       |
| CTA      | Centered (one exception)              | GlowButton + subtle pulse                 | Confident, direct    |

**Rule:** No two adjacent sections use the same layout pattern. If section N is a grid, section N+1 must be horizontal flow or split-screen or bento.

---

## 2. SECTION 1: NAVIGATION (revised)

```
┌──────────────────────────────────────────────────────────────┐
│ [◎ Materna]   How It Works   Safety   About    [Dashboard →] │
└──────────────────────────────────────────────────────────────┘
```

- **Keep:** Sticky, `backdrop-blur-xl`, teal-400 logo
- **Change:** Rename "Features" → "How It Works" (matches anchor). Remove "Product".
- **Add:** Subtle `border-b border-border/0 → border-border/50` transition on scroll via `useScroll` + `useMotionValueEvent` — border fades in after 80px scroll

---

## 3. SECTION 2: HERO (already redesigned — KEEP)

The current [`HeroSection.jsx`](antenatal-review-board/ui/src/pages/sections/HeroSection.jsx) with DotGrid, FloatingOrbs, animated gradient heading, counter animations, and glass trust bar is solid. No changes needed.

**One addition:** Replace the static tagline "Four specialist agents. One human obstetrician." with a **typewriter cycling effect** that rotates through:

1. "Four specialist AI agents. One human obstetrician."
2. "Cryptographic proof of every decision."
3. "Zero real patient data. Ever."

Cycle every 3.5 seconds with a subtle cursor blink. Implementation: `useState` + `setInterval` + character-level reveal animation (or just fade-swap the whole phrase — simpler, cleaner).

---

## 4. SECTION 3: THE PROBLEM (split-screen redesign)

**Layout:** Two-column split. Left = statistics + narrative. Right = visual comparison.

```
┌──────────────────────────────────────────────────────────────────┐
│  THE PROBLEM                                                      │
│                                                                   │
│  ┌─────────────────────────┐  ┌────────────────────────────────┐ │
│  │                         │  │                                │ │
│  │  Every 2 minutes,       │  │  BEFORE          AFTER         │ │
│  │  a woman dies from      │  │  ┌────────┐  →   ┌──────────┐ │ │
│  │  preventable pregnancy  │  │  │Illegible│      │Structured│ │ │
│  │  complications.         │  │  │handwrit-│      │JSON with │ │ │
│  │                         │  │  │ing      │      │confidence│ │ │
│  │  186 / 100,000          │  │  └────────┘      │scores    │ │ │
│  │  maternal mortality     │  │                  └──────────┘ │ │
│  │  Pakistan, WHO 2023     │  │                                │ │
│  │                         │  │  "BP 150/98, urine protein    │ │
│  │  5-8% pre-eclampsia     │  │   2+, Hb 10.2, LMP uncertain" │ │
│  │  25% GA discordance     │  │  → Extracted in < 3 seconds   │ │
│  │  in LMP-based dating    │  │                                │ │
│  │                         │  │                                │ │
│  └─────────────────────────┘  └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Left column:**

- Three large stats with source citations
- Stats appear with a **count-up animation** (reuse `AnimatedCounter` from Hero)
- Red/amber accent for urgency

**Right column:**

- **Before/After comparison** — this is KEY product info Claude missed
- Left side: A dark box with messy, semi-legible text representing a handwritten note
- Right side: A clean, structured JSON preview with teal highlights
- Arrow or morph animation between them
- Below: Real example clinical note → structured output

**Animation:** Left column stats count up on scroll. Right column before/after uses a **horizontal slide reveal** — the "BEFORE" panel slides left, revealing the "AFTER" panel behind it.

---

## 5. SECTION 4: PRODUCT PIPELINE (NEW — Claude missed this entirely)

This is the centerpiece. Show the actual product working — not described, but visualized.

**Layout:** Horizontal pipeline with 5 nodes connected by animated arrows.

```
┌──────────────────────────────────────────────────────────────────┐
│  HOW A CASE FLOWS THROUGH MATERNA                                │
│                                                                   │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌─────┐│
│  │ INTAKE │───→│DATING &│───→│GUIDELINE│──→│AUDITOR │──→│SEAL ││
│  │        │    │  RISK  │    │        │    │        │    │     ││
│  │Extract │    │GA calc │    │Check   │    │Adversa-│    │Hash ││
│  │+ norm- │    │+ risk  │    │rules   │    │rial    │    │chain││
│  │alise   │    │flags   │    │+ veto  │    │review  │    │+ PDF││
│  └────────┘    └────────┘    └────────┘    └────────┘    └─────┘│
│       ▲             ▲             ▲             ▲           ▲     │
│       │             │             │             │           │     │
│    ┌──┴──────────┴──────────┴──────────┴──────────┴──────────┐  │
│    │              BAND ROOM (shared message bus)               │  │
│    │   Every handoff visible, auditable, hash-chained         │  │
│    └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ LIVE DEMO: [▶ Run C-0001]  Watch a real case process        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Implementation:**

- Five circular nodes in a horizontal row (wrapping on mobile to 3+2)
- Nodes connected by animated SVG lines with **flowing dash animation** (data packets)
- Each node has: icon, label, one-line description beneath
- **Sequential illumination:** On scroll into view, nodes light up one by one (0.3s stagger)
- The "BAND ROOM" bar spans the full width below — a shared message bus
- Below that: A small **"Live Demo"** callout that links to the dashboard

**Visual details:**

- Active node: `bg-teal-500/15 ring-2 ring-teal-500/40`
- Inactive node: `bg-bg-card border border-border`
- Connecting lines: SVG paths with `stroke-dasharray` + `stroke-dashoffset` animation
- Node icons: lucide-react `FileCheck`, `Activity`, `Shield`, `Search`, `Lock`

**Animation:** Each node reveals with `scale(0.8) → scale(1)` + `opacity 0 → 1`, staggered at 0.3s intervals. Connecting lines animate from 0 length to full length simultaneously.

---

## 6. SECTION 5: THE AGENTS (enhance existing AgentCarousel)

Keep the existing [`AgentCarousel`](antenatal-review-board/ui/src/components/effects/AgentCarousel.jsx) but add:

**Per-step code preview:** Below each agent's description, show a **small code snippet** (2-4 lines) that demonstrates the actual implementation:

| Step       | Code Preview                                    |
| ---------- | ----------------------------------------------- |
| Intake     | `_local_normalise(raw_case) → StructuredCase`   |
| Dating     | `ga_from_ultrasound("BPD", 24.5) → 23.1 weeks`  |
| Guideline  | `check_schedule(structured) → ComplianceResult` |
| Auditor    | `_should_challenge(flags, compliance) → bool`   |
| Human Gate | `must_escalate(flags, compliance) → True`       |

Each snippet in a `<pre>` block with `font-mono text-xs bg-bg-dark/60 rounded-md px-3 py-2`.

**This is product substance.** It shows the system is real code, not marketing vapor. The 13-line `must_escalate()` function is THE trust signal.

---

## 7. SECTION 6: FEATURES (bento grid redesign)

**Layout:** Asymmetric bento grid — cards of different sizes, not a uniform list.

```
┌──────────────────────────────────────────────────────────────────┐
│  FEATURES                                                         │
│                                                                   │
│  ┌────────────────────────────┐  ┌──────────────────────────┐    │
│  │                            │  │                          │    │
│  │  DETERMINISTIC SAFETY GATE │  │  SHA-256 AUDIT CHAIN     │    │
│  │                            │  │                          │    │
│  │  must_escalate() is a pure │  │  Every state transition  │    │
│  │  function — 13 lines.      │  │  is hash-chained. Edit   │    │
│  │  No LLM can bypass it.     │  │  one byte → chain breaks │    │
│  │  6 adversarial tests.      │  │  at exact position.      │    │
│  │                            │  │                          │    │
│  │  ┌──────────────────────┐  │  │  ┌────────────────────┐  │    │
│  │  │ def must_escalate(): │  │  │  │ seq|case|actor|..  │  │    │
│  │  │   return any(...)    │  │  │  │ SHA-256 → a1b2c3  │  │    │
│  │  │   or compliance.veto │  │  │  │ SHA-256 → d4e5f6  │  │    │
│  │  └──────────────────────┘  │  │  └────────────────────┘  │    │
│  └────────────────────────────┘  └──────────────────────────┘    │
│                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐  │
│  │ LANGUAGE     │ │ HUMAN FINAL  │ │ SEALED PDF PACKETS       │  │
│  │ FILTER       │ │ AUTHORITY    │ │                          │  │
│  │              │ │              │ │ Tamper-evident clinical   │  │
│  │ "diagnosis"  │ │ Dr. Saima    │ │ PDFs with final SHA-256  │  │
│  │ "indicates"  │ │ Javed holds  │ │ hash in footer.          │  │
│  │ "consistent" │ │ final say    │ │ ReportLab-generated.     │  │
│  │ → BLOCKED    │ │ on every case│ │                          │  │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  SMART EXTRACTION — English + Urdu handwriting             │  │
│  │  Gemini Vision → structured JSON with per-field confidence │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

**Implementation:**

- Use CSS Grid with `grid-template` for the bento layout:
  ```css
  grid-template:
    "gate     audit" auto
    "filter   human   pdf" auto
    "extract  extract extract" auto
    / 1fr 1fr 1fr;
  ```
- Card 1 (Deterministic Gate) + Card 2 (SHA-256 Audit): side by side, equal width, both tall
- Cards 3, 4, 5: three across, shorter
- Card 6 (Smart Extraction): full-width banner
- Each card has a different internal layout — not all `icon + title + description`
- Gate card shows actual code. Audit card shows a hash chain visualization with colored blocks.

**Animation:** On scroll into view, cards animate in with a **staggered scale reveal** — first the top row (gate + audit), then the middle row (filter + human + pdf), then the bottom banner. Each with `scale(0.92) → scale(1)` + `opacity 0 → 1`, 0.15s stagger.

**Hover effect:** Cards lift slightly (`translateY(-2px)`) and get an inner glow via `box-shadow: inset 0 1px 0 0 rgba(45,212,191,0.1)`.

---

## 8. SECTION 7: SAFETY & COMPLIANCE (keep layout, enhance content)

Keep the current 3-column grid + full-width amber disclaimer layout. It's actually good — varied enough from the bento above.

**Enhancements:**

- Add real test file references: "121 tests in [`tests/`](antenatal-review-board/tests/)" with clickable links to GitHub
- Add the "Tamper Demo" as an interactive element: a small button that says "Try tamper detection →" which links to the dashboard demo tamper endpoint
- The amber disclaimer card should have `animate-border-glow` (already in tailwind config) — border pulses amber slowly

---

## 9. SECTION 8: PRIVACY (timeline layout)

Replace the numbered list with a **vertical timeline/stepper**:

```
┌──────────────────────────────────────────────────────────────────┐
│  YOUR DATA, STEP BY STEP                                          │
│                                                                   │
│  ● INPUT                    ─────────────────────────────────    │
│  │  You paste clinical notes or upload an ultrasound.            │
│  │  Synthetic data only. No real PHI.                           │
│  ●                                                               │
│  │                                                               │
│  ● PROCESS                  ─────────────────────────────────    │
│  │  Data sent to AI/ML API for extraction.                      │
│  │  No data stored beyond API call duration.                    │
│  ●                                                               │
│  │                                                               │
│  ● STORAGE                  ─────────────────────────────────    │
│  │  Case state stored in-memory + local filesystem.             │
│  │  Not a production database. No cloud.                        │
│  ●                                                               │
│  │                                                               │
│  ● AUDIT                    ─────────────────────────────────    │
│  │  SHA-256 hash chain on every transition.                     │
│  │  Append-only JSONL. Tamper-evident.                          │
│  ●                                                               │
│  │                                                               │
│  ● DELETION                 ─────────────────────────────────    │
│  │  Remove files from data/state/ and audit_log/.               │
│  │  No cloud backup. No trace remains.                          │
│                                                                   │
│  Questions? moiz.info1010@gmail.com                              │
└──────────────────────────────────────────────────────────────────┘
```

**Implementation:**

- Vertical line (1px, border color) running down the left side
- Each step: a circle on the line + content to the right
- Active step (on scroll): circle fills teal, line before it fills teal
- Steps reveal one at a time as you scroll (IntersectionObserver)
- Minimal, clean — like Apple's privacy labels

---

## 10. SECTION 9: CTA (keep, minor enhance)

Current CTA is fine. Two small enhancements:

1. Add a subtle pulsing ring around the GlowButton (not the mouse-tracking glow — an additional `animate-ping-slow` ring)
2. Add "10 seconds · No sign-up · Synthetic data only" as microcopy below buttons

---

## 11. SECTION 10: FOOTER (keep as-is)

Current footer is solid. No changes needed.

---

## 12. NEW COMPONENTS NEEDED

| Component         | Location                                 | Purpose                    |
| ----------------- | ---------------------------------------- | -------------------------- |
| `AnimatedCounter` | Already in Hero                          | Reuse in Problem section   |
| `TypewriterText`  | `components/effects/TypewriterText.jsx`  | Cycling tagline in hero    |
| `PipelineFlow`    | `components/effects/PipelineFlow.jsx`    | Horizontal agent pipeline  |
| `BeforeAfter`     | `components/effects/BeforeAfter.jsx`     | Problem section comparison |
| `BentoGrid`       | `components/ui/bento-grid.jsx`           | Asymmetric feature grid    |
| `PrivacyTimeline` | `components/effects/PrivacyTimeline.jsx` | Vertical stepper           |

---

## 13. FILE CHANGES REQUIRED

| File                                          | Action                                                   |
| --------------------------------------------- | -------------------------------------------------------- |
| `ui/src/pages/sections/HeroSection.jsx`       | Minor: add typewriter tagline                            |
| `ui/src/pages/sections/ProblemSection.jsx`    | **FULL REWRITE** — split-screen                          |
| `ui/src/pages/sections/HowItWorksSection.jsx` | Enhance AgentCarousel with code snippets                 |
| `ui/src/pages/sections/FeaturesSection.jsx`   | **FULL REWRITE** — bento grid                            |
| `ui/src/pages/sections/SafetySection.jsx`     | Minor: add links + border glow                           |
| `ui/src/pages/sections/PrivacySection.jsx`    | **FULL REWRITE** — timeline                              |
| `ui/src/pages/sections/CTASection.jsx`        | Minor: ping ring + microcopy                             |
| `ui/src/pages/LandingPage.jsx`                | Add `<PipelineSection />` between Problem and HowItWorks |
| `ui/src/components/effects/AgentCarousel.jsx` | Add codePreview prop support                             |
| `ui/tailwind.config.js`                       | No changes needed (already has all keyframes)            |

---

## 14. IMPLEMENTATION ORDER

1. `PipelineFlow.jsx` — centerpiece, highest impact
2. `BeforeAfter.jsx` — problem section split
3. `ProblemSection.jsx` — rewrite with BeforeAfter
4. `BentoGrid` + `FeaturesSection.jsx` — feature bento
5. `PrivacyTimeline` + `PrivacySection.jsx` — timeline
6. `TypewriterText` + HeroSection enhancement
7. AgentCarousel code snippets
8. CTA + Safety polish

---

## 15. QUALITY BAR

After implementation, the landing page must pass:

- [ ] No two adjacent sections use the same layout pattern
- [ ] Every section has a unique animation strategy (not all FadeIn)
- [ ] Code snippets appear in at least 2 sections (gate + agents)
- [ ] Product demo/pipeline section exists and animates sequentially
- [ ] Before/After comparison in Problem section
- [ ] No `text-text-subtle uppercase tracking-widest` section labels — each section header is styled differently
- [ ] Bento grid has uneven card sizes
- [ ] Privacy section uses timeline, not cards
- [ ] Zero emoji in labels
- [ ] `npm run dev` — no console errors
- [ ] Mobile: pipeline stacks vertically, bento collapses to single column, split-screen stacks

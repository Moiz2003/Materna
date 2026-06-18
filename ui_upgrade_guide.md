# 🎨 UI Upgrade Guide — From AI-Generic → Custom UI/UX Team Quality

> **Goal:** Build a UI that looks like a 4-person design team made it, not a single developer with AI.
> **Time:** ~4 hours total. **Approach:** Design first, code second.

---

## WHY YOUR CURRENT UI LOOKS "AI-GENERATED"

Your [`ui/src/App.jsx`](antenatal-review-board/ui/src/App.jsx:1) has 6 problems that instantly signal "AI built this":

| Problem                                                           | Why It Screams "AI"                |
| ----------------------------------------------------------------- | ---------------------------------- |
| Single 900-line file, no components                               | No separation of concerns          |
| Inline styles (`const s = {...}` with function calls)             | No design system, no design tokens |
| Hardcoded hex colors (`#0e7490`, `#22d3ee`, `#ef4444`) everywhere | No brand identity                  |
| Zero motion or animation                                          | Static, dead feel                  |
| Only emoji for icons (📋🔬⚖️🕵️🩺)                                 | No custom iconography              |
| No routing — one giant page                                       | No information architecture        |

**The core issue:** You coded the UI the same way you'd code backend logic — in one file, with inline values, focused on functionality. UI/UX teams think in layers: identity → structure → components → polish. You skipped the first two.

---

## THE 3 LAYERS OF A PROFESSIONAL UI

Every polished UI has 3 layers. AI-generated UIs only have layer 3.

### Layer 1: Visual Identity (20 min — NO CODE)

Design decisions made BEFORE touching a single line of CSS:

- Color palette (derived from domain, not from defaults)
- Typography pairing (2-3 fonts with clear roles)
- Visual motifs (shapes, patterns, icon style)
- Spacing scale (consistent rhythm)

### Layer 2: Information Architecture (15 min — NO CODE)

What pages exist, what's on each page, how users navigate:

- Landing page (product story → convince)
- Dashboard (tool → use)
- About page (story → trust)

### Layer 3: Implementation (3 hours — CODE)

Translating layers 1+2 into React components, CSS, and assets.

**If you start coding before completing layers 1+2, you get an AI-looking UI. Period.**

---

## LAYER 1: VISUAL IDENTITY FOR ANTENATAL REVIEW BOARD

### Color Palette

Your domain is **obstetric healthcare + AI safety**. The palette must say "medical trust" not "tech startup."

```
PRIMARY — Medical Teal
  Base:    #0D9488  (bg-arb-teal, buttons, links, active states)
  Light:   #2DD4BF  (hover states, highlights, success tints)
  Subtle:  rgba(13, 148, 136, 0.15)  (card borders, subtle backgrounds)

ACCENT — Warning Amber
  Base:    #F59E0B  (risk flags, veto badges, attention states)
  Subtle:  rgba(245, 158, 11, 0.15)  (flag backgrounds)

DANGER — Escalation Red
  Base:    #DC2626  (veto, escalation, tampered audit)
  Subtle:  rgba(220, 38, 38, 0.12)  (danger backgrounds)

SUCCESS — Verified Green
  Base:    #059669  (compliant, sealed, verified)
  Subtle:  rgba(5, 150, 105, 0.12)  (success backgrounds)

BACKGROUNDS — Dark Clinical
  Darkest: #020617  (page background)
  Mid:     #0F172A  (card surfaces, panels)
  Surface: rgba(15, 23, 42, 0.60)  (glassmorphic overlays)

TEXT
  Primary: #F1F5F9  (headings, body text)
  Muted:   #94A3B8  (descriptions, secondary info)
  Subtle:  #64748B  (labels, placeholders)

BORDERS
  Default: #1E293B  (card borders, dividers)
  Hover:   #334155  (interactive borders)
```

**Why this palette works:**

- Teal ≠ blue. Everyone uses blue. Teal reads "medical" without being cold.
- Amber ≠ red. Risk flags in amber feel urgent but not alarming. Red is reserved for veto/escalation.
- The dark background gives a "review board war room" feel — serious, focused, professional.
- This palette is unique among hackathon submissions. Nobody else will have it.

### Typography

This is the #1 AI tell. AI always uses `-apple-system, sans-serif`. Choosing specific fonts signals design intent.

```
Headings: "Plus Jakarta Sans" — geometric, modern, distinctive
  → Google Fonts: https://fonts.google.com/specimen/Plus+Jakarta+Sans
  → Use for: h1, h2, h3, nav items, buttons

Body: "Inter" — highly readable, professional
  → Google Fonts: https://fonts.google.com/specimen/Inter
  → Use for: paragraphs, labels, form inputs

Mono: "JetBrains Mono" — code, hashes, technical data
  → Google Fonts: https://fonts.google.com/specimen/JetBrains+Mono
  → Use for: case IDs, SHA-256 hashes, code blocks, audit entries
```

Add to `index.html`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap"
  rel="stylesheet"
/>
```

### Visual Motifs

These are the repeating visual patterns that create brand recognition:

1. **Pulse waveform** — A subtle ECG-like line in hero sections. Medical domain cue.
2. **Concentric circles** — Like ultrasound rings. Use in loading states, empty states.
3. **Connected dots + lines** — Representing multi-agent coordination. Use in "How It Works."
4. **Shield shape** — Safety, verification, audit. Use near security claims.
5. **Diagonal accent lines** — Thin 1px diagonal stripes at 45°. Use as section dividers.

### Spacing Scale

Consistent spacing is invisible when done right, jarring when wrong. Use multiples of 4px:

```
xs:  4px   (tight: icon+label, inline badges)
sm:  8px   (compact: card padding between items)
md:  16px  (default: section padding, card internal)
lg:  24px  (breathing: between sections)
xl:  32px  (generous: hero padding, page margins)
2xl: 48px  (dramatic: between major page sections)
3xl: 64px  (hero top/bottom)
```

---

## LAYER 2: INFORMATION ARCHITECTURE

### Page 1: Landing (`/`) — The Product Page

**Goal:** A visitor understands what this is and why it matters in 10 seconds.

```
┌─────────────────────────────────────────────────────┐
│ [Logo]  About  How It Works          [Launch Demo] │  ← Sticky nav
├─────────────────────────────────────────────────────┤
│                                                     │
│  AI-Powered Obstetric Safety Review                 │  ← Hero headline (56px)
│  4 AI agents coordinate through Band.               │  ← Subhead (20px, muted)
│  A real gynecologist holds final authority.         │
│  Every decision is cryptographically sealed.        │
│                                                     │
│  [See It In Action ↓]    [Launch Dashboard →]       │  ← Dual CTA
│                                                     │
│  [Illustration: 4 agents → Band room → Human gate]  │  ← Custom visual
│                                                     │
├─────────────────────────────────────────────────────┤
│  28 Adversarial Tests  │  SHA-256 Audit  │  Real OB │  ← Trust bar (3 stats)
├─────────────────────────────────────────────────────┤
│                                                     │
│  HOW IT WORKS                                       │  ← Section heading
│                                                     │
│  [Intake] → [Dating] → [Guideline] → [Auditor]      │  ← 4 agent cards + arrows
│       ↓                                            │
│  [Human Gate: Dr. Saima Javed]                      │  ← Human card (highlighted)
│       ↓                                            │
│  [🔐 SHA-256 Sealed PDF]                            │  ← Output card
│                                                     │
├─────────────────────────────────────────────────────┤
│  WHY IT MATTERS                                     │
│                                                     │
│  [186/100k]  [5-8%]     [25%]      [Illegible]      │  ← Stats grid
│  Maternal    Pre-eclamp  GA dating   Handwritten    │
│  mortality   prevalence  discordance records        │
├─────────────────────────────────────────────────────┤
│  SAFETY ARCHITECTURE (4 columns)                    │
│  [Deterministic Gate] [SHA-256 Audit]               │
│  [Diag. Lang Filter]  [Human Final Authority]        │
├─────────────────────────────────────────────────────┤
│  Ready to see it in action?                         │
│  [Launch Dashboard →]                               │  ← Final CTA
├─────────────────────────────────────────────────────┤
│  Footer: Hackathon info · Track 3 · MIT License     │
└─────────────────────────────────────────────────────┘
```

### Page 2: Dashboard (`/dashboard`) — The Tool

**Goal:** A novice user can review a case in under 2 minutes without reading docs.

Key UX principle: **Guided workflow, not exposed complexity.**

```
┌──────────────────────────────────────────────────────┐
│ ← Home    Antenatal Review Board           [New Case] │
├─────────────────────────┬────────────────────────────┤
│  STEP 1: Enter Data     │  LIVE BAND ROOM            │
│  ┌───────────────────┐  │  ┌──────────────────────┐ │
│  │ [Smart Extract]   │  │  │ 🏠 Room: 7515812f... │ │
│  │ Paste clinical    │  │  │                      │ │
│  │ notes or upload   │  │  │ 📋 intake     posted │ │
│  │ an image.         │  │  │ 🔬 dating_risk found │ │
│  │                   │  │  │ ⚖️ guideline  checked│ │
│  │ Quick-load:       │  │  │ 🕵️ auditor    passed │ │
│  │ [C-0001 High Risk]│  │  │ ⚙️ orchestrator gate │ │
│  │ [C-0002 Clean]    │  │  │ 🩺 human      pending│ │
│  │ [C-0003 Borderline]│ │  │                      │ │
│  │ [C-0004 Severe]   │  │  └──────────────────────┘ │
│  └───────────────────┘  │                            │
│          ↓              │  PIPELINE STATUS           │
│  STEP 2: Review Data    │  ● RECEIVED                │
│  ┌───────────────────┐  │  ● STRUCTURED              │
│  │ Confidence flags  │  │  ● ANALYZED                │
│  │ for each field.   │  │  ● CHECKED                 │
│  │ Fix anything      │  │  ● AUDITED                 │
│  │ the AI was unsure │  │  ○ ESCALATED               │
│  │ about.            │  │                            │
│  └───────────────────┘  │  SHA-256 AUDIT TRAIL       │
│          ↓              │  #1 orchestrator received  │
│  STEP 3: Findings       │  #2 intake structured       │
│  ┌───────────────────┐  │  #3 dating_risk analysed   │
│  │ GA: 27.3 / 23.0  │  │  ...                       │
│  │ Discordance: 4.3 ⚠│  │                            │
│  │ Flags: PE-001(HIGH)│  │                            │
│  │        GDM-002(MOD)│  │                            │
│  │ Auditor: PASSED ✓ │  │                            │
│  └───────────────────┘  │                            │
│          ↓              │                            │
│  STEP 4: Decision       │                            │
│  ┌───────────────────┐  │                            │
│  │ 🩺 Human Review   │  │                            │
│  │ [Approve] [Override]│  │                            │
│  └───────────────────┘  │                            │
│          ↓              │                            │
│  STEP 5: Download       │                            │
│  ┌───────────────────┐  │                            │
│  │ 📄 Sealed PDF     │  │                            │
│  │ 🔨 Tamper Demo    │  │                            │
│  │ ✅ Audit VERIFIED │  │                            │
│  └───────────────────┘  │                            │
└─────────────────────────┴────────────────────────────┘
```

**Novice-friendly details:**

- Each step has a number and completion checkmark
- "Quick-load" demo cases eliminate the "what do I type?" barrier
- The Band room shows LIVE agent messages — this is your demo's centrepiece
- The Audit Trail proves every transition is logged
- Empty states show instructions, not just "Awaiting..."

### Page 3: About (`/about`) — Trust & Story

**Goal:** Humanize the project. Judges connect with stories, not specs.

```
┌──────────────────────────────────────────────────────┐
│  The Problem                                         │
│  In antenatal clinics, handwritten records,          │
│  overworked staff, and disconnected specialists      │
│  mean critical pregnancy risks go undetected.        │
│                                                      │
│  The Solution                                        │
│  4 AI agents + 1 human OB, coordinated through Band, │
│  with cryptographic proof of every decision.         │
│                                                      │
│  The Team                                            │
│  [Your photo/name] — Builder                        │
│  [Dr. Saima Javed] — Reviewing Obstetrician          │
│                                                      │
│  The Technology                                      │
│  Band · AI/ML API · Gemini Vision · SHA-256 Audit    │
│                                                      │
│  The 8 Golden Rules                                  │
│  1. Band is the only coordination layer              │
│  2. Escalation gate is deterministic (never an LLM)  │
│  3. Synthetic data only — zero real PHI              │
│  4. Decision-support framing throughout              │
│  5. Math & rules are code, not AI vibes              │
│  6. Every transition is SHA-256 audited              │
│  7. 28 adversarial hardening tests                   │
│  8. Secrets in .env only                             │
│                                                      │
│  The Hackathon                                       │
│  Band of Agents · Track 3: Regulated Workflows       │
│  Built June 2026                                     │
└──────────────────────────────────────────────────────┘
```

---

## LAYER 3: IMPLEMENTATION PLAN

### File Structure You'll Build

```
ui/src/
├── main.jsx                          # Entry point
├── App.jsx                           # Router setup only (~30 lines)
├── index.css                         # Design tokens + Tailwind theme
│
├── pages/
│   ├── LandingPage.jsx               # Product page (~250 lines)
│   ├── DashboardPage.jsx             # The tool (~400 lines)
│   └── AboutPage.jsx                 # Story page (~150 lines)
│
├── components/
│   ├── dashboard/
│   │   ├── StepEnterData.jsx         # Step 1: extract + quick-load
│   │   ├── StepReviewData.jsx        # Step 2: confidence review
│   │   ├── StepFindings.jsx          # Step 3: GA, flags, auditor
│   │   ├── StepDecision.jsx          # Step 4: human approve/override
│   │   └── StepDownload.jsx          # Step 5: PDF + audit + tamper
│   ├── band/
│   │   └── BandRoom.jsx              # Live agent message feed
│   ├── shared/
│   │   ├── Header.jsx                # Nav with logo + links
│   │   ├── Footer.jsx                # Hackathon footer
│   │   ├── ProgressBar.jsx           # Pipeline state indicator
│   │   ├── AuditTrail.jsx            # SHA-256 chain display
│   │   └── TreatmentPlanCard.jsx     # Plan display
│   └── effects/
│       ├── PulseWave.jsx             # ECG heartbeat animation
│       ├── ConcentricRings.jsx       # Ultrasound-like rings
│       └── GradientOrb.jsx           # Ambient background glow
│
└── assets/
    └── icons/
        ├── intake.svg                # Document + checkmark
        ├── dating-risk.svg           # Ruler + triangle
        ├── guideline.svg             # Shield + scale
        └── auditor.svg               # Magnifying glass
```

### Dependencies to Add

```bash
cd ui
npm install react-router-dom framer-motion lucide-react
```

- **react-router-dom** — 3 routes: `/`, `/dashboard`, `/about`
- **framer-motion** — page transitions, hover effects, pulse animation
- **lucide-react** — professional icon library (Stethoscope, Shield, FileCheck, Activity, etc.)

### Build Order (Most Visible First)

**Hour 1: Design tokens + Landing page**

1. Create `index.css` with the teal+amber color palette as CSS custom properties
2. Add Google Fonts to `index.html`
3. Build `LandingPage.jsx` — Hero, How It Works (4 agent cards), Stats, CTA
4. Build `Header.jsx` and `Footer.jsx`

**Hour 2: Dashboard page (the tool)** 5. Build `DashboardPage.jsx` — the 5-step guided workflow layout 6. Extract each step into its own component 7. Move existing App.jsx logic into these components 8. Build `BandRoom.jsx` — the live agent message feed

**Hour 3: About page + effects + polish** 9. Build `AboutPage.jsx` 10. Create custom SVG icons for the 4 agents 11. Add `PulseWave.jsx` animation to the Landing hero 12. Add page transitions with framer-motion 13. Test the full flow: Landing → Dashboard → Submit C-0001 → Watch agents → Approve → Download

### Custom SVG Icons (The #1 "Not AI" Signal)

Replace emoji (📋🔬⚖️🕵️) with these custom SVGs. Each icon uses the teal+amber palette:

**intake.svg** — Clipboard with checkmark (normalization):

```svg
<svg viewBox="0 0 48 48" fill="none">
  <rect x="8" y="4" width="32" height="40" rx="4" stroke="#2DD4BF" stroke-width="2"/>
  <line x1="16" y1="12" x2="32" y2="12" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="16" y1="18" x2="28" y2="18" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="16" y1="24" x2="24" y2="24" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M18 32L22 36L30 28" stroke="#059669" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

**dating-risk.svg** — Caliper + warning diamond (measurement + risk):

```svg
<svg viewBox="0 0 48 48" fill="none">
  <path d="M8 10V18M8 14H18M8 14L18 4" stroke="#2DD4BF" stroke-width="2" stroke-linecap="round"/>
  <path d="M30 4L40 20L30 36L20 20L30 4Z" stroke="#F59E0B" stroke-width="2" stroke-linejoin="round"/>
  <line x1="30" y1="18" x2="30" y2="22" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
  <circle cx="30" cy="26" r="1.5" fill="#F59E0B"/>
</svg>
```

**guideline.svg** — Shield with balance scale (compliance + rules):

```svg
<svg viewBox="0 0 48 48" fill="none">
  <path d="M24 4L6 12V22C6 31.94 14.39 41.04 24 44C33.61 41.04 42 31.94 42 22V12L24 4Z" stroke="#0D9488" stroke-width="2"/>
  <line x1="14" y1="22" x2="34" y2="22" stroke="#2DD4BF" stroke-width="2" stroke-linecap="round"/>
  <circle cx="24" cy="22" r="3" stroke="#2DD4BF" stroke-width="1.5"/>
  <path d="M18 30L30 30" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```

**auditor.svg** — Magnifying glass over document (investigation):

```svg
<svg viewBox="0 0 48 48" fill="none">
  <rect x="6" y="8" width="26" height="34" rx="3" stroke="#94A3B8" stroke-width="2"/>
  <line x1="12" y1="14" x2="24" y2="14" stroke="#64748B" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="12" y1="20" x2="22" y2="20" stroke="#64748B" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="12" y1="26" x2="18" y2="26" stroke="#64748B" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="34" cy="32" r="10" stroke="#F59E0B" stroke-width="2"/>
  <line x1="41" y1="39" x2="44" y2="44" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round"/>
</svg>
```

### Transition Animation (framer-motion)

Every page gets this entrance animation. It's 8 lines of code that transform the feel:

```jsx
import { motion } from "framer-motion";

function PageTransition({ children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, filter: "blur(8px)" }}
      animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      exit={{ opacity: 0, y: -40, filter: "blur(8px)" }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

### Pulse Wave Animation (Hero Section)

This is your domain-specific visual — a fetal ECG heartbeat line that draws itself:

```jsx
function PulseWave() {
  return (
    <svg viewBox="0 0 600 120" className="w-full max-w-2xl opacity-70">
      <defs>
        <linearGradient id="pulse" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#0D9488" stopOpacity="0.1" />
          <stop offset="50%" stopColor="#2DD4BF" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#0D9488" stopOpacity="0.1" />
        </linearGradient>
      </defs>
      <path
        d="M0 60 L150 60 L180 60 L195 15 L210 105 L225 30 L240 90 L260 60 L600 60"
        fill="none"
        stroke="url(#pulse)"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="animate-pulse"
      />
    </svg>
  );
}
```

---

## EXECUTION CHECKLIST

**Before writing any code:**

- [ ] Choose Plus Jakarta Sans + Inter + JetBrains Mono fonts
- [ ] Define teal+amber color palette
- [ ] Sketch the 3 pages on paper (even rough rectangles)
- [ ] Create the 4 custom SVG icons

**Hour 1:**

- [ ] `npm install react-router-dom framer-motion lucide-react`
- [ ] Create `index.css` with design tokens
- [ ] Build `App.jsx` with router
- [ ] Build `LandingPage.jsx` (hero + how-it-works + CTA)

**Hour 2:**

- [ ] Build `DashboardPage.jsx` layout
- [ ] Extract 5 step components from existing App.jsx logic
- [ ] Build `BandRoom.jsx`

**Hour 3:**

- [ ] Build `AboutPage.jsx`
- [ ] Add page transitions
- [ ] Add PulseWave to hero
- [ ] Test full flow end-to-end

**Hour 4 (if available):**

- [ ] Responsive mobile layout
- [ ] Keyboard accessibility (tab order, skip link)
- [ ] Meta tags for social sharing
- [ ] Deploy to ngrok/Railway

---

## THE DIFFERENCE THIS MAKES

| Before (current)                 | After (this guide)                                |
| -------------------------------- | ------------------------------------------------- |
| 1 file, 900 lines, inline styles | 15+ files, components, design tokens              |
| Emoji icons                      | 4 custom SVG icons                                |
| `#0e7490` / `#22d3ee` everywhere | `var(--arb-teal)` design tokens                   |
| No motion                        | Page transitions + pulse animation                |
| One giant page                   | 3 routed pages with clear purposes                |
| "Awaiting agent messages..."     | Guided step-by-step with empty state instructions |
| Hardcoded `192.168.18.183`       | `VITE_API_URL` env var                            |
| Cyberpunk hacker aesthetic       | Clinical trust + modern professional              |

Judges see dozens of submissions. The ones that win have a visual identity that feels intentional. This guide gives you exactly that — without AI generating the design for you.

# 🚀 Landing Page Revolution — Materna (claude2.md)

> Goal: A medical-SaaS landing page that looks like a $50M Series A company built it. Zero AI slop. Full HIPAA/privacy compliance display. Interactive "How It Works" animation sequence. Brand loyalty through consistent design signals.

---

## 1. RESEARCH: What Makes Medical SaaS Landing Pages Look Premium

Studied patterns from: Vanta, Suki AI, Nabla, Abridge, Glass Health, Athelas.

### The Medical SaaS Landing Page Formula:

```
Hero (value prop + trust signal)
  ↓
Problem/Stats (why this exists — make it visceral)
  ↓
How It Works (animated interactive sequence — NOT static cards)
  ↓
Feature Deep-Dive (expandable detailed sections)
  ↓
Safety & Compliance (HIPAA, data handling, synthetic data, "no PHI")
  ↓
Privacy Policy (clear, human-readable, NOT legalese wall)
  ↓
Trust Bar (stats, certifications, hackathon badges)
  ↓
CTA (prominent, confident)
  ↓
Footer (links, legal, copyright)
```

### Anti-Slop Rules:

1. **Never use emoji as section markers** — use numbered steps or lucide-react icons
2. **Never use gradient text in more than ONE place** (hero only)
3. **Never use `text-[9px]` or `text-[11px]`** — minimum 13px for body, 15px for headings
4. **Never stack generic cards** — each section has a unique layout, not repeating card grids
5. **Never use "✨🚀🤖🔒" as features** — write actual descriptions
6. **Never use lorem ipsum or placeholder stats** — real WHO/ACOG data only

---

## 2. COLOR & BRAND SIGNALING (Consistency = Trust)

### Primary Palette (Medical Trust):

```
Teal-600 (#0D9488)  — Primary CTA, active states, links
Teal-400 (#2DD4BF)  — Highlights, hover states, accents
Teal-500/10         — Card backgrounds, subtle borders
```

### Accent Palette (Urgency + Positivity):

```
Amber-500 (#F59E0B) — Risk indicators, warnings, "attention" badges
Amber-500/10        — Flag backgrounds
Emerald-600 (#059669) — Success states, "compliant", "verified", "sealed"
Red-600 (#DC2626)   — Veto, escalation, tampered audit (sparingly)
```

### Neutral Palette:

```
Slate-950 (#020617) — Page background
Slate-900 (#0F172A) — Card surfaces
Slate-800 (#1E293B) — Borders, dividers
Slate-400 (#94A3B8) — Body text
Slate-300 (#CBD5E1) — Headings
White (#F1F5F9)     — High-emphasis text
```

### Brand Signal Rules:

1. Teal = Materna's brand color. Used on: logo, nav, primary CTAs, section accents
2. Amber = ONLY used for risk/attention. Never on positive elements.
3. Emerald = ONLY used for success/completion/verified states.
4. Never mix teal and amber in the same gradient on non-hero text
5. The brand logo uses concentric circles (ultrasound motif) — use this shape language in section dividers and loading states

---

## 3. PAGE SECTIONS (In Order)

### SECTION 1: NAVIGATION BAR

```
┌─────────────────────────────────────────────────────────┐
│ [◎ Materna]     Product  Safety  About     [Launch App] │
└─────────────────────────────────────────────────────────┘
```

- Sticky, glass-morphism background (`bg-bg-dark/80 backdrop-blur-xl`)
- "Launch App" is the ONLY teal button — everything else is muted text
- Logo uses the concentric circle SVG (already built)
- On scroll: nav gets a bottom border

---

### SECTION 2: HERO

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  [Track 3: Regulated Workflows badge]                   │
│                                                         │
│  AI-Powered Obstetric Safety Review                     │
│  Four specialist agents. One human OB.                  │
│  Cryptographic proof of every decision.                 │
│                                                         │
│  [Launch Dashboard →]  [See How It Works ↓]             │
│                                                         │
│  [PulseWave ECG animation — already built]              │
│                                                         │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │28 Tests  │SHA-256   │ Real OB  │ Synthetic Data   │ │
│  │Passed    │Verified  │in Loop   │No Real PHI       │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- Hero heading: 56px Plus Jakarta Sans, weight 800
- Subheading: 20px Inter, slate-400
- Trust bar: 4 stat cards in a row, subtle border-top/bottom
- CTA: GlowButton component (already built) with mouse-tracking glow

---

### SECTION 3: THE PROBLEM (Why This Exists)

```
┌─────────────────────────────────────────────────────────┐
│  Every 2 minutes, a woman dies from preventable         │
│  pregnancy complications.                               │
│                                                         │
│  In antenatal clinics across Pakistan, handwritten      │
│  records, overworked staff, and disconnected            │
│  specialists mean critical risks go undetected.         │
│                                                         │
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │   186    │  5-8%    │   25%    │   Illegible      │ │
│  │ /100k    │          │          │                  │ │
│  │ Maternal │ Pregnanc-│ GA disco-│ Handwritten      │ │
│  │mortality │ies with  │rdance in │ records =        │ │
│  │(Pakistan│ pre-ecla-│ LMP-based│ missed flags     │ │
│  │ WHO 2023)│mpsia     │ dating   │                  │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

- Section heading: "The Problem" in text-subtle, uppercase, tracking-wider
- Main stat: 56px bold, teal-400
- Sub-stats: 4-column grid with large numbers + small labels
- Sources cited (WHO 2023, ACOG, Hadlock et al.) — builds credibility

---

### SECTION 4: HOW IT WORKS (Interactive Animated Sequence)

```
┌─────────────────────────────────────────────────────────┐
│  HOW IT WORKS                                           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │                    STEP 1/5                       │  │
│  │                                                  │  │
│  │  📋 Intake Agent                                 │  │
│  │  ┌────────────────────────────────────────────┐ │  │
│  │  │ Paste clinical notes or upload an image.    │ │  │
│  │  │ AI extracts and normalizes the data.        │ │  │
│  │  │ Supports English and Urdu handwriting.      │ │  │
│  │  └────────────────────────────────────────────┘ │  │
│  │                                                  │  │
│  │  [●] [○] [○] [○] [○]  ← Step indicators        │  │
│  │                                                  │  │
│  │  [← Previous]              [Next →]              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**This is THE key section.** NOT static cards. An interactive step-by-step walkthrough:

**Implementation:**

- Use the AgentCarousel pattern (already built at `components/effects/AgentCarousel.jsx`)
- 5 steps: Intake → Dating & Risk → Guideline → Auditor → Human Gate + Seal
- Each step shows: agent icon (lucide-react), agent name, description, visual diagram
- Step indicators: animated dots that fill as you progress
- Auto-advances every 5 seconds (pause on hover)
- Manual navigation: Previous/Next buttons + dot click
- Background: subtle animated gradient that shifts color per step (teal → amber → teal → amber → green)

**Visuals per step:**

- Step 1 (Intake): Document icon → structured form visual
- Step 2 (Dating & Risk): Ruler/caliper icon → GA comparison chart
- Step 3 (Guideline): Shield icon → YAML ruleset visual
- Step 4 (Auditor): Magnifying glass → "challenge" animation
- Step 5 (Human Gate): Stethoscope icon → sealed packet visual

---

### SECTION 5: FEATURE DEEP-DIVE

```
┌─────────────────────────────────────────────────────────┐
│  FEATURES                                               │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🔒 Deterministic Safety Gate                     │   │
│  │                                                 │   │
│  │ The escalation decision is a pure function. No   │   │
│  │ LLM can bypass it. 6 adversarial tests prove it. │   │
│  │                                                 │   │
│  │ [Expand →]                                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🔐 SHA-256 Cryptographic Audit                   │   │
│  │                                                 │   │
│  │ Every state transition is hash-chained. Tamper   │   │
│  │ any entry and verification fails instantly.      │   │
│  │                                                 │   │
│  │ [Expand →]                                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [4 more feature cards: Diagnostic Filter, Human        │
│   Authority, Smart Extraction, Sealed PDF Packets]      │
└─────────────────────────────────────────────────────────┘
```

- Use ExpandablePanel component (already built) for each feature
- Collapsed: title + one-line description
- Expanded: detailed explanation + technical detail + link to relevant test

---

### SECTION 6: SAFETY & COMPLIANCE

```
┌─────────────────────────────────────────────────────────┐
│  SAFETY & COMPLIANCE                                    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🏥 SYNTHETIC DATA ONLY                           │   │
│  │ This system uses fabricated/anonymized data.     │   │
│  │ Zero real patient health information (PHI) ever  │   │
│  │ enters the system. All demo cases are synthetic.  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ⚕️ DECISION-SUPPORT — NOT DIAGNOSTIC             │   │
│  │ All AI output is labeled "decision-support       │   │
│  │ only." The human obstetrician holds final         │   │
│  │ authority on every flagged case. No autonomous    │   │
│  │ clinical decisions are made by AI.               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🔒 DATA HANDLING                                 │   │
│  │ • No PHI processed or stored                     │   │
│  │ • SHA-256 audit chain for all state transitions  │   │
│  │ • Tamper-evident sealed PDF packets              │   │
│  │ • Secrets in .env only, never committed          │   │
│  │ • 28 adversarial hardening tests                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ⚠️ NOT HIPAA CERTIFIED (HACKATHON PROJECT)       │   │
│  │ This is a hackathon demonstration project. It    │   │
│  │ has NOT undergone HIPAA certification, FDA       │   │
│  │ review, or any regulatory approval. Do NOT use   │   │
│  │ with real patient data. For demonstration only.  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

### SECTION 7: PRIVACY POLICY

```
┌─────────────────────────────────────────────────────────┐
│  PRIVACY & DATA POLICY                                  │
│                                                         │
│  This is a hackathon demonstration project. Here's      │
│  exactly what happens with your data:                   │
│                                                         │
│  1. INPUT: You paste clinical notes or upload an        │
│     ultrasound image. This data is synthetic only.      │
│                                                         │
│  2. PROCESSING: The data is sent to AI/ML API           │
│     (model provider) and Gemini Vision for extraction   │
│     and analysis. No data is stored by these providers  │
│     beyond the duration of the API call.                │
│                                                         │
│  3. STORAGE: Case state is stored in-memory and on      │
│     the local filesystem (data/state/, audit_log/).     │
│     This is NOT a production database.                  │
│                                                         │
│  4. AUDIT: Every state transition is recorded in a      │
│     SHA-256 hash-chained JSONL file. This is append-    │
│     only and tamper-evident.                            │
│                                                         │
│  5. DELETION: Cases can be deleted by removing the      │
│     corresponding files from data/state/ and            │
│     audit_log/. No cloud backup exists.                 │
│                                                         │
│  6. NO PHI: We do not process, store, or transmit       │
│     real Protected Health Information. The system       │
│     refuses to accept real patient identifiers.         │
│                                                         │
│  Questions? Contact: [your email]                       │
└─────────────────────────────────────────────────────────┘
```

- Plain English, not legalese
- Numbered steps for clarity
- Honest about hackathon/demo status
- Contact information

---

### SECTION 8: TRUST BAR

```
┌─────────────────────────────────────────────────────────┐
│  ┌──────────┬──────────┬──────────┬──────────────────┐ │
│  │🏆 Track 3│🤖 4 Agents│🩺 Real OB│🔐 132 Tests     │ │
│  │Regulated │via Band  │in the    │Passing          │ │
│  │Workflows │          │Loop      │                 │ │
│  └──────────┴──────────┴──────────┴──────────────────┘ │
│                                                         │
│  Built for Band of Agents Hackathon · June 2026         │
│  Tech: Band · AI/ML API · Gemini Vision · FastAPI       │
└─────────────────────────────────────────────────────────┘
```

---

### SECTION 9: FINAL CTA

```
┌─────────────────────────────────────────────────────────┐
│  Ready to see 4 AI agents review a case in 5 seconds?   │
│                                                         │
│  [🚀 Launch Dashboard →]    [📖 Read the Technical      │
│                              Audit →]                   │
└─────────────────────────────────────────────────────────┘
```

- GlowButton for primary CTA (already built)
- Secondary link to TECHNICAL_AUDIT.md

---

### SECTION 10: FOOTER

```
┌─────────────────────────────────────────────────────────┐
│  Materna · Band of Agents Hackathon 2026                │
│  Track 3: Regulated & High-Stakes Workflows             │
│                                                         │
│  Built by Abdul Moiz Ahmed                              │
│  Clinical Review: Dr. Saima Javed                       │
│                                                         │
│  Product  ·  Safety  ·  Privacy  ·  GitHub  ·  Contact  │
│                                                         │
│  © 2026 Materna. MIT License.                           │
│  Synthetic data only. Not for clinical use.             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. ANIMATION SPECIFICATIONS

### Hero:

- PulseWave ECG animation (already built) — keep
- Trust bar stats animate in with count-up effect

### How It Works (Interactive):

- AgentCarousel pattern (already built)
- Step transition: spring physics `{ stiffness: 300, damping: 25, mass: 0.5 }`
- Background color shifts per step using `AnimatePresence`
- Step dots: width animates from 8px to 24px on active

### Features (Expandable):

- ExpandablePanel component (already built)
- Spring height animation on expand/collapse
- Content fades in with 0.15s stagger per child

### Scroll Animations:

- FadeIn + FadeInStagger components (already built)
- `viewport: { once: true, margin: "0px 0px -100px" }`
- No animation on mobile (respect `prefers-reduced-motion`)

---

## 5. COMPONENT TREE

```
pages/
  LandingPage.jsx              ← FULL REWRITE
    sections/
      HeroSection.jsx          ← Hero + trust bar + PulseWave
      ProblemSection.jsx       ← Stats + visceral problem statement
      HowItWorksSection.jsx    ← Interactive 5-step agent walkthrough
      FeaturesSection.jsx      ← Expandable feature deep-dive
      SafetySection.jsx        ← Compliance + HIPAA disclaimer
      PrivacySection.jsx       ← Plain-English privacy policy
      TrustSection.jsx         ← Hackathon badges + tech stack
      CTASection.jsx           ← Final CTA
      FooterSection.jsx        ← Footer
    components/effects/
      GlowButton.jsx           ← ALREADY BUILT
      AgentCarousel.jsx        ← ALREADY BUILT (refine for 5 steps)
      PulseWave.jsx            ← Move from LandingPage inline
    components/ui/
      TexturePanel.jsx         ← ALREADY BUILT (use for feature cards)
      GradientHeading.jsx      ← ALREADY BUILT (hero heading only)
      FadeIn.jsx               ← ALREADY BUILT
      ExpandablePanel.jsx      ← ALREADY BUILT (feature cards)
```

---

## 6. CLAUDE PROMPT (Paste into Claude Code)

```
You are building a premium medical-SaaS landing page for "Materna" —
an AI-powered obstetric safety review system. The current landing page
at ui/src/pages/LandingPage.jsx works but looks like AI slop (emoji
everywhere, generic card grid, no compliance section, no interactive
walkthrough).

Read these files first for context:
- ui/src/pages/LandingPage.jsx (current page to replace)
- ui/src/ARCHITECTURE_PLAN.md (design tokens available)
- ui/src/components/ui/texture-panel.jsx (compound card component)
- ui/src/components/ui/gradient-heading.jsx
- ui/src/components/ui/fade-in.jsx
- ui/src/components/ui/expandable-panel.jsx
- ui/src/components/effects/GlowButton.jsx
- ui/src/components/effects/AgentCarousel.jsx

DESIGN PRINCIPLES:
1. No emoji in UI labels — use lucide-react icons
2. Gradient text ONLY in the hero heading — nowhere else
3. Minimum text size: 13px body, 15px headings
4. Every section has a UNIQUE layout — no repeating card grids
5. Teal = brand. Amber = risk/attention. Emerald = success. Never mix.
6. Real data only: WHO 2023, ACOG, Hadlock et al. citations

BUILD THESE 8 SECTION COMPONENTS (all in ui/src/pages/sections/):

1. HeroSection.jsx — Full-width hero with:
   - GradientHeading for "AI-Powered Obstetric Safety Review"
   - Subhead: "Four specialist agents. One human OB. Cryptographic proof."
   - Two GlowButton CTAs: "Launch Dashboard" + "See How It Works"
   - Inline PulseWave SVG animation below
   - 4-column trust bar: "28 Tests Passed | SHA-256 Verified | Real OB | Synthetic Data"
   - Use FadeIn with staggered delays for each element

2. ProblemSection.jsx — Visceral problem statement with:
   - Large stat: "186/100k maternal mortality (Pakistan, WHO 2023)"
   - 4 stat cards: 186/100k, 5-8% PE prevalence, 25% GA discordance, illegible records
   - Two-sentence narrative about Pakistani antenatal clinics
   - FadeInStagger for stat cards

3. HowItWorksSection.jsx — Interactive 5-step walkthrough:
   - Use AgentCarousel pattern but with 5 specific steps:
     Step 1: Intake (FileCheck icon) — "Paste notes or upload image. AI extracts data."
     Step 2: Dating & Risk (Activity icon) — "Computes GA, detects discordance, fires flags."
     Step 3: Guideline (Shield icon) — "Checks against antenatal ruleset. Vetoes if needed."
     Step 4: Auditor (Search icon) — "Adversarially challenges the Guideline agent."
     Step 5: Human Gate (Stethoscope icon) — "Dr. Saima Javed approves or overrides."
   - Spring physics: { stiffness: 300, damping: 25, mass: 0.5 }
   - Auto-advance every 5s, pause on hover
   - Previous/Next buttons + dot indicators
   - Background subtly shifts color per step

4. FeaturesSection.jsx — Expandable feature cards using ExpandablePanel:
   - "Deterministic Safety Gate" — pure function, 6 tests prove it
   - "SHA-256 Cryptographic Audit" — tamper detection, hash chain
   - "Diagnostic Language Filter" — AI output screened for diagnostic claims
   - "Human Final Authority" — real OB holds final decision
   - "Smart Extraction" — English + Urdu, confidence scoring
   - "Sealed PDF Packets" — tamper-evident, cryptographically verified
   Each card: collapsed shows title + one-liner, expanded shows detail

5. SafetySection.jsx — Compliance display:
   - Card 1: "Synthetic Data Only" — no PHI, all demo cases fabricated
   - Card 2: "Decision-Support — Not Diagnostic" — all AI output labeled
   - Card 3: "Data Handling" — SHA-256 audit, .env secrets, no cloud storage
   - Card 4: "⚠️ Not HIPAA Certified" — honest hackathon disclaimer
   Use TexturePanel variant="amber" for the disclaimer card

6. PrivacySection.jsx — Plain-English privacy policy:
   - 6 numbered steps explaining data flow
   - Honest about hackathon/demo status
   - Contact email
   Use TexturePanel with simple numbered list

7. CTASection.jsx — Final call-to-action:
   - Heading: "Ready to see 4 AI agents review a case?"
   - GlowButton "Launch Dashboard" + secondary link to TECHNICAL_AUDIT.md

8. FooterSection.jsx — Footer:
   - Materna branding, hackathon info, builder name
   - Links: Product, Safety, Privacy, GitHub, Contact
   - Disclaimer: "Synthetic data only. Not for clinical use."

REWRITE LandingPage.jsx to import and compose all 8 sections in order.

DO NOT:
- Use emoji in labels
- Use text-[9px] or text-[11px] — minimum 13px
- Use generic card grids for every section
- Use gradient text outside the hero
- Change any API calls or routing logic

The result should look like a $50M medical AI startup's landing page.
```

---

## 7. VERIFICATION CHECKLIST

After Claude builds this, verify:

- [ ] Landing page loads at `/`
- [ ] All 8 sections render
- [ ] How It Works auto-rotates through 5 steps
- [ ] Expand/collapse works on feature cards
- [ ] No emoji in labels (only lucide-react icons)
- [ ] No text smaller than 13px
- [ ] Gradient text only in hero heading
- [ ] Navigation links work (About, Dashboard)
- [ ] CTA buttons navigate to /dashboard
- [ ] Footer links are correct
- [ ] Mobile responsive (test at 375px width)
- [ ] `npm run dev` shows no console errors

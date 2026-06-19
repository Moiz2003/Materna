# 🏗️ Architecture Plan — Faithful Cult-UI Refactor for Materna

> Status: MCP research complete (7 components studied). Ready for implementation.
> Pattern: Compound components with React Context — the cult-ui secret sauce.

---

## 1. THE COMPOUND COMPONENT PATTERN (The Cult-UI DNA)

Every cult-ui component follows this exact architecture. We will replicate it faithfully:

```jsx
// 1. forwardRef — always accept ref
const MyComponent = React.forwardRef(({ className, children, ...props }, ref) => (
  <div ref={ref} className={cn("base-styles", className)} {...props}>
    {children}
  </div>
))
MyComponent.displayName = "MyComponent"

// 2. Sub-components as dot-notation exports
const MyComponentHeader = React.forwardRef(...)
MyComponentHeader.displayName = "MyComponentHeader"

export { MyComponent, MyComponentHeader }
export default MyComponent
```

**Key principles:**

- Every component accepts `className` for composability
- Uses `cn()` (clsx + tailwind-merge) for class merging
- Compound sub-components accessed via `MyComponent.Header`
- Context used ONLY when shared state is needed (Expandable, FloatingPanel)
- Spring physics from framer-motion: `{ stiffness: 300, damping: 25, mass: 0.5 }`

---

## 2. COMPONENT ADAPTATIONS — EXACT 1:1 MAPPING

### 2.1 `TexturePanel` (adapted from `texture-card.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/texture-card.tsx`
**Materna usage:** Every card panel in Dashboard + Landing

```jsx
// File: ui/src/components/ui/texture-panel.jsx
// Compound: TexturePanel, TexturePanel.Header, TexturePanel.Title,
//           TexturePanel.Description, TexturePanel.Content, TexturePanel.Footer

<TexturePanel>
  <TexturePanel.Header>
    <TexturePanel.Title>GA Metrics</TexturePanel.Title>
    <TexturePanel.Description>
      LMP vs Ultrasound dating
    </TexturePanel.Description>
  </TexturePanel.Header>
  <TexturePanel.Content>{/* content */}</TexturePanel.Content>
  <TexturePanel.Footer>{/* actions */}</TexturePanel.Footer>
</TexturePanel>
```

**Adaptation:** Replace cult-ui's zinc/white theme with Materna's teal/amber. Keep the 4-layer nested border pattern (rounded-[24px]→[23px]→[22px]→[21px]). Add `variant` prop: `"default"` | `"amber"` | `"danger"` | `"success"` for color-coded panels (PE flag card, veto card, etc.).

---

### 2.2 `ExpandablePanel` (adapted from `expandable-card.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/expandable-card.tsx`
**Materna usage:** Case findings sections that expand/collapse (GA details, flag evidence, auditor report)

```jsx
// Context-driven expand/collapse with spring height animation
<ExpandablePanel defaultExpanded={false}>
  <ExpandablePanel.Trigger>
    <TexturePanel.Title>Risk Flags (3)</TexturePanel.Title>
  </ExpandablePanel.Trigger>
  <ExpandablePanel.Content>
    {/* flag details show/hide with spring animation */}
  </ExpandablePanel.Content>
</ExpandablePanel>
```

**Adaptation:** Keep the `useExpandable()` context hook, spring height animation via `useSpring(animatedHeight, springConfig)`, and `AnimatePresence` for content. Reduce cult-ui's 16.5KB to ~5KB by removing unused presets (fade, slide-_, rotate, blur-_).

---

### 2.3 `FadeIn` / `FadeInStagger` (adapted from `fade-in.tsx`)

**Cult-UI source:** `apps/www/components/animate/fade-in.tsx`
**Materna usage:** All page sections — replace manual `motion.div` wrappers

```jsx
// Context-based stagger — child FadeIn components auto-animate in sequence
<FadeInStagger>
  <FadeIn>
    <TexturePanel>Card 1</TexturePanel>
  </FadeIn>
  <FadeIn>
    <TexturePanel>Card 2</TexturePanel>
  </FadeIn>
  <FadeIn>
    <TexturePanel>Card 3</TexturePanel>
  </FadeIn>
</FadeInStagger>
```

**Adaptation:** Copy almost verbatim. Add `delay` prop. Keep `useReducedMotion()` for accessibility. The `FadeInStaggerContext` pattern is elegant — child components detect they're in a stagger group and skip their own `viewport` trigger.

---

### 2.4 `GlowButton` (adapted from `glow-button.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/glow-button.tsx`
**Materna usage:** CTA buttons on Landing page + Dashboard "Submit" button

Already built at [`components/effects/GlowButton.jsx`](antenatal-review-board/ui/src/components/effects/GlowButton.jsx:1) — needs refinement:

- Add `glowColor` prop (default: teal `#2DD4BF` for primary, amber `#F59E0B` for warning)
- Add `variant` prop: `"primary"` | `"secondary"` | `"danger"`
- Add `size` prop: `"sm"` | `"md"` | `"lg"`
- Replace SVG arrow with `lucide-react` `ArrowRight`

---

### 2.5 `AgentCarousel` (adapted from `feature-carousel.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/feature-carousel.tsx` (21KB)
**Materna usage:** How It Works section on Landing — auto-rotating agent showcase

Already built at [`components/effects/AgentCarousel.jsx`](antenatal-review-board/ui/src/components/effects/AgentCarousel.jsx:1) — needs refinement:

- Add `useNumberCycler` hook (3.5s auto-advance, pause on hover)
- Add spring animation presets: `{ stiffness: 300, damping: 25, mass: 0.5 }`
- Keep TextureCard nested-border on each slide
- Keep step dot indicators

---

### 2.6 `ShiftCard` (adapted from `shift-card.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/shift-card.tsx`
**Materna usage:** Status indicator cards in Dashboard (RECEIVED→STRUCTURED→ANALYZED cards)

```jsx
<ShiftCard
  topContent={<Activity size={16} />}
  topAnimateContent={<span>ANALYZED</span>}
  middleContent={<span>3 flags found</span>}
  bottomContent={<span>PE-001 HIGH · GDM-002 MODERATE · ANE-003 MODERATE</span>}
/>
```

**Adaptation:** Hover expands card to show detailed status. Uses `AnimatePresence` to swap between `topContent`/`middleContent` (collapsed) and `topAnimateContent`/`bottomContent` (expanded). Spring physics on height: `{ from 38px to 194px }`.

---

### 2.7 `GradientHeading` (adapted from `gradient-heading.tsx`)

**Cult-UI source:** `apps/www/registry/default/ui/gradient-heading.tsx`
**Materna usage:** Hero heading on Landing, section titles

Already partially applied in LandingPage. Needs full adaptation:

- Create `ui/src/components/ui/gradient-heading.jsx`
- `cva` variants for `size` (xs/sm/md/lg/xl) and `variant` (teal/amber/teal-amber/light)
- Replace cult-ui's neutral zinc colors with Materna's teal/amber palette

---

## 3. FILE STRUCTURE (What We'll Build)

```
ui/src/components/ui/           # Compound component library (new)
├── texture-panel.jsx           # TexturePanel + sub-components
├── expandable-panel.jsx        # ExpandablePanel (context-driven)
├── gradient-heading.jsx        # GradientHeading (cva variants)
├── fade-in.jsx                 # FadeIn + FadeInStagger

ui/src/components/effects/      # Effects (refine existing)
├── GlowButton.jsx              # (refine: add variants/sizes)
└── AgentCarousel.jsx           # (refine: add useNumberCycler)

ui/src/pages/                   # Pages (replace inline with components)
├── LandingPage.jsx             # (replace manual cards with TexturePanel)
└── DashboardPage.jsx           # (replace glass divs with TexturePanel + ExpandablePanel)

ui/src/utils/
└── cn.js                       # (new) clsx + tailwind-merge utility
```

---

## 4. IMPLEMENTATION ORDER (3 Phases)

### Phase A: Foundation (20 min)

- Create `ui/src/utils/cn.js` — `export function cn(...inputs)`
- Create `ui/src/components/ui/texture-panel.jsx` — compound component with 4-layer nested borders, teal/amber/danger/success variants
- Create `ui/src/components/ui/gradient-heading.jsx` — cva variants
- Create `ui/src/components/ui/fade-in.jsx` — FadeIn + FadeInStagger

### Phase B: Dashboard Refactor (30 min)

- Replace all `.glass` divs in DashboardPage with `<TexturePanel>` compound components
- Add `<ExpandablePanel>` to GA metrics, risk flags, and auditor challenge sections
- Replace manual `motion.div` with `<FadeIn>` + `<FadeInStagger>`
- Refine GlowButton with variants

### Phase C: Landing Refactor (20 min)

- Replace manual cards in LandingPage with `<TexturePanel>`
- Replace manual motion wrappers with `<FadeInStagger>`
- Refine AgentCarousel with `useNumberCycler`

---

## 5. THE cn() UTILITY (Required by All Components)

```js
// ui/src/utils/cn.js
export function cn(...inputs) {
  return inputs.filter(Boolean).join(" ");
}
```

Minimal — cult-ui uses `clsx` + `tailwind-merge`. We'll start simple and add `clsx` later.

---

## 6. SWITCH TO CODE MODE

Ready to implement. Switch to Code mode and I'll build all 6 new component files + refactor both pages.

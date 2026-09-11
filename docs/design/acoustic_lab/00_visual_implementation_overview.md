# HydroSIM Acoustic Lab — Visual Implementation Overview

Status: **canonical design implementation brief — iterative**

This directory translates the canonical pedagogy in `docs/pedagogy/acoustic_lab/` into production-facing visual and interaction instructions for `web/pedagogical-explorer/`.

The pedagogical treatise remains authoritative for **what the learner must understand**. The Scientific Core/API remains authoritative for **what is physically/numerically true**. These design briefs define **how the learner should see, manipulate and recognize those relationships in production**.

## Work split

- **UX-A:** D1–D8 — wave, pulse/signal processing, sonar budget, refraction, physical array, beamforming/steering, SBES×MBES, bottom detection.
- **UX-B:** D9–D17 — multisector, vessel/sensors, motion, PU integration, timing, sounding formation, planning, coverage/trade-offs, uncertainty.

Do not swap ownership casually. Each range has a deliberate visual continuity.

## Production stack — use what already exists

The production frontend currently provides:

- React 19 (`react`, `react-dom`)
- TypeScript 7
- Vite 8
- `motion` 13 via `motion/react`
- `lucide-react`
- Playwright

There is **no charting library** in `package.json`. Do not add Recharts, D3, Plotly, Three.js, ECharts, Chart.js or another dependency merely to draw a graph that native SVG can express. A new library requires a concrete benefit that native React + SVG + Motion cannot provide.

### Preferred React primitives

Use:

- `useState` for learner-controlled UI state;
- `useEffect` for API requests, shared language event listeners and cleanup;
- `useMemo` only for presentation transforms/mappings derived from already-authoritative API output;
- `useRef` for direct pointer interaction, measured containers or animation anchors when necessary;
- `useId` for SVG `clipPath`, `mask`, `linearGradient`, marker or filter IDs;
- `onChange` for ordinary sliders/selects;
- `onPointerDown` / `onPointerMove` / `onPointerUp` for direct geometric manipulation where drag interaction teaches the concept better than a slider.

Do **not** reproduce scientific equations in TypeScript when the API/Core already owns them. Converting API values into screen coordinates is presentation logic and is allowed; deriving new physics is not.

### Preferred visual primitives

Use responsive native SVG as the default scientific graphics layer:

```tsx
<svg viewBox="0 0 1000 420" preserveAspectRatio="xMidYMid meet">
  <path />
  <polyline />
  <line />
  <circle />
  <rect />
  <text />
</svg>
```

For line charts, map API samples into a stable `viewBox` and render `path`/`polyline`. Keep scientific axis domains fixed/shared whenever the pedagogy says autoscaling would hide the effect.

For spatial scenes, prefer one connected SVG scene rather than many disconnected charts/cards when the causal chain is geometric.

For repeated channel/beam/sounding marks, render arrays with `.map(...)`; use a stable key from channel/beam/sector/sounding identity, not array index when an authoritative ID exists.

### Motion

Import:

```tsx
import { AnimatePresence, motion } from 'motion/react';
```

Use `motion.g`, `motion.path`, `motion.circle`, `motion.div` or `motion.line` for learner-visible changes that encode physical meaning. Prefer short transitions (`0.15–0.45 s`) for parameter response and longer continuous loops only for inherently continuous phenomena such as vessel motion or wave propagation.

Use Motion for:

- interpolation between reference/current geometry;
- moving TX/RX wavefronts;
- delay alignment;
- vessel DOF animation;
- timeline shifts;
- highlighting causal response after a control changes.

Do not animate geometry in a way that implies false physics. Honor `prefers-reduced-motion` and provide a static-but-complete state.

### Icons

Use `lucide-react` only for navigation, reset, reveal/advanced, comparison, timing or generic instrument affordances. Do not use icons as substitutes for the scientific visualization.

### CSS

Prefer one lab-specific stylesheet beside the lab source. Use CSS custom properties for family accent and stable semantic roles. Avoid deeply nested card-on-card styling. Use `container-type:inline-size` / container queries where useful, otherwise responsive grid/flex layouts.

Scientific plots should reflow before they introduce horizontal scrollbars. Scrolling is acceptable for long navigation lists, not as the default solution for a scientific graphic.

## Shared visual contract

Every lab must read visually as:

```text
CAUSE / CONTROL
      ↓
PHYSICAL OR SIGNAL MECHANISM
      ↓
OBSERVABLE CONSEQUENCE
      ↓
HYDROGRAPHIC CONSEQUENCE
```

The user should be able to hide most explanatory prose and still understand what changed.

### Layout hierarchy

Default desktop target:

```text
┌───────────────────────────────────────────────────────────┐
│ global HydroSIM lesson shell                             │
├───────────────┬───────────────────────────────────────────┤
│ primary       │                                           │
│ controls      │     dominant scientific visualization     │
│               │                                           │
│ Advanced ▸    │                                           │
├───────────────┴───────────────────────────────────────────┤
│ concise consequence / comparison / diagnostic strip      │
└───────────────────────────────────────────────────────────┘
```

Use 1–3 primary learner controls whenever possible. Put secondary variables in `<details>` / progressive disclosure only when their effect is already supported and visible.

### Reference/current comparison

When comparison is central, render both states in the **same geometry and scale**:

- reference: thin/dashed/low-emphasis ghost;
- current: higher-emphasis solid mark;
- difference: explicit vector, delta or changed footprint where meaningful.

Do not create two unrelated charts merely to say “before” and “after”.

### Text policy

Keep learner-facing text concise. Do not expose implementation vocabulary such as:

- `canonical`
- `Configured`
- `Derived`
- `Python Scientific Core`
- `API response`

Preserve text needed for units, signs, coordinate frames, warnings, scientific interpretation and accessibility.

### Localization

All visible labels, annotations, legends, axis labels and contextual help must follow the shared EN/PT-BR language state (`hydrosim-language` session key + `hydrosim-language-change` event). Do not add a second language button inside a lab.

### API / loading behavior

Do not let a successful value jump back to placeholder while a new request is in flight. Keep last valid data visible and use a subtle updating state.

For rapid sliders, preserve current debounce/abort patterns where present. Prefer `AbortController` and a short debounce only when the API needs it; never debounce purely local presentation state.

### Validation

Each visual revision must add/update focused Playwright coverage for the changed learner contract. At minimum verify:

1. the primary control is operable;
2. the dominant visualization changes;
3. a central consequence/readout changes when expected;
4. reset restores the reference state;
5. EN/PT-BR labels remain synchronized with the global shell;
6. no stale old chrome or obsolete explanatory label is required by tests.

Run from `web/pedagogical-explorer/`:

```powershell
npm run build
npm run test:ui
```

For focused Playwright work use the relevant spec directly, e.g.:

```powershell
npx playwright test tests/<lab>.spec.ts
```

Do not weaken tests merely to make a redesign pass. Update them to assert the new learner-visible contract.

## Completion criterion for a visual brief

A lab is visually implementation-ready when its design file states:

- dominant scene / image mental model;
- layout zones;
- primary controls and progressive-disclosure controls;
- exact SVG/chart/scenario to build;
- required Motion/interaction behavior;
- reference/current treatment where relevant;
- key React components/hooks/events;
- learner-visible outputs;
- implementation boundaries against the pedagogy/science;
- minimum Playwright assertions.

These briefs are implementation instructions, not permission to change the pedagogy or Scientific Core.
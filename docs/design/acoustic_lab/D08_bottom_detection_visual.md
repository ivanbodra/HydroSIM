# D8 — Bottom Detection — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D08_bottom_detection.md`  
Production source: `web/pedagogical-explorer/src/BottomDetectionLab.tsx`

## Dominant visual mental model

The learner must experience a detector making an evidence-based estimate, not see a bar chart that magically becomes a sounding:

```text
received field
  -> amplitude evidence + differential-phase evidence
  -> candidate / support / quality decision
  -> ONE retained conventional (t, theta)
  -> optional richer phase exploitation
  -> additional valid detections inside the SAME receive-beam support
```

The recognisable image of D8 must be a **signal microscope connected to a seafloor footprint**. The same selected evidence is highlighted in time/phase and projected spatially below.

## Production boundary first

Preserve `/api/v1/pedagogical/bottom-detection` as authority. Current `BottomDetectionLab.tsx` already consumes correlation, candidates, eligibility, retained detections, classifications and High Density output. Do not move detector decisions into React.

Current limitations matter:

- the UI scenario arrays and Truth lag arrays are still frontend fixtures;
- current phase-zero-crossing may return `unsupported`;
- the current High Density request uses fixed phase-support arrays;
- the current response type does not expose a synchronized `differential_phase(t)` trace, phase support/fit, or beam×time matrix.

Therefore implement the conventional amplitude experience now, preserve API-backed High Density spatial output, and **gate the full phase-ramp / BDI / PDI views on authoritative API fields**. Do not draw a decorative phase ramp, zero crossing, matrix, or `delta-phi -> theta` conversion.

## Layout and hierarchy

Desktop:

```text
+----------------------+--------------------------------------------------+
| CONTROLS             | DETECTION MICROSCOPE                             |
| scenario             | amplitude A(t) + gate + threshold + candidates   |
| method               | [phase trace occupies same x scale when backed]  |
| gate / threshold     |                                                  |
| More                 | FOOTPRINT / SEAFLOOR PROJECTION                  |
| retention / advanced | one retained conventional point                  |
| reset                | + enhanced points in same parent support         |
+----------------------+--------------------------------------------------+
| compact evidence strip: tA | tphi | retained | quality/support | count |
+-------------------------------------------------------------------------+
```

Use approximately `250–300px / minmax(0,1fr)`. The microscope must receive most of the viewport. On narrow screens stack controls above stage; never horizontally scroll the scientific SVG.

## React decomposition

Keep the fetch/state owner in `BottomDetectionLab.tsx`. Refactor presentation only when useful:

```tsx
<DetectionControls />
<DetectionMicroscope>
  <AmplitudeTrace />
  <PhaseTrace />          // only with authoritative samples
  <GateOverlay />
  <DetectionMarkers />
</DetectionMicroscope>
<FootprintProjection />
<DetectionEvidenceStrip />
<AdvancedDetectionView /> // API-gated BDI/PDI later
```

Use:

- `useState` for learner controls and local selected evidence;
- existing `useEffect` + `AbortController` for API refresh and language event;
- `useMemo` for SVG presentation paths, fixed-domain coordinate transforms and classification lookup;
- `useId` for SVG clip-path/mask ids if clipping is required;
- `useRef` only if pointer-to-SVG coordinate mapping becomes necessary;
- `onChange` for sliders/selects;
- `onPointerDown` on a candidate marker only for **selection/inspection**, never to create a detection that the API did not return.

## Controls

Primary, always visible:

1. **Echo / scene scenario**;
2. **Detection method** — Amplitude / Phase only when supported;
3. **Detection gate** — start/end;
4. **Threshold / quality criterion** with semantics matching the API.

The gate should visually support direct manipulation. Keep the sliders for accessibility, but allow two SVG gate handles to move the same `windowStartUs` / `windowEndUs` state with pointer events.

Progressive disclosure `More / Mais`:

- TX delay — timing-reference experiment only;
- steering / selected beam;
- single/multiple retention;
- High Density / enhanced mode;
- later BDI/PDI selector when backed.

Reset remains visible.

Do not let TX delay dominate the first screen.

## Dominant SVG — Detection microscope

Replace the current sample-height `<div>` chart with one responsive native SVG:

```tsx
<svg
  viewBox="0 0 1000 520"
  preserveAspectRatio="xMidYMid meet"
  aria-label={...}
>
```

Use a fixed/shared horizontal time domain for amplitude and phase. The current `WINDOW_MIN_US` / `WINDOW_MAX_US` may define the presentation domain while the API remains authoritative for samples.

### Amplitude band

Render the API `correlation.lag_us` + normalized magnitude as a continuous `<path>` / `<polyline>`, not bars. Use presentation-only mapping helpers:

```ts
mapTimeUsToX(...)
mapNormalizedAmplitudeToY(...)
```

Draw:

- gate as `<rect>` spanning selected time interval;
- threshold as horizontal `<line>`;
- candidates as `<circle>` / short vertical `<line>`;
- eligible candidates with one visual state;
- retained conventional candidate with the strongest state;
- rejected eligible candidates visibly different from below-threshold samples;
- Truth only when the teaching overlay is explicitly enabled.

The learner must be able to distinguish:

```text
physical echo != candidate != eligible != retained != Truth
```

### Phase band

When the Core/API exposes actual differential-phase samples and support:

- draw `delta_phi(t)` as `<path>` on exactly the same time x-domain;
- render valid-support interval as a bounded background region;
- show zero line;
- show API-provided fitted ramp only if provided or derivable from explicitly registered Core coefficients;
- mark API-provided zero crossing / `t_phi`;
- visibly suppress/unavailable-state the phase solution when support/coherence fails.

Until those fields exist, use a compact explicit `Phase evidence unavailable in current scientific contract` state. **Do not synthesize `HIGH_DENSITY_PHASE` into the conventional phase plot.**

## Conventional competition

When both `t_A` and `t_phi` eventually exist, show both candidates on the shared time axis, but render exactly one **Retained** conventional marker according to the API selector. Never project both as two conventional soundings merely because both estimators exist.

A small connector can link the retained marker to the spatial point below:

```tsx
<motion.path d={connectorPath} ... />
```

Motion is explanatory only; the connector may briefly draw after a detector change. It must not imply acoustic propagation.

## Footprint / seafloor projection

Create a second SVG scene or lower band sharing the visual stage:

- transducer / selected RX look direction;
- one parent receive-beam support / footprint;
- simple seabed line/shape supplied by scenario when authoritative;
- conventional retained point;
- High Density points from `high_density.detections[].local_bottom_point_m`.

Use `<path>`, `<line>`, `<circle>`, `<text>`.

The parent footprint must remain unchanged when High Density is enabled. Animate only the additional point markers with `AnimatePresence` / `motion.circle` so the learner sees:

```text
same support + more valid detections
```

not:

```text
more detections = more beams
```

Do not use opacity as a power proxy.

## Advanced phase / High Density transition

When the API exposes per-sample phase-to-angle mapping, the best transition is:

1. freeze one coherent phase ramp;
2. highlight the conventional zero crossing -> one point;
3. reveal additional valid phase samples;
4. connect each API-backed `(t_i, delta_phi_i)` to `(t_i, theta_i)`;
5. project those points inside the same parent footprint.

Use `motion.g` / `motion.path` only to trace these causal correspondences. Keep the physical beam static.

## BDI / PDI matrix — API-gated

Do not implement a fake matrix from screen-space interpolation. Once the Scientific Core returns a beam×time amplitude/phase field, render a native SVG matrix:

```tsx
<g className="beam-time-matrix">
  {cells.map(cell => <rect ... />)}
</g>
```

Required interactions:

- vertical cursor = fixed beam -> time-series;
- horizontal cursor = fixed time -> angle-series;
- synchronized amplitude / phase layer switch;
- selected row/column highlighted without rescaling;
- PDI candidates come only from Core output.

If cell count later makes native SVG demonstrably too slow, document that evidence before proposing Canvas. Do not add a chart library pre-emptively.

## Motion language

Use `motion/react` for:

- 150–250 ms gate-handle / retained-marker transitions;
- brief causal connector from retained signal evidence to spatial detection;
- `AnimatePresence` for High Density point reveal/removal;
- optional support-region emphasis when phase validity changes.

Never animate a decorative traveling echo unless the time semantics are explicitly tied to the API data.

## Styling / responsive behaviour

Suggested CSS:

```css
.d8-layout {
  display: grid;
  grid-template-columns: minmax(240px, 290px) minmax(0, 1fr);
  gap: clamp(12px, 2vw, 24px);
}
.d8-stage { min-width: 0; }
.d8-microscope { width: 100%; aspect-ratio: 1000 / 520; }
@media (max-width: 820px) {
  .d8-layout { grid-template-columns: 1fr; }
}
```

No nested chart scrollbars. Progressive controls may expand vertically below the primary controls.

## Language / accessibility

Reuse global `hydrosim-language-change`; no local language switch. Provide concise SVG `aria-label` summarizing active method, gate, retained count and High Density state. Candidate markers that are pointer-selectable must also be keyboard reachable through an adjacent semantic list/button representation; do not make raw SVG circles the only accessible control.

## Current-code changes to prioritize

1. Rename CSS namespace away from current `d9-*` to D8-specific classes while preserving behaviour.
2. Replace bar-like sample divs with the synchronized SVG microscope.
3. Make scenario/method/gate/threshold visually primary; demote TX delay and steering.
4. Keep existing API candidate/eligibility/retention/classification semantics.
5. Project existing API High Density points inside one unchanged parent support.
6. Show explicit scientific-contract unavailable states for phase-ramp/BDI/PDI instead of decorative approximations.

## Do not do

- no React phase-to-angle equation;
- no decorative phase ramp or zero crossing;
- no two conventional soundings from amplitude + phase candidates;
- no High Density as extra beams, narrower footprint or wider coverage;
- no BDI/PDI generic enhancement-filter metaphor;
- no TPU/uncertainty scoring here;
- no full coordinate transformation; D14 owns sounding formation.

## Minimum Playwright assertions

1. Changing gate start/end changes SVG gate geometry and the API-backed retained state where the scenario warrants it.
2. Threshold change changes candidate/eligible/retained visual state without changing the fixed time domain.
3. Amplitude method renders API correlation as an SVG path and marks the retained candidate.
4. Unsupported phase method shows an explicit unavailable state and does not render a fabricated phase curve.
5. Enabling High Density adds API-returned spatial points while parent footprint geometry remains identical.
6. Conventional retained count remains distinct from High Density added count.
7. Reset restores reference controls and detection state.
8. Global EN/PT-BR switch updates labels without local language control.

When authoritative phase/BDI/PDI fields land, extend focused tests to zero-crossing/support validity, one-retained conventional competition, fixed-beam/time-series and fixed-time/angle-series matrix cuts.

## Validation commands

From `web/pedagogical-explorer`:

```bash
npm run build
npx playwright test tests/bottom-detection*.spec.ts
```

Use the exact existing focused spec filename if it differs. Run:

```bash
npm run test:ui
```

only as the integration gate after the focused D8 checks pass.

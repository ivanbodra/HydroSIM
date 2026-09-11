# D16 — Survey Coverage & Acquisition Trade-offs — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D16_survey_coverage_tradeoffs.md`  
Production source: `web/pedagogical-explorer/src/TradeoffLab.tsx`  
Scientific contract: `docs/science/ped_d17_coverage_density_contract.md`

## Dominant visual mental model

D16 must look like a **moving acquisition strip**, not a wall of settings and metric cards.

The learner should see four different things in one physical coordinate system:

```text
where acoustic footprints touched
where retained soundings landed
how those samples are spaced / distributed
how fast the survey progresses
```

The visual must make this inequality impossible to miss:

```text
INSONIFIED COVERAGE != SOUNDING DENSITY != RESOLUTION != EFFICIENCY
```

The signature image of D16 is a short top-down local survey strip: vessel/ping origins along `+x`, across-track `+y`, finite footprint support for several pings, retained soundings, gaps and merged coverage. High Density adds points **inside existing support** without widening the covered region.

## Scientific boundary

Keep the current API chain in `TradeoffLab.tsx`:

- `/api/v1/pedagogical/echosounders`;
- `/api/v1/pedagogical/multisector`;
- `/api/v1/pedagogical/bottom-detection`;
- `/api/v1/pedagogical/survey-density`.

The `survey-density` response is authoritative for speed conversion, ping spacing/density, actual retained across-track spacings, finite-footprint union, gaps, covered width, along-track gap state and High Density counts.

Do not replace those outputs with React formulas. The current local survey frame remains:

```text
+x = along-track
+y = Starboard
```

Do not mix this frame with D8/D9 beam-angle sign conventions.

## Layout

Desktop:

```text
+----------------------+--------------------------------------------------+
| GUIDED CONTROLS      | ACQUISITION STRIP                                |
| 1 speed              | top-down local x/y physical scene                |
| 2 ping rate          | ping origins + finite support + soundings        |
| 3 distribution       | gaps/merged coverage directly visible            |
| 4 footprint          |                                                  |
| 5 High Density       |                                                  |
| More / upstream      |                                                  |
+----------------------+--------------------------------------------------+
| COVERAGE | DENSITY | RESOLUTION | EFFICIENCY — compact evidence rail    |
+-------------------------------------------------------------------------+
| optional Baseline × Current comparison on the SAME scales               |
+-------------------------------------------------------------------------+
```

Use `grid-template-columns:minmax(240px,300px) minmax(0,1fr)`. On narrow screens stack controls above stage. Never horizontally scroll the acquisition scene.

## Guided control hierarchy

Primary sequence, always visible:

1. vessel speed;
2. effective ping rate;
3. beam count / beam-spacing mode;
4. registered RX beamwidth / footprint geometry;
5. High Density on/off.

Secondary `More / Mais`:

- depth;
- angular sector;
- ordinary multiple-detection mode;
- multisector/TX sequence;
- frequency and pulse only if their current API-backed consequence is intentionally being inspected.

Do not present all current controls with equal visual weight. Keep `Use current as baseline`, `Restore baseline`, and Reset available but visually secondary to the causal controls.

## React decomposition

Keep orchestration/fetching in `TradeoffLab.tsx`. Presentation can move to small local components:

```tsx
<TradeoffControls />
<AcquisitionStrip>
  <SurveyTrack />
  <PingOrigins />
  <FootprintSupport />
  <CoverageUnion />
  <SoundingPattern />
  <GapAnnotations />
</AcquisitionStrip>
<ConceptEvidenceRail />
<BaselineComparison />
```

Use:

- existing `useState` for settings/baseline;
- existing `useEffect` + `AbortController` for API updates;
- `useMemo` for presentation geometry from API outputs, fixed-scale extents and baseline/current overlays;
- `useId` for clip-path ids if footprint rendering needs clipping;
- `useRef` only if later direct inspection maps pointer coordinates into the local survey frame;
- `onChange` for controls;
- `onPointerDown` on a sounding/footprint only for selection/inspection, never to alter scientific geometry directly.

## Dominant SVG — acquisition strip

Use native SVG, for example:

```tsx
<svg
  viewBox="0 0 1100 620"
  preserveAspectRatio="xMidYMid meet"
  aria-label={...}
>
```

The coordinate transform is presentation-only:

```ts
surveyXToSvg(alongTrackM)
surveyYToSvg(starboardM)
```

Derive screen extents from a **stable reference envelope** capable of containing baseline and allowed/current states. Do not autoscale independently after every control change; otherwise speed/gap/swath changes become visually invisible.

### Survey track and ping origins

Render the vessel trajectory as a longitudinal `<line>` / `<path>`. Generate displayed ping-origin positions from the authoritative `along_track_ping_spacing_m` for a small fixed number of illustrative pings, e.g. 4–6 rows. This repetition is presentation geometry using the Core-provided spacing, not a second cadence model.

Use `<circle>` or a compact vessel glyph at the active origin. `lucide-react` may provide a small control icon but must not be the scientific vessel/coverage scene.

When speed or ping rate changes, animate ping-row positions with `motion.g` over ~200–300 ms. This motion means **changed spatial spacing**, not vessel speed animation.

### Finite footprint support

Use the API `coverage.footprint_intervals` as the authoritative across-track support for one ping. Replicate that support at each illustrative ping origin.

If the Core exposes only 1-D across-track intervals plus along-track footprint/gap values, render support as explicit idealized local rectangles/capsules whose across-track boundaries come from the intervals and whose along-track length comes only from an authoritative footprint-length field. If no authoritative along-track footprint length is exposed in the response, do **not** invent one; render across-track support bands at ping rows and label along-track continuity from the API classification separately.

Use `<rect>` / `<path>` with outline and subtle fill. Opacity indicates layer separation only, not acoustic power.

### Merged coverage and gaps

Render `merged_coverage_intervals` distinctly from geometric beam-centre extent. Internal gaps from `internal_gap_intervals` must remain visibly empty and receive explicit width brackets when selected.

Never fill from first beam centre to last beam centre and call it coverage.

Use:

- `<rect>` / `<path>` for merged covered intervals;
- `<line>` + ticks + `<text>` for gap widths;
- a separate thin bracket for `geometric_beam_center_swath_width_m` if shown.

The learner must be able to see a wide geometric swath with internal acoustic-support gaps.

### Sounding pattern

Plot retained bottom positions from the canonical echosounder/bottom-detection responses. Across-track positions must preserve actual spacing; do not use `swath / beamCount`.

For High Density, add only API-returned points. Use `AnimatePresence` + `motion.circle` for the added points while keeping all footprint/coverage paths geometrically unchanged.

This is the critical visual invariant:

```text
High Density OFF -> N retained points, coverage C
High Density ON  -> N+k retained points, SAME coverage C
```

Expose a testable `data-coverage-geometry` or stable SVG path/rect attributes so Playwright can assert that invariant.

## Four-concept evidence rail

Beneath the scene, use four compact columns, not four competing dashboard cards:

### Coverage

- classification: continuous/gapped/unavailable;
- total covered width;
- internal gap count/selected width.

### Density

- along-track ping spacing;
- mean/min/max actual across-track sounding spacing;
- retained count / High Density-added count.

### Resolution

Do **not** synthesize a quality score. Show only registered physical evidence already available upstream, such as beamwidth/footprint/range-resolution indicators, and label them as physical sampling/resolution evidence rather than density.

### Efficiency

Do not invent a universal efficiency percentage. In the minimum version show vessel speed and spatial progression/cadence evidence. Add an efficiency proxy only if Scientific Core defines it.

The rail exists to name the concepts that the spatial scene demonstrates.

## Baseline × current

The current `baseline` snapshot is useful and should remain, but comparison must occur on shared visual scales.

Preferred implementation:

- current acquisition strip in full strength;
- baseline footprint/sounding positions as a thin ghost overlay toggled by `Compare`;
- compact text below naming benefit + cost, e.g. API-backed facts such as `ping spacing decreased` / `retained point count increased`.

Do not automatically label every numeric increase as improvement. If benefit/cost semantics are not defined by the Core/pedagogy, state the changed quantity neutrally.

Use `motion.path`/`motion.circle` only for transitions between current states. Ghost baseline remains static.

## Interaction sequence encoded in UI

The control panel should visually encourage the canonical sequence rather than expose an undifferentiated cockpit:

```text
1 SPEED
2 PING RATE
3 BEAM DISTRIBUTION
4 FOOTPRINT CONTINUITY
5 HIGH DENSITY
6 INTEGRATED COMPARISON
```

A small step marker may highlight the last changed causal group, but do not lock later controls. Poor configurations must remain possible.

### Speed experiment

At fixed ping rate, changing speed must primarily move ping rows farther/closer apart. Keep across-track geometry unchanged unless the API says otherwise.

### Ping-rate experiment

At fixed speed, change the same spatial separation in the reciprocal direction. Do not animate a faster blinking sonar as the primary explanation.

### Beam distribution experiment

Change retained centre distribution / actual across-track spacing. Keep physical beamwidth/footprint distinction explicit.

### Footprint continuity experiment

Allow gap formation/closure to occur visibly from canonical finite support. This is where merged coverage should dominate.

### High Density experiment

Freeze support geometry and reveal additional soundings. Never add beam wedges or widen the support.

## Motion language

Use `motion/react` for:

- ping-origin rows sliding to new Core-backed spacing;
- sounding positions transitioning when beam distribution changes;
- `AnimatePresence` for High Density-added points;
- brief gap bracket emphasis when a gap appears/disappears;
- baseline ghost fade in/out.

Do not continuously animate the vessel along the strip; that can confuse speed with sampling spacing and adds no required pedagogy.

## Styling / responsive strategy

Suggested CSS:

```css
.d16-layout {
  display: grid;
  grid-template-columns: minmax(240px, 300px) minmax(0, 1fr);
  gap: clamp(12px, 2vw, 24px);
}
.d16-stage { min-width: 0; }
.d16-acquisition-svg { width: 100%; aspect-ratio: 1100 / 620; }
.d16-evidence-rail {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
@media (max-width: 900px) {
  .d16-layout { grid-template-columns: 1fr; }
  .d16-evidence-rail { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
```

Avoid fixed stage heights and nested scrollbars. On very narrow screens the evidence rail becomes one column; the SVG remains full width.

## Language / accessibility

Reuse global `hydrosim-language-change`; no local toggle. SVG `aria-label` should summarize speed, ping rate, coverage classification, covered width and retained/High Density count. Provide text equivalents for gap and spacing annotations. Selected sounding inspection must have a semantic keyboard-accessible equivalent if pointer interaction is added.

## Current-code changes to prioritize

1. Rename current `d17-*` CSS namespace to D16-specific classes.
2. Replace the approximately equal-weight linked-control wall with the guided control hierarchy.
3. Make one top-down physical acquisition SVG the dominant output.
4. Use `survey.coverage.footprint_intervals`, `merged_coverage_intervals` and `internal_gap_intervals` directly for coverage geometry.
5. Use actual retained positions/spacings; do not infer uniform spacing.
6. Preserve baseline snapshot but move comparison into the same physical scene/shared scales.
7. Make High Density visibly add points without changing coverage geometry.
8. De-emphasize multisector/pulse/frequency controls until a specific upstream consequence is being compared.

## Do not do

- no `swath / beamCount` replacement for actual spacing;
- no beam-centre span painted as coverage;
- no High Density as wider support or extra beams;
- no point count labelled acoustic resolution;
- no React achievable-ping-rate solver;
- no universal efficiency score;
- no TPU score; D17 owns uncertainty;
- no independent autoscale for baseline/current;
- no opacity-as-power encoding.

## Minimum Playwright assertions

1. Increasing speed at fixed ping rate increases the displayed API-backed along-track spacing and separates ping rows on a fixed scene scale.
2. Increasing ping rate at fixed speed decreases the same spacing.
3. Coverage SVG geometry is derived from API footprint/merged intervals and preserves visible internal gaps when classification is `gapped`.
4. Beam-count/spacing changes alter sounding distribution without being labelled as narrower beam/resolution unless an upstream physical field actually changes.
5. Enabling High Density increases displayed sounding count while the coverage geometry/path attributes remain identical.
6. Baseline ghost and current state use the same SVG coordinate transform.
7. Reset restores default settings; restore-baseline restores captured settings.
8. Global EN/PT-BR switch updates D16 labels without local language control.
9. At vessel speed zero, UI does not display infinite useful spatial density.

## Validation commands

From `web/pedagogical-explorer`:

```bash
npm run build
npx playwright test tests/tradeoff*.spec.ts
```

Use the exact existing focused spec filename if it differs. Run:

```bash
npm run test:ui
```

only as the integration gate after focused D16 checks pass.

# D11 — Vessel Motion — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D11_vessel_motion.md`  
Production source: `web/pedagogical-explorer/src/MotionLab.tsx`  
Scientific adapter: `src/hydrosim/app/motion_lesson.py`

## Concept to communicate

D11 must stop reading as an exaggerated CSS motion demo and become a **rigid-body motion instrument** driven by the Scientific Core.

The learner should see:

```text
actual vessel motion
  -> VRP / transducer pose changes
  -> body axes and beam/swath geometry change
  -> uncompensated sounding geometry moves
  -> measured motion enables stabilization / geometric compensation
```

The dominant visual idea is **moving vessel versus stable seabed geometry**, with the neutral state always available as a ghost reference.

The vessel must visibly continue to move even when compensation/stabilization is enabled. Compensation changes measurement/acoustic geometry, not the physical vessel motion.

## Scientific boundary

Use `src/hydrosim/app/motion_lesson.py` as the minimum authoritative geometry slice. It already provides:

- configured roll/pitch/yaw deviation in radians;
- physical heave in metres with HydroSIM convention `positive heave = Up`;
- VRP position in navigation frame;
- transducer position after lever-arm application;
- body forward/starboard/down axes in navigation frame;
- beam direction in navigation frame.

Do not reproduce `rotation_matrix_from_rpy`, lever-arm rotation, axis transforms, or heave/frame semantics in React.

The current `MotionLab.tsx` CSS mappings:

```tsx
animate={{ rotate: roll, y: heave, x: yaw*.8, skewX: pitch*.35 }}
```

and synthetic sounding displacement are concept-only. They must not become production scientific geometry.

## Production component structure

Refactor toward:

```tsx
<MotionControls />
<MotionStage>
  <MotionScene />
  <CompensationComparison />
  <MotionReadout />
  <TemporalMotionStrip />   // later progressive experience
</MotionStage>
```

Recommended presentation subcomponents:

```tsx
<VesselPoseGraphic />
<BodyAxes />
<BeamGeometry />
<SeabedReference />
<SoundingGhosts />
```

Keep these local to D11 unless a neighboring lab already exposes an appropriate shared primitive. Do not build a generic 3-D engine.

## Required API consumption

The UX must consume the motion snapshot endpoint/adaptor exposed by the application layer. If the HTTP route is not yet connected, route that concrete blocker to `software-engineering`; do not temporarily reproduce the geometry in TypeScript.

Expected authoritative state mirrors `MotionLessonSnapshot`:

```ts
type Vec3={x:number;y:number;z:number};
type MotionSnapshot={
  controls:{roll_rad:number;pitch_rad:number;yaw_deviation_rad:number;heave_m:number};
  vrp_position_n_m:Vec3;
  transducer_position_n_m:Vec3;
  body_forward_axis_n:Vec3;
  body_starboard_axis_n:Vec3;
  body_down_axis_n:Vec3;
  beam_direction_n:Vec3;
}
```

React may map these values into screen coordinates. It may not derive a replacement rigid-body solution.

## Control hierarchy

Start with **single-DOF experiments**.

Recommended control surface:

```tsx
<SegmentedControl value={activeDof}>
  Roll / Pitch / Yaw / Heave
</SegmentedControl>

<input type="range" value={activeValue} ... />

<SegmentedControl value={compensationMode}>
  Off / Ideal
</SegmentedControl>
```

Primary controls:

1. selected DOF;
2. active DOF value;
3. compensation mode `Off / Ideal`.

Secondary disclosure:

- lever arm configuration/reference inherited from D10, preferably preset rather than a full editor;
- simple sinusoidal dynamic experiment;
- architecture-specific stabilization examples only after instantaneous geometry works.

Do not show four equal sliders as the default experience. The pedagogy explicitly requires isolation before combination.

### Units

- roll/pitch/yaw: degrees in learner UI; convert only through the existing API contract/request adapter;
- heave: **metres**, never `rel.`.

Preserve sign conventions from the Scientific Core. Do not infer sign from SVG screen Y.

## Dominant visual scene

Use one large responsive native SVG. Recommended viewBox:

```tsx
<svg viewBox="0 0 1100 560" preserveAspectRatio="xMidYMid meet">
```

The scene should combine:

- fixed seabed reference;
- neutral vessel ghost;
- current vessel pose;
- VRP marker;
- transducer marker;
- body axes;
- baseline beam/swath ghost;
- current beam direction;
- uncompensated/current bottom-intersection evidence when authoritative geometry supports it;
- ideal compensated/stabilized reference when supported.

### Vessel rendering

Reuse the canonical HydroSIM vessel silhouette/vector where feasible. Vessel motion itself can be drawn by applying a **presentation transform derived from API-returned axes/positions**, but do not use CSS rotate/skew as the source of scientific geometry.

A safe 2-D projection strategy:

- for Roll view: across-track section using starboard/down axes;
- for Pitch view: along-track section using forward/down axes;
- for Yaw view: plan view using forward/starboard axes;
- for Heave view: section with fixed attitude and translated VRP/transducer.

This keeps each DOF geometrically legible without requiring WebGL/Three.js.

Use `useMemo` to project authoritative vectors into SVG screen coordinates:

```ts
const projected = useMemo(()=>projectSnapshot(snapshot, activeDof), [snapshot, activeDof])
```

`projectSnapshot` is presentation projection only. It must not alter the physical vectors.

## SVG primitives

Use:

```tsx
<path />      // vessel silhouette / beam/swath envelope
<line />      // axes, lever arm, seabed, compensation vectors
<circle />    // VRP, transducer, sounding/reference points
<polyline />  // optional sampled footprint or temporal trail from authoritative data
<text />      // concise labels
<g />         // grouped vessel/current/reference states
```

Use `markerEnd` arrowheads for body axes where useful. Generate SVG IDs with `useId()`.

Do not encode scientific motion using DOM `skewX` or arbitrary pixel multipliers.

## Baseline ghost

The baseline ghost is central and should remain visible:

```tsx
<g className="d11-baseline-ghost" opacity="...">
```

Opacity here communicates **reference state**, not acoustic power, so it is acceptable.

Show:

- baseline vessel;
- baseline transducer;
- baseline beam/swath;
- baseline sounding/footprint position where supported.

Current geometry must remain more visually prominent.

## Per-DOF visual grammar

### Heave

Use a section view.

- vessel remains unrotated;
- VRP/transducer translate according to API state;
- draw a vertical displacement bracket from baseline transducer to current transducer;
- label signed `h` in metres;
- baseline seabed stays fixed.

If ideal compensation output is available, show raw/uncompensated depth geometry and compensated reference on the same vertical scale.

### Roll

Use across-track section.

- show baseline and current body starboard/down axes;
- representative beam/swath rotates with authoritative beam direction;
- outer-bottom displacement should be shown only from authoritative geometry, not inferred from arbitrary screen fan width;
- if RX roll stabilization is later supported by the API, draw **vessel-rotated beam** and **stabilized look direction** distinctly.

The vessel must still visibly roll while stabilized geometry opposes the rotation.

### Pitch

Use along-track section.

- forward/down axes become dominant;
- show transducer translation caused by non-zero lever arm if returned by Core;
- show fore/aft acoustic direction change;
- TX pitch stabilization, when supported, is a separate acoustic vector, not a vessel pose correction.

### Yaw

Switch to plan view.

- fixed track/seabed frame;
- forward/starboard body axes rotate horizontally;
- current acoustic/sector direction rotates with heading deviation;
- optional stabilized TX yaw direction only when supported by authoritative model.

## Lever-arm consequence

D11 should reuse one non-zero transducer lever arm from D10. Do not expose all D10 installation controls again.

Draw:

```tsx
<line className="lever-arm" x1={vrp.x} y1={vrp.y} x2={tx.x} y2={tx.y} />
```

When roll/pitch/yaw changes, both the transducer position and orientation may move according to the Core. This is one of the most important spatial consequences to preserve.

## Compensation / stabilization comparison

The pedagogical contract requires `Off / Ideal` first.

Do not implement `Ideal` in React unless the API exposes the needed compensated/stabilized geometry.

Until then:

- `Off` can render authoritative current geometry;
- show `Ideal` control disabled or omit it from production until supported;
- route the missing scientific/API output to the appropriate specialist.

When supported, visual distinction should be:

```text
physical vessel/current geometry      = solid vessel + body axes
uncompensated acoustic/sounding path  = solid warm/current line
ideal compensated/stabilized target   = cool/ghost reference line or marker
```

Avoid PASS/FAIL language. This is a comparison of geometry, not validation status.

## Motion animation

Use `motion/react` to interpolate **between authoritative snapshots**, not to invent motion.

Recommended:

```tsx
<motion.g animate={{ ...screenTransformFromSnapshot }} />
<motion.path animate={{ d: authoritativeProjectedBeamPath }} />
<motion.circle animate={{ cx, cy }} />
```

Transitions:

```tsx
transition={{ duration: .18, ease: 'easeOut' }}
```

Prefer short deterministic interpolation after slider/API updates. Avoid spring overshoot because it can imply physical dynamics not present in the model.

Do not retain the current infinite expanding `motion-pulse` unless it is explicitly decorative and clearly unrelated to the scientific motion state; simplest is to remove it.

## Direct manipulation

The current free drag gesture maps horizontal drag to roll and vertical drag to heave. That is intuitive but scientifically ambiguous.

For the production D11:

- keep sliders as the authoritative control first;
- optional direct manipulation may be added per-DOF only, e.g. dragging a dedicated roll handle changes the roll control value;
- use `onPointerDown/onPointerMove` on explicit handles, not free vessel dragging that simultaneously changes unrelated quantities;
- clamp pointer-derived control values to the same input range and send them through the same API request path.

A `useRef<SVGSVGElement>` may support pointer coordinate conversion.

## Temporal motion strip — second-stage experience

Only after the instantaneous slice is correct, add a simple deterministic selected-DOF temporal experiment.

UI:

```tsx
<details>
  <summary>Animate motion / Animar movimento</summary>
  amplitude
  period
  play/pause
</details>
```

The Scientific Core should own time-varying motion values. If only instantaneous API snapshots exist, do not create a frontend sine-wave physics model as a substitute.

When supported, draw a small fixed-scale timeline with:

- motion value vs time;
- synchronized uncompensated geometric response from API output.

Use native `<path>` SVG.

## Current production elements to remove or replace

From current `MotionLab.tsx`, remove/rework as production science becomes available:

- local back/system-map toolbar duplication if the global shell already owns it;
- local conceptual/exaggerated chips;
- large explanatory hero text;
- simultaneous four-slider wall;
- CSS `rotate / skewX / x / y` as scientific vessel geometry;
- synthetic 18-point sounding trail based on arbitrary multipliers;
- `dominant rel.` readouts;
- `heave rel.` units;
- arbitrary free vessel drag coupling roll and heave.

The useful ideas to preserve are:

- neutral ghost;
- single-scene causal continuity;
- dedicated roll/pitch/yaw/heave focus;
- direct visual comparison;
- visual link from platform state to downstream sounding geometry.

## Responsive CSS

Recommended desktop:

```css
.motion-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
}
.motion-stage { min-width:0; }
.motion-scene-svg {
  width:100%;
  height:auto;
  aspect-ratio:1100/560;
}
```

For narrow widths, stack controls above the scene. Do not add horizontal scrolling around the SVG.

Avoid internal vertical scrollbars inside the scientific scene. Page scroll is acceptable when the viewport is short.

## Language and accessibility

Integrate the same global `hydrosim-language-change` event used by the other labs. D11 currently lacks this production localization contract and must add it.

PT-BR terminology:

- keep `Roll`, `Pitch`, `Yaw`, `Heave` visible as established terms;
- provide concise Portuguese explanation at first occurrence or via tooltip/help;
- translate descriptive copy, units, compensation labels and axes.

Give the main SVG one `aria-label` summarizing active DOF, value, VRP/transducer state and compensation mode. Decorative vessel geometry should not flood the accessibility tree.

## Icons

Use `lucide-react` only for controls/navigation such as:

- `Rotate3D` for DOF selector context;
- `RotateCcw` for reset;
- `Play/Pause` if temporal mode is added;
- `GitCompare` for compensation comparison.

Do not use icons as beam, vessel, axis or scientific geometry.

## Do not do

- no CSS transform as the scientific motion model;
- no frontend Euler-angle rotation math duplicating Python;
- no invented stabilization model;
- no synthetic sounding displacement based on screen pixels;
- no `rel.` heave;
- no motion-sensor noise, latency, bias or TPU controls in primary D11;
- no patch-test/static mounting-error controls;
- no assumption that every MBES stabilizes all axes identically;
- no double application of stabilization and compensation;
- no Three.js dependency for this lesson.

## Minimum focused Playwright assertions

1. Selecting each DOF leaves only that DOF's primary control active/foregrounded.
2. Heave is displayed in metres and API-updated VRP/transducer screen positions change vertically without attitude decoration changing independently.
3. Roll change updates authoritative body-axis/beam projection while baseline ghost remains fixed.
4. Pitch with non-zero lever arm updates transducer screen position from returned API geometry.
5. Yaw switches/uses plan-view presentation and updates forward-axis/acoustic-direction projection.
6. Reset returns all motion controls to zero and baseline/current geometry coincides within display tolerance.
7. No synthetic sounding trail changes when there is no corresponding authoritative sounding/geometry output.
8. Global EN/PT-BR language change updates D11 labels with no local language control.
9. Supported narrow viewport has no horizontal scrollbar around the scene.
10. If compensation/stabilization API is unavailable, the UI does not present a fake functional `Ideal` result.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test <focused-D11-spec>
npm run test:ui
```

Use focused tests during implementation. Full UI suite remains the integration gate.

## Explicit blocker boundary

The visual brief is implementation-ready for the **authoritative instantaneous motion scene** because the Python adapter already returns vessel/transducer axes and beam direction.

The following learner-visible experiences remain gated on explicit Core/API support and must not be fabricated in React:

- bottom intersection / sounding displacement if not returned authoritatively;
- ideal geometric motion compensation result;
- architecture-specific RX roll / TX pitch-yaw stabilized directions;
- time-varying sinusoidal motion snapshots if no endpoint exists yet.

UX-B should implement the unblocked instantaneous geometry first and route only these exact missing outputs when encountered.
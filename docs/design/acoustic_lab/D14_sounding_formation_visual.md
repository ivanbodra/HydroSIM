# D14 — Sounding Formation — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D14_sounding_formation.md`  
Production source: `web/pedagogical-explorer/src/SoundingFormationLab.tsx`  
Scientific adapter: `src/hydrosim/app/sounding_formation_api.py`

## Dominant visual mental model

D14 must make one transformation unforgettable:

```text
OBSERVED DETECTION != HYDROGRAPHIC SOUNDING
```

A retained acoustic observation becomes a spatial sounding only after propagation, installation geometry, time-matched platform pose and reference-frame transforms are associated correctly.

The visual identity should be a **single point being reconstructed through connected frames**, not ten stage buttons plus a decorative beam.

```text
TWTT + direction
 -> local acoustic vector
 -> sonar frame
 -> vessel frame / lever arm
 -> time-matched pose
 -> navigation frame
 -> reconstructed 3-D sounding
```

The learner should be able to hold the acoustic detection fixed, change one association/configuration, and watch the reconstructed point move while Truth remains fixed.

## Production hierarchy

Refactor toward:

```tsx
<SoundingFormationLab>
  <ObservationControls />
  <ReconstructionWorkspace>
    <ObservedDetectionStrip />
    <TransformScene />
    <TransformRail />
    <SoundingResult />
    <TruthComparison />
  </ReconstructionWorkspace>
</SoundingFormationLab>
```

Do not keep every upstream quantity at equal visual priority.

## Progressive interaction sequence

Use the existing `active_stage` API concept, but group the current ten low-level stages into learner-facing milestones rather than making the top stagebar the dominant navigation:

1. **Detection** — retained TWTT + direction;
2. **Range / path** — propagation model applied;
3. **Sensor geometry** — local vector and sonar origin;
4. **Vessel geometry** — lever arm / installation transform;
5. **Pose association** — navigation placement;
6. **Sounding** — final derived point;
7. **Compare** — optional Truth/error diagnostic.

The request may continue sending the authoritative existing stage names. React may map those names to presentation groups only; do not alter scientific ordering.

## Controls

### Primary, always visible

- TWTT;
- detected across-track angle;
- one compact pose experiment control set appropriate to the active milestone.

At the opening milestone, only TWTT and direction should be prominent.

### Contextual controls

Reveal only when the relevant transform is active:

- vessel position;
- roll/pitch/yaw;
- lever arm;
- sound speed.

Use a selected-axis segmented control or compact X/Y/Z editor rather than nine equally weighted number fields when possible.

### Move out of primary interaction

Current `pingIndex`, `rxStartMs`, and `rxEndMs` must not occupy the main control panel. Ping identity belongs in provenance/context. RX-window controls belong upstream and should be removed from primary D14 UX; retain request defaults only as required by the current adapter until the API contract changes.

Do not add wrong-pose-epoch arithmetic locally. The planned stale-pose experiment must wait for authoritative D13/Core output.

## A. Observed detection strip

At the top of the workspace show a narrow provenance strip:

```text
OBSERVED
Ping 12 / Beam n / Detection n
TWTT 40 ms     direction +17.5°
```

Use API-returned `ping_index`, `beam_index`, `detection_index`, `detection_method`, `twtt_seconds`, and `detected_across_track_angle_rad`.

This strip must explicitly say `Observed acoustic detection / Detecção acústica observada`. Do not label it sounding.

## B. Transform scene — dominant visualization

Replace `.sf-vessel`, `.sf-beam`, `.sf-truth`, `.sf-recon` CSS-positioned geometry with one responsive native SVG.

Recommended:

```tsx
<svg viewBox="0 0 1100 620" className="sounding-transform-scene" role="img">
```

Use a fixed physical/project scale for comparison within a scenario. Do not map every coordinate through `50 + value * .8` with clipping as the current `posPct()` does.

### Required primitives

- `<g>` for each coordinate frame;
- `<line>` with arrow markers for X/Y/Z axes;
- `<circle>` for VRP, sensor origin, Truth and reconstructed sounding;
- `<line>` for lever-arm vector;
- `<path>` or `<line>` for the API-backed local observation direction/path representation;
- `<line>` for Truth-to-reconstruction error vector;
- `<text>` for concise frame/point labels;
- optional `<rect>`/simple `<path>` vessel silhouette as context only.

Use `useId()` for SVG marker IDs.

The scene must not use a decorative rotated CSS beam. Direction must be represented from authoritative returned angle/vector semantics and registered geometry. If the API does not expose a destination-frame direction vector yet, show only the supported across-track observation geometry and label the simplification.

## C. Frame transforms as visible geometry

The core visual should expose at least these anchors:

- sonar/sensor origin;
- vessel VRP;
- lever-arm vector;
- vessel body axes;
- associated pose position;
- reconstructed point;
- optional Truth point.

When lever arm changes, the sensor origin must move relative to VRP according to API output; the acoustic detection values remain unchanged.

When pose/attitude changes, animate the authoritative frame/point transition but do not imply the detection itself changed.

Recommended Motion:

```tsx
<motion.g animate={{ transform: frameTransform }} transition={{ duration:.2 }} />
<motion.circle animate={{ cx: reconX, cy: reconY }} transition={{ duration:.2 }} />
```

Only use screen transforms computed from API-returned geometry. Do not implement rotation-order science in CSS/TypeScript.

## D. Transform rail

Under or beside the scene, render a compact connected rail:

```text
Observed detection
   -> range/path
   -> sonar frame
   -> vessel frame
   -> pose
   -> navigation frame
   -> sounding
```

Use native HTML buttons or SVG nodes. The active node is highlighted; completed nodes remain subdued. `ChevronRight` from `lucide-react` is acceptable for navigation, but scientific transforms must be represented by the scene, not icons.

The rail replaces the current visually dominant ten-button stagebar.

## E. Reference/current treatment

Truth is a teaching-only reference and should default off until the comparison milestone.

When enabled:

- Truth = fixed ghost/reference point;
- reconstructed = current point;
- error vector = direct line between them;
- both use identical physical scale and axes;
- show `ΔX, ΔY, ΔZ` adjacent to the vector or in one compact readout.

Never animate Truth in response to processing-only changes. If the current API truth changes because the configured physical scenario itself changed, distinguish that scenario change from a processing mismatch experiment.

## F. Range/path presentation

The current first slice is constant-sound-speed reciprocal reconstruction. Show `reconstructed_range_m` as an API-backed range/path consequence. Do not write `R = ct/2` as a universal final sounding equation.

A small path-length bracket can use SVG `<line>` plus end ticks and `<text>`.

When advanced D4 ray tracing is later connected, replace straight-path presentation with the authoritative returned ray path. Do not draw decorative refraction now.

## G. Provenance rail

Add a small collapsible provenance view:

```text
Ping -> Beam -> Detection -> Pose association -> Reconstruction
```

Populate only identities/semantics returned by the API. Sector/TX-epoch provenance waits for D9/API support.

This is context, not a second timing lab.

## Hooks and events

Preserve:

- `useState` for configured learner inputs and active milestone;
- `useMemo` for request payload, returned-angle conversion and screen-coordinate transforms;
- `useEffect` for language event and debounced/abortable API request.

Add:

- `useId` for SVG arrow/clip IDs;
- `useRef` only if needed for pointer-to-SVG coordinate conversion or focus management.

Use `onChange` for sliders/number fields. Direct manipulation of a sounding point is **not** appropriate: the point is Derived and must not become an input.

## Motion language

Use `motion/react` for:

- movement of reconstructed sounding after authoritative response changes;
- movement/rotation of frame groups when API-backed geometry changes;
- reveal of the next transform in the rail;
- short highlight of the transform responsible for the latest change.

Use `AnimatePresence` for optional Truth comparison and contextual controls.

Do not animate acoustic travel time as literal propagation speed unless the Scientific Core later supplies a time-domain scene contract.

## Styling / responsive behavior

Desktop:

```css
.sf-layout {
  display:grid;
  grid-template-columns:minmax(230px,290px) minmax(0,1fr);
}
.sounding-transform-scene { width:100%; height:auto; }
.sf-maincol { min-width:0; }
```

The main scene must remain visible while contextual controls change. Avoid a tall controls column that forces the learner to scroll away from the sounding. On narrow widths stack controls above the scene and keep the transform rail horizontally wrapping rather than horizontally scrolling.

No horizontal scrollbar inside the scientific SVG/workspace.

## EN/PT-BR

Use the existing global `hydrosim-language-change` event. Translate new semantic labels including `Observed acoustic detection`, `Sensor frame`, `Vessel frame`, `Navigation frame`, `Reconstructed sounding`, `Truth`, `Error vector`, `Pose association`, and `Provenance`.

Do not add a local language switch.

## Current code to preserve/reuse

`SoundingFormationLab.tsx` and its API already provide:

- authoritative staged reconstruction;
- TWTT and detected across-track angle;
- vessel position and roll/pitch/yaw configuration;
- lever arm;
- sound speed;
- ping/beam/detection identity;
- associated pose position;
- reconstructed range;
- Truth and reconstructed 3-D sounding;
- `truth_minus_reconstructed` error vector;
- reconstruction basis/semantics;
- abortable API updates and global language synchronization.

Preserve the request/response contract. The design change is primarily hierarchy, explicit frames and physical-scale spatial comparison.

## Scientific/API blockers to respect

Do not fake these features in React:

- stale/wrong pose epoch from D13 until API supplies association alternatives;
- mounting-orientation transform until D10/Core exposes it;
- refracted ray path until D4 registered ray output is integrated;
- sector/TX-epoch association until D9/API exposes it;
- hydrographic vertical-datum transform until a registered transform exists.

The UX can reserve progressive-disclosure placeholders only if clearly disabled and labelled as future capability; preferably omit them until supported.

## Do not do

- no local rotation matrices or frame transforms that duplicate Core science;
- no decorative CSS beam angle multiplier;
- no `posPct()` autoscaling/clipping that hides physical error magnitude;
- no RX-window controls as primary D14 pedagogy;
- no Truth presented as operationally available data;
- no uncertainty ellipse/TPU — belongs to D17;
- no assumption that constant-c straight-line range is universal in refracting water;
- no direct dragging of Derived sounding as an input.

## Minimum focused Playwright assertions

1. Opening state labels TWTT/direction as an observed acoustic detection, not a sounding.
2. Advancing milestones reveals transforms progressively without changing authoritative stage order.
3. Lever-arm change leaves observed TWTT/angle unchanged and changes API-backed sensor/reconstruction geometry.
4. Pose/attitude change moves reconstructed sounding according to API response.
5. Truth comparison is optional and uses the same fixed scene scale as reconstruction.
6. Error vector/readout matches API-returned `truth_minus_reconstructed` values.
7. RX-window controls are absent from the primary control surface.
8. Reset restores the canonical first scenario.
9. Global EN/PT-BR switch updates D14 semantic labels.
10. No horizontal scientific-workspace scrollbar at standard desktop viewport.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/didactic-explorer.spec.ts -g "sounding formation|D14|reconstruction"
```

Run the full UI suite only as the integration gate:

```powershell
npm run test:ui
```

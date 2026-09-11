# D10 — Vessel & Sensor Configuration — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D10_vessel_sensor_configuration.md`  
Production source: `web/pedagogical-explorer/src/VesselConfigurationLab.tsx`

## Concept to communicate

D10 must make one distinction visually unforgettable:

```text
MOVE A SENSOR physically
  -> physical installation changes

MOVE / REDEFINE VRP only
  -> coordinates / lever arms change
  -> physical sensor geometry does not
```

Secondarily, the learner must see that sensor orientation belongs to the rigid installation, while vessel motion belongs later to D11.

The lab should feel like an interactive vessel blueprint, not a long configuration form.

## Production direction

Preserve the current `/api/v1/pedagogical/vessel` contract and the current correct VRP invariant already implemented in `VesselConfigurationLab.tsx`.

Do not recompute lever arms, vertical relationships, pairwise distances or orientation science in React if the Core/API provides them or is expected to provide them.

The current API already supports the positional/static-geometry slice. The pedagogy additionally requires sensor mounting orientation/body axes. If orientation is not yet available from the Scientific Core/API, the UX must not fake the scientific relationship. Build the positional/reference experience now and keep the orientation panel structurally ready for the authoritative data contract.

## Recommended React decomposition

Refactor toward a scene-first structure:

```tsx
<VesselConfigurationLab>
  <InstallationControls />
  <VesselBlueprintStage>
    <PlanView />
    <ProfileView />
    <InvariantStrip />
  </VesselBlueprintStage>
  <OrientationPanel />
  <ConfigurationSummary />
</VesselConfigurationLab>
```

Use:
- `useState` for selected edit target, sensor positions, VRP and secondary geometry controls;
- `useEffect` for API requests and global language sync;
- `useMemo` for presentation mapping, selected readouts and export payload;
- `useId` for SVG marker/gradient IDs if needed;
- pointer events only for direct-manipulation handles whose final values still feed the existing state/API.

Do not build a generic vessel CAD framework.

## Control hierarchy

Primary first experience:
1. edit target selector: `VRP / GNSS / IMU / Sonar`;
2. X / Y / Z controls for the selected target only.

Do not show four full X/Y/Z slider blocks simultaneously as the dominant interaction.

Recommended control pattern:

```tsx
<div role="tablist" aria-label="Edit target">
  <button>VRP</button>
  <button>GNSS</button>
  <button>IMU</button>
  <button>Sonar</button>
</div>
<XYZEditor value={selectedVector} onChange={...} />
```

Secondary controls inside `<details>`:
- vessel envelope length/beam/height;
- waterline Z;
- static draft;
- hydrographic water level relative to datum;
- body-axis visibility.

Keep Reset visible. Configuration export is secondary and should not compete with the learning scene.

## Dominant vessel blueprint scene

Replace the current CSS-positioned plan points as the main teaching surface with one responsive native SVG scene.

Recommended `viewBox`:

```tsx
<svg viewBox="0 0 1100 680" preserveAspectRatio="xMidYMid meet">
```

Upper/main region: plan view.  
Lower/narrow region: profile / vertical-reference view.

Use native SVG:
- `<path>` for simplified vessel outline;
- `<circle>` for VRP and sensor centres;
- `<line>` for +X/+Y axes and lever-arm vectors;
- `<polyline>` or `<path>` for dimension brackets;
- `<text>` for compact labels;
- `<g>` per sensor/VRP;
- `<marker>` for arrowheads where helpful.

The canonical HydroSIM vessel asset may be reused as visual identity only if its geometry maps cleanly to the reference scene. Do not distort it to imply hydrostatics.

## Coordinate mapping

Presentation mapping from metres to SVG coordinates is allowed.

Use one explicit display transform helper, e.g.:

```ts
const vesselToPlan=(p:V)=>({
  x:cx + p.y * scaleY,
  y:cy - p.x * scaleX,
});
```

This is only screen mapping. It must not change the canonical `+X Forward, +Y Starboard, +Z Down` semantics.

Display the frame continuously but lightly:
- +X arrow toward bow;
- +Y arrow starboard;
- +Z shown in profile or an axis triad.

Never silently substitute a vendor coordinate convention.

## Sensor and VRP direct manipulation

The scene should make physical move vs reference move immediately obvious.

For sensor editing:
- selected sensor receives a large handle/ring;
- slider/pointer change moves that sensor marker physically;
- its lever-arm arrow from VRP updates;
- other physical sensor positions stay fixed.

For VRP editing:
- VRP marker moves;
- all sensor markers remain visually stationary;
- every VRP->sensor vector updates;
- a brief local emphasis highlights changing lever-arm numbers.

Use `motion/react` for marker/vector transitions:

```tsx
<motion.g animate={{ x, y }} transition={{ duration:.2, ease:'easeOut' }} />
```

Do not animate sensor markers when only VRP changes.

That non-movement is the lesson.

## Lever-arm vectors

Draw explicit vectors from VRP to GNSS/IMU/Sonar.

Visual language:
- VRP = neutral/high-contrast reference marker;
- each sensor gets a stable semantic accent;
- vector line uses the sensor accent with modest opacity;
- selected vector becomes more prominent.

Near the selected vector, show compact components:

```text
ΔX +2.0 m   ΔY 0.0 m   ΔZ +3.0 m
```

These values must come from API-derived lever arms when available.

Do not replace directed components with only scalar distance.

## Pairwise invariants

The pedagogical key for a pure VRP change is that pairwise physical sensor separations remain unchanged.

If the current API does not return pairwise distances explicitly, do not silently promote locally computed geometry as scientific authority. Request/consume an authoritative output before using numeric invariant values as a teaching claim.

Until then, the scene itself can show the physical points remaining fixed while the VRP moves.

When authoritative values are available, add a narrow `Installation invariants` strip:

```text
GNSS↔IMU   3.16 m   unchanged
IMU↔Sonar  4.12 m   unchanged
```

On VRP change, briefly highlight `unchanged` rather than animating the number.

## Guided compare mode

Add a small two-state compare affordance after the basic interaction is stable:

```text
INSTALLATION MOVE | REFERENCE MOVE
```

This is not a second scientific mode. It is a teaching preset that selects which target is manipulated and what should be observed.

Optional reference ghost:
- previous physical sensor location = faint circle only when a sensor physically moves;
- do **not** ghost sensor movement when VRP alone changes, because the sensors did not move.

## Orientation / body-axis panel

This is required by pedagogy but must depend on an authoritative Core/API contract.

When available, render a selected sensor body triad over the vessel frame:
- vessel axes in neutral lines;
- sensor body axes in sensor accent;
- position centre remains fixed;
- mounting roll/pitch/yaw rotates only the sensor body axes.

Prefer a local 2.5-D axis glyph using SVG line projections over introducing WebGL/Three.js.

Use `motion.g` for smooth visual interpolation only after receiving authoritative orientation values/matrices/angles.

Do not derive 3-D rotation matrices in React unless the Scientific Core explicitly returns the final orientation representation intended for display. Presentation projection is allowed; scientific frame transformation is not.

If the backend does not yet support orientation, show no fake orientation controls. Keep a concise disabled/hidden future slot only if UX needs structural continuity.

## Guided sign/axis error preset

Only implement after the Scientific Core/API or an approved configuration preset defines the semantics.

Desired experience:
- preset intentionally maps a sensor to the wrong sign/axis;
- scene shows the configured point on the wrong side or depth;
- learner diagnoses using visible +X/+Y/+Z frame.

Do not implement this by arbitrarily negating values in presentation code.

## Vertical-reference view

Use the lower profile band to show one consistent body-frame vertical geometry:
- VRP;
- waterline;
- transducer;
- keel/static draft.

Render with SVG horizontal lines and labelled markers on the same Z display mapping.

Hydrographic `water_level_m_relative_to_datum` must be placed in a **separate side lane** visually disconnected from the body-frame Z axis, unless an authoritative datum-to-vessel transform exists.

Recommended:

```tsx
<g className="body-frame-profile">...</g>
<g className="datum-lane">...</g>
```

A vertical separator and heading can reinforce `Vessel frame` vs `Hydrographic datum`.

Changing hydrographic water level must not move the vessel, VRP, sensors, waterline-to-keel geometry or lever-arm vectors.

## Motion language

Use `motion/react` for:
- selected sensor point translation during physical installation edits;
- VRP marker/vector transitions during reference edits;
- short changed-readout emphasis;
- orientation-axis interpolation once authoritative orientation exists.

Do not animate vessel heave/roll/pitch/yaw here. D11 owns dynamic motion.

No decorative rocking vessel.

## Styling

Recommended layout:

```css
.d10-config-grid {
  display:grid;
  grid-template-columns:minmax(220px,300px) minmax(0,1fr);
  gap:clamp(14px,2vw,24px);
}

.d10-blueprint-stage {
  min-width:0;
  display:grid;
  grid-template-rows:minmax(420px,1fr) auto;
}

.d10-blueprint-svg {
  width:100%;
  min-height:clamp(460px,62vh,720px);
}
```

On narrower screens, stack controls above the scene rather than creating horizontal scroll.

Avoid multiple equally weighted cards. The blueprint is the protagonist; summary/export are subordinate.

## Accessibility and language

Use the global `hydrosim-language-change` event only.

The blueprint SVG needs a concise dynamic `aria-label`, e.g.:

`Vessel reference frame with VRP, GNSS, IMU and sonar positions. Selected target: Sonar.`

Direct-manipulation handles must have keyboard-equivalent sliders/inputs. Do not make drag the only way to edit geometry.

## Current-code specific notes

`VesselConfigurationLab.tsx` already provides:
- sensor and VRP state;
- authoritative vessel API call;
- the correct VRP reference-change invariant;
- global language sync;
- static vessel envelope;
- body-frame metadata;
- vertical-reference quantities;
- separate hydrographic water level;
- configuration export.

Preserve these. Main visual refactor:
- one selected target instead of all slider groups competing;
- plan/profile views become one integrated SVG blueprint;
- explicit lever-arm arrows;
- VRP move visibly leaves sensors fixed;
- body-frame vs datum lanes become unmistakable;
- orientation only after authoritative API support.

## Do not do

- no Three.js/WebGL dependency for this lab;
- no vessel motion simulation;
- no timing/latency controls;
- no React-only lever-arm science or orientation transforms;
- no water-level line that physically moves body-frame sensors;
- no assumption that IMU must be at centre of gravity;
- no manufacturer coordinate convention replacing HydroSIM's canonical frame;
- no generic JSON/configuration panel as the dominant experience.

## Minimum Playwright assertions

1. Selecting Sonar and changing X/Y/Z moves only the sonar marker and changes its authoritative lever-arm readout.
2. Changing VRP moves the VRP marker and lever-arm vectors while GNSS/IMU/Sonar screen positions remain unchanged.
3. Frame labels continuously show `+X Forward / +Y Starboard / +Z Down` or localized equivalent without changing semantics.
4. Hydrographic water-level control changes its separate datum readout/lane but does not move physical sensor markers.
5. Vessel-envelope controls are under progressive disclosure.
6. Reset restores canonical reference geometry.
7. Global EN/PT-BR updates all D10 labels without a local language control.
8. When authoritative orientation support lands, changing mounting orientation rotates only the selected sensor body-axis glyph, not its centre or vessel attitude.

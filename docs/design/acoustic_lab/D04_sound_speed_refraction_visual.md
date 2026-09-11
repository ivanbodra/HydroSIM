# D4 — Sound Speed & Refraction — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D04_sound_speed_refraction.md`  
Production source: `web/pedagogical-explorer/src/RefractionLab.tsx`

## Dominant visual mental model

**The water column bends the acoustic path; a wrong processing SVP reconstructs the same observation along the wrong path and moves the sounding endpoint.**

The learner should read D4 as one connected geometry, not as a profile chart beside an unrelated ray chart:

```text
c(z) -> ray bending -> Truth endpoint
                   \-> Processing reconstruction -> endpoint error Δx / Δz
```

The endpoint separation on the bottom is the dominant consequence. Profile and travel/path values support that consequence.

## Production direction

Keep `/api/v1/pedagogical/refraction` authoritative. `RefractionLab.tsx` already receives `reference_ray`, optional `profile_comparison.processing`, endpoint errors, segment geometry, path length and travel time. Do not reproduce Snell/ray tracing or endpoint calculations in TypeScript.

The current `points()`, `xy()`, `polyline()` and `profilePath()` helpers are acceptable **screen projection only**. Refactor them only to make fixed shared geometry clearer.

### Recommended React decomposition

```tsx
<RefractionControls />
<RefractionStage>
  <SoundSpeedProfile />
  <RayGeometry />
  <EndpointErrorOverlay />
</RefractionStage>
<RefractionEvidenceStrip />
```

Keep this local to D4; do not create a generic scientific-chart framework.

Hooks:
- `useState` for scenario, launch angle and profile controls;
- `useMemo` for request/profile objects and SVG projection/path strings;
- `useEffect` for API request and global language event;
- `useId` only if SVG marker/clip IDs need collision-safe definitions;
- no animation state loop is required.

## Layout and hierarchy

Desktop:

```css
.refraction-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
  min-height:0;
}
.refraction-stage { min-width:0; min-height:0; }
```

The right side should be one large **water-column stage**. Integrate the narrow `c(z)` profile into the left edge of that stage rather than making it feel like a separate dashboard card.

Recommended main SVG:

```tsx
<svg viewBox="0 0 1000 560" preserveAspectRatio="xMidYMid meet">
```

Reserve roughly 20–24% width for `c(z)` and 76–80% for ray geometry. Both share the same vertical depth mapping.

At narrow widths, stack controls above the stage. Do not introduce an internal vertical scrollbar inside the SVG. If controls exceed viewport height, the page/lab shell may scroll; keep the scientific scene intact.

## Controls and progression

Preserve the existing scenario progression because it matches pedagogy:

1. `Constant sound speed`
2. `Two-layer refraction`
3. `Profile comparison`

Primary controls:
- launch angle — always visible and visually dominant;
- Truth/reference lower-layer sound speed or registered gradient control when the scenario supports it;
- Processing-profile sound speed only in comparison mode.

Reset remains visible.

Secondary diagnostics (path length, travel time, segment/ray parameter) belong in a low-height evidence strip or `<details>`; do not let them compete with endpoint error.

If future Core/API exposes richer layer/gradient presets, put layer editing/presets behind `More / Mais`; do not synthesize continuous profiles in React from unsupported assumptions.

## Main SVG scene

Use native SVG primitives only.

### Shared depth geometry

Draw:
- `<line>` or `<path>` for water surface;
- subtle horizontal layer interface(s) when present;
- `<line>` / `<path>` for bottom at target depth;
- `<text>` for sparse depth labels;
- optional light `<rect>` layer bands only to distinguish media, not to imply density or acoustic power.

Truth and Processing must share exactly the same depth and horizontal screen domains. Never autoscale each ray independently.

### Sound-speed profile

Render `c(z)` with `<polyline>` using the same vertical depth coordinate as the ray scene. Keep fixed sound-speed bounds broad enough to compare all supported values; the current 1450–1570 m/s range can remain while it covers the registered API controls.

Truth/reference profile: solid stroke.  
Processing profile: contrasting dashed or secondary stroke.

Do not use filled area under `c(z)` as if it represented energy.

### Ray geometry

Render API-backed ray paths with:

```tsx
<motion.polyline points={referencePoints} ... />
<motion.polyline points={processingPoints} ... />
```

or `motion.path` if converting to `d` improves interpolation. Motion is only a transition between solved geometries; duration around `180–280 ms`, no elastic overshoot.

Truth ray remains visually primary and stable. Processing ray appears only in comparison mode.

Do **not** animate a pulse travelling along the ray unless the animation is explicitly labelled illustrative; the current API solves path geometry, not time-domain packet propagation.

### Endpoints and error vector

Endpoints must be the strongest local marks in comparison mode:

```tsx
<circle data-testid="truth-endpoint" ... />
<circle data-testid="processing-endpoint" ... />
<line data-testid="endpoint-error-vector" ... />
```

Add small SVG dimension brackets/arrows for `Δx` and `Δz` when both are visually resolvable. Use API-returned `horizontal_endpoint_error_m` and `depth_endpoint_error_m` for labels; the UI may project endpoint coordinates to screen but must not recompute the scientific errors.

Use `<AnimatePresence>` for the comparison-only Processing ray/error overlay so the transition communicates `matched -> mismatched`, not decorative entrance animation.

When Truth and Processing are matched, show one coincident endpoint and a compact `Δx 0 / Δz 0` state rather than fake visual separation.

## Reference/current semantics

Truth/reference is the reference state. Processing/reconstructed is the learner-configured interpretation.

Never allow Processing-profile changes to move the Truth ray. A focused UI test must protect this.

When launch angle changes, both relevant solved rays may change because the common observation geometry changed. When only Processing profile changes, the Truth path/endpoint must remain fixed.

## Optional error-vs-angle view

Pedagogy recommends an error-vs-angle curve or small swath fan, but it must come from the Scientific Core/API. Do **not** loop over angles in React and call/reimplement a ray solver as frontend science.

If/when an API returns an angle sweep, reveal it behind `Across swath / Ao longo da faixa` and render a fixed-domain SVG `<path>` with current-angle `<line>` cursor. Until then, the single-beam endpoint geometry is the production authority.

## Motion language

Use `motion/react` for:
- short interpolation/fade between API-solved ray geometries;
- endpoint movement after a solved profile/angle change;
- comparison overlay entrance/exit;
- brief emphasis of the error vector when mismatch changes.

Do not:
- make ray brightness represent acoustic power;
- continuously oscillate the water column;
- animate refraction before the API result exists;
- use spring overshoot on physically solved endpoints.

## Readouts

Keep a compact evidence strip below the stage:

```text
Travel time | Path length | Truth x | Processing x | Δx | Δz
```

In constant/layered modes, hide Processing-only values rather than showing empty cards. In comparison mode, `Δx / Δz` should receive the strongest typographic weight.

## Language and accessibility

Continue using global `hydrosim-language-change`; no local language toggle.

Main SVG `aria-label` should describe scenario, launch angle and whether Truth/Processing endpoints coincide or differ. Do not expose every polyline point.

Do not translate canonical symbols `c(z)`, `Δx`, `Δz`.

## Current-code-specific changes

`RefractionLab.tsx` already has the correct API boundary and most scientific ingredients. UX-A should primarily change composition:
- merge profile + ray views into one depth-coherent stage;
- make bottom/endpoints/error vector dominant;
- reduce layer labels and diagnostic cards;
- preserve fixed `MAX_X` / `MAX_DEPTH` shared geometry while API range supports it;
- preserve scenario progression and global language sync.

The current comparison button sets Processing equal to the current Truth lower layer before entering comparison. Preserve this useful matched starting state.

## Scientific guardrails

- Scientific Core ray tracer and sign/angle conventions are authoritative.
- Processing SVP must never alter Truth propagation.
- No universal sign claim for `Δx`/`Δz`.
- Surface/transducer sound speed is not interchangeable with water-column SVP; do not add a surface-speed steering control here without a registered scientific contract.
- Layer coloring is categorical only.
- No TPU/uncertainty propagation in D4.

## Minimum focused Playwright assertions

1. Constant mode renders one Truth ray and no Processing ray.
2. Entering comparison begins with matched profiles/endpoints.
3. Changing Processing profile changes Processing ray/endpoint while Truth ray `points`/`d` remains unchanged.
4. Endpoint error vector and `Δx/Δz` readout appear only when comparison data exists.
5. Increasing launch angle causes an API-backed geometry update while shared SVG domain/viewBox remains unchanged.
6. Reset returns to constant mode/reference values.
7. Global EN/PT-BR switch updates labels without a local language button.
8. Error/retry state remains usable.

Suggested focused command after the UX implementation adds/updates its spec:

```powershell
cd web/pedagogical-explorer
npm run build
npx playwright test tests/refraction-lab.spec.ts
```

Use `npm run test:ui` only as the broader integration gate.
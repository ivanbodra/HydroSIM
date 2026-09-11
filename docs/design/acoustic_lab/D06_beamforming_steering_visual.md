# D6 — Beamforming & Electronic Steering — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D06_beamforming_steering.md`  
Production source: `web/pedagogical-explorer/src/BeamformingLab.tsx`

## Dominant visual mental model

The learner must see the causal chain, not merely a steering ray and a table:

```text
OBLIQUE WAVEFRONT
 -> different arrival time at each fixed element
 -> applied per-channel compensation
 -> residual timing / phase
 -> aligned or misaligned channel traces
 -> coherent sum
 -> directional response
```

Then make the distinction explicit:

```text
beamforming = coherent spatial combination
steering = changing the compensation set so the formed response looks elsewhere
```

The physical array never rotates. Multiple RX beams are multiple processing paths from the same captured element data, never multiple physical transducers.

## Production hierarchy

Refactor the current stage toward:

```tsx
<BeamformingLab>
  <BeamformingControls />
  <BeamformingStage>
    <WavefrontArrayScene />
    <ChannelAlignmentView />
    <CoherentSumMeter />
    <DirectionalResponsePlot />
    <MultiBeamBridge />
  </BeamformingStage>
</BeamformingLab>
```

Keep these as local presentation components unless reuse becomes concrete. Do not create a generic signal-visualization framework.

### Primary controls

Always visible for the first RX experiment:

1. `source_angle_deg` — arrival/source angle;
2. `steering_angle_deg` — steering target when angle mode is active.

Use the current `onChange` state path and authoritative `/api/v1/pedagogical/beamforming` request.

### Progressive disclosure

Place behind `More / Mais`:

- steering control mode `angle | delay_gradient`;
- raw delay-gradient slider;
- RX/TX role switch until RX intuition is established;
- array-factor diagnostic overlay;
- grating-lobe diagnostic labels.

Aperture weighting and true-time-delay/phase-only modes must not be added until the Core/API supports them.

## A. Wavefront + fixed-array scene

Replace the current CSS `steer-ray/source-ray` scene with a native SVG scene so arrival geometry and element timing share one coordinate system.

Recommended:

```tsx
<svg viewBox="0 0 1000 330" className="beamforming-scene" role="img">
```

Use:

- `<line>` or `<path>` for 3–5 parallel incoming wavefronts;
- `<rect>` for the six physical elements;
- `<circle>` for the arrival intersection/activation marker at each element;
- `<line>` for source-direction and requested/effective-steering guides;
- `<text>` only for concise angle labels and channel IDs.

Map `data.elements[].position_y_m` to a fixed physical array rail. Do not evenly redistribute elements based on current state.

Wavefront orientation must come from `data.source_angle_deg`. Steering guides must come from `data.steering_angle_deg` / requested steering. Do not rotate the array.

### Arrival timing visualization

For each element, use `relative_arrival_offset_us` to position a small timing marker on a common local time rail below the element. The marker is a representation of the Core-returned offset, not a simulated moving pulse.

If Motion is used:

```tsx
<motion.circle animate={{ cx: mappedArrivalX }} transition={{ duration: .18 }} />
```

This means only “the authoritative relative arrival offset changed.” Do not animate wavefront travel speed.

## B. Channel alignment view — the visual heart of D6

The current timing table is numerically useful but insufficient as the dominant explanation. Convert the six rows into six horizontal mini-traces sharing one fixed time domain.

For every channel render three aligned landmarks from API values:

- arrival: `relative_arrival_offset_us`;
- compensation: `relative_compensation_delay_us`;
- residual: `residual_relative_timing_us`.

A compact visual implementation can use native SVG:

```tsx
<g data-channel={e.index}>
  <path d={channelWaveletPath} />
  <line className="arrival-marker" ... />
  <line className="compensation-vector" ... />
  <circle className="residual-marker" ... />
</g>
```

The wavelet is presentation geometry centred on the returned timing coordinate; it must not claim to be a Core-generated pressure waveform. Label the view `relative channel timing` rather than `measured waveform`.

Use one fixed domain derived from the maximum permitted control range, not per-state autoscaling. Source movement with steering fixed must visibly spread residuals; steering toward source must bring residual markers back together.

Add a vertical reference line at zero/reference channel.

### Direct causal highlighting

When the learner changes source angle, briefly emphasize arrival markers. When steering changes, emphasize compensation vectors. Use keyed `motion.g` opacity/stroke-width transitions of about 150–250 ms. Never encode coherent power by opacity.

## C. Coherent sum

The current `coherent_sum_real/im` already gives the authoritative complex sum. Keep magnitude presentation as a compact consequence, but make it visually adjacent to the aligned-channel view.

Use a fixed-scale meter or vector length with a domain appropriate to the fixed six-element array. The TypeScript may compute only `Math.hypot(real, imag)` as a display magnitude from API components, as it already does; do not derive beamforming physics locally.

Label it `Coherent sum / Soma coerente`, not gain unless the API explicitly returns gain.

## D. Directional response

Keep the current `physical_beam_pattern` and optional `array_factor_pattern`, but redraw them with a fixed angular domain `-80°..+80°` and fixed normalized-power vertical domain.

Use SVG `<path>` rather than a dense dashboard card where practical. Add explicit vertical guides for:

- source angle;
- requested/effective steering angle;
- `peak_angle_deg`;
- grating-lobe angles only when returned.

Do not use autoscale. The broadside reference should remain available as a ghost/reference overlay only if it comes from an API call or preserved authoritative reference response; do not synthesize a broadside pattern formula in React.

## E. Same channels -> multiple RX beams bridge

This is required by pedagogy but is not represented by the current response contract as simultaneous multiple beamformer outputs.

Implement only a **structural bridge** until the API supplies multiple delay/weight sets in one response:

```text
same captured channel set
       ├─ delay set A -> look direction A
       ├─ delay set B -> look direction B
       └─ delay set C -> look direction C
```

Render the shared six-channel source once and three subdued processing branches using `<path>` connectors. Label this `Concept bridge / Ponte conceitual` if no simultaneous Core outputs exist. Do not calculate three patterns in React.

When an authoritative multi-beam response is later exposed, replace the structural bridge with real branch outputs.

## RX first, TX second

Default `role='rx'` as today. Move TX into progressive disclosure or a second-step control. In RX the scene emphasizes incoming wavefront and channel alignment. In TX, reverse the narrative carefully: applied channel timing produces a directional transmitted response. Do not simply reverse an animation and imply a different physical model.

## Hooks and events

Preserve:

- `useState` for learner controls;
- `useMemo` for request payload and SVG path/screen-coordinate transforms;
- `useEffect` for global language event and abortable API request.

Add `useId()` for SVG marker/clip IDs if needed. Use `useRef()` only for pointer geometry or focus management, not as an alternate scientific state store.

No `requestAnimationFrame` acoustic simulation is required.

## Motion language

Use `motion/react` for:

- arrival-marker repositioning;
- compensation/residual convergence;
- directional-response path interpolation when controls change;
- short causal emphasis.

Use `AnimatePresence` only for aliased/grating-lobe diagnostics or progressive-disclosure sections.

Do not animate array rotation, propagation speed, or power by transparency.

## Styling / responsiveness

Desktop:

```css
.beamforming-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
}
.beamforming-stage { min-width:0; }
.beamforming-scene { width:100%; height:auto; }
```

Within the stage, prioritize scene + channel alignment before response plot. On narrower widths stack those vertically. Avoid horizontal scrolling inside any scientific SVG. The controls column may scroll only when viewport height requires it; the principal visualization should remain visible.

## EN/PT-BR

Continue the global `hydrosim-language-change` event. Do not add a local language button. Translate new labels including `Beamforming`, `Steering`, `Arrival offset`, `Compensation`, `Residual`, `Same channels`, and `Virtual RX directions`.

## Current code to preserve/reuse

`BeamformingLab.tsx` already provides:

- fixed six-element geometry for the core experiment;
- angle and delay-gradient control modes;
- RX/TX role;
- authoritative element positions, arrival offsets, compensation delays and residuals;
- coherent-sum complex components;
- physical and array-factor patterns;
- peak, beamwidth, steering regime and grating-lobe outputs;
- abortable API updates and global language synchronization.

The UX task is primarily to turn these authoritative values into one causal visual instrument, not to replace the model.

## Do not do

- no rotating physical transducer/array to represent electronic steering;
- no local delay/phase equations in TypeScript;
- no local array-factor calculation;
- no fake multi-beam patterns;
- no footprint — belongs to D7;
- no range-resolution claims;
- no adaptive plot domains that hide steering penalties or sidelobes;
- no opacity-as-power metaphor.

## Minimum focused Playwright assertions

1. RX is the default role.
2. Changing source angle changes API-backed arrival-offset positions while fixed element positions remain unchanged.
3. With steering fixed, source-angle mismatch produces visible non-zero residuals.
4. Steering toward the source reduces residual timing and increases/recover coherent-sum display according to API response.
5. Switching angle/delay-gradient mode preserves the same physical array.
6. Physical response plot remains on the fixed `-80°..+80°` domain.
7. Aliased response shows API-returned grating-lobe diagnostics.
8. Global EN/PT-BR switch updates D6 labels.
9. Reset returns RX, broadside source and broadside steering.
10. No horizontal scientific-stage scrollbar at the standard desktop test viewport.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/didactic-explorer.spec.ts -g "beamforming|steering|D6"
```

Run the full UI suite only as the integration gate:

```powershell
npm run test:ui
```

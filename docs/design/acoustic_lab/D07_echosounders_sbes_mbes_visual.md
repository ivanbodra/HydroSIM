# D7 — Echosounders: SBES vs MBES — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D07_echosounders_sbes_mbes.md`  
Production source: `web/pedagogical-explorer/src/EchosounderLab.tsx`

## Dominant visual mental model

D7 must stop reading as “one ray versus many rays”. The learner must see one physical acoustic observation chain:

```text
one TX insonified region
       +
one physical RX aperture -> many virtual RX look directions
       ->
TX × selected RX directional cell
       ->
finite seafloor footprint + distinct beam centre/detection location
```

The recognizable image of D7 is a vessel/transducer above a fixed-scale cross-track section, a broad TX envelope, many thin receive look directions, and a physically scaled footprint field on the seafloor. SBES is the same grammar collapsed to one finite observation cell.

## Current production assessment

Preserve the existing `/api/v1/pedagogical/echosounders` request, language synchronization, SBES/MBES toggle, depth/sector/beam-count/spacing inputs, canonical beam endpoints, incidence angles, footprint widths/areas, limiting mechanism, swath width and adjacent spacing.

Replace the current presentation shortcuts:

- `.echo-beam` CSS rays positioned from endpoint percentage;
- visual ray rotation using `steering_angle_deg * .32`;
- footprint width/height normalized independently to the largest footprint;
- footprint opacity proportional to area.

Those shortcuts destroy the physical comparisons required by pedagogy. **Never use opacity as a proxy for footprint area or acoustic power.**

The current API is already sufficient for a strong geometry-first slice. A full selected TX/RX/two-way response plot requires an authoritative response contract; do not synthesize it in TypeScript.

## Layout and hierarchy

Desktop:

```text
┌ controls 260–300 px ┐ ┌──────────── dominant observation stage ────────────┐
│ SBES / MBES          │ │ cross-track water column + TX + RX + bottom       │
│ depth                │ │ selected beam geometry / footprint annotation      │
│ sector               │ ├────────────────────────────────────────────────────┤
│ beam count           │ │ top-down footprint field — SAME physical scale     │
│ spacing mode         │ └────────────────────────────────────────────────────┘
│ More ▾               │ compact causal readout strip / comparison
└──────────────────────┘
```

At <= 900 px stack controls above stage. Do not put independent scrollbars inside either SVG. The page may scroll normally.

## Controls

Always visible:

1. `SBES | MBES` segmented toggle;
2. depth;
3. MBES sector;
4. MBES formed RX direction count;
5. beam-spacing mode.

Move to `<details>` `More / Mais`:

- pulse duration;
- TX along-track beamwidth;
- RX across-track beamwidth.

Keep these advanced controls because the current Core uses them, but do not let them visually compete with the D7 sequence.

Add `Reset` with `RotateCcw` from `lucide-react`. Icons are UI affordances only.

## React decomposition

Keep API/state ownership in `EchosounderLab`. Extract local presentation components only where they clarify geometry:

```tsx
<EchosounderControls />
<EchosounderStage>
  <CrossTrackObservationScene />
  <FootprintField />
  <SelectedBeamStrip />
</EchosounderStage>
```

State additions:

```ts
const [selectedBeamIndex, setSelectedBeamIndex] = useState<number | null>(null)
```

Use `useMemo` for screen-coordinate transforms, selected-beam lookup and SVG path construction only. Do not use `useMemo` to reproduce footprint, incidence, swath or spacing science.

When the active beam set changes, use `useEffect` to retain a valid selected index or choose the beam nearest nadir. Selection is presentation state.

## Cross-track observation SVG

Use native SVG, e.g.:

```tsx
<svg viewBox="0 0 1000 560" preserveAspectRatio="xMidYMid meet">
```

Build a **fixed physical x/z mapping** from the largest pedagogically supported comparison envelope, not from the current endpoints. A change in depth or sector must visibly change scale-relative geometry rather than re-fill the viewport.

Required primitives:

- `<g>` for vessel/transducer and body axes;
- `<path>` for broad TX envelope boundary;
- `<line>` or narrow `<path>` for RX centre/look directions;
- `<line>` for bottom plane;
- `<circle>` for canonical beam centre/endpoints;
- `<path>` or `<ellipse>` only for footprints when dimensions are authoritative;
- `<text>` for selected angle/range/incidence annotations.

### TX versus RX grammar

TX must be visually broader and read as the insonified region. RX directions originate from the **same physical RX aperture**. Do not draw a separate transducer for each beam.

A selected RX direction should receive stronger stroke/emphasis while non-selected directions remain visible. Selection must not imply that only one beam existed during the ping.

Use `onPointerDown` on an invisible/wider hit target around each beam centre or direction:

```tsx
<line className="beam-hit" onPointerDown={() => setSelectedBeamIndex(i)} />
```

Keyboard selection should be available through an associated button/list or focusable SVG group with a concise label.

## Selected directional response

Pedagogy requires `TX one-way -> selected RX one-way -> two-way response`. Implement this only to the level supported by API/Core.

If authoritative response samples are available when UX implements D7, render one shared-domain SVG plot:

```text
TX one-way
RX selected one-way
TX×RX two-way
```

with three `<path>` traces and explicit amplitude/power convention in the axis label.

If those samples are not available, **do not manufacture sinc curves, Gaussian lobes, or hard-edged beam multiplication in React**. Instead render a compact causal strip:

```text
TX envelope × RX direction -> canonical footprint
```

and use the authoritative footprint outputs as the consequence. File a scientific/API blocker only if the response plot is needed to satisfy the active pedagogical slice.

## Footprint field — physical scale is mandatory

Replace normalized pixel patches with a top-down SVG sharing a local-metre scale across all beams.

Recommended:

```tsx
<svg viewBox={footprintViewBox} preserveAspectRatio="xMidYMid meet">
```

Across-track position comes directly from `endpoint_across_track_m`. Across-track footprint width comes directly from `effective_across_track_width_m`.

Do not derive along-track width from area unless the Scientific Core explicitly defines that relationship. If only area and across-track width are available, show a physically scaled across-track footprint bar/interval and list area numerically. Add an ellipse/polygon only when both independent dimensions or an authoritative polygon exist.

Keep beam centre distinct:

- footprint = outlined/filled finite region;
- beam centre = small dot/cross;
- accepted detection = **not invented here**; D8 owns detection.

Nadir, intermediate and outer beams must be directly comparable on the same physical scale.

## SBES mode

SBES must show a finite TX/RX observation region and footprint. Never collapse it to a mathematical vertical line.

When switching SBES -> MBES, preserve depth and the common stage scale so the learner sees the transition from one finite observation cell to many simultaneous directional cells.

Use `AnimatePresence` only for the system-mode transition if it improves continuity; duration ~200–300 ms. Do not animate fictitious pulse travel unless time is scientifically mapped.

## Spacing experiments

For equiangular/equidistant:

- preserve the same x-domain;
- show beam centres and footprint intervals together;
- optional small spacing brackets between selected adjacent centres;
- changing spacing mode must visibly redistribute centres, not change physical beamwidth by itself.

For beam-count experiment:

- keep sector and physical footprint geometry fixed by Core;
- adding beams increases centre density;
- do not narrow footprints merely because count increased.

## Motion language

Use `motion/react` for geometric transitions between **authoritative endpoint/footprint states**:

```tsx
<motion.g animate={{ ...screenTransform }} transition={{ duration: .22 }} />
<motion.path animate={{ d: authoritativePath }} />
```

Prefer short tween transitions. No perpetual glow/pulse. No opacity-as-power encoding.

## Styling

```css
.echo-grid {
  display:grid;
  grid-template-columns:minmax(240px,290px) minmax(0,1fr);
  gap:clamp(14px,2vw,26px);
}
.echo-stage { min-width:0; }
.echo-observation-svg,
.echo-footprint-svg { width:100%; height:auto; display:block; }
@media (max-width:900px) {
  .echo-grid { grid-template-columns:1fr; }
}
```

Use a subdued water/background field, crisp axes/bottom, one stable TX visual family and one RX family. Selected beam emphasis can be brighter/thicker but must remain accessible without color alone.

## Readouts

Reduce the current card wall. Keep one compact selected-beam consequence strip:

```text
angle | slant/endpoint geometry | incidence | footprint width | area | limiting mechanism
```

Only show values actually supplied by API. Keep whole-system swath and adjacent spacing as secondary readouts.

## EN/PT-BR and accessibility

Continue the global `hydrosim-language-change` listener. No local language toggle.

Give each scientific SVG one concise `aria-label` summarizing system, depth, sector and selected beam. Do not expose every decorative path.

## Scientific prohibitions

- no hard-edged TX×RX polygon multiplication;
- no invented directional-response function;
- no adaptive scale that makes outer geometry look unchanged when depth changes;
- no opacity mapped to area/power;
- no statement that outer beams intrinsically have worse range resolution;
- no conflation of beam count, sounding density and independent acoustic resolution;
- no accepted-bottom detection logic; D8 owns it;
- no multisector sequencing; D9 owns it.

## Minimum focused Playwright assertions

1. SBES/MBES switch preserves depth and changes beam-centre count.
2. MBES beams originate visually from one RX aperture, not separate transducers.
3. Selecting nadir then outer beam changes selected angle/incidence/footprint outputs without changing TX control state.
4. Increasing depth changes endpoint/footprint geometry on a preserved physical stage scale.
5. Equiangular/equidistant changes beam-centre distribution while RX beamwidth control remains unchanged.
6. Increasing beam count at fixed sector increases centre count and does not imply a changed RX beamwidth setting.
7. Footprint field contains no style opacity derived from `effective_area_m2`.
8. Advanced controls live in progressive disclosure.
9. Reset restores reference configuration.
10. Global EN/PT-BR switch updates labels.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/echosounder-lab.spec.ts
```

Use the actual focused spec filename if different. Run:

```powershell
npm run test:ui
```

only as the integration gate after the focused D7 assertions pass.
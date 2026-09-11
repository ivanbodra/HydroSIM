# D5 — Transducer & Array Construction — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D05_transducer_array.md`  
Production source: `web/pedagogical-explorer/src/ArrayDirectivityLab.tsx`

## Dominant visual mental model

The learner should feel that the **beam is being physically sculpted by the array**. D5 is not primarily two directivity charts. It is one connected instrument:

```text
PHYSICAL ELEMENT LAYOUT
        ↓
APERTURE / λ + SPACING / λ
        ↓
ORTHOGONAL DIRECTIVITY CUTS
        ↓
ANISOTROPIC 3-D / PSEUDO-3-D MAIN LOBE
```

Changing only the along-track aperture must visibly reshape only the associated angular plane; changing only across-track aperture must reshape the orthogonal plane. Spacing and weighting then expose sidelobe/grating-lobe trade-offs.

D5 is **broadside array construction/directivity**. Steering/delay/phase belongs to D6.

## Production architecture

Keep `ArrayDirectivityLab.tsx`, its existing `/api/v1/pedagogical/array-directivity` request and the authoritative response fields. Do not implement array factor, beamwidth, grating-lobe detection or element-factor science in TypeScript.

Recommended local presentation decomposition:

```tsx
<ArrayControls />
<ArrayStage>
  <ArrayPlanView />
  <DirectivityVolume />
  <OrthogonalCuts />
  <ArrayRelationStrip />
</ArrayStage>
```

Use `useState` for learner controls and selected experiment mode; retain `useEffect` for API fetch/language synchronization; use `useMemo` for SVG projection/path construction only. `useId` may generate stable SVG gradient/mask IDs. No canvas/WebGL/Three.js is required.

## Guided control hierarchy

### Always visible
1. Frequency.
2. Across-track element count + spacing.
3. Along-track element count + spacing.
4. Reset.

Present X and Y geometry as two compact axis groups rather than six visually equal sliders. Beside each spacing slider show the API-backed/derived presentation readout `d/λ`; beside each axis show physical aperture and `L/λ` from Core outputs.

### Progressive disclosure: `Shape sidelobes / Modelar lóbulos`
Move weighting (`uniform` / `hann`) here until the learner has established aperture intuition.

Later element-factor controls belong here only when Core/API exposes them.

Do not expose TX/RX eccentricity or steering controls in D5.

## Dominant SVG scene

Use one responsive SVG, approximately:

```tsx
<svg viewBox="0 0 1000 620" preserveAspectRatio="xMidYMid meet">
```

Compose three spatially connected zones inside the same coordinate system:

- upper/left: fixed-scale plan-view array;
- center: broadside array origin and vessel axes;
- lower/right: pseudo-3-D response volume / main-lobe envelope.

### Array plan view

Replace percentage-positioned `<i>` elements with native SVG using `element_positions_array_frame_m`:

```tsx
<g aria-label="2-D element layout">
  <line ... className="axis along" />
  <line ... className="axis across" />
  {points.map(p => <circle cx={...} cy={...} r={...} />)}
</g>
```

Keep the **physical plan-view scale fixed** across learner changes. If the configured array becomes small, it should visibly become small; do not renormalize each geometry to fill the box.

Label vessel/body axes explicitly: `+X Along-track / Longitudinal`, `+Y Across-track / Transverse`. Use short EN/PT-BR labels in the global language system.

Draw aperture dimension brackets in both axes with `<line>` + end ticks + `<text>` and values from API physical apertures.

### Pseudo-3-D directivity volume

Do not invent a new 3-D response solver. Construct a pedagogical pseudo-3-D **main-lobe envelope** only from API-provided orthogonal patterns/beamwidths. The exact scientific evidence remains the two cuts.

Implementation option with native SVG:

- project an ellipse/conic envelope whose horizontal angular width is tied to `across_track_half_power_beamwidth_deg` and orthogonal width to `along_track_half_power_beamwidth_deg`;
- use `<path>` for front/back elliptical arcs and 3–5 meridian curves;
- use a subtle `<linearGradient>` or `<radialGradient>` for depth cue only, **not as a power scale**;
- label it `−3 dB main-lobe envelope` so it is not mistaken for the complete computed 3-D field.

If either beamwidth is `null`, do not fabricate the envelope: show the orthogonal cuts and an unavailable-state annotation.

The response volume must remain broadside. Never rotate it from any D5 control.

## Orthogonal directivity cuts

Evolve the existing `PatternPlot` rather than replace the API series.

Render both cuts with native SVG `<path>` on the **same fixed angular domain** (pedagogy currently expects approximately −80°…+80°) and fixed dB domain, e.g. `0…−40 dB` matching current presentation.

Add:
- visible `−3 dB` horizontal guide;
- vertical broadside `0°` guide;
- beamwidth bracket at the −3 dB crossings when API beamwidth exists;
- baseline/current overlay toggle or ghost baseline captured from reset/reference response.

Use one color grammar per physical plane consistently across plan view, cut and pseudo-3-D envelope. Do not use color to imply power unless explicitly encoded by a labelled dB scale.

## Grating/sidelobe consequence

The learner must be allowed to choose poor spacing. When the computed pattern visibly develops competing lobes, highlight them **from the API pattern itself**, not from a frontend `d/λ > threshold` rule.

Until Core/API exposes classified lobe locations, UX may emphasize local maxima only as a visual reading aid if labelled `pattern peaks`, not `grating lobes`. Do not claim scientific classification in React.

The strongest visual event in this experiment should be the appearance of a competing angular response, not a warning badge.

## Immediate causal response

When X/along aperture changes:
- plan geometry stretches/contracts along X;
- X aperture bracket changes;
- `Lx/λ` changes;
- corresponding along-track cut changes;
- pseudo-3-D envelope reshapes in that plane.

The orthogonal plane should remain visually stable except where the Scientific Core response actually changes.

Repeat symmetrically for Y/across.

When frequency changes at fixed geometry:
- element locations do not move;
- wavelength readout changes;
- both `L/λ` and `d/λ` change;
- computed patterns and envelope respond.

This distinction is pedagogically essential.

## Motion language

Use `motion/react` for **state transition**, not decorative pulsing:

```tsx
<motion.g animate={{ scaleX, scaleY }} transition={{ duration: .22 }} />
<motion.path animate={{ d }} transition={{ duration: .22 }} />
```

Prefer Motion on the pseudo-3-D envelope and aperture brackets. For high-point-count directivity paths, direct React updates are acceptable if path morphing is unstable.

Use `AnimatePresence` only for appearance/disappearance of advanced annotations or unavailable-state overlays.

Do not animate wave propagation here; D5 is geometry/directivity.

## Relation strip

Below the scene, one low-height strip should make the causal quantities legible:

```text
λ | Y: d/λ · L/λ · BW−3dB | X: d/λ · L/λ · BW−3dB | weighting
```

Values should come from API response or presentation-only ratios of API wavelength + configured physical geometry already sent to the Core. Do not recompute beamwidth.

## Responsive CSS / scrolling

Recommended shell:

```css
.array-grid {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
  min-height:0;
}
.array-stage { min-width:0; min-height:0; }
.array-scene { width:100%; height:auto; max-height:min(68vh,680px); }
```

At narrow widths stack controls above stage. Do not create nested scrolling inside plots. The lab page may scroll vertically when needed; controls may use progressive disclosure rather than an independent long scrollbar.

## Language / accessibility

Use the existing `hydrosim-language-change` event and global PT-BR/EN control. No local language toggle.

The main SVG gets one concise `aria-label` describing current X/Y aperture and beamwidth. Individual element circles should be `aria-hidden` unless selected interaction is later added.

## Current-code preservation / correction

Preserve:
- API debounce/abort behavior;
- `frequency`, X/Y counts/spacings and weighting state;
- authoritative `element_positions_array_frame_m`;
- `across_track_pattern`, `along_track_pattern` and API beamwidths;
- fixed dB clipping presentation.

Correct:
- current `xyPoints()` renormalizes every geometry independently and hides physical aperture changes; replace it with a fixed physical projection;
- current plan layout is disconnected from the directivity cuts; connect them in one stage;
- current readout wall is too dominant; collapse it into spatial annotations + relation strip;
- add the required pseudo-3-D −3 dB envelope without pretending it is a full 3-D power field.

## Do not do

- no steering/delay/phase controls;
- no frontend array-factor or beamwidth formula;
- no adaptive geometry scale that hides aperture change;
- no `N ↑ = beam narrower` message without aperture context;
- no full-field 3-D claim from only two cuts;
- no opacity-as-power encoding;
- no TX×RX two-way combination; that belongs to D7.

## Minimum focused Playwright assertions

1. Changing along-track spacing/count changes physical X layout extent and the along-track directivity path.
2. Changing across-track spacing/count changes physical Y layout extent and the across-track directivity path.
3. Frequency change leaves SVG element physical coordinates unchanged while wavelength/normalized-aperture readouts and pattern path(s) change.
4. Both plots retain the same fixed angular and dB scale at extreme controls.
5. Weighting is behind progressive disclosure and changes API-backed pattern response.
6. Reset restores baseline geometry and beamwidth readouts.
7. Global EN/PT-BR changes labels without a local language button.
8. The pseudo-3-D envelope is labelled as a −3 dB envelope and is absent/marked unavailable when required beamwidth is null.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/pedagogical-explorer.spec.ts -g "array|directivity|D5"
```

Use `npm run test:ui` only as the integration gate after the focused assertions pass.
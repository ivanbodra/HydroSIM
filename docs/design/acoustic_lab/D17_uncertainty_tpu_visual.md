# D17 — Uncertainty / TPU — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D17_uncertainty_tpu.md`  
Production source: `web/pedagogical-explorer/src/UncertaintyLab.tsx`

## Dominant visual mental model

D17 closes the Acoustic Lab by making uncertainty visible as a **computed region of knowledge around a sounding**, not as an error that happened.

The learner should read one causal scene:

```text
input standard uncertainties
        +
measurement geometry
        ↓
Scientific-Core covariance propagation
        ↓
sounding uncertainty geometry
        ↓
which contributor dominates here?
```

The lab must be visually recognizable by one sounding, its beam geometry, a physically scaled uncertainty projection, and contribution traces connected to that same sounding.

## Production direction

Keep `UncertaintyLab.tsx` and its existing `/api/v1/pedagogical/uncertainty/scalar` contract. Do not reproduce covariance/Jacobian/THU/TVU arithmetic in TypeScript.

The current implementation already has useful API orchestration, seven scalar controls, contribution data and a five-angle sweep. The main redesign is hierarchy and semantics: replace normalized decorative panels with one spatial uncertainty instrument and subordinate evidence views.

### Suggested React decomposition

```tsx
<UncertaintyControls />
<UncertaintyWorkspace>
  <SoundingUncertaintyScene />
  <UncertaintyReadoutStrip />
  <ContributionInspector />
  <GeometrySweep />
</UncertaintyWorkspace>
<UncertaintyTheoryDisclosure />
```

Keep these local to D17 unless reuse is proven. Do not create a generic chart framework.

### Hooks and events

Use existing `useState`, `useEffect`, `useMemo` patterns.

Add `useId()` for SVG marker/clip IDs if needed. Use `useMemo()` only for presentation transforms such as fixed-domain screen coordinates, ranked contribution display data and SVG paths. Use `onChange` for scalar sliders. Pointer interaction is appropriate for selecting a sweep angle or contributor, but must only select API-backed evidence; it must not synthesize new scientific values.

## Interaction hierarchy

### Primary first slice

Do **not** present seven equally prominent sliders at first sight. Provide isolated-contributor presets as the pedagogical entry:

- Position only
- Water level only
- Timing only
- Range only
- Sound speed only
- Roll only
- Combined

A preset is allowed to populate the existing seven API inputs; it does not calculate outputs.

Below the preset selector, show the currently relevant uncertainty control prominently. `Combined` reveals all seven.

### Progressive disclosure

Place behind `More / Mais`:

- installation/across offset when not the active preset;
- full seven-input editor;
- raw component values;
- covariance/matrix evidence only when generic API support is deliberately exposed;
- theory/notation.

Coverage factor / expanded uncertainty must remain unavailable until wired to the existing generic Scientific-Core coverage contract. Do not implement `U = k u` locally merely because it is simple arithmetic.

## Dominant spatial scene

Replace the current CSS ellipse whose width/height normalize independently to the current maximum. That construction makes every state visually similar and therefore hides absolute uncertainty magnitude.

Use one native SVG, for example:

```tsx
<svg viewBox="0 0 1000 560" preserveAspectRatio="xMidYMid meet">
```

Scene elements:

1. sonar/transducer origin near upper centre;
2. vertical/down axis and across-track axis with units;
3. current beam/ray to the sounding;
4. sounding point;
5. uncertainty projection centred on the sounding;
6. horizontal and vertical span brackets;
7. optional ghost/reference envelope from the zero or preset baseline.

Use `<line>` for axes/ray/brackets, `<circle>` for sounding, `<ellipse>` only when its axes are explicitly derived from API-backed horizontal/vertical uncertainty summaries, and `<text>` for physical labels.

### Fixed physical scale

Choose a fixed pedagogical uncertainty domain that accommodates the documented slider limits and reference geometry, and keep it fixed across the interaction. If an extreme state exceeds the chosen inset domain, show an overflow cue/value rather than renormalizing the envelope to fill the panel.

The scene may use a magnified **uncertainty inset** around the sounding because the 50 m slant geometry and sub-metre uncertainty cannot share one useful literal pixel scale. If used:

- label the inset scale in metres;
- keep that inset scale fixed across states;
- connect it visibly to the actual sounding location;
- never imply the ellipse is drawn at the same scale as the full 50 m beam scene unless it actually is.

This is preferable to a decorative halo.

### Semantics

Learner-facing labels for current scalar API values:

- `Horizontal standard uncertainty` for `thu_m`;
- `Vertical standard uncertainty` for `tvu_m`;
- `3-D combined standard uncertainty` for `combined_3d_standard_uncertainty_m`.

Do not persistently label the first two simply `THU` / `TVU`; the pedagogy explicitly prevents confusion with IHO 95%-level requirements.

## Contribution inspector

Keep the Core-returned `variance_contributions` and ranked ordering.

Render a compact horizontal bar view using native SVG or CSS bars. Bars represent **variance contribution in m²** and must say so. Do not convert variance to standard deviation in React.

When the learner selects a contributor:

- emphasize its bar;
- emphasize the relevant input control;
- keep the sounding envelope unchanged except through the actual API response;
- optionally draw a thin semantic connector from the contributor panel toward the relevant along/across/down bracket, but only when the Core data supports that directional contribution.

Do not use opacity as a quantitative encoding.

## Geometry sweep

Replace the current normalized five-column bars with a fixed-axis plot tied to the same uncertainty semantics.

Recommended SVG:

```tsx
<svg viewBox="0 0 760 260">
```

x-axis: across-track beam angle `-60° ... +60°`.  
y-axis: standard uncertainty in metres, fixed for the current experiment domain.

Render API-returned points as:

```tsx
<polyline ... />
<circle ... />
```

for horizontal and vertical standard uncertainty. Keep both series on the same y-scale.

Selecting a point updates only the **selected geometry indicator** unless the production API is deliberately changed to make the main sounding scenario selectable. Do not silently substitute the current 45° scenario with a frontend-only calculation.

Symmetric input/model cases must look symmetric in magnitude. Do not introduce port/starboard styling that suggests a magnitude asymmetry absent from the Core.

## Reference/current treatment

Provide a persistent zero/reference ghost when useful:

- zero uncertainty -> sounding point collapses to no envelope;
- current -> computed envelope.

For isolated-contributor experiments, a previous-state ghost may be shown briefly so the learner sees growth direction. It must be clearly a comparison state, not Truth.

Never call the centre point `Truth`. It is the Derived/nominal sounding about which uncertainty is represented.

## Motion language

Use `motion/react` only for transitions that communicate changed uncertainty:

```tsx
<motion.ellipse animate={{ rx, ry }} transition={{ duration: .2 }} />
<motion.line ... />
<AnimatePresence>...</AnimatePresence>
```

Appropriate motion:

- envelope axes grow/shrink after API response;
- horizontal/vertical brackets move with the envelope;
- selected contribution emphasis changes;
- sweep selection marker moves.

Do not continuously pulse the uncertainty envelope; that suggests time variability not present in the scalar contract. Do not animate random samples inside the ellipse; the current API does not provide a probability distribution sample cloud.

## Styling / responsive strategy

Desktop:

```css
.uncertainty-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
}
.uncertainty-workspace { min-width:0; }
.uncertainty-scene { width:100%; aspect-ratio:1000/560; }
```

The spatial scene remains dominant. Contribution inspector and sweep sit below or beside it according to width.

At narrow widths, stack controls above workspace. Avoid internal scrollbars in the SVG, contribution view or sweep. Let the page scroll vertically. Use `clamp()` for gaps and typography.

## EN / PT-BR

Continue the existing global `hydrosim-language-change` event. No local language toggle.

Use technically explicit translations:

- `Standard uncertainty` / `Incerteza-padrão`
- `Horizontal standard uncertainty` / `Incerteza-padrão horizontal`
- `Vertical standard uncertainty` / `Incerteza-padrão vertical`
- `Variance contribution` / `Contribuição para a variância`
- `Expanded uncertainty` / `Incerteza expandida`

Avoid translating uncertainty as accuracy/precision.

## Current-code elements to preserve

Preserve and evolve:

- `Inputs` and current unit conversions (`mrad -> rad`, `ms -> s`);
- `AbortController` request cancellation;
- scalar API as source of scientific outputs;
- `variance_contributions` returned by the Core;
- five authoritative API requests for the sweep;
- global language synchronization;
- `useMemo` ranking as presentation ordering only.

Replace or demote:

- current `THU` / `TVU` shorthand labels;
- `envelopeScale`, `envelopeWidth`, `envelopeHeight` normalization;
- separate equal-weight dashboard panels;
- sweep bars normalized to current maximum.

## Explicit scientific boundaries

React must never:

- construct covariance matrices or Jacobians;
- add standard deviations or variances to create a new uncertainty output;
- derive expanded uncertainty locally;
- invent confidence levels;
- turn an uncertainty envelope into an error vector;
- fabricate Truth or residuals;
- add pitch/heading/full-SVP/detection/dynamic-heave/datum uncertainty controls without a Core contract;
- interpret `combined_3d_standard_uncertainty_m` as universal TPU;
- claim IHO order compliance from the scalar 1σ outputs.

If Truth/error/residual comparison is later exposed, consume the generic Core API and render three visually distinct objects: uncertainty envelope, signed Truth-error vector, and A-B residual.

## Minimum focused Playwright assertions

1. Learner-facing labels say horizontal/vertical **standard uncertainty**, not bare THU/TVU.
2. Zero/isolated preset can drive the API-backed envelope to the expected zero/isolated response.
3. Increasing water-level uncertainty changes the vertical API-backed envelope/readout without frontend arithmetic.
4. Increasing timing uncertainty changes the API-backed result while the displayed vessel-speed scenario remains explicit.
5. Contribution bars preserve `m²` units and ranking updates after an input change.
6. Geometry sweep contains the five API-backed angles on one fixed y-scale.
7. Main uncertainty inset keeps the same physical scale across at least two materially different input states.
8. No local language control; global EN/PT-BR switch updates labels.
9. Reset/preset transitions do not create stale responses after rapid slider changes (`AbortController` behavior remains intact).
10. No learner-facing claim of IHO compliance or 95% confidence appears for the scalar 1σ outputs.

## Validation commands

From `web/pedagogical-explorer`:

```bash
npm run build
npx playwright test <focused-D17-spec>
```

Run the full UI suite only as the integration gate:

```bash
npm run test:ui
```

## Completion condition

D17 is visually complete when the learner can change one uncertainty source, see the physically scaled sounding envelope respond, identify the variance contributor that changed, alter/inspect geometry across the swath, and explain why **uncertainty is neither a realized error nor an IHO compliance verdict** — all without reading a long explanatory card.
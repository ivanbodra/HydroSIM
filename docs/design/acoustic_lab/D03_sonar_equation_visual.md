# D3 — Sonar Equation & Propagation Loss — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D03_sonar_equation.md`  
Production source: `web/pedagogical-explorer/src/SonarEquationLab.tsx`

## Concept to communicate

D3 is not primarily a pair of plots. It is an **acoustic budget being spent and recovered along one two-way path**:

```text
SL
  -> outbound spreading + absorption
  -> bottom return
  -> inbound spreading + absorption
  -> RL
  -> compare with NL
  -> SNR / margin
```

The learner should visually discover four causal distinctions:

```text
range ↑      -> two-way TL ↑ -> RL ↓ -> SNR ↓
SL ↑         -> RL ↑ -> SNR ↑
NL ↑         -> RL unchanged -> SNR ↓
frequency ↑  -> absorption usually ↑ -> long-range margin ↓
```

The visual identity of D3 should be a **journey / energy budget**, with the fixed-scale RL and SNR curves acting as evidence rather than the whole experience.

## Preserve existing production strengths

`SonarEquationLab.tsx` already provides:

- authoritative POST request to `/api/v1/pedagogical/sonar-equation`;
- fixed `RANGE_DOMAIN`, `RL_DOMAIN`, `SNR_DOMAIN`;
- paired primary/comparison frequency requests;
- RL and SNR traces;
- shared range marker;
- core-provided contribution breakdown;
- global EN/PT-BR synchronization;
- reset/retry behavior.

Keep these. Do not recreate transmission-loss or sonar-equation calculations in TypeScript.

## Production composition

Refactor presentation toward:

```tsx
<SonarControls />
<SonarBudgetStage>
  <AcousticJourney />
  <RangeEvidencePlots />
  <BudgetRail />
  <DetectionMargin />
</SonarBudgetStage>
```

This may remain in `SonarEquationLab.tsx` initially. Split into local files only if code clarity materially improves.

## Control hierarchy

The first experiment is range. Control order must therefore be:

1. **Range** — primary, visually dominant.
2. **Source level** — primary.
3. **Noise level** — primary.
4. **Frequency** — primary, but after SL/NL.
5. Comparison frequency — secondary; place in `Compare / Comparar` disclosure or compact compare strip.

The existing environmental/scattering/gain values already sent in `Config` should remain fixed by default. Do not expose them as equal-weight controls merely because they exist in the request body.

Use the current React state pattern:

```tsx
const [config, setConfig] = useState<Config>(initial)
```

Continue with controlled `<input type="range">` values and the existing debounced `useEffect` request. `onInput` is acceptable for continuous sliders; use `onChange` if consistency with neighboring labs is preferred.

## Dominant visual: Acoustic Journey

Add one responsive SVG scene above or alongside the plots.

Recommended viewBox:

```tsx
<svg viewBox="0 0 1000 300" preserveAspectRatio="xMidYMid meet">
```

Scene grammar:

- sonar/transducer at left/top-left;
- simplified water column / path space;
- bottom interaction point toward centre/right;
- return path to receiver;
- optional noise field around receiver;
- small selected-range label attached to the path.

Use native SVG primitives only:

```tsx
<circle />        // transducer / receiver anchor
<path />          // outbound and inbound path
<line />          // range marker / local annotations
<rect />          // bottom strip / compact budget blocks
<text />          // concise labels
```

Do not depict literal acoustic intensity by arbitrary geometric beam width. If line thickness or opacity is varied, it must be clearly presentation emphasis only and must not suggest a calibrated physical amplitude mapping.

### Journey state mapping

React may map API-provided terms to visual emphasis:

- outbound spreading/absorption losses -> labelled deductions on outbound path;
- backscatter strength -> labelled bottom-return contribution;
- inbound losses -> labelled deductions on return path;
- `received_level_db_re_1upa` -> receiver readout;
- `noise_level_db` -> noise reference readout;
- `snr_db` -> final margin readout.

Do not recompute any of these quantities.

## Motion language

Import:

```tsx
import { motion, AnimatePresence } from 'motion/react'
```

Use Motion to clarify sequence, not to decorate continuously.

Recommended uses:

```tsx
<motion.path />
```

for a short travelling highlight along outbound then inbound segments when a control changes;

```tsx
<motion.g />
```

for brief emphasis around the budget term that changed most directly;

```tsx
<AnimatePresence />
```

only for compare-frequency overlay or detection-margin state transitions.

Do not continuously pulse the entire sonar path. Avoid animations that imply sound propagation speed is proportional to range slider motion.

## Budget Rail

Replace the current long vertical list as the main budget representation with a compact horizontal or stepped rail:

```text
SL
↓ spreading
↓ absorption
+ bottom
↓ spreading
↓ absorption
= RL
− NL
= SNR
```

Implement as semantic HTML or SVG, whichever fits the layout best. A strong option is a horizontal rail of compact blocks with signs:

```tsx
<div className="d3-budget-rail">
  <BudgetTerm kind="source" />
  <BudgetTerm kind="loss" />
  ...
</div>
```

Each term displays the API value. Group outbound and inbound losses separately but keep the causal chain readable in one glance.

Keep TX/RX relative beam gains present only if needed for completeness; visually de-emphasize them when fixed at zero.

## RL and SNR evidence plots

Retain two plots, but make them visually secondary evidence under the journey/budget.

Use the existing fixed scales exactly:

```ts
RANGE_DOMAIN = { min: 10, max: 500 }
RL_DOMAIN = { min: 0, max: 220 }
SNR_DOMAIN = { min: -100, max: 180 }
```

Keep the shared selected-range marker in both plots.

Refactor `Plot` if useful, but do not introduce a generic chart library. Native SVG remains sufficient:

```tsx
<path d={currentPath} />
<path d={comparisonPath} />
<line x1={markerX} x2={markerX} ... />
```

Current and comparison frequency must use identical axes so the absorption consequence remains visible.

### Reference/current treatment

The current frequency is the dominant solid trace. The comparison frequency should be a restrained dashed/ghost trace. It must never be autoscaled independently.

If the compare-frequency control is collapsed, keep the comparison trace hidden rather than leaving an unexplained second line.

## Detection margin

Pedagogy requires an explicit margin relative to a clearly labelled SNR reference, but D3 must not become D8's detector.

Implementation rule:

- if the Scientific Core/API already exposes a registered required/reference SNR, render `margin = SNR - reference` from authoritative values;
- if it does **not**, do not invent a threshold in React.

Until API support exists, render only the authoritative SNR readout and a visually reserved placeholder/disabled region labelled in implementation notes, not learner-facing speculative math.

If/when supported, use a simple gauge:

```tsx
<svg viewBox="0 0 360 70">
  <line ... />
  <line className="reference" ... />
  <circle className="current" ... />
</svg>
```

Label it `SNR reference`, not `detector threshold`.

## Interaction-specific causal emphasis

### Range changes

The most important visual sequence:

- range marker moves in both plots;
- path length annotation changes;
- outbound and inbound losses receive brief emphasis;
- RL/SNR result decreases/increases from API response;
- noise readout does not change.

### Source-level changes

- source block receives short emphasis;
- RL and SNR move;
- TL blocks remain visually stable.

### Noise-level changes

This distinction must be especially clear:

- journey up to `RL` stays visually unchanged;
- only the final `NL -> SNR` comparison emphasizes;
- RL curve/readout must not move because noise changed.

Do not animate the outbound/return path for an NL-only edit.

### Frequency changes

- update current RL/SNR curves and absorption term from API;
- selected range remains fixed;
- briefly emphasize absorption terms and frequency label;
- comparison trace stays on the same axes.

## Hooks and local implementation details

Use existing hooks:

- `useState` for config/data/error/loading;
- `useEffect` for API calls and global language event;
- `useMemo` for SVG `path` strings and display-only coordinate transforms.

Optional:

```tsx
const previousDataRef = useRef<Response | null>(null)
```

may be used only to decide which visual region to emphasize after an API response. Do not use it for scientific differencing or model calculations.

`useId()` may be used for SVG `clipPath`, `mask`, or gradient IDs if introduced. Gradients should be decorative context only, not quantitative encodings.

## Responsive CSS

Preferred desktop structure:

```css
.d3-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
}

.d3-stage {
  min-width:0;
  display:grid;
  gap:clamp(.7rem,1.4vw,1.2rem);
}

.d3-journey-svg,
.d3-chart-svg {
  width:100%;
  height:auto;
}
```

At narrow widths, stack controls above stage. Do not create horizontal plot scrollbars. SVG should scale through `viewBox`.

Avoid large nested cards. The journey, plot pair, and budget rail should read as one instrument.

## Language and accessibility

Continue global `hydrosim-language-change`; no local language selector.

Translate:

- axis labels;
- `Outbound / Ida`, `Inbound / Volta`;
- spreading/absorption;
- received level/noise/SNR;
- comparison labels;
- detection-reference copy if supported.

Give the journey SVG one concise `aria-label` containing selected range, RL and SNR. Do not expose every decorative SVG element individually.

Use `<title>` inside SVG when useful.

## Do not do

- no percent-power control unless mapped authoritatively to SL by the Core;
- no TypeScript sonar equation;
- no React absorption model;
- no invented bottom backscatter model;
- no autoscaling RL/SNR plots;
- no claim that higher frequency intrinsically produces finer bathymetry;
- no learner-facing detector threshold that belongs to D8;
- no opacity-as-power proxy;
- no decorative waveform unrelated to API data.

## Minimum focused Playwright assertions

1. Range slider moves the range marker in both RL and SNR SVGs.
2. Increasing range changes authoritative RL/SNR readouts and the two-way-loss display.
3. Changing SL changes RL and SNR but leaves the configured noise value unchanged.
4. Changing NL changes SNR while RL readout and RL path remain unchanged for the same other inputs.
5. Changing frequency changes the absorption readout and current RL/SNR paths.
6. Comparison frequency uses the same fixed axes and appears only in compare mode/disclosure as designed.
7. Budget rail displays the API-provided outbound and inbound spreading/absorption components.
8. Reset restores the canonical initial range, SL, NL and frequency.
9. Global EN/PT-BR change updates D3 controls, axis labels and budget labels without local language chrome.
10. No horizontal scrollbar appears at the supported narrow viewport.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test <focused-D3-spec>
npm run test:ui
```

Use the focused Playwright spec during implementation. Run full `npm run test:ui` only as the integration gate.
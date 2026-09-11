# D2 — Pulse & Signal Processing — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D02_pulse_signal_processing.md`  
Production source: `web/pedagogical-explorer/src/SignalLab.tsx`

## Concept to communicate

The learner must see one causal story:

```text
finite transmission -> waveform occupancy -> signal bandwidth -> matched filter -> compressed response
```

The central contrast is:

```text
CW: longer pulse -> more transmitted energy + poorer raw range resolution
LFM: long energetic pulse + bandwidth + matched filtering -> narrow compressed response
bandwidth ↑ -> compressed response narrows
```

Do not present D2 as three unrelated charts. It should feel like a signal moving through a processing chain.

## Production direction

Keep the existing `/api/v1/pedagogical/signal` request and `SignalResponse` traces in `SignalLab.tsx`. Do not compute range resolution, energy, chirp law, matched filtering or pulse-compression physics in React.

The current API already supports:
- finite waveform;
- instantaneous frequency;
- matched-filter trace.

The pedagogy also requires explicit range-resolution and relative-energy/occupancy outputs. If these are not yet present in the API response, UX must not invent them numerically. Render only presentation proxies whose semantics are explicit, and route a Core/API gap for any required scientific quantity.

## Recommended React decomposition

Refactor only as far as needed for clarity:

```tsx
<SignalControls />
<SignalProcessStage>
  <TxPulsePanel />
  <InstantaneousFrequencyPanel />
  <MatchedFilterPanel />
  <SignalConsequenceStrip />
</SignalProcessStage>
```

If the existing `focus` routing is retained, each focused view must still preserve enough of the chain context that the learner understands where the active stage sits.

Use the current hooks:
- `useState` for `SignalConfig`;
- `useEffect` for debounced API requests and global language events;
- `useMemo` for path generation and screen-coordinate mapping only.

Do not introduce a global chart abstraction.

## Controls and hierarchy

Always-visible primary controls:
1. `CW / LFM` segmented control;
2. pulse duration `τ`;
3. LFM bandwidth `B` when LFM is selected.

Centre frequency `fc` remains visible but visually secondary because D2 is not primarily a propagation or array lesson.

Move these into `<details>` labelled `More / Mais`:
- chirp direction;
- envelope/window.

When CW is selected:
- hide or disable `B`, direction and LFM-only controls without leaving visually dominant dead controls;
- keep duration range appropriate to the existing implementation.

Keep Reset visible.

## Dominant visual composition

Use one wide horizontal process stage. Recommended semantic geometry:

```text
TX PULSE          SWEEP / SPECTRAL CONTENT          MATCHED FILTER
[ waveform ]  ->  [ f(t) / bandwidth ]        ->   [ compressed peak ]
```

This may be implemented as three synchronized SVG panels inside one containing surface rather than three separate cards.

Recommended responsive SVG structure:

```tsx
<svg viewBox="0 0 1200 430" preserveAspectRatio="xMidYMid meet">
```

Native SVG only:
- `<path>` for waveform/frequency/matched-filter traces;
- `<line>` for shared time/lag markers;
- `<rect>` for pulse-duration and bandwidth extents;
- `<text>` for compact labels;
- `<g>` for each processing stage.

Use the authoritative API traces directly.

## TX pulse visualization

Make pulse occupancy visible before emphasizing fine carrier oscillations.

Render:
- one translucent duration envelope rectangle spanning the actual pulse duration;
- the waveform path inside it;
- explicit `τ` bracket beneath the pulse.

For high centre frequencies, do not attempt to make every carrier cycle visually legible at full-pulse scale. Provide either:
- a small magnified inset of several cycles; or
- the existing short `waveWindow` detail, clearly labelled as a zoom.

Do not let the zoom imply that the transmitted pulse duration is shorter than configured.

## LFM instantaneous-frequency visualization

For LFM, connect the pulse and `f(t)` visually.

Use a second panel sharing the same horizontal pulse-time mapping. Render:
- API `instantaneous_frequency` as `<path>`;
- centre-frequency line;
- upper/lower frequency extents;
- a vertical `B` bracket or shaded band showing configured bandwidth.

When chirp direction changes, animate only the path transition or local directional cue. Do not animate frequency in a way that suggests the sound propagates faster.

For CW, collapse the frequency panel to a horizontal line at `fc` and de-emphasize bandwidth.

## Matched-filter visualization

This is the visual payoff of D2.

Render the API `matched_filter` trace on a **fixed/shared lag scale** suitable for comparing configurations. Do not rescale the y-axis to make every peak look equally large or wide if that hides the conceptual change.

Use a ghost/reference trace when comparing two meaningful states:
- previous configuration in low-opacity neutral stroke;
- current configuration in primary accent.

For LFM, when bandwidth increases, the learner should see the compressed response narrow. If an authoritative range-resolution value is available from the API, place it directly below this panel as the primary derived readout.

## Causal animation

Use `motion/react` only to connect stages, not decorate them.

Recommended primitives:

```tsx
import { motion, AnimatePresence } from 'motion/react';
```

Use:
- `motion.path` for short trace morph/fade between configurations;
- `motion.rect` for duration/bandwidth extents;
- `motion.g` for a brief processing-highlight travelling TX -> f(t) -> matched filter after a control change;
- `AnimatePresence` when CW/LFM changes the visible stage content.

Keep animations short (`~150–350 ms`) and deterministic. No continuous decorative pulsing.

## Energy / occupancy presentation

The pedagogy requires a relative pulse-energy indicator at fixed normalized amplitude. Do not compute physical acoustic energy in TypeScript.

If the API exposes a recognized relative-energy quantity, show it as a compact horizontal bar labelled `Relative pulse energy / Energia relativa do pulso`.

If not, the UI may show **pulse occupancy** as the visible duration rectangle but must not label its area as physical energy. Route the missing quantitative output rather than deriving it locally.

## Optional delayed-return bridge

Only implement if the Scientific Core/API supplies or explicitly validates the semantics.

Recommended visual if available:
- a faint delayed echo waveform below the TX pulse;
- shared time axis;
- one travel-time offset marker;
- arrow into the matched filter.

Do not add propagation loss, noise, threshold or bottom-detection behavior here; those belong to D3/D8.

## Styling

Recommended production layout:

```css
.signal-lab .lab-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
  gap:clamp(14px,2vw,24px);
}

.signal-process-stage {
  min-width:0;
  display:grid;
  grid-template-rows:auto 1fr auto;
}

.signal-process-svg {
  width:100%;
  min-height:clamp(360px,52vh,620px);
}
```

Avoid vertical scrolling inside the graph surface. Let the page scroll if the viewport is genuinely small.

Keep nested borders to a minimum; the three stages should read as one instrument.

## Accessibility and language

Use global `hydrosim-language-change`; no local language button.

Each SVG stage should expose one concise `aria-label`, not thousands of sampled points.

Controls must remain keyboard accessible. Segmented CW/LFM buttons should use `aria-pressed` or an equivalent clear state.

## Current-code specific notes

`SignalLab.tsx` already provides:
- `SignalConfig` state;
- authoritative API call;
- `waveform`, `instantaneous_frequency`, `matched_filter` traces;
- `Plot` and `tracePath()`;
- global language sync;
- focused view routing;
- CW/LFM-dependent duration bounds.

Preserve these strengths. Main changes are hierarchy and continuity:
- duration + bandwidth become the first causal experiment;
- chirp direction/envelope become progressive disclosure;
- plots share one process-stage composition;
- duration and bandwidth become visible spans;
- matched-filter compression becomes the primary visual outcome.

## Do not do

- no Recharts/Plotly/D3 dependency for these traces;
- no matched-filter implementation in TypeScript;
- no formula-derived range-resolution value in React if the API does not provide it;
- no claim that centre frequency alone determines range resolution;
- no threshold detector or bottom-pick UI;
- no adaptive scale that makes short/long compressed responses look artificially identical;
- no text-heavy explanation between every stage.

## Minimum Playwright assertions

1. Switching CW/LFM changes visible controls and stage state.
2. Duration slider changes the visible `τ` extent and API-driven waveform.
3. LFM bandwidth slider changes the instantaneous-frequency extent and matched-filter trace.
4. Chirp direction is under progressive disclosure and reverses the LFM frequency trend.
5. Matched-filter plot remains present and comparable across two bandwidth states.
6. Reset restores the canonical reference config.
7. Global EN/PT-BR changes all D2 labels without adding a local language control.
8. If range-resolution output is API-backed, bandwidth increase changes that readout in the expected direction without any frontend calculation.

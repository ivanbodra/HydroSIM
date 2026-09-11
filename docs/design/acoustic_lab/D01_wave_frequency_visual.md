# D1 — Acoustic Wave & Frequency — Visual Implementation Brief

Owner: **UX-A**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D01_wave_frequency.md`  
Production source: `web/pedagogical-explorer/src/WaveLab.tsx`

## Concept to communicate

The learner must see one relationship, not a collection of charts:

```text
frequency ↑ -> period ↓
frequency ↑ at fixed c -> wavelength ↓
```

Amplitude and phase are secondary distinctions. Sound speed is a secondary experiment that changes wavelength without changing frequency.

The lab should feel like **one acoustic field viewed in two coordinated ways**: time and space.

## Production direction

Keep the existing API and fixed scientific domains already present in `WaveLab.tsx`. Do not rewrite wave physics in TypeScript.

### Component structure

Refactor toward these presentation components inside `WaveLab.tsx` or small local files only if the split improves readability:

```tsx
<WaveControls />
<WaveStage>
  <TemporalWaveView />
  <SpatialWaveView />
  <WaveRelationStrip />
</WaveStage>
```

Do not create a generic chart framework for one lab.

### Controls

Primary control must be visually dominant:

```tsx
<input type="range" ... value={frequency} onChange={...} />
```

Order:

1. Frequency — primary, always visible.
2. Normalized amplitude — secondary.
3. Initial phase — secondary.
4. Sound speed — move into `<details>` labelled `More / Mais` or equivalent progressive disclosure.

Keep Reset visible.

Do not present period or wavelength as controls.

## Dominant visualization

Use one large responsive SVG stage containing two synchronized bands rather than two unrelated framed cards.

Recommended `viewBox`:

```tsx
<svg viewBox="0 0 1000 460" preserveAspectRatio="xMidYMid meet">
```

Top band: `p(t)` on the existing fixed time domain.  
Bottom band: `p(x)` on the existing fixed spatial domain.

Reuse the API series already returned as `temporal_waveform` and `spatial_waveform`.

Implement one shared helper for **screen-coordinate mapping only**:

```ts
const mapX=(x:number, domain:Domain, left:number, width:number)=>...
const mapY=(y:number, top:number, height:number)=>...
```

This is presentation logic, not science.

Render paths with native SVG:

```tsx
<path d={temporalPath} className="wave-line temporal" />
<path d={spatialPath} className="wave-line spatial" />
```

Keep amplitude scale fixed. Keep time and distance domains fixed/shared as required by pedagogy.

## Period and wavelength markers

Replace the current isolated marker-line feel with explicit span brackets:

- period `T`: horizontal bracket from one cycle start to the next in the time band;
- wavelength `λ`: horizontal bracket spanning one spatial cycle in the space band.

Use SVG `<line>`, short end ticks and `<text>`.

Animate only the bracket width/position when the relevant value changes:

```tsx
<motion.g animate={{ opacity: 1 }} transition={{ duration: .2 }}>
```

Do not animate the whole chart in a way that suggests propagation speed changes with frequency.

## Immediate causal response

When Frequency changes:

- both waveform paths update;
- `T` bracket visibly contracts/expands;
- `λ` bracket visibly contracts/expands;
- period/wavelength readouts update in one compact strip.

Add a very brief local emphasis (`150–250 ms`) around the two derived outputs using Motion or a CSS class keyed from `frequency`, but do not flash the whole screen.

When Sound speed changes:

- temporal waveform and `T` should not visually imply a frequency change;
- the spatial waveform / `λ` is the visually dominant changed region.

This distinction is required by the pedagogy.

## Relation strip

Replace the current equation block hierarchy with a small, low-height consequence strip beneath the SVG:

```text
f      T      c      λ
200kHz 5µs    1500m/s 7.5mm
```

Optionally place `c = fλ` between `c` and `λ`, but do not make the Euler-form equation a dominant persistent card. If retained, place it behind a small `Theory / Teoria` disclosure.

## Motion language

Use `motion/react` only for:

- transition of cycle/wavelength markers;
- subtle emphasis of changed outputs;
- optional moving phase cursor if it helps compare the two views.

Do **not** use a continuously translating sinusoid as the main visual unless the time/space semantics remain unambiguous. The current pedagogy requires recognition of frequency/period/wavelength, not a full propagating wavefield solver.

## Styling

Recommended layout:

```css
.wave-layout { display:grid; grid-template-columns:minmax(220px,280px) minmax(0,1fr); }
.wave-stage { min-width:0; }
.wave-unified-chart { width:100%; aspect-ratio: 1000 / 460; }
```

Use `clamp()` for major spacing and avoid fixed heights that create unnecessary scrolling.

The time and spatial bands should share visual grammar but have clearly different axis labels.

## Accessibility / language

The SVG needs a concise `aria-label` describing the active frequency, period and wavelength. Do not expose every path point.

Use global `hydrosim-language-change`; do not add a local translation control.

## Current-code specific notes

`WaveLab.tsx` already has:

- fixed `TIME_DOMAIN`, `SPACE_DOMAIN`, `AMP_DOMAIN`;
- authoritative API request;
- language synchronization;
- `TraceSeries` data;
- a `Trace` component and `tracePath()` helper.

Prefer **evolving those pieces** rather than replacing them. The main changes are hierarchy and composition:

- frequency first;
- sound speed progressive disclosure;
- two traces read as one coordinated stage;
- period/wavelength become obvious spatial markers;
- equation/readouts become subordinate.

## Do not do

- no adaptive x-domain;
- no new chart library;
- no source-level/power language for normalized amplitude;
- no propagation loss or absorption visualization;
- no claim that higher frequency automatically improves bathymetric resolution;
- no duplicated scientific calculation of `T` or `λ` in React if API outputs exist.

## Minimum Playwright assertions

1. Frequency slider changes period readout.
2. Frequency slider changes wavelength readout.
3. Frequency change alters both temporal and spatial SVG path `d` values.
4. Sound-speed control is inside progressive disclosure and changes wavelength while frequency remains unchanged.
5. Reset restores reference values.
6. Global EN/PT-BR switch updates D1 labels without a local language button.
7. Fixed chart domains remain present after extreme frequency values.
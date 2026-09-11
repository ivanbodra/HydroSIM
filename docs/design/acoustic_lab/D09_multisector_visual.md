# D9 — Multisector MBES — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D09_multisector_mbes.md`  
Production source: `web/pedagogical-explorer/src/MultisectorLab.tsx`

## Concept to communicate

The learner must distinguish TX sectors from RX beams and understand that sector identity carries geometry, signal configuration and TX epoch.

```text
one swath / ping
 -> one or more TX sectors
 -> sector angle + TX epoch + signal configuration
 -> detections reference the correct sector
```

The dominant image is **one swath assembled from identified TX events**, not a row of configuration cards.

## Production direction

Keep the existing `/api/v1/pedagogical/multisector` contract. The current lab already contains the correct one-sector / three-sector baseline, sector centre/support controls, delay, frequency, pulse duration, coverage supports and transmit groups. Re-compose this into a connected spatial + temporal instrument.

### Component structure

Recommended local decomposition:

```tsx
<MultisectorControls />
<MultisectorStage>
  <SectorGeometryScene />
  <TransmitTimeline />
  <SectorIdentityStrip />
</MultisectorStage>
```

Keep all authoritative values from `Response`. Do not infer sector/RX association in React if the API does not provide it.

## Controls

Primary controls:

1. mode: `One TX sector / Three TX sectors`;
2. selected sector centre;
3. selected sector angular support;
4. selected sector TX delay.

Do not render three full control stacks simultaneously by default. Add a selected-sector control:

```tsx
const [selectedSectorId, setSelectedSectorId] = useState('centre');
```

Clicking a sector in the scene selects it. The side panel then edits that sector only.

Put frequency and pulse duration under:

```tsx
<details><summary>Signal / Sinal</summary>...</details>
```

This follows the pedagogy: they are secondary, not the first discovery.

## Dominant geometry scene

Replace flat horizontal sector bands as the primary visual with a cross-track SVG scene.

Recommended structure:

```tsx
<svg viewBox="0 0 1000 500" preserveAspectRatio="xMidYMid meet">
  <g className="transducer" />
  <g className="tx-sectors" />
  <g className="rx-fan-reference" />
  <path className="seafloor" />
  <g className="coverage-strip" />
</svg>
```

At the top centre, draw a fixed transducer reference. Each TX sector is a wedge/polygon projected downward from the same origin.

Use API `coverage_supports_deg` / sector angular min/max to compute **display geometry only**.

Write a helper that maps angle to a point on a fixed visual radius:

```ts
const polarPoint=(angleDeg:number,r:number,cx:number,cy:number)=>...
```

This is allowed presentation geometry. Do not calculate beam physics.

### TX sectors

Render sectors as translucent wedges with a stable sector identity hue. Do not encode power as opacity.

Each sector wedge should show:

- sector ID near its centreline;
- centre angle line;
- angular support boundary lines;
- selected state with a clear outline, not a brighter “power” fill.

Use `motion.path` so moving centre/support smoothly morphs the wedge:

```tsx
<motion.path animate={{ d: sectorPath }} transition={{ duration:.22, ease:'easeOut' }} />
```

### RX fan reference

Render a faint, fixed set of narrow RX beam lines behind the sectors. These are conceptual only and must not change when the TX sector count changes.

This makes the pedagogical statement `TX SECTORS ≠ RX BEAMS` visible without relying on a paragraph.

Do not generate a physically interpreted RX fan if the Scientific Core does not provide one; keep it as a clearly labelled conceptual reference.

## Gap / overlap experiment

The learner should be able to drag or slider-adjust sector centre/support and immediately see:

- gap: uncovered angular interval highlighted along the bottom coverage strip;
- overlap: shared angular interval cross-hatched or double-outlined;
- contiguous coverage: continuous strip.

The coverage strip must use the same fixed angular scale in one-sector and three-sector modes.

Do not create a second comparison chart. Keep a low-emphasis single-sector reference wedge/outline behind the current multisector configuration when in `multi` mode.

## Transmit timeline

The timeline is equally important to the geometry and must sit directly below it, aligned to sector identity colors.

Use a native SVG or CSS grid timeline with fixed 0–max window derived from the current authoritative response.

Preferred SVG:

```tsx
<svg viewBox="0 0 1000 190">
  {data.sectors.map(...)}
</svg>
```

Each sector row should contain:

- TX start marker at `tx_delay_ms`;
- pulse rectangle spanning authoritative pulse duration;
- TX group label;
- a shared vertical ping epoch line.

When delay changes, animate only the bar x-position. Geometry should remain unchanged if only timing changes. This visual separation is a core pedagogical requirement.

Use `motion.rect` with `animate={{x,width}}`.

## One-sector -> multisector reveal

Start the lab in `single` mode.

When the learner activates `Three TX sectors`:

- keep the same fixed swath scale;
- morph/reveal three identified wedges inside the same overall angular space;
- retain the single-sector outline as a faint baseline ghost for the first transition;
- display the timeline rows below.

Do not imply that “more sectors = more RX beams” or “more sectors = more soundings”.

## Identity strip

Keep one concise statement near the geometry:

```text
TX sectors ≠ RX beams
```

Remove the long explanatory sentence if the geometry/faint RX fan communicates it successfully. Use tooltip/help only if needed.

A compact selected-sector strip can show:

```text
CENTRE · +0°   |   TX +0.35 ms   |   300 kHz   |   0.50 ms
```

Values come from the API response/configured state; labels localize EN/PT-BR.

## Motion / interaction

Use `motion/react` for:

- sector wedge morph when centre/support changes;
- selected sector outline emphasis;
- timeline bar movement when delay changes;
- mode transition from one to three sectors.

Use pointer selection on sector wedges:

```tsx
onPointerDown={()=>setSelectedSectorId(sector.sector_id)}
```

Do not implement freehand dragging of wedge boundaries unless it can be done robustly with the same authoritative inputs. Slider control remains acceptable; clicking the wedge to select it is strongly recommended.

## Styling

Desktop composition:

```text
┌──────────────┬─────────────────────────────────────┐
│ mode         │      spatial TX-sector scene        │
│ sector       │                                     │
│ centre       │                                     │
│ support      │                                     │
│ delay        │                                     │
│ Signal ▸     ├─────────────────────────────────────┤
│ Reset        │      transmit timeline              │
└──────────────┴─────────────────────────────────────┘
```

Target stage ratio roughly 2:1 spatial scene plus a shallow timeline. Avoid stacking multiple full-height cards.

## Current-code specific notes

`MultisectorLab.tsx` already has:

- one-sector and three-sector configurations;
- `configured` array state;
- authoritative API response with `coverage_supports_deg`, `transmit_groups`, `tx_time_s`, `tx_end_time_s`, `wavelength_m`;
- delay/frequency/duration controls;
- language synchronization;
- reset;
- a current CSS-based timeline.

Preserve the API/state logic. The main refactor is visual and interaction hierarchy:

- one selected sector instead of three repeated primary-control blocks;
- spatial sector fan becomes primary;
- timeline becomes visually linked to the same sector identity;
- fixed RX reference visually proves sectors are not beams;
- gap/overlap consequence appears in the same scene.

## Do not do

- no opacity-as-power encoding;
- no assumption that all MBES have exactly three sectors;
- no claim that sector frequency changes intrinsically improve resolution/coverage;
- no fake acoustic crosstalk;
- no invented RX-beam association;
- no motion stabilization controls here unless supported by the pedagogical/core contract;
- no new chart library.

## Minimum Playwright assertions

1. Initial state displays one TX sector on a fixed angular scale.
2. Switching to three sectors displays three selectable sector wedges while the RX reference remains unchanged.
3. Changing selected-sector centre changes the wedge geometry.
4. Changing angular support changes coverage and can produce a visible gap/overlap state.
5. Changing TX delay moves the sector timeline bar without changing its sector wedge geometry.
6. Frequency/pulse controls are behind progressive disclosure.
7. Reset returns to one-sector baseline.
8. Global EN/PT-BR switch updates labels without a local language button.
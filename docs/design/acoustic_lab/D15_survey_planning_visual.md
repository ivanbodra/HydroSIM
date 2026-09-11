# D15 — Survey Planning — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D15_survey_planning.md`  
Production source: `web/pedagogical-explorer/src/SurveyPlanningLab.tsx`  
Scientific contract: `docs/science/ped_d16_survey_planning_contract.md`

## Dominant visual mental model

D15 is a **hydrographer's planning table**, not a metrics dashboard.

The learner should visually perform this decision:

```text
area + expected usable swath
 -> rotate line family
 -> choose spacing / overlap
 -> inspect nominal strips
 -> expose gap or margin
 -> pay acquisition effort
```

The signature image is a large local-metre plan view where line centrelines and their nominal swath strips visibly rearrange under direct planning controls. A persistent visual boundary must state that these strips are **planned/nominal**, never verified field coverage.

## Preserve from current production

`SurveyPlanningLab.tsx` already has an unusually strong API-backed slice. Preserve:

- `/api/v1/pedagogical/survey-planning` request;
- Core-generated clipped line segments and coverage polygons;
- area dimensions;
- depth/sector upstream sonar controls;
- overlap and explicit-spacing modes;
- line direction;
- intentional-gap action;
- vessel speed with **time-only** consequence;
- requested/actual spacing distinction;
- coverage classification;
- line count, total on-line length and idealized on-line time;
- baseline/current snapshot mechanism;
- global language synchronization.

Do not move any line placement, clipping, overlap/gap, swath or time calculation into TypeScript.

## Main design change

The current SVG map is scientifically useful but visually buried inside a card/readout hierarchy. Make the **map the instrument** and move numeric metrics into annotations/compact consequence strips around it.

Desktop:

```text
┌ controls 270 px ┐ ┌──────────────── planning table ────────────────┐
│ AREA             │ │ fixed local-metre SVG                         │
│ depth / sector   │ │ area + strips + centrelines + direction       │
│                  │ │ overlap/gap drawn spatially                   │
│ PLANNING         │ │ optional baseline ghost                       │
│ overlap/spacing  │ └────────────────────────────────────────────────┘
│ direction        │ [coverage state] [lines] [length] [time]
│ speed            │ baseline/current decision strip
└──────────────────┘
```

At <= 900 px controls stack above map. No internal map scrollbar. Preserve aspect ratio and allow normal page scroll.

## Controls and progressive disclosure

Primary, always visible:

1. survey area length and width;
2. reference depth;
3. line direction;
4. spacing mode;
5. overlap **or** explicit line spacing;
6. `Create intentional gap / Criar lacuna intencional`.

Secondary:

- angular sector if it changes canonical usable swath;
- vessel speed, explicitly marked `time only / somente tempo`.

Progressive disclosure `<details>`:

- beam count. Keep it because current request accepts it, but visually demote it. It must never read as a swath-width planning knob by itself.

Keep Reset with `RotateCcw`. Use `Compass`, `Map`, `Route`, `Ship`, `TriangleAlert` only for controls/status/navigation.

## React structure

Keep state/API ownership in `SurveyPlanningLab`.

Recommended presentation split:

```tsx
<SurveyPlanningControls />
<PlanningTable>
  <PlanMap />
  <CoverageConsequenceStrip />
</PlanningTable>
<PlanComparison />
```

Use existing `useState` and `useEffect` request flow. Keep the current short request debounce/abort behavior.

Use `useMemo` for SVG coordinate transforms and rendering only. Never calculate planned lines or coverage polygons in `useMemo`.

Add presentation-only state if needed:

```ts
const [showBaselineGhost, setShowBaselineGhost] = useState(true)
const [selectedLineIndex, setSelectedLineIndex] = useState<number | null>(null)
```

Selection may highlight an existing Core line/strip; it must not alter planning science.

## Plan-map SVG

Retain native SVG and Core-provided metre coordinates. Evolve the existing implementation instead of introducing a chart/map library.

Use a stable `viewBox` derived from **survey-area dimensions plus a fixed proportional margin**. Do not normalize lines independently.

Required primitives:

- `<rect>` survey boundary;
- `<polygon>` authoritative coverage strips;
- `<line>` authoritative planned centrelines;
- `<line>`/`<path>` direction arrow / heading reference;
- `<text>` concise line indices only when legible;
- `<path>`/`<polygon>` baseline ghost if baseline comparison is enabled.

Use `<defs><pattern>` only if helpful to distinguish nominal coverage from verified data. A restrained hatch is preferable to heavy opacity overlays because it visually communicates “planned region” rather than acoustic intensity.

### Coverage state must be spatial

Do not rely on a `Gapped`/`Overlapping` card.

For overlap:
- allow intersecting nominal strips to show a neutral overlap texture/boundary;
- optionally annotate one representative overlap bracket with Core `overlap_width_m`.

For gap:
- show the uncovered corridor between strips as the map background exposed through the nominal strips;
- add one explicit bracket/annotation from Core `gap_width_m`;
- `TriangleAlert` may accompany the annotation, not replace the geometry.

For touching:
- show adjacent strip boundaries meeting without inventing margin.

## Direct manipulation — limited and honest

The current Core accepts line direction and spacing values, so UX may add map-adjacent direct manipulation **only as an input proxy** to existing controls.

### Direction handle

A compass/direction handle can use pointer interaction:

```tsx
onPointerDown
onPointerMove
onPointerUp
```

Convert pointer angle to the same discrete degree input accepted by the existing slider, then call `set('direction', snappedAngle)`. This is UI input mapping, not planning science.

Do not drag individual Core-generated survey lines independently; that would imply arbitrary line placement not represented by the contract.

### Spacing handle

Optional: in explicit-spacing mode, a bracket between two representative centrelines can act as a drag affordance. Convert pointer distance in the known SVG metre transform to the existing `spacing` input, clamp to the current allowed input domain, and let the API regenerate the plan. Do not locally move the lines while waiting for Core response; a brief preview bracket may move, but authoritative lines update only from API.

## Nominal != achieved boundary

Keep this distinction persistent, but reduce prose.

Recommended visual treatment:

```text
NOMINAL PLAN
hatched strips = expected usable coverage
FIELD COVERAGE -> must be verified
```

Use a small persistent banner/legend integrated into the map corner. Do not simulate weather, reflectivity, motion or SSP degradation here because the current Core does not.

The map should never use wording such as `coverage complete` without `nominal` qualification.

## Requested versus actual spacing

When edge anchoring makes `actual_spacing_m` differ from `requested_spacing_m`, visualize the distinction:

- requested spacing: small ghost/reference bracket;
- actual spacing: solid bracket between Core line centrelines;
- compact text `requested 120 m / actual 112 m`.

Do not recompute actual spacing from SVG coordinates if API provides it.

## Direction experiment

Rotating direction must visibly change:

- clipped line orientation;
- cross-line span;
- line lengths/count where Core changes them;
- traversal direction cue.

`α` and `α + 180°` should look like the same geometric line family with reversed traversal sense. Do not create a false geometry change just to make the control feel active.

Use `motion/react` to interpolate presentation between successive **authoritative** line/strip states only when matching elements is stable. If polygon morphing is unreliable, prefer a 120–180 ms cross-fade with `AnimatePresence`; never invent intermediate survey geometry that the Core did not return.

## Baseline/current comparison

The current comparison is mostly rows of numbers. Make it decision-oriented.

When baseline exists:

- optional baseline line family/strip boundaries as a thin dashed ghost on the same map;
- current remains solid;
- toggle `Baseline ghost` if visual density becomes excessive;
- below map, show only decision metrics:
  `actual spacing | lines | total on-line length | time | nominal coverage state`.

Swath may remain if it changed upstream.

The learner should be able to answer: **what margin did I buy, and what effort did it cost?**

## Speed treatment

Speed is explicitly time-only in the current contract.

When speed changes:

- map geometry must remain pixel-identical after the new API result if no other setting changed;
- only idealized on-line time receives a brief local emphasis.

Never animate vessel dots moving faster across lines; that would imply acquisition-density/quality effects not modeled here.

## Motion language

Use Motion sparingly:

- `motion.g`/`motion.path` for short authoritative plan transitions when safe;
- `AnimatePresence` for overlap/gap annotation state;
- 150–250 ms emphasis on changed effort metric;
- baseline ghost fade.

No perpetual route animation. No moving vessel as a proxy for survey execution.

## CSS

```css
.d15-grid {
  display:grid;
  grid-template-columns:minmax(240px,290px) minmax(0,1fr);
  gap:clamp(14px,2vw,28px);
}
.d15-stage { min-width:0; }
.d15-map svg { width:100%; height:auto; display:block; }
@media (max-width:900px) {
  .d15-grid { grid-template-columns:1fr; }
}
```

Existing classes use `d16-*`; UX should rename them to `d15-*` when safe because this is pedagogical D15. Do that as a focused styling/test refactor, not a broad application rename. If existing automated selectors depend on `d16-*`, update the focused D15 tests in the same PR.

## EN/PT-BR and accessibility

Continue `hydrosim-language-change`; no local language switch.

SVG `aria-label` should summarize area, direction, line count and nominal coverage state. Individual survey lines should not all become verbose accessibility nodes; expose selected-line details through one accessible readout.

Coverage must not depend on color alone: combine line style, hatch/boundary and text state.

## Scientific prohibitions

- no frontend swath calculation;
- no frontend line placement/clipping;
- no frontend overlap/gap classification;
- no implication that nominal strips are achieved coverage;
- no fixed overlap percentage presented as universally sufficient;
- no beam-count -> swath-width visual shortcut;
- no speed -> density/SNR/quality effect;
- no turns, run-ins, cross-lines, transits or delays added to Core time;
- no non-rectangular area/exclusion zones until contracted by Core;
- no terrain/weather/current/SSP degradation simulation in D15.

## Minimum focused Playwright assertions

1. Changing overlap changes authoritative strip spacing and planning effort.
2. `Create intentional gap` switches to explicit spacing and produces a spatially visible uncovered corridor plus `gapped` nominal state.
3. Requested versus actual spacing are both visible when edge anchoring makes them differ.
4. Changing direction rearranges Core lines; `α + 180°` preserves the line family geometry while traversal cue reverses.
5. Changing speed leaves plan geometry unchanged and changes idealized time only.
6. Beam count remains in progressive disclosure and does not present itself as a primary swath control.
7. Baseline ghost/current comparison uses the same map coordinate system.
8. All coverage wording remains explicitly nominal/planned.
9. Reset restores defaults.
10. Global EN/PT-BR switch updates D15 labels.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/survey-planning-lab.spec.ts
```

Use the repository's actual focused filename if different. After focused assertions pass, use:

```powershell
npm run test:ui
```

as the integration gate only.
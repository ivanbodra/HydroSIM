# D13 — Timing, Synchronization & Latency — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D13_timing_sync_latency.md`  
Production source: `web/pedagogical-explorer/src/TimingLab.tsx`  
Scientific/API path: `src/hydrosim/app/timing_api.py`

## Dominant visual mental model

D13 should feel like a **scientific timeline editor where the learner can see a correct measurement become the wrong state for a sonar event because of time**.

The screen must visually separate:

```text
MEASURED at t_sample
      ↓ latency
AVAILABLE at t_available
      ↓ causal selection at TX
USED for sonar event t_TX
      ↓ moving platform
SPATIAL / STATE CONSEQUENCE
```

The learner must never confuse update rate, latency and synchronization. The first production slice can fully teach cadence + fixed latency + causal sample association because those exist in the Core. Clock offset/synchronization remains a visually reserved but disabled/future stage until Core/API supports it.

## Production architecture

Keep `TimingLab.tsx` and `/api/v1/pedagogical/timing`. Do not recreate sample-selection or timing-consequence equations in React.

Refactor presentation toward:

```tsx
<TimingControls />
<TimingStage>
  <EventTimeline />
  <CadenceLane stream="position" />
  <CadenceLane stream="attitude" />
  <AssociationInspector />
  <PositionConsequence />
</TimingStage>
```

Use `useState` for current learner controls/selected stream and stage disclosure; retain `useEffect` for API and language synchronization; use `useMemo` for projected timeline ticks and SVG paths; `useRef` only if measuring a responsive container is unavoidable (prefer `viewBox`); `useId` for SVG marker/gradient IDs.

## Guided controls

The current ten-slider wall must be staged.

### Stage 1 — `Cadence & latency`
Always visible:
1. selected stream (`Position` initially; `Attitude` as second tab/segmented button);
2. selected stream update rate;
3. selected stream latency;
4. vessel speed when Position is selected;
5. Reset.

Use existing checkbox state only if multi-stream comparison is intentionally active. For the first lesson, a single selected stream is clearer than two equal association cards.

### Stage 2 — `Ping timing`
Progressive disclosure via `<details>` or compact accordion:
- TX delay;
- RX start delay;
- receive-window duration;
- stream start / first-sample epoch.

### Stage 3 — `Synchronization`
Render as an explicit future/locked lesson only if useful, labelled that Core support is required. Do **not** create a clock-offset slider in React.

The existing generic `Timeline latency` control should be removed from the dominant control stack unless it has a distinct API-backed pedagogical role. Per-stream latency is the causal lesson.

## Main SVG timeline

Replace percentage-positioned HTML events with one native SVG timeline so every event shares one fixed coordinate system.

Recommended:

```tsx
<svg viewBox="0 0 1100 520" preserveAspectRatio="xMidYMid meet">
```

Use a fixed/shared time domain for the current lesson (the existing 0–70 ms domain is acceptable while inputs fit it). Do not autoscale after every slider move.

### Required lanes

1. **Sonar events** — trigger, TX, RX start, RX end.
2. **Measurement epochs** — periodic sample ticks for selected stream.
3. **Availability epochs** — corresponding ticks shifted by API/configured latency.
4. Optional comparison stream lane when the learner explicitly enables comparison.

SVG primitives:

```tsx
<line />      // lane baselines, TX epoch, sample→availability connectors
<circle />    // sample epochs
<rect />      // availability markers / receive window
<path />      // causal connector to selected sample
<text />      // concise event/time labels
```

Use `<defs><marker>` only for arrowheads that clarify direction from sample to availability/association.

## Periodic cadence rendering

The current API returns the retained association plus generic timeline events, not necessarily every periodic sample tick. The UX may generate **display ticks** from the API/configured `update_rate_hz`, `sample_period_s`, stream start and latency because this is deterministic presentation of the registered cadence, but must not independently decide which sample is causally selected.

Render at least the visible ticks around TX:

- measurement tick at `t_n`;
- availability tick at `t_n + latency`;
- thin connector between them.

The **selected sample** must come from `Association.sample_time_s` / `availability_time_s`, not from frontend selection logic.

If generated display ticks cannot be made identical to Core cadence semantics, request an API tick list instead of guessing.

## Causal association visual

Draw a strong vertical TX line through all lanes.

For the retained sample:
- emphasize its measurement tick;
- emphasize its availability tick;
- connect availability to TX with a path/arrow labelled `latest available at TX` / `mais recente disponível no TX`;
- draw a bracket from sample epoch to TX labelled `sample age`.

If `available === false`, show no connector and a clear empty causal state: **no sample available at TX**. Never select a future sample visually.

This is the central D13 interaction.

## Position spatial consequence

Below the timeline, add a fixed-scale horizontal vessel strip for Position:

```text
sample-epoch vessel ghost  -------- Δx -------->  TX vessel
```

Use a simple vessel glyph/path twice:
- ghost/reference at the position represented by the retained sample;
- current/Truth-at-TX marker.

Use `along_track_timing_consequence_m` directly from API for the signed separation. Do not calculate `v × Δt` in React even though the simplified Core model is known.

Keep the physical distance scale fixed across the experiment so increasing vessel speed at unchanged sample age visibly increases separation.

For Attitude, replace this strip with a compact **sample-age-only** panel. Do not turn attitude milliseconds into degrees or metres until D11/Core supplies the time-varying angular state contract.

## Ping events

Use the same timeline for trigger, TX, RX start and RX end. Render receive window as a horizontal `<rect>` band from RX start to RX end, not merely two event markers.

The learner should see that TX is a precise event epoch and that receive-window timing is separate from sensor association.

If D9 later supplies sector-specific TX epochs, add one TX line per sector with stable sector identity; do not collapse them into a generic ping epoch.

## Synchronization visual — reserved contract

Once Core/API exposes `Δt_clock` / common-time basis, extend the same scene with two aligned rulers:

```text
COMMON / TRUTH TIME
SENSOR-REPORTED TIME
```

Clock offset should shift reported timestamp alignment while leaving the physical measurement event fixed. Latency must continue to move availability, not measurement epoch.

Until then, **do not animate or simulate clock synchronization**. A disabled `Synchronization — scientific model pending` disclosure is preferable to false behavior.

## Motion language

Use `motion/react` only for physically meaningful transitions:

- `<motion.circle>` measurement/availability tick movement when rate/latency changes;
- `<motion.path>` causal connector switching to a different retained sample;
- `<motion.g>` vessel ghost/current separation as API consequence changes;
- `<AnimatePresence>` for available/unavailable state and Position/Attitude consequence swap.

Transitions around 180–280 ms are enough to preserve causality without making the timeline feel delayed.

Do not continuously move a clock cursor; the lesson is event association, not decorative passage of time.

## Fixed/reference treatment

- fixed time axis during a guided experiment;
- fixed physical distance scale in Position consequence;
- retain a subtle baseline/reference marker for zero-latency/high-rate configuration when useful;
- do not normalize sample-age or Δx bars independently per state.

A poor configuration should remain visible rather than being rescued by autoscaling.

## Responsive CSS / scrollbar policy

Recommended:

```css
.timing-grid {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
  min-height:0;
}
.timing-stage { min-width:0; }
.timing-svg { width:100%; height:auto; }
```

On narrow screens stack controls above the timeline. The page may scroll vertically. Do not put a horizontal scrollbar inside the timeline; preserve the full SVG with `viewBox`. Progressive disclosure prevents the controls column from becoming an independent scroll trap.

## Language / accessibility

Continue using `hydrosim-language-change`; no local language button.

Main SVG `aria-label` should state selected stream, update rate, latency, TX epoch, retained sample age and availability status. Decorative tick marks are `aria-hidden`.

Use `lucide-react` only for Reset/disclosure/navigation cues. Clock icons are not the scientific timeline.

## Current-code preservation / correction

Preserve:
- current API request/AbortController behavior;
- selected streams, update rates, per-stream latency, vessel speed and ping timing inputs;
- API `Association` fields and causal unavailable state;
- explicit attitude boundary (age only, no metre conversion);
- global language sync.

Correct:
- replace ten equal sliders with staged control hierarchy;
- replace HTML/percentage event placement with fixed-domain SVG;
- add periodic sample and availability ticks around TX;
- make `sample → available → selected at TX` the visual center;
- turn Position consequence from a text card into a fixed-scale spatial separation;
- demote/remove generic `Timeline latency` from the main lesson;
- do not claim synchronization until Core clock-offset support exists.

## Do not do

- no frontend causal sample selector;
- no future sample used at TX;
- no latency == clock-offset visual treatment;
- no update-rate == latency language;
- no attitude-age-to-metres conversion;
- no full sounding-error claim from position Δx;
- no autoscaling that hides worsening sample age/position consequence;
- no decorative packet animation suggesting transport behavior the Core does not model.

## Minimum focused Playwright assertions

1. Reducing Position update rate changes visible cadence spacing and API-backed retained sample age on the fixed time axis.
2. Increasing Position latency moves availability markers later without moving their measurement ticks.
3. Selected-sample highlight matches API `sample_time_s`/`availability_time_s` and never selects an availability after TX.
4. A configuration with no causal sample renders the explicit unavailable state and no causal connector.
5. Increasing vessel speed with unchanged timing association changes API-backed spatial separation while sample age remains unchanged.
6. Attitude mode shows sample age but no metre consequence.
7. Ping-timing disclosure changes TX/RX events and receive-window rectangle on the same fixed axis.
8. Global EN/PT-BR changes labels without local language control.
9. No enabled clock-offset/synchronization control exists until API support is present.

## Validation commands

From `web/pedagogical-explorer`:

```powershell
npm run build
npx playwright test tests/pedagogical-explorer.spec.ts -g "timing|latency|D13"
```

Use `npm run test:ui` only as the integration gate after focused tests pass.
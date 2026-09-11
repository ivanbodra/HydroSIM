# D12 — PU & Sensor Integration — Visual Implementation Brief

Owner: **UX-B**  
Pedagogy authority: `docs/pedagogy/acoustic_lab/D12_pu_sensor_integration.md`  
Production source: `web/pedagogical-explorer/src/PuSensorLab.tsx`  
Scientific/API: `src/hydrosim/integration/pu_sensor.py`, `src/hydrosim/app/pu_sensor_api.py`

## Dominant visual mental model

**A cable is not integration. A sensor stream becomes eligible for use only when each interface layer satisfies the PU input contract.**

The lab must read as a diagnostic stack:

```text
SENSOR ROLE
   -> TRANSPORT
   -> PROTOCOL / MESSAGE
   -> CADENCE
   -> TIME SOURCE
   -> PU INPUT CONTRACT
   -> CONFIGURATION COMPATIBLE / REJECTED AT ONE LAYER
```

The learner should be able to break one layer and see exactly where the stream stops. D12 must not look like generic animated packets entering a computer.

## Critical production boundary

The current Core/API evaluates **configuration compatibility only**. It does not simulate packet delivery, electrical integrity, latency, jitter, observation values or scientific sensor accuracy.

Therefore:
- do not animate packets moving through the cable/network as if runtime delivery were simulated;
- do not use blinking link lights to imply measured network health;
- do not infer timing correctness from accepted timestamp-source semantics;
- keep latency/jitter/event alignment for D13.

The current `PuSensorLab.tsx` incorrectly embeds the `PU-A` acceptance profile in the request body in React. The pedagogy explicitly identifies moving that contract to a registered Scientific-Core/API profile as a next-version requirement. UX-B must **not expand or duplicate that frontend acceptance logic**. If the API cannot yet provide/select a registered profile, preserve the existing slice but visually label it as the current configured profile and route the API-profile blocker rather than inventing new rules.

## Recommended React decomposition

```tsx
<PuIntegrationControls />
<PuContractHeader />
<IntegrationStage>
  <SensorNode />
  <IntegrationLayerStack />
  <PuInputNode />
</IntegrationStage>
<NominalCadenceStrip />
<DiagnosticReason />
```

Local subcomponents are appropriate because the current single return block is dense. Keep state ownership in `PuSensorLab`.

Hooks:
- `useState` for learner stream settings and selected layer if inspection is supported;
- `useEffect` for API request + global language event;
- `useMemo` for display labels and API-returned layer/status mapping only;
- `useId` for SVG marker IDs if needed;
- no timer/`requestAnimationFrame` loop for packet animation.

## Layout and hierarchy

Desktop:

```css
.pu-layout {
  display:grid;
  grid-template-columns:minmax(220px,280px) minmax(0,1fr);
  min-height:0;
}
.pu-stage { min-width:0; }
```

The right side should contain one dominant horizontal integration scene, not a top flow card + status card + four equal readout cards + reason card.

Recommended scene SVG:

```tsx
<svg viewBox="0 0 1100 420" preserveAspectRatio="xMidYMid meet">
```

At narrow widths, stack controls above stage and allow the page/lab shell to scroll vertically. Do not add horizontal scroll to the scientific scene; use SVG scaling and compact labels.

## Controls

Primary guided controls:
1. sensor/device class;
2. transport;
3. protocol;
4. message/datagram;
5. update rate;
6. timestamp source.

Transport-specific controls appear conditionally:
- serial -> port/baud controls supported by the API/profile;
- network -> network transport/endpoint controls when exposed by the production model.

Do not show serial baud as an active concept when Network is selected.

Reset stays visible.

For the first production slice, `PU-A` can remain the visible fixed destination if the API has only that contract. When multiple registered profiles become available, use a profile selector supplied by API data; never hard-code a new acceptance matrix in React.

## Dominant SVG: layered integration path

Build the stage from native SVG. The scientific visualization is the path itself; `lucide-react` icons may identify Sensor/PU controls but must not replace it.

### Nodes

Left: sensor role/device class node.  
Right: PU input/profile node.

Use `<rect>`, `<text>`, and simple connector `<line>`/`<path>` geometry.

Between them place five explicit layer gates:

```text
TRANSPORT | PROTOCOL/MESSAGE | CADENCE | TIME SOURCE | PU INPUT
```

Each gate should have one of:
- pass;
- fail;
- not-applicable/unknown only when the API contract actually yields that state.

### Deriving gate states

Do not create independent compatibility rules in TypeScript. Map API `reason_codes` to the visual layer that failed:

```ts
const reasonToLayer: Record<ReasonCode, LayerId> = {
  transport_mismatch: 'transport',
  serial_baud_mismatch: 'transport',
  missing_required_connection_parameter: 'transport',
  protocol_mismatch: 'protocol',
  message_mismatch: 'protocol',
  update_rate_out_of_range: 'cadence',
  time_source_mismatch: 'time',
  device_class_mismatch: 'role',
};
```

This mapping is presentation taxonomy, not a new acceptance rule: status and reasons still come from the API.

If the API later returns structured per-layer results, delete this mapping and consume those fields directly.

### Visual state

A failed layer should be the strongest mark. Earlier/later layers remain legible so the learner sees that one local error does not rewrite unrelated settings.

Use shape + icon/text, not color alone:
- pass: small check mark / `PASS`;
- fail: cross / `REJECTED HERE`;
- overall endpoint: `CONFIGURATION COMPATIBLE` or `NEEDS CORRECTION`.

Avoid simply turning the entire path red.

## Motion language

Use `motion/react` only for state transitions after API results:
- `motion.g` for a gate changing pass/fail;
- `motion.path` for a short causal highlight from selected control to the affected gate;
- `<AnimatePresence>` for transport-specific control groups and diagnostic reason changes.

Recommended duration `150–250 ms`, no looping.

Do **not** animate packet dots traversing the path. The Core does not simulate packet transfer.

A subtle one-shot connector emphasis after a valid response is acceptable if clearly a UI transition rather than packet telemetry.

## Visible PU contract

The learner must know what is being tested. Add a compact contract header/panel near the PU node, sourced from API/profile data when available:

```text
PU-A
accepts: POSITION / ATTITUDE
transport: SERIAL / NETWORK
rate: 1–20 Hz
clock semantics: GNSS UTC / PU RECEIVE
```

Do not teach these values as universal hydrographic limits. Label them `Selected profile / Perfil selecionado`.

Until the API returns the profile, do not duplicate the full acceptance list into another frontend constant just for display. Use only information already returned or route the blocker.

## Nominal cadence visualization

The API already returns `nominal_update_period_s`. Use it to build a **nominal sampling ruler**, not a live timing simulation.

Example SVG strip:

```tsx
<svg viewBox="0 0 800 90">
  <line ... />
  {ticks.map(x => <line key={x} ... />)}
  <text>10 Hz · 100 ms nominal interval</text>
</svg>
```

Tick positions are screen-layout repetition based on the API-derived period/rate; they do not represent measured packet arrivals.

Use a fixed visible time window (for example one second) so changing update rate visibly changes tick density on a shared scale. Label it `Nominal cadence / Cadência nominal`.

No jitter, latency or clock offset in D12.

## Interaction sequence encoded in UX

The interface should make the canonical sequence easy without a tutorial wall:

1. default compatible position stream;
2. learner changes baud -> transport gate fails;
3. repair -> protocol/message gate can be broken;
4. change sensor role -> role/input mismatch visible without changing the wire;
5. change rate -> cadence gate fails outside profile range;
6. change time source -> time-source gate fails;
7. switch Serial/Network -> transport-specific controls swap, semantic stream controls persist.

Use brief contextual labels at the failed gate rather than paragraphs.

## Diagnostics

Replace the current generic reason block hierarchy with a diagnostic callout anchored visually to the failed gate. The prose comes from the existing localized `reason_codes` mapping.

When compatible, say **Configuration compatible / Configuração compatível**, not merely `Compatible`, to preserve the scientific boundary.

Never say:
- `sensor valid`;
- `data synchronized`;
- `packet received`;
- `measurement accurate`.

## Multi-stream suite

Pedagogy allows this only after the single-stream mechanism is understood. Do not implement a frontend-only suite by evaluating multiple hard-coded contracts locally.

If the Core/API later returns multiple independently evaluated streams, add an `Integrated suite / Conjunto integrado` disclosure that reuses the same layer-stack component in compact form for Position, Attitude, Sound Speed and Sonar/external streams.

Until then, leave this out rather than faking integration.

## Language and accessibility

Use global `hydrosim-language-change`; no local language toggle.

Each layer gate should have visible text and an accessible label such as `Protocol/message: rejected — message not accepted`.

The main SVG can use `role="img"` plus a concise dynamic `aria-label`; do not expose every connector primitive.

Preserve technical identifiers (`PU-A`, protocol/message IDs, Hz, ms) while translating descriptive labels.

## Current-code-specific changes

`PuSensorLab.tsx` already provides:
- device class;
- Serial/Network selection;
- baud;
- protocol/message;
- update rate;
- timestamp source;
- API `status`, `reason_codes`, summary and nominal period;
- conditional baud control;
- global language sync.

UX-B should preserve those pieces and change the visual hierarchy from:

```text
sensor -- link -- PU
+ overall badge
+ readout cards
+ reason list
```

to:

```text
sensor -> [layer gates with local state] -> visible PU contract
                     |
              diagnostic reason
              nominal cadence
```

Do not add frontend acceptance logic while doing this visual rework.

## Scientific/API blocker to respect

The acceptance profile is currently constructed in React. A fully correct `visible PU contract` and future multiple-profile selector require the profile to be registered/provided by Scientific Core/API. UX-B may proceed with the visual layer-stack using current API reason/status outputs, but must not expand the hard-coded profile. Route the profile-registration requirement to software/scientific ownership if not already tracked.

## Minimum focused Playwright assertions

1. Default stream renders overall `Configuration compatible` and all applicable layer gates passing.
2. Unsupported serial baud causes only the Transport gate to be the highlighted rejection and displays the API-backed diagnostic reason.
3. Protocol/message mismatch highlights Protocol/Message rather than Transport.
4. Rate outside the accepted profile range highlights Cadence and changes nominal cadence ticks/readout from the API-derived period.
5. Timestamp-source mismatch highlights Time Source without implying latency/jitter.
6. Switching Serial -> Network removes/hides the baud control while retaining logical stream controls.
7. No packet-motion loop/telemetry indicator is required for compatibility state.
8. Reset restores the compatible default stream.
9. Global EN/PT-BR switch updates labels without a local language button.
10. Error/loading states remain usable.

Suggested focused validation command after implementation:

```powershell
cd web/pedagogical-explorer
npm run build
npx playwright test tests/pu-sensor-lab.spec.ts
```

Run `npm run test:ui` only as the integration gate.
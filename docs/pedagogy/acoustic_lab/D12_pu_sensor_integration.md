# D12 — PU & Sensor Integration

Status: **Mapped**

**Decision:** `KEEP + REFINE + ADD LAYERED INTEGRATION EXPERIENCE`  
**Current:** `web/pedagogical-explorer/src/PuSensorLab.tsx`  
**Scientific/API path:** `src/hydrosim/integration/pu_sensor.py`, `src/hydrosim/app/pu_sensor_api.py`  
**Historical implementation alias:** current Python classes still use `D13*`; pedagogical numbering in this directory is authoritative.

## Purpose
Teach how independent hydrographic sensors become usable inputs to an acquisition system through a **Processing Unit (PU)**. The learner must understand that physically connecting a device is only the first layer: the PU must receive an accepted sensor type over a supported transport, interpret the correct protocol/message, receive observations at an appropriate cadence, and know what time reference the stream uses.

D12 teaches **configuration and data-interface integration**, not sensor accuracy and not timing-error correction. The central distinction is:

```text
CONNECTED
  != CONFIGURATION-COMPATIBLE
  != CORRECTLY TIME-SYNCHRONIZED
  != SCIENTIFICALLY VALID OBSERVATION
```

## Dominant discovery

```text
sensor observation
  -> transport / connection
  -> protocol + message semantics
  -> update cadence
  -> timestamp source
  -> PU input profile
  -> accept / reject with explicit reason
  -> stream becomes available to the acquisition system
```

A stream can fail at any layer even when a cable or network link exists. Conversely, a configuration-compatible stream is only **eligible to be consumed**; D13 still has to teach whether its timestamps, latency and interpolation align the observation with the sonar event.

The lab succeeds when the learner can diagnose why a sensor stream is rejected, repair one layer without changing unrelated layers, and explain why “data arriving at the PU” is not yet proof that the data are correctly synchronized or scientifically correct.

## Inputs

### Primary — guided progression
1. **sensor / device class** — position, attitude/motion, sound speed, echosounder or another registered class;
2. **PU input profile / destination input** — begin with one visible fixed profile such as `PU-A`;
3. **transport kind** — serial or network;
4. **protocol**;
5. **message / datagram type**;
6. **update rate** in Hz;
7. **timestamp source** — e.g. GNSS/UTC, device clock, PU receive time, only where registered by the selected profile.

### Transport-specific secondary controls
For serial:
- port identifier;
- baud rate.

For network:
- network transport where relevant (for example UDP/TCP under a registered system profile);
- endpoint/address/port.

The UI must reveal only controls that apply to the selected transport; a serial baud rate must not appear to govern an Ethernet stream.

### Advanced / optional
Only after one-stream compatibility is understood:
- several PU inputs shown simultaneously;
- one stream each for position, attitude, sound speed and sonar/external sensor data where supported;
- redundant sensor streams / preferred-fallback input only if a Scientific-Core model defines the selection rule;
- multiple accepted message formats for one sensor class as architecture-specific examples.

Do not expose vendor protocol internals merely to increase parameter count.

## Outputs / visual response

### A. Layered integration path
Show a synchronized path such as:

```text
SENSOR ROLE
   -> TRANSPORT
   -> PROTOCOL / MESSAGE
   -> UPDATE CADENCE
   -> TIME SOURCE
   -> PU INPUT
```

Each layer must have an explicit pass/fail state. A failure should appear at the layer that caused it rather than collapsing everything into one red `incompatible` label.

### B. Sensor -> PU flow diagram
Required:
- selected sensor/device class;
- serial or network connection;
- PU input identifier;
- accepted/rejected state;
- rejected layer highlighted;
- no animation implying real packet transfer unless packet/runtime behaviour is actually simulated.

### C. Stream semantics / readout
Show:
- protocol ID;
- message/datagram ID;
- update rate `f_update`;
- derived nominal update period `T_update = 1/f_update`;
- timestamp source;
- selected PU profile requirements relevant to the current stream.

The PU profile should be visible as the **contract being tested**, not a hidden rule discovered only after failure.

### D. Diagnostic reason
For every rejection, expose a concise cause such as:
- device class not accepted;
- transport not accepted;
- serial baud mismatch;
- protocol not accepted;
- message not accepted for the protocol;
- update rate outside the selected profile range;
- timestamp source not accepted;
- required connection parameter missing.

### E. Nominal cadence view
Recommended after basic compatibility is understood: show evenly spaced **nominal** observation ticks for the configured update rate. This is cadence only; do not add simulated latency/jitter unless D13 is active.

### F. Integrated-suite view
Advanced: after several individual streams are configured, show a simple acquisition-system map with accepted position, attitude, sound-speed and sonar/external streams entering their respective PU inputs. Keep each stream's role and source identity visible.

## Interaction sequence

1. **Start with one compatible position stream.** Show sensor role, serial/network path, protocol/message, update rate, time source and `PU-A` input. All layers pass.
2. **Break only the physical/logical transport layer.** For a serial example, choose an unsupported baud rate. The stream should fail at `transport parameters` while device class, message, rate and time source remain unchanged.
3. **Repair transport; break protocol/message.** Select a protocol the input does not accept, then an invalid message for an otherwise accepted protocol. The learner should distinguish protocol identity from message identity.
4. **Change device class without changing the wire.** A sound-speed sensor or echosounder may be rejected by a PU input intended only for position/attitude. The connection can remain physically plausible while the input contract rejects the measurement role.
5. **Change update rate.** Move below and above the selected profile's accepted range and show both Hz and nominal period. Explain that the limit belongs to this PU/profile, not to hydrography universally.
6. **Change timestamp source.** Keep all other layers valid. Show that a stream may be rejected because its time-source semantics do not match the input contract. Do not yet simulate the resulting time error.
7. **Switch transport.** Configure the same logical measurement through a supported network path. The transport changes while the measurement role and message semantics need not. This separates `what the data mean` from `how the bytes travel`.
8. **Configure an attitude stream.** Use a different accepted protocol/message while preserving the same layered reasoning. Connect this stream conceptually to D11 motion.
9. **Diagnose a near-valid stream.** Present one deliberately subtle single-layer error and require the learner to identify it from the integration stack before changing controls.
10. **Advanced suite.** Show multiple individually accepted streams feeding distinct PU inputs. Only after that, hand the question `are these observations aligned to the same event time?` to D13.

## Operational intuition / trade-offs

| Layer / choice | Benefit | Risk / lesson |
|---|---|---|
| Serial interface | simple, common for time-critical external sensors | baud/electrical/protocol parameters must match the receiving input |
| Network interface | scalable, supports higher-rate/multiple data flows | endpoint/transport configuration and network behaviour still matter; Ethernet alone does not guarantee timing correctness |
| Standardized protocol/message | improves interoperability and explicit semantics | both ends must support the same version/message; a valid sentence/datagram can still contain bad measurements |
| Higher update rate | more frequent observations / smaller nominal sample interval | increases data load and does not intrinsically improve sensor accuracy |
| Lower update rate | lower data volume | coarser temporal sampling; whether it is adequate depends on platform dynamics and downstream interpolation |
| GNSS/UTC or disciplined device time | can place observations on a common time scale | only if the source is actually synchronized and timestamps represent the intended measurement epoch |
| PU receive time | convenient when source timestamps are absent | includes transport/processing arrival effects and is not automatically the measurement time |
| Multiple integrated streams | enables the PU to combine sonar with position, motion and environmental observations | increases configuration, identity and synchronization burden |

Desired learner message: **the PU does not integrate sensors merely because they are connected. A usable stream must match the input contract at the transport, message, cadence and time-reference layers; only then can the next problem—correct synchronization—be solved.**

## Scientific guardrails

- D12's current Scientific Core evaluates **configuration compatibility only**. It does not prove packet delivery, electrical integrity, network performance, hardware interoperability, sensor accuracy or observation generation.
- `compatible` means compatible with the **selected PU input profile**, not universally compatible with all hydrographic systems.
- Update-rate limits are profile-specific. Do not teach the current `1–20 Hz` range as a general hydrographic requirement.
- Update rate is not accuracy. A high-rate biased/noisy sensor remains biased/noisy.
- Timestamp-source compatibility is not timestamp correctness. Clock offset, latency, jitter, interpolation and event-time alignment belong to D13.
- PU receive time is an arrival/reference time, not automatically the physical measurement epoch.
- Do not infer deterministic timing merely because transport is Ethernet/network based.
- Do not reproduce proprietary/copyrighted NMEA or manufacturer message definitions beyond what authoritative public documentation supports. Use identifiers and semantics needed for the lesson.
- Message-format acceptance does not validate the measurement value itself. A correctly parsed sound-speed, attitude or position message can still carry a bad observation.
- Keep sensor installation geometry in D10 and vessel motion physics in D11. D12 connects their streams; it does not recompute those models.
- Formal uncertainty and sensor-quality propagation belong to D17.

## Dependencies / forward reuse

Consumes:
- D10 sensor identities / installation roles and common vessel-system context;
- D11 position/attitude/heave data as examples of dynamic sensor streams;
- D4 surface/water-column sound-speed distinction when sound-speed streams are shown;
- D9 sonar/PU architecture context where relevant.

Passes forward:
- configured stream identity, cadence and timestamp-source semantics to D13 Timing, Synchronization & Latency;
- accepted position/motion/environment/sonar inputs to D14 Sounding Formation;
- update cadence / stream availability context to D15/D16;
- sensor-stream quality/availability context to D17, without doing TPU here.

## Current implementation delta

`PuSensorLab.tsx`, `pu_sensor_api.py` and `integration/pu_sensor.py` already provide a useful configuration-compatibility slice:
- device class;
- serial vs network transport;
- serial baud or network endpoint;
- protocol and message identity;
- update rate and derived nominal period;
- timestamp source;
- explicit `compatible/incompatible` state;
- reason codes for mismatches.

The API explicitly states the present boundary: **configuration compatibility only; no packet delivery, latency, hardware interoperability or observation generation**. Preserve that boundary.

Next-version changes:
- make the **layered integration path** the dominant visual story instead of one final compatibility badge;
- expose the selected PU input profile as a visible contract so the learner knows what is being tested;
- rename/phrase the positive result as `configuration compatible` where useful to avoid implying end-to-end validation;
- add a nominal cadence/tick visualization from the core-derived update period;
- distinguish timestamp **source** from timestamp **correctness** and link explicitly to D13;
- keep transport-specific controls conditional;
- move the hard-coded `PU-A` acceptance profile out of React and into a registered Scientific-Core/API profile or API-provided configuration so the presentation layer does not define system acceptance rules;
- add a multi-stream suite summary only after the single-stream mechanism is understood, preferably by composing the same core compatibility model rather than adding frontend-only logic;
- keep real packet loss, latency, jitter, clock offset and interpolation out of D12.

## Recognized references

- **IHO S-5A Ed. 2.0.0 (Aug 2026), H6.1a — Hydrographic data acquisition / real-time data acquisition and control**: explicitly covers integration of echo sounders, sound-speed sensors, positioning systems and IMU/INS, data-acquisition systems, time-tagging, data visualization, error sources, and the learning outcome to specify/justify/configure communication interfaces between survey devices and system components: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **IHO S-5A Ed. 2.0.0, H6.1b — Real-time data monitoring**: integrated-system performance, quality control and troubleshooting context: <https://portal.iho.int/share/api/files/AAAAAAABALI/Standard%20S-5A%20Ed.2.0.0/S-5A_Ed2.0.0_05May26.pdf>
- **Kongsberg EM 304 Installation Manual** — real-system evidence for external position, clock, motion and sound-speed datagram interfaces, including NMEA ZDA and Kongsberg motion formats: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/427620_em304_installation_manual_en.pdf>
- **Kongsberg EM 2040 Instruction Manual** — PU architecture with serial interfaces for external time-critical sensors, Ethernet communication and synchronization links: <https://www.kongsberg.com/globalassets/kongsberg-maritime/km-products/product-documents/346210_em2040_instruction_manual.pdf>
- **National Marine Electronics Association (NMEA), NMEA 0183 — Serial Data Networking** — authoritative public description of serial electrical/data-protocol/timing/sentence-format layers and examples including time, position and depth: <https://www.nmea.org/nmea-0183.html>
- **National Marine Electronics Association (NMEA), OneNet®** — authoritative example of standardized IP/Ethernet marine-device networking and coexistence with other marine protocols: <https://www.nmea.org/nmea-onenet.html>

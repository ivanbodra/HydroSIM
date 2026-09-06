# PED-D13 Scientific Contract — PU / Sensor Integration

Status: authoritative pedagogical-generation contract  
Experience: `PED-D13`  
Scope: minimum generic, vendor-neutral first production slice

## Purpose

PED-D13 teaches that a hydrographic processing/acquisition unit (PU) can use a sensor stream only when the configured transport, message/protocol, rate, and time-base requirements are mutually compatible. This first slice is a **configuration/compatibility model**, not a byte-level network simulator and not a manufacturer-specific integration table.

The model must preserve the distinction between physical sensor quantities, digital transport properties, message cadence, and time tagging. A connection shown as `compatible` means that the declared configuration can be interpreted consistently by the configured PU profile; it does not prove real-world interoperability, certification, latency performance, data quality, or guaranteed delivery.

## 1. Conceptual device classes

The minimum learner-selectable device classes are:

- `position_sensor` — produces position/navigation observations;
- `attitude_sensor` — produces roll/pitch/heave/heading or equivalent motion observations;
- `sound_speed_sensor` — produces sound-speed observations used at the transducer or in the water-column workflow;
- `echosounder` — produces acoustic measurement/detection data for downstream sounding formation.

These are functional classes, not manufacturers or products. A future device may expose more than one class through separate declared streams; the first slice may represent one selected stream at a time.

## 2. PU and stream capability profiles

Each selected sensor stream and PU input define explicit Configured capability profiles.

A sensor stream profile contains at minimum:

- `device_class`;
- `stream_id`;
- `transport_kind`;
- transport-specific connection parameters;
- `protocol_id`;
- `message_id` or message family;
- `update_rate_hz`;
- `timestamp_source`.

A PU input profile contains the corresponding accepted sets/ranges:

- accepted device class(es);
- accepted transport kind(s);
- accepted protocol/message combinations;
- accepted update-rate range or maximum rate where the scenario defines one;
- accepted timestamp/time-base source(s).

Compatibility is Derived from these declared profiles. The UI must not invent compatibility rules.

## 3. Transport semantics

The first slice supports two generic transport families:

### Serial

Configured fields:

- logical/physical `port_id` (opaque identifier for the scenario);
- `baud_rate_baud` [Bd], positive;
- optional serial framing profile if the scenario explicitly defines one.

`baud_rate_baud` is a symbol rate in baud. It must not be relabelled as bit/s unless the active serial encoding/framing model explicitly makes that equivalence. The first slice does not derive payload throughput from baud rate.

### Network

Configured fields:

- `network_transport`: `udp` or `tcp`;
- endpoint/port identifier(s) sufficient to distinguish the configured channel in the scenario.

The first slice does not simulate packet loss, retransmission, MTU, socket buffering, multicast routing, bandwidth contention, or operating-system behavior.

## 4. Rate semantics

`update_rate_hz` [Hz] is the nominal message/sample publication cadence of the selected logical sensor stream. It is distinct from serial baud rate and from any network link capacity.

For a nominal periodic stream,

`nominal_update_period_s = 1 / update_rate_hz`

for `update_rate_hz > 0`.

This is a Configured cadence, not proof that every real message arrives exactly periodically. PED-D14 owns timing/latency/sample-association consequences; PED-D13 should expose only the configured rate and whether it is accepted by the selected PU profile.

No generic conversion from baud rate to update rate is authorized without an explicit message-length/framing model.

## 5. Protocol and message semantics

`protocol_id` identifies the declared digital interface/message protocol family. `message_id` identifies the selected message or message family within that protocol when relevant.

For the generic first slice, compatibility is set-based:

- the selected PU input must declare the same `protocol_id` as accepted;
- the selected `message_id` must belong to the PU input's accepted message set for that protocol;
- the declared device class must be semantically compatible with that message family.

HydroSIM must not fabricate vendor-specific message definitions. A scenario may include a small canonical example profile based on a recognized marine interface standard, but message parsing and sentence-field semantics remain outside this first slice unless separately specified.

IEC 61162-1 is an appropriate recognized reference for the existence of one-way serial maritime instrument interfaces carrying navigation quantities such as position, speed and depth. NMEA 0183 is closely related and likewise defines a single-talker/multiple-listener serial interface. These references motivate the generic transport/message separation; they do not make every HydroSIM stream an IEC 61162/NMEA stream.

## 6. Time-source semantics

`timestamp_source` identifies the time basis used to tag the sensor observation. Minimum generic values for the first slice are:

- `device_internal_clock`;
- `gnss_utc`;
- `pu_receive_time`.

These meanings remain distinct:

- a sensor-generated timestamp is the time associated with the observation according to the sensor's declared clock basis;
- `pu_receive_time` is a reception/availability epoch and must not be silently reinterpreted as measurement time;
- `gnss_utc` means the observation is tagged to a GNSS-disciplined UTC time basis in the didactic scenario; it does not model PPS disciplining accuracy, leap-second handling, clock steering, or timestamp uncertainty.

PED-D13 checks whether the selected PU input accepts/interprets the declared time source. PED-D14 owns latency, sample age, availability time, and association to ping epochs.

## 7. Compatibility algorithm

A configured sensor stream is `compatible` with a PU input only when all applicable checks pass:

1. device class accepted;
2. transport kind accepted;
3. required transport parameters valid and accepted;
4. protocol accepted;
5. message/message family accepted for that protocol;
6. `update_rate_hz` positive and within the configured PU acceptance range, when a range is declared;
7. timestamp source accepted.

The Derived status is one of:

- `compatible`;
- `incompatible`.

The model must also return deterministic reason codes for every failed condition, for example:

- `device_class_mismatch`;
- `transport_mismatch`;
- `serial_baud_mismatch`;
- `protocol_mismatch`;
- `message_mismatch`;
- `update_rate_out_of_range`;
- `time_source_mismatch`;
- `missing_required_connection_parameter`.

A configuration may have multiple simultaneous incompatibility reasons. Do not collapse all failures into one generic status.

## 8. State semantics

Configured:

- selected device/stream class and identity;
- transport/connection parameters;
- serial baud [Bd] where applicable;
- protocol/message selection;
- update/message rate [Hz];
- timestamp source;
- PU input capability profile.

Derived:

- nominal update period [s];
- compatibility status;
- incompatibility reason codes;
- learner-renderable connection/stream configuration summary.

Observed:

- none required by this first slice. A real or simulated stream of timestamped measurements belongs to later runtime/acquisition behavior.

Truth / Estimated:

- none introduced by this configuration-only contract.

## 9. Learner-visible consequence boundary

PED-D13 may show:

- PU-to-sensor connection topology;
- selected device/transport/protocol/message/time-source configuration;
- configured update rate;
- `compatible` / `incompatible` state;
- explicit incompatibility reasons.

It must not claim, without another model, that a compatible configuration guarantees:

- successful real hardware communication;
- complete packet/message delivery;
- sufficient bandwidth under load;
- correct physical measurement values;
- low latency;
- synchronized timing;
- valid georeferenced soundings.

Those are distinct runtime, timing, scientific-quality, or acquisition questions.

## 10. Acceptance anchors

- a serial stream and PU profile with matching device class, transport, baud, protocol, message, update-rate acceptance and timestamp source returns `compatible`;
- changing only the protocol to an unsupported value returns `incompatible` with `protocol_mismatch`;
- changing only the message to one not accepted under the selected protocol returns `message_mismatch`;
- a serial stream outside the accepted baud profile returns `serial_baud_mismatch`;
- a positive update rate above a declared PU maximum returns `update_rate_out_of_range`;
- a `device_internal_clock` stream connected to a PU input accepting only `gnss_utc` returns `time_source_mismatch`;
- network configuration does not require or expose serial baud;
- serial baud [Bd] is never automatically converted into payload bit rate;
- compatibility evaluation does not generate sensor observations or packet traffic.

## 11. Fidelity boundary

This contract is suitable for teaching generic PU/sensor integration logic and common configuration mismatch classes. It is not a replacement for manufacturer installation manuals, IEC/NMEA conformance testing, packet-level simulation, electrical-interface validation, serial framing analysis, network performance modelling, clock synchronization modelling, or raw sensor message parsing.

## References

- IEC 61162-1:2024, *Maritime navigation and radiocommunication equipment and systems — Digital interfaces — Part 1: Single talker and multiple listeners*.
- National Marine Electronics Association, NMEA 0183 Interface Standard overview; serial one-talker/multiple-listener marine data interface and standard/HS baud rates.
- HydroSIM `docs/science/ped_d14_timing_association_contract.md` for sample-time / availability-time / latency semantics where timing consequences are needed.

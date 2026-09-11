# D13 Clock Synchronization v0.1 Scientific Contract

Status: implementation-ready scientific contract for the minimum D13 clock-offset experience.

## Purpose

Define the smallest clock model needed to distinguish **synchronization error** from **latency** and **sample age** without pretending to model a particular PPS/PTP/GNSS implementation.

## Time quantities and state semantics

HydroSIM uses one authoritative scenario/common time coordinate `t_common` for physical event epochs. Physical measurement, trigger, TX, RX and availability events remain on this common time basis.

For one sensor clock, define configured clock offset

`delta_t_clock = t_sensor - t_common`.

Positive `delta_t_clock` means the sensor clock reads **ahead** of common time. Negative means it reads behind.

For v0.1, the sensor-reported timestamp for a physical measurement made at common epoch `t_meas` is

`t_reported = t_meas + delta_t_clock`.

Therefore, if an acquisition system incorrectly interprets that reported timestamp as though it were already common time, its interpreted measurement epoch is

`t_interpreted = t_reported`,

and the timestamp-induced epoch error is

`t_interpreted - t_meas = delta_t_clock`.

State classification:
- `t_meas`, physical trigger/TX/RX epochs: **Truth** scenario epochs;
- `delta_t_clock`: **Configured** clock condition for the didactic experiment;
- `t_reported`: **Observed/Reported** sensor timestamp derived from Truth epoch plus configured clock condition;
- corrected/common-time timestamp, when synchronization correction is applied: **Derived** from reported time and configured/known offset.

## Synchronization modes

The minimum API may expose two pedagogical modes:

1. `ideal_common_time`
   - `delta_t_clock = 0` by definition;
   - sensor-reported time and common time coincide.

2. `fixed_clock_offset`
   - learner/configuration supplies constant `delta_t_clock`;
   - no skew, drift, jitter or stochastic timing error is implied.

A label such as `disciplined_reference` may be used only as a descriptive real-system example. HydroSIM v0.1 must **not** assign PPS/PTP/NTP/GNSS-specific accuracy, jitter or holdover performance without a separate implementation-specific model.

## Clock correction

If the offset is known, conversion back to common time is

`t_common = t_reported - delta_t_clock`.

This algebraic correction represents known fixed-offset compensation only. It is not a clock-estimation algorithm and does not model synchronization acquisition, servo dynamics or uncertainty.

## Separation from latency

Latency `L` remains a delay from physical measurement epoch to data availability:

`t_available = t_meas + L`.

Changing `delta_t_clock` must **not** change `t_meas` or `t_available`. It changes the timestamp relation to common time and therefore may change association if the reported timestamp is interpreted without correction.

Changing `L` must **not** rewrite `t_meas` or `t_reported`; it changes when the sample becomes causally available.

This gives the required pedagogical separation:

- clock offset -> **what epoch the timestamp appears to represent**;
- latency -> **when the already-measured sample becomes available**;
- update cadence -> **when physical samples exist**;
- sample age -> **difference between the selected sample's physical epoch and the sonar association epoch**.

## Association semantics

Causal availability remains mandatory: a sample cannot be used in a real-time association before `t_available`.

The API should preserve both physical and reported/corrected timestamps so UX can demonstrate two cases without inventing physics:

- synchronized/corrected association: use the common-time measurement epoch after applying the known clock relation;
- unsynchronized/misinterpreted association: treat `t_reported` as common time and expose the resulting timestamp/association error explicitly.

Do not silently replace the physical sample epoch with the erroneous interpreted epoch. Both must remain inspectable.

## Drift/skew boundary

Clock skew/drift is out of scope for v0.1. The fixed-offset model assumes

`d(delta_t_clock)/dt = 0`.

A future clock model may define fractional frequency error, drift, jitter, quantization and synchronization uncertainty. Those must not be inferred from this contract.

## Required implementation outputs

Minimum render-ready quantities:
- `common_measurement_time_s`;
- `sensor_reported_time_s`;
- `clock_offset_s`;
- `availability_time_s`;
- `association_time_s` (for example TX epoch);
- `interpreted_measurement_time_s` when demonstrating uncorrected timestamp use;
- `clock_epoch_error_s = interpreted_measurement_time_s - common_measurement_time_s`;
- synchronization mode;
- explicit indication whether clock-offset correction was applied.

Existing cadence, latency, causal availability and sample-age outputs remain separate.

## Invariants / validation anchors

1. `delta_t_clock = 0` implies `t_reported = t_meas`.
2. Positive offset implies `t_reported > t_meas` by exactly the configured offset.
3. With fixed `t_meas` and `L`, changing clock offset does not change `t_available`.
4. With fixed `t_meas` and clock offset, changing latency does not change `t_reported`.
5. Applying exact known offset correction returns `t_meas` within numerical tolerance.
6. A sample with `t_available > association_time` remains causally unavailable regardless of its reported timestamp.
7. The v0.1 model never implies clock drift, PPS/PTP performance or probabilistic synchronization quality.

## References and evidence boundary

The D13 pedagogical treatment records institutional/manufacturer evidence that hydrographic acquisition depends on time-tagging and common clock synchronization, including IHO S-5A and Kongsberg hydrographic-system documentation. Those sources justify the operational importance of synchronized timestamps and the distinction from latency. The fixed-offset equations above are the explicit HydroSIM v0.1 clock model: an affine clock relation with unit scale and constant offset, not a vendor performance model.

See:
- `docs/pedagogy/acoustic_lab/D13_timing_sync_latency.md`;
- `scientific_registry/references/bibliography.yaml`;
- `docs/science/scientific_references_by_submodule.md`.

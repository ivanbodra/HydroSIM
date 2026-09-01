# D8 Observation-State Contract

Status: canonical scientific-state semantics for the v0.1 Sounding Formation / Detection Chain.

## Purpose

D8 must preserve the HydroSIM distinction

`Truth != Observed != Configured != Estimated != Derived`.

In particular, a detected acoustic observation is not itself a Cartesian sounding point. A sounding point exists only after measurement observables are interpreted with processing/configuration state.

## Canonical v0.1 boundary

### Truth

Truth is the synthetic physical state known only to the forward simulator and diagnostics. For one sounding this includes the physical beam/ray state and the physical seabed intersection represented by `SoundingComparison.true` / its `SoundingState`.

Truth values are never relabelled as observations merely because they are reused to generate an ideal synthetic measurement.

### Observed

For v0.1, **Observed remains a measurement tuple, not an "Observed sounding point"**.

The canonical observation is the existing `BottomDetection` associated with a ping and receive beam. Its measurement content includes, when available:

- `twtt_seconds`;
- `detected_across_track_angle_rad`;
- detection method and detector indices/lag metadata;
- normalized amplitude and quality.

The observation identity/association key is the tuple:

`(ping_index, parent_beam_index, detection_index)`

where `ping_index` comes from the associated `AcquisitionPing`, `parent_beam_index` and `detection_index` from `BottomDetection`.

`arrival_offset_seconds` and `tx_delay_seconds` are timing quantities used to form the reported TWTT; they may remain attached to the observation record for traceability.

### Configured

Configured state contains values selected, assumed, or supplied to interpret the observation. For the current D8 composition this includes, as applicable:

- configured/processing vessel or sensor pose used for reconstruction;
- lever arms and sensor alignment used by processing;
- configured beam/steering geometry when distinct from a detected angle;
- processing sound-speed/profile state used to map TWTT and angle to geometry;
- other processing parameters explicitly identified as Configured by their owning model.

A `BeamRay` describing commanded/processing beam geometry is therefore not automatically an Observed angle. The observed angular quantity is `BottomDetection.detected_across_track_angle_rad` when that field exists.

Likewise, an associated `Pose` is not automatically Observed merely because it is time-associated with the ping; its scientific state follows the source stream/model that supplied it. In the current D8 application adapter, where that distinction is not yet represented by a separate sensor-observation object, it must not be relabelled as an acoustic observation.

### Derived

A Cartesian sounding reconstructed from the Observed measurement tuple using Configured/processing state is **Derived**.

Conceptually:

`Observed(TWTT, detected angle, association) + Configured(processing state) -> Derived reconstructed sounding`.

The existing `SoundingComparison.configured` object is a reconstruction computed with configured geometric state. Despite the legacy field name `configured`, its Cartesian point/result is scientifically a **Derived result from configured inputs**. D8 must not alias it as `observed_sounding`.

The current geometry helper also reconstructs its `configured` branch using the Truth-derived slant range rather than `BottomDetection.twtt_seconds`. Therefore that branch is suitable as a deterministic configured-geometry comparison/reference result, but it is **not evidence of a fully integrated observation-driven sounding** until the D8 processing path explicitly consumes the detection observables.

## Minimum D8 typed state

The reusable D8 state should expose, without duplicating the underlying models:

- `truth_sounding`: Truth `SoundingState`;
- `observation`: the existing `BottomDetection` plus stable ping/beam/detection association;
- `configured_state`: references to the processing geometry/state actually used by reconstruction, without relabelling them as observations;
- `derived_sounding` (or `reconstructed_sounding`): the Cartesian result produced from observation + configured processing state;
- stable `ping_index`, `beam_index`, and `detection_index` association.

For v0.1 there should be no property named `observed_sounding` if it returns a Cartesian point. If a presentation layer needs a final comparison label, use **Truth × Reconstructed** or **Truth × Derived sounding** until an explicit product-language decision is made; the scientific state remains as defined here.

## Non-goals

This contract does not introduce sensor-noise, angle-error, timing-error, sound-speed-error, or other new observation physics. It only defines the state boundary for scientific correctness of the existing D8 chain.

## Implementation consequence

The temporary PR #84 alias `SoundingFormationSnapshot.observed_sounding -> SoundingComparison.configured` is scientifically incorrect and should be removed/replaced by a Derived/reconstructed naming boundary.

If the first implementation cannot yet reconstruct a Cartesian point directly from `BottomDetection` because the processing conversion is not integrated, the typed API should still expose the observation tuple separately and identify the current geometric comparison result as Derived/reference reconstruction rather than calling it Observed.

## Sources

- `docs/conventions.md` — HydroSIM state separation and timing semantics.
- `src/hydrosim/acquisition/bottom_detection.py` — detection measurement model.
- `src/hydrosim/geometry/soundings.py` — Truth/configured-input reconstruction and residual model.
- `src/hydrosim/app/sounding_formation.py` — D8 composition introduced by PR #84.
- Issues #85 and #88.

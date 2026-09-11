# D2 Range Resolution & Relative Pulse Energy Scientific Contract

Status: implementation-ready scientific extension for D2 — Pulse & Signal Processing.

## Scope

This contract defines the two render-ready quantities required by the revised D2 treatment: a range-resolution reference and a relative pulse-energy indicator. It does not define propagation, detection threshold, minimum range, ping rate, bottom scattering, or receiver noise.

## State semantics

Pulse type, centre frequency, pulse duration `tau`, LFM swept bandwidth `B`, chirp direction and envelope/window are **Configured** quantities.

The range-resolution and relative-energy quantities below are **Derived** from those configured values and the canonical pulse model. They are not Observed measurements and are not manufacturer performance claims.

## 1. Ideal range-resolution reference

HydroSIM D2 shall expose an **ideal analytical two-way range-resolution reference**, distinct from any measured width of the sampled matched-filter trace.

For a rectangular, unmodulated CW pulse of duration `tau`, the reference is

`delta_R_CW = c * tau / 2`

where `c` is the configured/reference sound speed in m/s, `tau` is in seconds, and `delta_R_CW` is in metres.

This is the spatial extent corresponding to the finite pulse duration in monostatic two-way ranging. In D2 it is a resolution reference, not an assertion that every real detector resolves targets exactly at this separation.

For an ideal rectangular-spectrum LFM pulse with swept bandwidth `B`, the compressed range-resolution reference is

`delta_R_LFM = c / (2 * B)`

where `B` is the absolute swept bandwidth in Hz.

This is the canonical ideal bandwidth-limited reference for the D2 lesson. It deliberately separates LFM duration (primarily transmission occupancy/energy at fixed normalized amplitude) from swept bandwidth (compressed range-response scale).

### Window/envelope boundary

If the learner selects a non-rectangular envelope/window (currently Tukey), HydroSIM must **not silently reinterpret** `c/(2B)` as the exact achieved resolution of that weighted waveform. The ideal analytical value remains a clearly labelled bandwidth reference. Windowing changes the actual autocorrelation/mainlobe/sidelobe shape, which is already visible in the canonical matched-filter response.

A future measured-width output may be added only with an explicit width definition (for example FWHM or first-null width), sampling/interpolation rule and unit. It must be named separately, e.g. `matched_filter_fwhm_range_m`; it must not replace or be conflated with `ideal_range_resolution_m`.

### Sound-speed input

The conversion from time/bandwidth to metres requires sound speed. D2 should use an explicit configured/reference `sound_speed_mps`, defaulting to 1500 m/s when the treatment does not expose it as a learner control. This is a didactic conversion constant for D2, not an environmental propagation model; sound-speed-profile/refraction physics belongs elsewhere.

## 2. Relative pulse energy

For the canonical normalized real passband waveform `s(t)`, define the pulse-energy proxy

`E_rel = integral |s(t)|^2 dt`.

Because the waveform amplitude is normalized and no acoustic impedance/source calibration is supplied, this is a **relative normalized energy proxy**, not joules and not acoustic source energy.

To make comparisons dimensionless and stable, expose

`relative_energy = E_rel / E_ref`

where `E_ref` is the energy of the canonical rectangular-envelope pulse at the same normalized amplitude and a declared fixed reference duration `tau_ref`.

For the D2 API, use `tau_ref = 1 ms` unless a different reference is explicitly versioned later. Therefore a 1 ms rectangular CW pulse at the canonical normalized amplitude has `relative_energy = 1` by definition.

Engineering should compute `E_rel` from the canonical pulse/envelope model rather than from a display-decimated trace. An analytic envelope integral is preferred when available; sufficiently dense canonical numerical integration is acceptable if deterministic and convergence-tested.

For equal normalized amplitude, equal duration and equal envelope, ideal CW and LFM pulses should have the same relative-energy proxy apart from numerical tolerance: frequency sweep by itself does not create extra transmitted energy in this normalized model.

A tapered envelope has lower `relative_energy` than a rectangular envelope of equal duration and peak normalized amplitude. Increasing duration with envelope shape otherwise fixed increases `relative_energy` proportionally.

## 3. Required render-ready outputs

The D2 scientific/API boundary should expose at least:

- `ideal_range_resolution_m: float`;
- `range_resolution_basis: "cw_pulse_duration" | "lfm_swept_bandwidth"`;
- `range_resolution_kind: "ideal_analytical_reference"`;
- `relative_energy: float`;
- `relative_energy_reference_duration_ms: float` (v0.1 = 1.0);
- `relative_energy_kind: "normalized_waveform_energy_proxy"`;
- `sound_speed_mps: float` used for the range conversion.

The existing matched-filter trace remains the authoritative visual representation of the actual canonical autocorrelation response. Do not derive a measured resolution from its plotted pixel width in React.

## 4. Analytical anchors / invariants

With all else fixed:

1. CW: doubling `tau` doubles `ideal_range_resolution_m` (poorer analytical range resolution).
2. LFM: doubling `B` halves `ideal_range_resolution_m`.
3. LFM: changing `tau` at fixed `B` does not change the ideal `c/(2B)` reference.
4. Rectangular envelope at fixed normalized amplitude: doubling `tau` doubles `relative_energy`.
5. Equal duration/amplitude/envelope: CW and LFM have equal `relative_energy` within numerical tolerance.
6. A non-rectangular taper must not be advertised as having exact achieved resolution `c/(2B)`; that value remains the ideal bandwidth reference while the matched-filter trace shows the changed response.
7. Neither range-resolution quantity may be labelled minimum range or detection threshold.

## 5. Scientific basis and fidelity

The `c*tau/2` pulse-length relation and `c/(2B)` ideal pulse-compression range-resolution relation are standard active-sonar/radar time-bandwidth results and match the D2 pedagogical distinction between finite CW pulse duration and LFM bandwidth. The energy proxy follows the standard signal-energy definition `integral |s(t)|^2 dt`; HydroSIM intentionally keeps it normalized because the D2 pulse model does not contain calibrated source impedance or projector power.

Recognized project references for this lesson remain:

- IHO S-5A Ed. 2.0.0 (2026), H2.1/H2.2 — acoustic signals, pulse length, bandwidth, matched filtering and echo-sounding principles.
- Schock, LeBlanc & Mayer (2000), *The Development of Chirp Sonar Technology and Its Applications* — chirp/pulse-compression energy and resolution context.
- Hughes Clarke (2017), *Multibeam Echosounders* — hydrographic multibeam signal/measurement context.

No manufacturer-specific performance is inferred by this contract.

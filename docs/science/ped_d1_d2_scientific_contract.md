# PED-D1 / PED-D2 scientific contract

Status: implementation boundary for the first pedagogical-generation acoustic-signal experiences.

This document reuses `docs/science/signal_waveform_contract.md` and the existing waveform implementation. It does not replace that contract or reopen settled waveform choices.

## Shared boundary

`PED-D1` and `PED-D2` use ideal, normalized acoustic/signal representations. Unless a quantity is explicitly connected to a calibrated pressure or source-level model, plotted amplitude is **dimensionless normalized amplitude** and must not be labelled Pa, dB re 1 uPa, source level, received level, or intensity.

The baseline excludes projector/electronics transfer functions, propagation loss, calibrated receive amplitude, noise, bottom scattering, and detection probability. Those belong to later experiences.

Where a sound speed is needed only to convert temporal/acoustic quantities to distance, use a configured reference `sound_speed_mps > 0` with a pedagogical default of 1500 m/s. In PED-D1/PED-D2 it is context/configuration, not the scientific variable being taught; sound-speed variation and refraction belong to PED-D4.

State classification:

- learner controls are `Configured`;
- analytic samples/curves and quantities computed from configured values are `Derived`;
- these lessons create no `Observed`, `Estimated`, or environmental `Truth` state.

## PED-D1 — Acoustic Wave & Frequency

### Learning question

How do frequency, period, wavelength, amplitude and phase describe a propagating acoustic sinusoid when propagation speed is held fixed?

### Allowed learner inputs

Minimum learner-facing controls:

- `frequency_hz = f > 0`;
- `normalized_amplitude = A >= 0`;
- `initial_phase_rad = phi0` (the interface may expose degrees while the Core remains radians).

Configured but not required as a learner control:

- `sound_speed_mps = c > 0`, default 1500 m/s.

Pulse duration, bandwidth, chirp direction, attenuation and source level are not PED-D1 controls.

### Authoritative equations and outputs

Derived period:

`T = 1/f`.

Derived wavelength in the configured homogeneous reference medium:

`lambda = c/f`.

A minimum propagating-wave representation is the one-dimensional plane-wave kinematic model

`a(x,t) = A cos(2*pi*f*t - 2*pi*x/lambda + phi0)`.

The `-kx` sign defines propagation in the positive-x direction under this convention. A reverse-propagating demonstration, if later needed, must change the sign explicitly rather than silently changing conventions.

Authoritative learner-visible outputs:

- period `T` in seconds (or scaled display units);
- wavelength `lambda` in metres;
- normalized amplitude versus time at a fixed point;
- normalized amplitude versus distance at a fixed time, or an equivalent animation of the same analytic field;
- frequency/wavelength comparison showing the inverse relation at fixed `c`;
- phase displacement produced by `phi0` without implying a travel-time change.

### Fidelity and simplifications

This is a monochromatic 1-D plane wave in a homogeneous, non-dispersive reference medium. It teaches wave kinematics, not geometric spreading, absorption, near-field behavior, transducer directivity, pressure calibration or sound-speed-profile physics.

### Existing capability and real gap

`ContinuousWavePulse`, `sample_waveform_passband`, and `initial_phase_rad` already provide the temporal sinusoid used by PED-D1. However, the current waveform API has no canonical spatial propagating-wave field and no canonical `period`/`wavelength` derivation tied to a configured sound speed.

A small Core/API addition is therefore required: a vendor-neutral acoustic-wave kinematics helper/model that validates `f` and `c`, returns `period_seconds` and `wavelength_m`, and evaluates the normalized 1-D field using the convention above. The presentation layer must not independently invent these equations.

## PED-D2 — Pulse & Signal Processing

### Learning question

How do finite CW and LFM/chirp pulses differ, and how do pulse duration and bandwidth affect their time-domain waveform and matched-filter/pulse-compression response?

### Allowed learner inputs

Reuse the canonical waveform parameters from `signal_waveform_contract.md`:

- pulse type: CW or LFM;
- `center_frequency_hz > 0`;
- `duration_seconds > 0`;
- for LFM, `bandwidth_hz > 0`;
- for LFM, `chirp_direction in {up, down}`;
- `envelope_model in {rectangular, tukey}`;
- `initial_phase_rad` may be learner-visible when teaching phase/zero crossing, otherwise it may retain the default of zero.

Configured but not required as a learner control:

- `sound_speed_mps > 0`, default 1500 m/s, only for converting time lag/width into two-way range separation.

### Authoritative learner-visible outputs

The existing waveform contract remains authoritative for:

- physical real passband CW/LFM waveform;
- instantaneous frequency;
- explicit complex-baseband representation;
- normalized matched-filter/autocorrelation response;
- up/down chirp semantics;
- rectangular/Tukey envelope semantics.

PED-D2 may additionally expose, without changing the physics:

- pulse envelope `w(t)`;
- zero crossings of the **passband** waveform, explicitly as a visualization aid rather than a bottom-detection algorithm;
- a normalized delayed echo made from the same ideal waveform, provided it is labelled an ideal delayed replica and not a propagated/calibrated received echo;
- matched-filter lag converted to equivalent monostatic two-way range offset by `Delta R = c * Delta t / 2`.

### Pulse-compression and resolution semantics

Do not present bandwidth alone as an exact universal range-resolution law for every configured envelope and finite numerical waveform.

For the actual HydroSIM pulse, the authoritative numerical object is the normalized matched-filter/autocorrelation response already computed by `waveform_autocorrelation`. If a scalar compressed-pulse width is shown, its definition must be explicit (for example full width at half maximum of normalized **power**, or another documented threshold) and measured from that response.

The corresponding equivalent two-way range width is

`Delta R_width = c * Delta t_width / 2`.

The familiar ideal-bandwidth relation `Delta R approximately c/(2B)` may be shown only as an **approximation/reference relation** for an ideal bandwidth-limited pulse and must not silently replace the measured response width. For CW finite pulses, pulse duration controls range extent/separation behavior; CW has no LFM bandwidth parameter and must not inherit `c/(2B)` by fabrication.

### Envelope, filtering and phase boundary

- The configured waveform envelope is authoritative for the ideal transmitted pulse shape.
- Matched filtering is the baseline filtering operation for PED-D2.
- No generic receive-bandpass, transducer-response or electronics filter is implied unless a specific transfer function is later added to the Core.
- Zero crossings and phase are waveform properties in this experience. They must not be described as the MBES phase-bottom-detection method; bottom detection belongs to PED-D9.

### Existing capability and real gaps

The current Core already supplies `ContinuousWavePulse`, `LinearFMPulse`, passband/baseband sampling, instantaneous frequency, envelope sampling, `matched_filter`, and `waveform_autocorrelation`. These are sufficient for the primary CW-vs-LFM and matched-filter behavior.

Two small reusable Core/API capabilities are still needed if PED-D2 is to expose the complete minimum outputs without presentation-layer science:

1. a documented conversion from time lag/temporal width to monostatic two-way range using configured `sound_speed_mps`;
2. a canonical scalar width measurement for `WaveformAutocorrelation` (recommended baseline: FWHM of normalized power, with interpolation or sample-grid semantics documented), returning temporal width and optionally equivalent range width.

An ideal delayed-replica helper is optional: the existing `matched_filter(received, reference, ...)` API is scientifically sufficient if the application already has a canonical signal-delay utility. Do not add a new abstraction solely for UI convenience.

## References authoritative within HydroSIM

Primary internal sources:

- `docs/science/signal_waveform_contract.md` — canonical finite CW/LFM, passband/baseband, chirp, envelope and matched-filter semantics;
- `src/hydrosim/acquisition/waveform.py` — current implementation of those waveform primitives;
- `docs/pedagogy/hydrosim_pedagogical_plan.md` — PED-D1/PED-D2 learning scope.

The equations used here are standard acoustic/signal kinematics: `T=1/f`, `lambda=c/f`, a 1-D harmonic travelling wave, monostatic two-way conversion `Delta R=c Delta t/2`, and matched-filter autocorrelation. Manufacturer-specific claims are neither needed nor allowed for these baseline experiences without traceable sources.

## Completion boundary

PED-D1 is scientifically complete for implementation when the temporal waveform reuses the existing CW primitive and the missing wave-kinematics helper provides canonical period, wavelength and propagating-field values.

PED-D2 is scientifically complete for implementation using the existing waveform primitives once the range-lag conversion and explicitly defined autocorrelation-width metric are available if those scalar outputs are shown. No broader propagation, sonar-equation, bottom-detection or transducer model should be pulled into these experiences.
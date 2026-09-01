# Signal lesson waveform scientific contract

Status: implementation-ready scientific contract for the Didactic Explorer Signal lesson.

## Purpose

The Signal lesson must distinguish the physical passband acoustic waveform from its complex analytic/baseband representation. Baseband is valid for signal processing and matched filtering, but its real part must not be labelled as the transmitted acoustic waveform.

## 1. Time support and envelope

Let a finite pulse occupy `0 <= t <= T` and use a real, non-negative envelope `w(t)`.

Two baseline envelope options are allowed:

1. `rectangular` — ideal/reference case: `w(t)=1` inside the pulse and zero outside. It is useful analytically but has discontinuous onset/termination and broad spectral sidelobes.
2. `tapered` — didactic finite-rise/fall case. Use a symmetric Tukey envelope with configurable taper fraction `alpha` and a conservative default such as `alpha=0.1`. A Hann envelope is also scientifically valid, but the first implementation should choose one tapered model only to avoid unnecessary surface area.

The envelope is a configured waveform model, not a claim about a specific transducer/electronics impulse response. Real projector dynamics, amplifier limits, transducer ring-up/ring-down, filtering, clipping and calibration remain outside this baseline unless modelled separately.

## 2. CW passband waveform

For carrier frequency `f_c`, phase `phi_0`, pulse duration `T` and envelope `w(t)`:

`s_CW(t) = A w(t) cos(2*pi*f_c*t + phi_0)`.

The corresponding complex analytic signal is:

`a_CW(t) = A w(t) exp[j(2*pi*f_c*t + phi_0)]`.

After ideal complex down-conversion by `f_c`, the complex baseband signal is:

`b_CW(t) = A w(t) exp(j*phi_0)`.

Therefore a constant complex baseband CW is scientifically correct, but it must be labelled `complex baseband` or equivalent, not `transmitted acoustic waveform`.

## 3. LFM passband waveform

Define start frequency `f_start`, end frequency `f_end`, duration `T`, signed sweep rate

`k = (f_end - f_start)/T`.

For `0 <= t <= T`, instantaneous frequency is

`f_i(t) = f_start + k t`.

The passband phase is

`phi(t) = 2*pi*(f_start*t + 0.5*k*t^2) + phi_0`,

and the physical waveform is

`s_LFM(t) = A w(t) cos(phi(t))`.

Equivalent centre-frequency semantics are

`f_c = (f_start + f_end)/2`,

`B = |f_end - f_start|`.

The bandwidth parameter is always non-negative. Chirp direction is represented separately:

- `up`: `f_end > f_start`, `k > 0`;
- `down`: `f_end < f_start`, `k < 0`.

For a symmetric sweep about `f_c`:

- up-chirp: `f_start=f_c-B/2`, `f_end=f_c+B/2`;
- down-chirp: `f_start=f_c+B/2`, `f_end=f_c-B/2`.

Down-chirp is scientifically valid and should be supported explicitly rather than encoded as negative bandwidth.

## 4. Complex baseband LFM

Using local time `tau=t-T/2`, a symmetric LFM baseband representation may be written

`b_LFM(tau) = A w(tau) exp[j*pi*k*tau^2]`,

where signed `k` determines chirp direction. The instantaneous baseband frequency is `k*tau`.

This view is suitable for phase evolution and matched-filter diagnostics. It is not the physical carrier waveform.

## 5. Parameter semantics

Canonical quantities:

- `duration_seconds = T > 0`;
- `center_frequency_hz = f_c > 0`;
- `bandwidth_hz = B >= 0` for LFM magnitude;
- `chirp_direction in {up, down}`;
- derived `start_frequency_hz`, `end_frequency_hz`, and signed `sweep_rate_hz_per_second`;
- `initial_phase_rad` may default to zero and need not be user-facing in the first lesson;
- `envelope_model in {rectangular, tukey}` with a fixed or progressively disclosed taper fraction for the first release.

Invariant for LFM: `center_frequency_hz == (start_frequency_hz + end_frequency_hz)/2` and `bandwidth_hz == abs(end_frequency_hz-start_frequency_hz)`.

The first implementation may continue to construct LFM from centre frequency, positive bandwidth and direction; direct independent editing of centre/start/end/bandwidth simultaneously should be avoided because those quantities are constrained.

## 6. Didactic views and labels

Recommended separation:

1. **Transmitted acoustic waveform (passband)** — real CW/LFM carrier waveform using the finite pulse envelope. This is the view in which CW must visibly oscillate and LFM cycles must compress/expand as instantaneous frequency changes.
2. **Instantaneous frequency** — optional but strongly useful for LFM; plots `f_i(t)` and makes up/down direction unambiguous.
3. **Complex baseband / phase evolution** — diagnostic representation; label explicitly as baseband/analytic processing representation.
4. **Matched-filter / autocorrelation response** — continue using complex baseband/analytic samples because carrier removal does not invalidate the pulse-compression lesson when reference and received representations are consistent.

Do not compute matched filtering from a low-rate passband display trace. Display sampling and scientific processing sampling are separate numerical concerns.

## 7. Presets

Generic didactic presets may be offered only as clearly labelled examples such as `short`, `medium`, `long` pulse duration and `narrow`, `medium`, `wide` LFM bandwidth, with numeric values chosen to keep the lesson visually and numerically well conditioned. They must not be called manufacturer presets unless sourced to an authoritative manufacturer manual for a named system and configuration.

Manufacturer-specific frequency, bandwidth, pulse-length or sector presets require explicit source traceability because values vary by model, operating mode, depth range, power level and firmware generation.

For the first lesson, generic presets are preferable to manufacturer branding.

## 8. Scientific boundaries

The baseline waveform model represents commanded/ideal finite-duration pressure waveform shape. It does not yet model:

- calibrated source level or source voltage response;
- transducer electro-mechanical transfer function;
- ring-up/ring-down beyond the configured envelope;
- analogue transmit/receive filtering;
- nonlinearity or clipping;
- frequency-dependent projector sensitivity;
- noise or propagation.

These effects must not be implied by a simple tapered envelope.

## 9. Required implementation tests

At minimum:

- CW passband instantaneous frequency remains `f_c` during pulse support;
- up-LFM start/end frequencies and signed sweep rate are correct;
- down-LFM reverses start/end with equal positive bandwidth magnitude;
- centre-frequency and bandwidth invariants hold;
- rectangular envelope reproduces the current ideal baseband amplitude inside support;
- tapered envelope is zero (or numerically defined endpoint value) at pulse boundaries and symmetric;
- baseband CW remains constant-phase apart from envelope;
- matched-filter peak remains at zero lag for self-correlation;
- labels/API do not identify baseband real part as transmitted acoustic waveform.

## References

The formulation is the standard finite-duration sinusoid and linear-frequency-modulated chirp representation used in radar/sonar signal processing. Existing HydroSIM baseband implementation remains scientifically valid after introducing signed sweep direction and explicit envelope semantics; the required correction is primarily representation and parameterization, not replacement of matched-filter physics.

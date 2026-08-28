# Vessel Motion and Trajectory Foundation

Version: 0.1.0

## 1. Purpose

HydroSIM separates mean vessel trajectory from dynamic vessel motion. This keeps the physical causes of platform state explicit and allows simple didactic scenarios to remain computationally light while supporting higher-fidelity acquisition simulations later.

The initial implementation provides deterministic straight-line translation and controlled harmonic roll, pitch, yaw deviation, and heave.

## 2. Architecture

```text
Mean trajectory
    +
Dynamic motion signals
    ↓
Continuous vessel pose model
    ↓
Regular or requested sampling
    ↓
PoseTimeSeries
    ↓
Acquisition / integration / propagation models
```

The motion generator creates scenario Truth. Measurement noise, sensor error, timing error, and configured integration error belong to later layers and must not be silently embedded in the Truth motion generator.

## 3. Straight-line trajectory

The reference trajectory uses constant speed and heading in the canonical North-East-Down navigation frame.

For speed `v`, heading `ψ`, and elapsed time `Δt`:

\[
\Delta N = v\Delta t\cos\psi
\]

\[
\Delta E = v\Delta t\sin\psi
\]

Heading is radians clockwise from North, consistent with the HydroSIM convention.

The initial straight-line model leaves navigation-frame `Z` unchanged. Vertical vessel motion is composed separately through heave.

## 4. Harmonic motion

Each controlled scalar motion component may use:

\[
x(t)=x_0+A\sin\left(\frac{2\pi t}{T}+\phi\right)
\]

where:

- `A` is amplitude;
- `T` is period;
- `φ` is phase at simulation time zero;
- `x0` is an optional offset.

Roll, pitch, and yaw deviation use radians internally. Heave uses metres.

This is not intended as a complete stochastic vessel-response model. It is a transparent reference generator suitable for controlled experiments, didactic demonstrations, regression tests, and future sensitivity studies.

## 5. Heave sign

HydroSIM defines positive heave as Up, while the canonical navigation frame is Down-positive.

Therefore:

\[
Z_{pose}=Z_{trajectory}-heave
\]

A positive one-metre heave moves the vessel pose one metre upward and decreases navigation-frame `Z` by one metre.

## 6. Yaw and course

The straight-line trajectory heading defines the mean direction of travel. The motion model adds a separate `yaw_deviation` signal:

\[
yaw(t)=heading_{trajectory}+yaw_{deviation}(t)
\]

This permits the vessel heading to oscillate around the mean track direction without changing the initial translational trajectory model.

The distinction is deliberate. Future trajectory models may allow curved tracks, sideslip, steering dynamics, or velocity independent of heading, but these effects must be introduced explicitly rather than overloaded into the current reference model.

## 7. Sampling

The continuous motion model is sampled into the existing `PoseTimeSeries` infrastructure.

A sampling configuration declares:

- simulation interval;
- sample period;
- whether a non-grid interval endpoint is explicitly included.

Endpoint inclusion is useful because downstream interpolation must not require silent extrapolation beyond the generated support.

## 8. Scientific-state separation

The generated pose is `Truth` state.

Future architecture should preserve the following separation:

```text
Truth motion / trajectory
        ↓
Observed navigation / motion samples
        ↓
Configured timing and installation parameters
        ↓
Integrated sounding reconstruction
```

For example, INS latency should sample the Truth or Observed time series at an older epoch. It must not be represented by shifting the physical vessel trajectory itself.

## 9. Fidelity roadmap

The initial capability is intentionally small:

```text
trajectory:
    straight_constant_speed

motion:
    harmonic_roll
    harmonic_pitch
    harmonic_yaw_deviation
    harmonic_heave

sampling:
    regular
```

Potential later additions include waypoint trajectories, acceleration and turns, independently prescribed surge/sway, recorded motion-series replay, stochastic sea-state motion, cross-spectral six-degree-of-freedom models, and vessel-response models.

Those additions are not required for the current acquisition foundation and should remain optional capabilities.

## 10. Performance principle

Motion generation is a low-cost deterministic capability. Simple scenarios should instantiate only the trajectory and motion signals that are required. More advanced stochastic or hydrodynamic vessel-response models must not become implicit dependencies of ordinary HydroSIM experiments.

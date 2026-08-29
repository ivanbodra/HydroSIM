# Dynamic Acquisition Event Model

Version: 0.6.0

## Purpose

HydroSIM represents acoustic acquisition as a sequence of physical events occurring while the platform moves. A ping is not attached to one universal vessel pose, and a received beam is not attached to one universal physical point on an array.

The current propagation layer uses an ideal geometric **pencil-ray proxy**. It is a reference geometry, not yet a complete finite-aperture MBES transmit/receive beam model.

## Event chain

```text
continuous / sampled Truth motion
        ↓
ping trigger
        ↓
transmit epoch (Tx)
        ↓
ideal geometric pencil ray at Tx
        ↓
Truth terrain interaction point
        ↓
beam-specific TWTT
        ↓
beam-specific array-centre return epoch
        ↓
receive-array pose at that epoch
        ↓
element-specific arrival epochs
        ↓
receive steering hypothesis / delay law
        ↓
element phase at carrier frequency
        ↓
equal-weight coherent sum
```

The acquisition scheduler records `tx_time`, `rx_start_time`, and `rx_end_time`, while the propagation layer produces an individual physical return epoch for each simulated pencil ray. The receive-array layer then resolves the echo at each physical array element.

## Pencil-ray proxy versus physical MBES beam

`BeamRay` is currently used as a deterministic geometric ray that selects a Truth interaction point on the terrain. Its `role` metadata does not by itself turn this calculation into a complete TX- or RX-aperture model.

This distinction is essential for later Mills-Cross modeling. A real MBES may use separate transmit and receive arrays and finite beam patterns. The final two-way response is therefore not equivalent to one infinitely narrow ray.

The current ray model is retained because it gives a simple, traceable reference geometry for timing, motion, terrain intersection, and later validation. Finite TX/RX patterns and their two-way combination will be added as separate fidelity layers.

## Why there is no single rx_time

A multibeam ping contains acoustic returns with different paths and therefore different two-way travel times. Their bottom returns occur at different epochs. HydroSIM does not invent one universal `rx_time` for the ping.

For return `b`:

\[
t_{return,b}=t_{Tx}+TWTT_b
\]

and platform state is sampled at that return-specific epoch.

## Current constant-sound-speed Truth propagation

The first dynamic propagation backend is a straight-ray, constant-sound-speed reference model.

The Truth pencil ray is rotated using the sensor pose at `tx_time` and intersected with Truth terrain. This defines one bottom interaction point and outbound range:

\[
R_{out,b}=\left\|\mathbf{x}_{bottom,b}-\mathbf{x}_{Tx}\right\|.
\]

The present reference return model treats that bottom point as a **point scatterer**. It does not assume a specular mirror reflection and does not require the received energy to retrace the outbound ray.

Because the receive platform moves during propagation, the inbound range is evaluated at the unknown return epoch:

\[
R_{in,b}(t)=\left\|\mathbf{x}_{bottom,b}-\mathbf{x}_{Rx}(t)\right\|.
\]

The array-centre return time therefore satisfies

\[
t_{return,b}=t_{Tx}+\frac{R_{out,b}+R_{in,b}(t_{return,b})}{c}.
\]

HydroSIM solves this equation iteratively. For a stationary monostatic platform it reduces to

\[
TWTT_b=\frac{2R_b}{c}.
\]

The numerical solution stores the vessel/sensor state evaluated at exactly the stored return epoch. The remaining fixed-point equation error is exposed as `fixed_point_residual_seconds` rather than hidden.

## Receive-array element arrivals

The vessel may translate and rotate between transmission and reception. Therefore the bottom echo is perceived in the receive-array frame at the receive attitude, not at the transmit attitude.

HydroSIM records the unit vector from the receive-array centre toward the physical bottom interaction point in both navigation and array-local frames. The explicit name `direction_to_bottom_array_frame` is used because the vector points toward the acoustic source point; the propagating wave travels in the opposite direction.

For physical receive element `i`, its navigation-frame position varies with time:

\[
\mathbf{x}_i(t)=\mathbf{x}_{sensor}(t)+R_{N,S}(t)\,\mathbf{l}_{i,S}.
\]

Its echo arrival epoch is solved independently:

\[
t_i=t_{Tx}+\frac{R_{out,b}+\left\|\mathbf{x}_{bottom,b}-\mathbf{x}_i(t_i)\right\|}{c}.
\]

Consequently, different elements generally observe the same bottom echo at slightly different epochs. HydroSIM stores each element's arrival time and its delay relative to the array-centre beam-return epoch. Element state is evaluated at the same epoch stored in `arrival_time`, and its remaining fixed-point error is recorded explicitly.

These inter-element time differences are the geometric precursor to receive beamforming delay/phase processing.

## Ideal receive steering layer

The first receive-beamforming layer uses the deterministic delay law of an ideal far-field plane wave.

For a unit vector \(\mathbf{u}\) pointing from the receive-array centre toward the hypothesized acoustic source and element position \(\mathbf{r}_i\) relative to the array centre, the predicted arrival offset is

\[
\Delta t_i^{pred}=-\frac{\mathbf{u}\cdot\mathbf{r}_i}{c}.
\]

An element displaced toward the source has a shorter path and therefore a negative arrival offset: it receives the wavefront earlier. The corresponding ideal compensation delay is

\[
\Delta t_i^{comp}=-\Delta t_i^{pred}.
\]

HydroSIM can compare these ideal predicted offsets against the Truth element-arrival offsets generated by the moving-array propagation model:

\[
e_i=\Delta t_i^{Truth}-\Delta t_i^{pred}.
\]

The RMS and maximum absolute timing residuals provide a simple geometric measure of how well a steering hypothesis matches the received wavefront.

Across-track steering retains the canonical HydroSIM convention: zero is the array-local +Z normal, positive angles are Port (-Y), and negative angles are Starboard (+Y).

## Element phase and narrowband coherent sum

The first signal-domain receive model treats each physical element as an equal-amplitude, ideal narrowband channel. It deliberately isolates phase coherence from element directivity, sensitivity, attenuation, noise, waveform envelope, and electronics.

Using the complex-signal convention

\[
s(t)=e^{i2\pi f t},
\]

a Truth arrival offset \(\Delta t_i^{Truth}\) contributes the element phase

\[
\phi_i^{Truth}=-2\pi f\Delta t_i^{Truth}.
\]

Applying a steering compensation delay \(\tau_i\) contributes

\[
\phi_i^{steer}=-2\pi f\tau_i.
\]

The residual phase after steering is therefore

\[
\phi_i^{res}=\phi_i^{Truth}+\phi_i^{steer}.
\]

The initial equal-weight delay-and-sum beamformer forms

\[
B=\sum_{i=1}^{N} e^{i\phi_i^{res}},
\]

with normalized coherent magnitude

\[
A_N=\frac{|B|}{N}
\]

and normalized coherent power

\[
P_N=A_N^2.
\]

A perfectly matched steering law yields \(A_N=1\). A mismatch produces phase dispersion and a smaller coherent sum. At this stage the result is a normalized coherence measure, not received level, source level, target strength, or sonar-equation output.

Because phase depends on frequency, the same timing mismatch becomes more consequential as carrier frequency increases. This is the first place where physical element spacing can naturally be interpreted relative to wavelength,

\[
\lambda=\frac{c}{f},
\]

which prepares the later array-factor, beamwidth, sidelobe, and grating-lobe models.

Independent closed-form regression checks are required in addition to self-consistency tests. The first analytical anchors use a two-element array with `d = lambda/2` and known phasor sums.

## Scope of the current propagation and receive model

The current model represents geometric pencil-ray propagation, a point-scattered Truth return, physical element arrival times, ideal receive steering delays, narrowband element phase, and equal-weight coherent summation. It does not yet model:

- refraction through an SSP;
- finite transmit footprint;
- explicit TX/RX two-way beam-pattern intersection;
- physical element directivity or sensitivity;
- finite bandwidth or waveform envelope;
- receive weighting / shading;
- calibrated received amplitude;
- frequency-dependent element response;
- full angular array-factor scans, beamwidth, sidelobes, or grating lobes;
- scattering strength or incidence-angle dependence;
- pulse footprint integration;
- detection threshold;
- bottom-detection algorithm;
- multipath;
- electronic channel noise or mismatch.

Those are separate capabilities and must not be activated implicitly by the current geometric and narrowband calculations.

## Scheduling

The first scheduler is deterministic and regular. It defines:

- scenario-relative start and end trigger times;
- ping period;
- trigger-to-transmit delay;
- receive-start delay after Tx;
- receive-window duration.

This scheduler is intentionally independent of beam generation and acoustic propagation. Later ping-rate controllers may derive the next trigger from depth, swath, operating mode, or sonar constraints without changing event semantics.

## Truth-state invariant

Acquisition event generation, bottom interaction, return propagation, and array reception use Truth motion. Receive steering hypotheses and coherent summation are processing constructs applied downstream of Truth element arrivals.

```text
Truth motion + Truth terrain
    ↓
Acquisition event
    ↓
Truth pencil-ray interaction point
    ↓
Truth scattered return + TWTT
    ↓
Truth moving-array element arrivals
    ↓
receive steering hypothesis
    ↓
element phase + coherent sum
    ├── future Observed element/channel streams
    └── future Configured receive beamformer
```

A Configured or erroneous processing model must not move the physical Truth interaction point by re-intersecting an erroneous ray with Truth terrain.

## Temporal support

HydroSIM does not extrapolate vessel motion silently. If a scheduled Tx, receive-window boundary, solved return epoch, or element-arrival epoch lies outside the available pose series, simulation fails explicitly. Scenario construction must provide sufficient motion support for the complete acoustic event interval.

## Future extensions

The model is designed to accept, without redefining the current semantics:

- physical element directivity and sensitivity;
- receive weighting / shading;
- angular array-factor scans;
- beamwidth, sidelobes, and grating lobes;
- explicit TX and RX finite beam patterns and two-way response;
- Mills-Cross and sector geometry;
- broadband waveform and matched-filter processing;
- layered and full ray tracing;
- separate transmit and receive arrays;
- ping-rate control from depth and listening time;
- dual-head and multi-sector systems;
- latency-distorted Observed streams;
- bottom-scattering and bottom-detection models;
- RISC and other integration-error experiments.

## Review checkpoint

The reasoning, approximations, corrections, and source links for this stage are recorded in:

`docs/reviews/physics_architecture_review_1.md`

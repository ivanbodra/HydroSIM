# Dynamic Acquisition Event Model

Version: 0.3.0

## Purpose

HydroSIM represents acoustic acquisition as a sequence of physical events occurring while the platform moves. A ping is not attached to one universal vessel pose, and a received beam is not attached to one universal physical point on an array.

## Event chain

```text
continuous / sampled Truth motion
        ↓
ping trigger
        ↓
transmit epoch (Tx)
        ↓
beam direction at Tx
        ↓
terrain interaction
        ↓
beam-specific TWTT
        ↓
beam-specific array-centre return epoch
        ↓
receive-array pose at that epoch
        ↓
element-specific arrival epochs
```

The acquisition scheduler records `tx_time`, `rx_start_time`, and `rx_end_time`, while the propagation layer produces an individual physical return epoch for each simulated beam. The receive-array layer then resolves the echo at each physical array element.

## Why there is no single rx_time

A multibeam ping contains beams with different acoustic paths and therefore different two-way travel times. Their bottom returns occur at different epochs. HydroSIM does not invent one universal `rx_time` for the ping.

For beam `b`:

\[
t_{return,b}=t_{Tx}+TWTT_b
\]

and platform state is sampled at that beam-specific epoch.

## Current constant-sound-speed Truth propagation

The first dynamic propagation backend is a straight-ray, constant-sound-speed reference model.

The transmitted Truth beam is rotated using the sensor pose at `tx_time` and intersected with Truth terrain. This defines the bottom interaction point and outbound range:

\[
R_{out,b}=\left\|\mathbf{x}_{bottom,b}-\mathbf{x}_{Tx}\right\|.
\]

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

This is more physically faithful than simply assigning `2R/c` while simultaneously allowing the receiver to move.

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

Consequently, different elements generally observe the same bottom echo at slightly different epochs. HydroSIM stores each element's arrival time and its delay relative to the array-centre beam-return epoch.

These inter-element time differences are the geometric precursor to receive beamforming delay/phase processing. They are not yet beamformer output and no steering weights are applied at this layer.

## Scope of the current propagation model

The current model represents geometric propagation only. It does not yet model:

- refraction through an SSP;
- receive beamforming weights or phase processing;
- transmit/receive beam acceptance;
- waveform shape;
- bottom scattering strength;
- pulse footprint;
- detection threshold;
- bottom-detection algorithm;
- multipath.

Those are separate capabilities and must not be activated implicitly by the current geometric return calculation.

## Scheduling

The first scheduler is deterministic and regular. It defines:

- scenario-relative start and end trigger times;
- ping period;
- trigger-to-transmit delay;
- receive-start delay after Tx;
- receive-window duration.

This scheduler is intentionally independent of beam generation and acoustic propagation. Later ping-rate controllers may derive the next trigger from depth, swath, operating mode, or sonar constraints without changing event semantics.

## Truth-state invariant

Acquisition event generation, beam-return propagation, and array reception use Truth motion. They do not yet apply sensor latency, noise, configuration error, or estimated-state corrections.

```text
Truth motion
    ↓
Acquisition events
    ↓
Truth beam propagation
    ↓
Truth bottom interaction + TWTT + beam return epoch
    ↓
Truth moving-array element arrivals
    ├── future Observed element/channel streams
    └── future Configured receive beamformer
```

## Temporal support

HydroSIM does not extrapolate vessel motion silently. If a scheduled Tx, receive-window boundary, solved beam-return epoch, or element-arrival epoch lies outside the available pose series, simulation fails explicitly. Scenario construction must provide sufficient motion support for the complete acoustic event interval.

## Future extensions

The model is designed to accept, without redefining the current semantics:

- sector-specific transmit epochs;
- receive beamforming and beam acceptance;
- layered and full ray tracing;
- separate transmit and receive arrays;
- ping-rate control from depth and listening time;
- dual-head and multi-sector systems;
- latency-distorted Observed streams;
- waveform and bottom-detection models;
- RISC and other integration-error experiments.

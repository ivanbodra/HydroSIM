# Dynamic Acquisition Event Model

Version: 0.2.0

## Purpose

HydroSIM represents acoustic acquisition as a sequence of physical events occurring while the platform moves. A ping is not attached to one universal vessel pose.

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
beam-specific return epoch
        ↓
Truth receive-platform state at that epoch
```

The acquisition scheduler still records `tx_time`, `rx_start_time`, and `rx_end_time`, while the propagation layer now produces an individual physical return epoch for each simulated beam.

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

The return time therefore satisfies

\[
t_{return,b}=t_{Tx}+\frac{R_{out,b}+R_{in,b}(t_{return,b})}{c}.
\]

HydroSIM solves this equation iteratively. For a stationary monostatic platform it reduces to

\[
TWTT_b=\frac{2R_b}{c}.
\]

This is more physically faithful than simply assigning `2R/c` while simultaneously allowing the receiver to move.

## Scope of the current propagation model

The current model represents geometric propagation only. It does not yet model:

- refraction through an SSP;
- transmit/receive beam intersection or receive acceptance;
- waveform shape;
- bottom scattering strength;
- pulse footprint;
- detection threshold;
- bottom-detection algorithm;
- amplitude or phase;
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

Acquisition event generation and beam-return propagation use Truth motion. They do not yet apply sensor latency, noise, configuration error, or estimated-state corrections.

```text
Truth motion
    ↓
Acquisition events
    ↓
Truth beam propagation
    ↓
Truth bottom interaction + TWTT + return epoch
    ├── future Observed sensor streams
    └── future Configured reconstruction
```

## Temporal support

HydroSIM does not extrapolate vessel motion silently. If a scheduled Tx, receive-window boundary, or solved beam-return epoch lies outside the available pose series, simulation fails explicitly. Scenario construction must provide sufficient motion support for the complete acoustic event interval.

## Future extensions

The model is designed to accept, without redefining the current semantics:

- sector-specific transmit epochs;
- receive-array geometry and receive beam acceptance;
- layered and full ray tracing;
- transmit and receive array poses;
- ping-rate control from depth and listening time;
- dual-head and multi-sector systems;
- latency-distorted Observed streams;
- waveform and bottom-detection models;
- RISC and other integration-error experiments.

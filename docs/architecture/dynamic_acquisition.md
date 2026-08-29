# Dynamic Acquisition Event Model

Version: 0.1.0

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
receive interval
        ↓
future beam-specific bottom-return epochs
```

The initial implementation records Truth pose at `tx_time`, `rx_start_time`, and `rx_end_time` independently.

## Why there is no single rx_time

A multibeam ping contains beams with different two-way travel times. Their bottom returns therefore occur at different epochs. The current acquisition layer models a receive window rather than inventing one universal `rx_time` for the ping.

When propagation and beam-specific TWTT are connected, a return epoch may be computed as:

\[
t_{return,b}=t_{Tx}+TWTT_b
\]

and platform state can then be sampled at that beam-specific epoch.

## Scheduling

The first scheduler is deterministic and regular. It defines:

- scenario-relative start and end trigger times;
- ping period;
- trigger-to-transmit delay;
- receive-start delay after Tx;
- receive-window duration.

This scheduler is intentionally independent of beam generation and acoustic propagation. Later ping-rate controllers may derive the next trigger from depth, swath, operating mode, or sonar constraints without changing event semantics.

## Truth-state invariant

Acquisition event generation samples the Truth motion stream. It does not yet apply sensor latency, noise, configuration error, or estimated-state corrections.

Those belong to later Observed and Configured branches:

```text
Truth motion
    ↓
Acquisition events
    ├── Truth state at event epochs
    ├── future Observed sensor streams
    └── future Configured reconstruction
```

## Temporal support

HydroSIM does not extrapolate vessel motion silently. If a scheduled Tx or Rx epoch lies outside the available pose series, acquisition generation fails explicitly. Scenario construction must provide sufficient motion support for the complete acoustic event interval.

## Future extensions

The model is designed to accept, without redefining the current semantics:

- sector-specific transmit epochs;
- beam-specific return epochs;
- transmit and receive array poses;
- ping-rate control from depth and listening time;
- dual-head and multi-sector systems;
- latency-distorted Observed streams;
- acoustic TWTT and bottom interaction;
- RISC and other integration-error experiments.

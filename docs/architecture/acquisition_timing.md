# Acquisition Timing and Dynamic State

Version: 0.1.0

## Purpose

HydroSIM must represent hydrographic acquisition as a time-dependent physical process without coupling scientific simulation time to wall-clock execution time.

The timing layer therefore defines scenario-relative simulation epochs and dynamic-state sampling independently from UI refresh rate, processor speed, or real-time execution.

## Canonical time semantic

`SimulationTime.seconds` is a finite number of seconds relative to a scenario-defined simulation epoch.

It does not by itself imply UTC, GPS time, TAI, Unix time, or any other external time scale. Mapping a scenario epoch to an external time standard is a separate metadata concern.

This permits the same scenario to execute in real time, faster than real time, or slower than real time while preserving identical scientific event times.

## Ping epochs

A ping shall not be represented by one ambiguous timestamp. The initial canonical model distinguishes:

```text
trigger_time
    ↓
tx_time
    ↓
rx_start_time
    ↓
rx_end_time
```

These epochs may coincide in simplified experiments, but their meanings remain distinct.

Future sector- and beam-level timing may refine the transmit and receive events without changing these semantics.

## Dynamic state

Dynamic platform and sensor state is represented as time-series data rather than duplicated inside every ping.

The first reference implementation provides `PoseTimeSeries` with:

- strictly increasing sample times;
- one explicit Cartesian frame per series;
- exact retrieval at sample epochs;
- bounded linear position interpolation;
- shortest-path wrapped interpolation of roll, pitch, and yaw;
- no silent extrapolation.

Rejecting extrapolation is intentional. Missing temporal support is a simulation configuration problem and must not be hidden by invented state.

## Reference interpolation versus future fidelity

The current interpolator is a transparent reference implementation, not a claim that linear Euler-angle interpolation is the highest-fidelity motion solution.

Future explicit alternatives may include:

```text
motion.interpolation:
    sample_hold
    linear_rpy
    quaternion_slerp
    cubic
    high_rate_reference
```

Changing interpolation backend must be explicit and reproducible.

## Latency

The timing infrastructure enables the exact HydroSIM latency semantic:

\[
state_{used}(t)=state(t-\Delta t).
\]

A future integration-error model can therefore query a dynamic stream at the delayed epoch instead of relying only on a first-order derivative approximation.

## Computational principle

Time-series infrastructure is lightweight and reusable. More expensive capabilities such as acoustic propagation, waveform simulation, or RISC estimation are not activated merely because a scenario contains dynamic state.

This follows HydroSIM's minimal-dependency execution rule: simulation components instantiate only the capabilities required by the experiment.

## Initial implementation

```text
src/hydrosim/timing/models.py
src/hydrosim/timing/timeseries.py
src/hydrosim/timing/__init__.py
tests/test_timing.py
```

This is the first infrastructure increment. Acquisition events, sector timing, beam receive epochs, vessel trajectory generators, and motion generators should build on these primitives rather than introduce parallel time semantics.

# PED-D14 Scientific Contract — Sensor Timing, Association, and Temporal-to-Spatial Consequence

Status: authoritative pedagogical-generation contract  
Experience: `PED-D14`  
Scope: first learner-facing sensor-rate / timestamp / latency / vessel-speed timing experiment

## Learning question

PED-D14 teaches why a sensor value can be scientifically valid yet still be associated with the wrong vessel state if its sampling epoch, delivery latency, update rate, and sonar ping epoch are not handled consistently.

The first slice is deliberately narrow: ideal periodic position and attitude streams are associated to sonar transmit time, and a controlled constant-speed case converts position-state age into an along-track spatial consequence. It is not a complete navigation fusion or vendor datagram simulator.

## Canonical time concepts

Keep these times distinct:

- `sample_time`: epoch at which the sensor quantity represents the platform state;
- `availability_time`: epoch at which that sample becomes available to the consuming system;
- `tx_time`: canonical sonar transmit epoch receiving the associated navigation/motion state in this first slice;
- `use_time`: processing/association epoch; for the first slice this is `tx_time`.

For a configured non-negative stream latency `L`:

`availability_time = sample_time + L`

Latency does not change what physical epoch the measurement represents. It changes when the measurement can be used.

## First-slice sensor streams

The authoritative first learner set is:

1. `position`;
2. `attitude`.

Each selected stream has its own configured `update_rate_hz > 0`. The first slice treats each stream as ideal periodic sampling with period

`T_s = 1 / update_rate_hz`.

The streams are independent: different rates and latencies are permitted. No assumption is made that position and attitude arrive in the same message or share a device.

## State semantics

### Truth

The scenario owns a continuous Truth platform trajectory/pose from the canonical timing/pose model.

For the controlled temporal-to-spatial anchor, vessel speed is constant and directed along the vessel forward/along-track axis. Speed magnitude `v >= 0` is a configured scenario parameter [m/s], while the resulting continuous position versus time is Truth scenario state.

### Observed sensor sample

A sensor sample consists minimally of:

- `stream_id`;
- represented value/state;
- `sample_time`;
- `availability_time`.

Its value represents Truth evaluated at `sample_time` in this ideal pedagogical slice. No stochastic sensor noise or bias is added here.

### Configured

- stream selector;
- `update_rate_hz` [Hz];
- latency `L` [s];
- vessel speed `v` [m/s];
- scenario/ping timing configuration.

### Derived

- sample period;
- sample age relative to `tx_time`;
- latest causally available sample associated with the ping;
- position/attitude-to-ping association metadata;
- along-track temporal-to-spatial position consequence for the position stream.

## Association epoch

PED-D14 associates position and attitude to **`tx_time`**.

This is the explicit first-slice reference epoch because the lesson concerns the vessel/sensor state associated with acoustic transmission. It must not be silently replaced by `trigger_time`, receive epoch, detection epoch, or processing completion time.

Later higher-fidelity acquisition may require distinct transmit- and receive-array states, but that is outside the first PED-D14 timing lesson.

## Causal sample-selection rule

At `tx_time`, the associated sample for a selected stream is the latest sample satisfying

`availability_time <= tx_time`.

Equivalently, the consumer may only use a sample that has actually arrived by the association epoch.

The selected sample still represents `sample_time`; therefore define its non-negative state age

`age = tx_time - sample_time_used`.

This age can include both sampling discretization and latency. Do not replace `sample_time` with `availability_time` as the represented measurement epoch.

If no sample is causally available, the association state is explicitly unavailable. No extrapolation is permitted in the minimum slice.

Interpolation may be shown only when two causally available samples bracket the desired represented epoch under a separately explicit interpolation mode. It must not use future/unavailable samples.

## Position and attitude association

The learner-visible association output must preserve stream identity and show, at minimum:

- ping `tx_time`;
- selected sample `sample_time`;
- selected sample `availability_time`;
- age relative to ping;
- selected value/state;
- available/unavailable state.

Position and attitude are associated independently. A position sample and an attitude sample used for one ping may therefore have different represented epochs.

This is the intended PED-D14-O03 scientific consequence.

## Vessel-speed semantics

For the first controlled spatial-consequence case:

- vessel speed is constant;
- direction is vessel forward / along-track (`+X` in body-aligned reference for zero yaw deviation);
- no acceleration, turn, current, sideslip, or vertical velocity is introduced;
- `v` is a configured scenario parameter and the time-varying platform position generated from it is Truth.

This is a didactic anchor, not a general navigation model.

## PED-D14-O04 temporal-to-spatial consequence

The first authoritative spatial consequence applies to the **position stream** only.

Let

`delta_t = sample_time_used - tx_time` [s]

so a stale sample has `delta_t < 0`.

For constant forward speed `v`, the signed along-track position error caused solely by using that stale position state is

`delta_x = v * delta_t` [m].

Equivalently, using non-negative age,

`delta_x = -v * age`.

Interpretation: with forward motion and a stale sample, the used position lies behind the Truth position at transmit time.

The vector form in the declared body/along-track reference is

`delta_p_time = [delta_x, 0, 0]` [m].

This is a `Derived` **position-state timing consequence**, not a complete sounding error or uncertainty.

PED-D14 must not label `v * delta_t` as full 3-D sounding displacement because attitude age, beam geometry, lever arms, heave, refraction, and receive-time effects can contribute independently. Those require the integrated reconstruction path of later lessons.

For the attitude stream, PED-D14 may show age and association mismatch but must not convert attitude age into metres using `v * delta_t`. Any sounding displacement from stale attitude requires actual angular-rate/geometry propagation and is outside this first slice.

## Expected cause -> effect behavior

- higher update rate reduces maximum sampling-age contribution for otherwise equal timing;
- larger latency can force selection of an older sample even when newer samples have been generated but are not yet available;
- zero latency does not guarantee zero age unless a sample occurs exactly at `tx_time` or an explicit causal interpolation mode provides the state;
- at fixed age, doubling vessel speed doubles the magnitude of the controlled along-track position consequence;
- at zero speed, the controlled position temporal-to-spatial consequence is zero even if sample age is non-zero;
- position and attitude streams with different cadence/latency can associate different sample epochs to the same ping.

## Minimum analytical anchors

1. `v = 0`: `delta_x = 0` for any available sample age.
2. `v = 5 m/s`, used position sample 0.2 s before `tx_time`: `delta_x = -1.0 m`.
3. A sample with `sample_time < tx_time` but `availability_time > tx_time` is not eligible for association.
4. If two samples are causally available, the default selection is the one with greatest `sample_time`.
5. Position and attitude selection is independent and may yield different ages.
6. No available sample => explicit unavailable state, not extrapolation.

## Fidelity boundary

Included:

- ideal periodic sampling;
- explicit sample and availability epochs;
- deterministic configured latency;
- causal latest-sample association to `tx_time`;
- independent position/attitude stream association;
- constant-speed along-track position timing consequence.

Excluded:

- clock drift/bias estimation;
- stochastic timestamp jitter;
- vendor message transport/protocol behavior;
- navigation filtering/smoothing;
- noncausal interpolation;
- full 6-DOF stale-attitude sounding displacement;
- receive-array epoch association;
- complete reconstructed sounding error/uncertainty.

## Traceability

This contract reuses HydroSIM canonical `SimulationTime`, `PingTiming`, `TimedPose`, and deterministic pose/time-series behavior. It also preserves the project-wide positive-latency convention that a delayed state corresponds to an earlier physical epoch. No frontend timing equation is authoritative; the Python/Core path owns sample selection and derived timing consequences.

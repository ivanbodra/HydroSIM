"""Application adapter for the PED-D14 timing and latency learner slice."""

from __future__ import annotations

from math import floor
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.timing import PingTiming, SimulationTime

D14StreamId = Literal["position", "attitude"]
D14SynchronizationMode = Literal["ideal_common_time", "fixed_clock_offset"]


class D14TimingRequest(BaseModel):
    """Configured ping and ideal periodic sensor streams."""

    model_config = ConfigDict(extra="forbid")

    trigger_time_s: float = 0.0
    tx_delay_ms: float = Field(default=1.0, ge=0.0)
    rx_start_delay_ms: float = Field(default=2.0, ge=0.0)
    rx_duration_ms: float = Field(default=20.0, ge=0.0)
    sensor_sample_time_s: float = 0.0
    sensor_latency_ms: float = Field(default=0.0, ge=0.0)
    synchronization_mode: D14SynchronizationMode = "ideal_common_time"
    clock_offset_ms: float = 0.0
    apply_clock_correction: bool = True
    selected_streams: tuple[D14StreamId, ...] = ("position", "attitude")
    position_update_rate_hz: float = Field(default=10.0, gt=0.0)
    attitude_update_rate_hz: float = Field(default=100.0, gt=0.0)
    position_latency_ms: float = Field(default=0.0, ge=0.0)
    attitude_latency_ms: float = Field(default=0.0, ge=0.0)
    vessel_speed_mps: float = Field(default=0.0, ge=0.0)

    @model_validator(mode="after")
    def _validate_clock_mode(self) -> "D14TimingRequest":
        if self.synchronization_mode == "ideal_common_time" and abs(self.clock_offset_ms) > 1e-12:
            raise ValueError("clock_offset_ms must be zero in ideal_common_time mode")
        return self


class D14TimelineEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Literal["trigger", "tx", "rx_start", "rx_end", "sensor_sample", "sensor_available"]
    time_s: float
    state: Literal["Configured", "Derived"]


class D14StreamAssociation(BaseModel):
    """Latest causally available ideal-periodic sample associated to TX."""

    model_config = ConfigDict(frozen=True)

    stream_id: D14StreamId
    update_rate_hz: float
    sample_period_s: float
    latency_ms: float
    tx_time_s: float
    available: bool
    sample_time_s: float | None = None
    availability_time_s: float | None = None
    age_s: float | None = None
    represented_along_track_m: float | None = None
    represented_state: str | None = None
    along_track_timing_consequence_m: float | None = None


class D14ClockSynchronization(BaseModel):
    """Render-ready fixed-offset clock relation kept distinct from latency."""

    model_config = ConfigDict(frozen=True)

    synchronization_mode: D14SynchronizationMode
    clock_offset_s: float
    common_measurement_time_s: float
    sensor_reported_time_s: float
    availability_time_s: float
    association_time_s: float
    correction_applied: bool
    corrected_common_time_s: float | None
    interpreted_measurement_time_s: float
    clock_epoch_error_s: float


class D14TimingResponse(BaseModel):
    """Render-ready event timeline and causal position/attitude associations."""

    model_config = ConfigDict(frozen=True)

    trigger_time_s: float
    tx_time_s: float
    rx_start_time_s: float
    rx_end_time_s: float
    receive_duration_ms: float
    tx_to_rx_end_ms: float
    sensor_sample_time_s: float
    sensor_available_time_s: float
    sensor_latency_ms: float
    vessel_speed_mps: float
    clock_synchronization: D14ClockSynchronization
    associations: tuple[D14StreamAssociation, ...]
    timeline: tuple[D14TimelineEvent, ...]
    metadata: dict[str, str]


def _associate_stream(
    *, stream_id: D14StreamId, first_sample_time_s: float, update_rate_hz: float,
    latency_ms: float, tx_time_s: float, trigger_time_s: float, vessel_speed_mps: float,
) -> D14StreamAssociation:
    period_s = 1.0 / update_rate_hz
    latency_s = latency_ms * 1e-3
    latest_eligible_sample_s = tx_time_s - latency_s
    sample_index = floor((latest_eligible_sample_s - first_sample_time_s) / period_s + 1e-12)
    if sample_index < 0:
        return D14StreamAssociation(
            stream_id=stream_id, update_rate_hz=update_rate_hz, sample_period_s=period_s,
            latency_ms=latency_ms, tx_time_s=tx_time_s, available=False,
        )

    sample_time_s = first_sample_time_s + sample_index * period_s
    availability_time_s = sample_time_s + latency_s
    age_s = tx_time_s - sample_time_s
    if stream_id == "position":
        represented_along_track_m = vessel_speed_mps * (sample_time_s - trigger_time_s)
        consequence_m = vessel_speed_mps * (sample_time_s - tx_time_s)
        represented_state = "Truth along-track position at sample_time"
    else:
        represented_along_track_m = None
        consequence_m = None
        represented_state = "Truth attitude state at sample_time; no metre conversion"

    return D14StreamAssociation(
        stream_id=stream_id, update_rate_hz=update_rate_hz, sample_period_s=period_s,
        latency_ms=latency_ms, tx_time_s=tx_time_s, available=True,
        sample_time_s=sample_time_s, availability_time_s=availability_time_s, age_s=age_s,
        represented_along_track_m=represented_along_track_m, represented_state=represented_state,
        along_track_timing_consequence_m=consequence_m,
    )


def _clock_synchronization(
    request: D14TimingRequest,
    *,
    common_measurement_time_s: float,
    availability_time_s: float,
    association_time_s: float,
) -> D14ClockSynchronization:
    offset_s = 0.0 if request.synchronization_mode == "ideal_common_time" else request.clock_offset_ms * 1e-3
    sensor_reported_time_s = common_measurement_time_s + offset_s
    corrected_common_time_s = (
        sensor_reported_time_s - offset_s if request.apply_clock_correction else None
    )
    interpreted_measurement_time_s = (
        corrected_common_time_s if corrected_common_time_s is not None else sensor_reported_time_s
    )
    return D14ClockSynchronization(
        synchronization_mode=request.synchronization_mode,
        clock_offset_s=offset_s,
        common_measurement_time_s=common_measurement_time_s,
        sensor_reported_time_s=sensor_reported_time_s,
        availability_time_s=availability_time_s,
        association_time_s=association_time_s,
        correction_applied=request.apply_clock_correction,
        corrected_common_time_s=corrected_common_time_s,
        interpreted_measurement_time_s=interpreted_measurement_time_s,
        clock_epoch_error_s=interpreted_measurement_time_s - common_measurement_time_s,
    )


def prepare_d14_timing_response(request: D14TimingRequest) -> D14TimingResponse:
    """Build canonical ping timing plus PED-D14 causal stream associations."""

    trigger = SimulationTime(seconds=request.trigger_time_s)
    tx = trigger.shifted(request.tx_delay_ms * 1e-3)
    rx_start = trigger.shifted(request.rx_start_delay_ms * 1e-3)
    rx_end = rx_start.shifted(request.rx_duration_ms * 1e-3)
    ping = PingTiming(trigger_time=trigger, tx_time=tx, rx_start_time=rx_start, rx_end_time=rx_end)

    sensor_sample = SimulationTime(seconds=request.sensor_sample_time_s)
    sensor_available = sensor_sample.shifted(request.sensor_latency_ms * 1e-3)
    timeline = tuple(sorted((
        D14TimelineEvent(kind="trigger", time_s=float(trigger.seconds), state="Configured"),
        D14TimelineEvent(kind="tx", time_s=float(tx.seconds), state="Derived"),
        D14TimelineEvent(kind="rx_start", time_s=float(rx_start.seconds), state="Derived"),
        D14TimelineEvent(kind="rx_end", time_s=float(rx_end.seconds), state="Derived"),
        D14TimelineEvent(kind="sensor_sample", time_s=float(sensor_sample.seconds), state="Configured"),
        D14TimelineEvent(kind="sensor_available", time_s=float(sensor_available.seconds), state="Derived"),
    ), key=lambda event: event.time_s))

    stream_config = {
        "position": (request.position_update_rate_hz, request.position_latency_ms),
        "attitude": (request.attitude_update_rate_hz, request.attitude_latency_ms),
    }
    associations = tuple(_associate_stream(
        stream_id=stream_id, first_sample_time_s=request.sensor_sample_time_s,
        update_rate_hz=stream_config[stream_id][0], latency_ms=stream_config[stream_id][1],
        tx_time_s=float(ping.tx_time.seconds), trigger_time_s=request.trigger_time_s,
        vessel_speed_mps=request.vessel_speed_mps,
    ) for stream_id in dict.fromkeys(request.selected_streams))

    clock = _clock_synchronization(
        request,
        common_measurement_time_s=float(sensor_sample.seconds),
        availability_time_s=float(sensor_available.seconds),
        association_time_s=float(ping.tx_time.seconds),
    )

    return D14TimingResponse(
        trigger_time_s=float(ping.trigger_time.seconds), tx_time_s=float(ping.tx_time.seconds),
        rx_start_time_s=float(ping.rx_start_time.seconds), rx_end_time_s=float(ping.rx_end_time.seconds),
        receive_duration_ms=ping.receive_duration_seconds * 1e3,
        tx_to_rx_end_ms=ping.tx_to_rx_end_seconds * 1e3,
        sensor_sample_time_s=float(sensor_sample.seconds), sensor_available_time_s=float(sensor_available.seconds),
        sensor_latency_ms=request.sensor_latency_ms, vessel_speed_mps=request.vessel_speed_mps,
        clock_synchronization=clock,
        associations=associations, timeline=timeline,
        metadata={
            "time_basis": "scenario/common simulation time for physical epochs",
            "association_epoch": "sonar tx_time",
            "association_rule": "latest sample with availability_time <= tx_time",
            "clock_offset_definition": "t_sensor - t_common; positive means sensor clock ahead",
            "clock_correction": "known fixed-offset algebra only; no drift, jitter or synchronization performance model",
            "position_consequence": "Derived along-track position-state timing consequence; not full sounding error",
            "attitude_consequence": "age only; no conversion to metres",
            "state_semantics": "Truth physical epochs; Configured cadence/latency/clock offset/speed; Observed reported timestamp; Derived association/correction/consequence",
        },
    )

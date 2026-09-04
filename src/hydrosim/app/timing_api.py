"""Application adapter for the PED-D14 timing and latency learner slice.

The adapter exposes scenario-relative timing from HydroSIM's canonical timing
primitives. It intentionally stops at temporal consequences: no temporal-to-spatial
error is inferred here because that consequence is not represented canonically.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.timing import PingTiming, SimulationTime


class D14TimingRequest(BaseModel):
    """Configured ping and sensor epochs expressed in learner-facing units."""

    model_config = ConfigDict(extra="forbid")

    trigger_time_s: float = 0.0
    tx_delay_ms: float = Field(default=1.0, ge=0.0)
    rx_start_delay_ms: float = Field(default=2.0, ge=0.0)
    rx_duration_ms: float = Field(default=20.0, ge=0.0)
    sensor_sample_time_s: float = 0.0
    sensor_latency_ms: float = Field(default=0.0, ge=0.0)


class D14TimelineEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: Literal[
        "trigger",
        "tx",
        "rx_start",
        "rx_end",
        "sensor_sample",
        "sensor_available",
    ]
    time_s: float
    state: Literal["Configured", "Derived"]


class D14TimingResponse(BaseModel):
    """Render-ready scenario-relative event timeline."""

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
    timeline: tuple[D14TimelineEvent, ...]
    metadata: dict[str, str]


def prepare_d14_timing_response(request: D14TimingRequest) -> D14TimingResponse:
    """Build a PED-D14 timeline using only canonical simulation-time semantics."""

    trigger = SimulationTime(seconds=request.trigger_time_s)
    tx = trigger.shifted(request.tx_delay_ms * 1e-3)
    rx_start = trigger.shifted(request.rx_start_delay_ms * 1e-3)
    rx_end = rx_start.shifted(request.rx_duration_ms * 1e-3)
    ping = PingTiming(
        trigger_time=trigger,
        tx_time=tx,
        rx_start_time=rx_start,
        rx_end_time=rx_end,
    )

    sensor_sample = SimulationTime(seconds=request.sensor_sample_time_s)
    sensor_available = sensor_sample.shifted(request.sensor_latency_ms * 1e-3)

    timeline = tuple(
        sorted(
            (
                D14TimelineEvent(kind="trigger", time_s=float(trigger.seconds), state="Configured"),
                D14TimelineEvent(kind="tx", time_s=float(tx.seconds), state="Derived"),
                D14TimelineEvent(kind="rx_start", time_s=float(rx_start.seconds), state="Derived"),
                D14TimelineEvent(kind="rx_end", time_s=float(rx_end.seconds), state="Derived"),
                D14TimelineEvent(
                    kind="sensor_sample",
                    time_s=float(sensor_sample.seconds),
                    state="Configured",
                ),
                D14TimelineEvent(
                    kind="sensor_available",
                    time_s=float(sensor_available.seconds),
                    state="Derived",
                ),
            ),
            key=lambda event: event.time_s,
        )
    )

    return D14TimingResponse(
        trigger_time_s=float(ping.trigger_time.seconds),
        tx_time_s=float(ping.tx_time.seconds),
        rx_start_time_s=float(ping.rx_start_time.seconds),
        rx_end_time_s=float(ping.rx_end_time.seconds),
        receive_duration_ms=ping.receive_duration_seconds * 1e3,
        tx_to_rx_end_ms=ping.tx_to_rx_end_seconds * 1e3,
        sensor_sample_time_s=float(sensor_sample.seconds),
        sensor_available_time_s=float(sensor_available.seconds),
        sensor_latency_ms=request.sensor_latency_ms,
        timeline=timeline,
        metadata={
            "time_basis": "scenario-relative simulation time",
            "time_unit": "s",
            "latency_unit": "ms",
            "state_semantics": "Configured epochs/latency; Derived shifted event epochs",
            "unsupported": "temporal-to-spatial consequence",
        },
    )

"""Core simulation-time models for HydroSIM.

HydroSIM separates simulation time from wall-clock execution time. Values in this
module are expressed in seconds relative to a scenario-defined simulation epoch.
They do not imply UTC, GPS time, or any external time scale.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, FiniteFloat, model_validator


class SimulationTime(BaseModel):
    """One instant in scenario-relative simulation time, expressed in seconds."""

    model_config = ConfigDict(frozen=True)

    seconds: FiniteFloat

    def shifted(self, delta_seconds: float) -> "SimulationTime":
        """Return a new instant offset by ``delta_seconds``."""

        return SimulationTime(seconds=self.seconds + float(delta_seconds))

    def delta_to(self, other: "SimulationTime") -> float:
        """Return ``other - self`` in seconds."""

        return float(other.seconds - self.seconds)


class TimeInterval(BaseModel):
    """Closed simulation-time interval with non-decreasing endpoints."""

    model_config = ConfigDict(frozen=True)

    start: SimulationTime
    end: SimulationTime

    @model_validator(mode="after")
    def end_must_not_precede_start(self) -> "TimeInterval":
        if self.end.seconds < self.start.seconds:
            raise ValueError("end time must not precede start time")
        return self

    @property
    def duration_seconds(self) -> float:
        return float(self.end.seconds - self.start.seconds)

    def contains(self, time: SimulationTime) -> bool:
        return self.start.seconds <= time.seconds <= self.end.seconds


class PingTiming(BaseModel):
    """Canonical event epochs associated with one acoustic ping.

    ``trigger_time`` is the command/scheduler epoch for the ping.
    ``tx_time`` is the acoustic transmit epoch.
    ``rx_start_time`` and ``rx_end_time`` delimit the receive interval.

    They are intentionally distinct. Future sector- or beam-level timing models may
    refine these epochs without changing their semantic meaning.
    """

    model_config = ConfigDict(frozen=True)

    trigger_time: SimulationTime
    tx_time: SimulationTime
    rx_start_time: SimulationTime
    rx_end_time: SimulationTime

    @model_validator(mode="after")
    def times_must_be_ordered(self) -> "PingTiming":
        values = (
            self.trigger_time.seconds,
            self.tx_time.seconds,
            self.rx_start_time.seconds,
            self.rx_end_time.seconds,
        )
        if values != tuple(sorted(values)):
            raise ValueError(
                "ping timing must satisfy trigger_time <= tx_time <= "
                "rx_start_time <= rx_end_time"
            )
        return self

    @property
    def receive_duration_seconds(self) -> float:
        return float(self.rx_end_time.seconds - self.rx_start_time.seconds)

    @property
    def tx_to_rx_end_seconds(self) -> float:
        return float(self.rx_end_time.seconds - self.tx_time.seconds)

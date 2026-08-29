"""Acquisition event models for dynamic HydroSIM surveys."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from hydrosim.geometry import Pose
from hydrosim.timing import PingTiming, SimulationTime


class PingSchedule(BaseModel):
    """Regular acoustic ping schedule in simulation time."""

    model_config = ConfigDict(frozen=True)

    start_time: SimulationTime
    end_time: SimulationTime
    ping_period_seconds: FiniteFloat = Field(gt=0.0)
    trigger_to_tx_seconds: FiniteFloat = Field(default=0.0, ge=0.0)
    receive_start_delay_seconds: FiniteFloat = Field(default=0.0, ge=0.0)
    receive_window_seconds: FiniteFloat = Field(default=0.0, ge=0.0)

    @model_validator(mode="after")
    def end_must_not_precede_start(self) -> "PingSchedule":
        if self.end_time.seconds < self.start_time.seconds:
            raise ValueError("end_time must not precede start_time")
        return self


class AcquisitionPing(BaseModel):
    """One scheduled ping and the Truth vessel states at its event epochs.

    The initial acquisition infrastructure records vessel pose at transmit and at
    the receive-window boundaries. Beam-specific bottom-return epochs will be added
    later, because a multibeam ping does not have one universal physical rx_time.
    """

    model_config = ConfigDict(frozen=True)

    ping_index: int = Field(ge=0)
    timing: PingTiming
    tx_pose: Pose
    rx_start_pose: Pose
    rx_end_pose: Pose


class AcquisitionSequence(BaseModel):
    """Time-ordered sequence of dynamic acquisition pings."""

    model_config = ConfigDict(frozen=True)

    pings: tuple[AcquisitionPing, ...]

    @model_validator(mode="after")
    def pings_must_be_ordered(self) -> "AcquisitionSequence":
        indices = [ping.ping_index for ping in self.pings]
        if indices != list(range(len(indices))):
            raise ValueError("ping indices must be contiguous and start at zero")
        tx_times = [ping.timing.tx_time.seconds for ping in self.pings]
        if any(b <= a for a, b in zip(tx_times, tx_times[1:])):
            raise ValueError("ping transmit times must be strictly increasing")
        return self

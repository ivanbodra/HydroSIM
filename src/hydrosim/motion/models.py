"""Deterministic vessel trajectory and motion generators for HydroSIM.

These models generate scenario Truth. They intentionally separate mean translational
trajectory from oscillatory vessel motion so that each contribution remains explicit,
auditable, and independently controllable.
"""

from __future__ import annotations

from math import cos, pi, sin

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from hydrosim.geometry import Attitude, Pose, Vector3
from hydrosim.timing import SimulationTime


class HarmonicSignal(BaseModel):
    """A deterministic sinusoidal scalar signal.

    ``amplitude`` and ``offset`` use the units of the quantity being represented.
    Angular quantities therefore use radians internally, while heave uses metres.
    ``phase_rad`` is the phase at simulation time zero.
    """

    model_config = ConfigDict(frozen=True)

    amplitude: FiniteFloat = 0.0
    period_seconds: FiniteFloat = Field(default=1.0, gt=0.0)
    phase_rad: FiniteFloat = 0.0
    offset: FiniteFloat = 0.0

    def value_at(self, time: SimulationTime) -> float:
        phase = 2.0 * pi * float(time.seconds) / float(self.period_seconds) + float(
            self.phase_rad
        )
        return float(self.offset + self.amplitude * sin(phase))


class StraightLineTrajectory(BaseModel):
    """Constant-speed straight trajectory in a North-East-Down navigation frame.

    Heading is radians clockwise from North, consistent with HydroSIM's canonical
    navigation convention. ``start_position`` is in metres in the declared frame.
    The trajectory itself does not add heave; vertical vessel motion is composed
    separately by :class:`VesselMotionModel`.
    """

    model_config = ConfigDict(frozen=True)

    start_time: SimulationTime = SimulationTime(seconds=0.0)
    start_position: Vector3
    speed_mps: FiniteFloat = Field(ge=0.0)
    heading_rad: FiniteFloat
    frame: str = Field(default="N", min_length=1)

    @model_validator(mode="after")
    def frame_must_not_be_blank(self) -> "StraightLineTrajectory":
        normalized = self.frame.strip()
        if not normalized:
            raise ValueError("frame must not be blank")
        object.__setattr__(self, "frame", normalized)
        return self

    def position_at(self, time: SimulationTime) -> Vector3:
        dt = float(time.seconds - self.start_time.seconds)
        distance = float(self.speed_mps) * dt
        return Vector3(
            x=self.start_position.x + distance * cos(float(self.heading_rad)),
            y=self.start_position.y + distance * sin(float(self.heading_rad)),
            z=self.start_position.z,
        )


class VesselMotionModel(BaseModel):
    """Compose a mean trajectory with deterministic roll, pitch, yaw, and heave.

    Roll, pitch, and yaw-deviation signals are radians. Heave is metres and follows
    HydroSIM's hydrographic motion convention: positive heave is Up. Because the
    navigation frame is Down-positive, positive heave subtracts from navigation Z.

    ``yaw_deviation`` is added to the trajectory heading; it is not a separate
    integration/configuration error.
    """

    model_config = ConfigDict(frozen=True)

    trajectory: StraightLineTrajectory
    roll: HarmonicSignal = HarmonicSignal()
    pitch: HarmonicSignal = HarmonicSignal()
    yaw_deviation: HarmonicSignal = HarmonicSignal()
    heave: HarmonicSignal = HarmonicSignal()

    def pose_at(self, time: SimulationTime) -> Pose:
        base_position = self.trajectory.position_at(time)
        heave_up = self.heave.value_at(time)

        return Pose(
            position=Vector3(
                x=base_position.x,
                y=base_position.y,
                z=base_position.z - heave_up,
            ),
            attitude=Attitude(
                roll=self.roll.value_at(time),
                pitch=self.pitch.value_at(time),
                yaw=float(self.trajectory.heading_rad) + self.yaw_deviation.value_at(time),
            ),
            frame=self.trajectory.frame,
        )

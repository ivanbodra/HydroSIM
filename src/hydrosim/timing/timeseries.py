"""Deterministic time-series primitives for dynamic HydroSIM state."""

from __future__ import annotations

from bisect import bisect_left
from math import pi

from pydantic import BaseModel, ConfigDict, model_validator

from hydrosim.geometry import Attitude, Pose, Vector3

from .models import SimulationTime


class TimedPose(BaseModel):
    """One vessel or sensor pose sample at a simulation-time instant."""

    model_config = ConfigDict(frozen=True)

    time: SimulationTime
    pose: Pose


def _lerp(a: float, b: float, fraction: float) -> float:
    return a + fraction * (b - a)


def _lerp_angle_shortest(a: float, b: float, fraction: float) -> float:
    """Interpolate radians using the shortest wrapped angular difference."""

    delta = (b - a + pi) % (2.0 * pi) - pi
    return a + fraction * delta


class PoseTimeSeries(BaseModel):
    """Strictly time-ordered pose samples with deterministic linear interpolation.

    Position is interpolated componentwise. Roll, pitch, and yaw use shortest-path
    wrapped interpolation in radians. This is a reference interpolation backend,
    suitable for ordinary densely sampled motion streams and exact latency sampling.
    Higher-order or quaternion interpolation may be added as explicit alternatives.
    """

    model_config = ConfigDict(frozen=True)

    samples: tuple[TimedPose, ...]

    @model_validator(mode="after")
    def samples_must_be_valid(self) -> "PoseTimeSeries":
        if not self.samples:
            raise ValueError("pose time series requires at least one sample")

        frames = {sample.pose.frame for sample in self.samples}
        if len(frames) != 1:
            raise ValueError("all pose samples must use the same frame")

        times = [sample.time.seconds for sample in self.samples]
        if any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("pose sample times must be strictly increasing")
        return self

    @property
    def start_time(self) -> SimulationTime:
        return self.samples[0].time

    @property
    def end_time(self) -> SimulationTime:
        return self.samples[-1].time

    def pose_at(self, time: SimulationTime) -> Pose:
        """Return the pose at ``time`` using bounded linear interpolation.

        Extrapolation is intentionally rejected. Simulation components must make
        missing temporal support explicit rather than silently inventing state.
        """

        target = float(time.seconds)
        times = [float(sample.time.seconds) for sample in self.samples]

        if target < times[0] or target > times[-1]:
            raise ValueError("requested time lies outside pose-series support")

        index = bisect_left(times, target)
        if index < len(times) and times[index] == target:
            return self.samples[index].pose
        if index == 0 or index == len(times):
            raise ValueError("requested time lies outside pose-series support")

        left = self.samples[index - 1]
        right = self.samples[index]
        dt = float(right.time.seconds - left.time.seconds)
        fraction = (target - float(left.time.seconds)) / dt

        lp = left.pose.position
        rp = right.pose.position
        la = left.pose.attitude
        ra = right.pose.attitude

        return Pose(
            position=Vector3(
                x=_lerp(lp.x, rp.x, fraction),
                y=_lerp(lp.y, rp.y, fraction),
                z=_lerp(lp.z, rp.z, fraction),
            ),
            attitude=Attitude(
                roll=_lerp_angle_shortest(la.roll, ra.roll, fraction),
                pitch=_lerp_angle_shortest(la.pitch, ra.pitch, fraction),
                yaw=_lerp_angle_shortest(la.yaw, ra.yaw, fraction),
            ),
            frame=left.pose.frame,
        )

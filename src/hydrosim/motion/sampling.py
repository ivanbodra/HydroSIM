"""Sampling utilities that turn continuous scenario motion into pose time series."""

from __future__ import annotations

from math import floor

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.timing import PoseTimeSeries, SimulationTime, TimeInterval, TimedPose

from .models import VesselMotionModel


class MotionSamplingConfig(BaseModel):
    """Regular sampling configuration for generated vessel motion."""

    model_config = ConfigDict(frozen=True)

    interval: TimeInterval
    sample_period_seconds: FiniteFloat = Field(gt=0.0)
    include_end: bool = True


def _sample_seconds(config: MotionSamplingConfig) -> tuple[float, ...]:
    start = float(config.interval.start.seconds)
    end = float(config.interval.end.seconds)
    step = float(config.sample_period_seconds)

    if end == start:
        return (start,)

    count = floor((end - start) / step)
    values = [start + index * step for index in range(count + 1)]

    tolerance = 1e-12 * max(1.0, abs(start), abs(end), abs(step))
    if values and abs(values[-1] - end) <= tolerance:
        values[-1] = end
    elif config.include_end:
        values.append(end)

    return tuple(values)


def generate_pose_time_series(
    motion: VesselMotionModel,
    config: MotionSamplingConfig,
) -> PoseTimeSeries:
    """Sample a continuous vessel-motion model into a deterministic pose series."""

    samples = tuple(
        TimedPose(
            time=SimulationTime(seconds=seconds),
            pose=motion.pose_at(SimulationTime(seconds=seconds)),
        )
        for seconds in _sample_seconds(config)
    )
    return PoseTimeSeries(samples=samples)

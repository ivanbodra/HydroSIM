from math import pi

import pytest

from hydrosim.geometry import Attitude, Pose, Vector3
from hydrosim.timing import PingTiming, PoseTimeSeries, SimulationTime, TimeInterval, TimedPose


def _pose(*, x: float, yaw: float = 0.0, frame: str = "N") -> Pose:
    return Pose(
        position=Vector3(x=x, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=yaw),
        frame=frame,
    )


def test_simulation_time_shift_and_delta() -> None:
    t0 = SimulationTime(seconds=10.0)
    t1 = t0.shifted(2.5)

    assert t1.seconds == pytest.approx(12.5)
    assert t0.delta_to(t1) == pytest.approx(2.5)


def test_time_interval_rejects_reversed_endpoints() -> None:
    with pytest.raises(ValueError):
        TimeInterval(start=SimulationTime(seconds=2.0), end=SimulationTime(seconds=1.0))


def test_ping_timing_preserves_distinct_event_epochs() -> None:
    timing = PingTiming(
        trigger_time=SimulationTime(seconds=1.000),
        tx_time=SimulationTime(seconds=1.002),
        rx_start_time=SimulationTime(seconds=1.003),
        rx_end_time=SimulationTime(seconds=1.043),
    )

    assert timing.receive_duration_seconds == pytest.approx(0.040)
    assert timing.tx_to_rx_end_seconds == pytest.approx(0.041)


def test_ping_timing_rejects_nonphysical_ordering() -> None:
    with pytest.raises(ValueError):
        PingTiming(
            trigger_time=SimulationTime(seconds=1.0),
            tx_time=SimulationTime(seconds=1.1),
            rx_start_time=SimulationTime(seconds=1.05),
            rx_end_time=SimulationTime(seconds=1.2),
        )


def test_pose_series_interpolates_position() -> None:
    series = PoseTimeSeries(
        samples=(
            TimedPose(time=SimulationTime(seconds=0.0), pose=_pose(x=0.0)),
            TimedPose(time=SimulationTime(seconds=2.0), pose=_pose(x=10.0)),
        )
    )

    interpolated = series.pose_at(SimulationTime(seconds=0.5))
    assert interpolated.position.x == pytest.approx(2.5)


def test_pose_series_uses_shortest_wrapped_angular_path() -> None:
    series = PoseTimeSeries(
        samples=(
            TimedPose(
                time=SimulationTime(seconds=0.0),
                pose=_pose(x=0.0, yaw=pi - 0.1),
            ),
            TimedPose(
                time=SimulationTime(seconds=2.0),
                pose=_pose(x=0.0, yaw=-pi + 0.1),
            ),
        )
    )

    midpoint = series.pose_at(SimulationTime(seconds=1.0))
    assert abs(abs(midpoint.attitude.yaw) - pi) < 1e-12


def test_pose_series_rejects_extrapolation() -> None:
    series = PoseTimeSeries(
        samples=(
            TimedPose(time=SimulationTime(seconds=0.0), pose=_pose(x=0.0)),
            TimedPose(time=SimulationTime(seconds=1.0), pose=_pose(x=1.0)),
        )
    )

    with pytest.raises(ValueError):
        series.pose_at(SimulationTime(seconds=-0.01))


def test_pose_series_requires_strictly_increasing_times_and_one_frame() -> None:
    with pytest.raises(ValueError):
        PoseTimeSeries(
            samples=(
                TimedPose(time=SimulationTime(seconds=0.0), pose=_pose(x=0.0)),
                TimedPose(time=SimulationTime(seconds=0.0), pose=_pose(x=1.0)),
            )
        )

    with pytest.raises(ValueError):
        PoseTimeSeries(
            samples=(
                TimedPose(time=SimulationTime(seconds=0.0), pose=_pose(x=0.0, frame="N")),
                TimedPose(time=SimulationTime(seconds=1.0), pose=_pose(x=1.0, frame="B")),
            )
        )

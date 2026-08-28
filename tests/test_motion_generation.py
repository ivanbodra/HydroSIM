from math import pi

import pytest

from hydrosim.geometry import Vector3
from hydrosim.motion import (
    HarmonicSignal,
    MotionSamplingConfig,
    StraightLineTrajectory,
    VesselMotionModel,
    generate_pose_time_series,
)
from hydrosim.timing import SimulationTime, TimeInterval


def test_straight_line_trajectory_north_and_east_headings() -> None:
    origin = Vector3(x=100.0, y=200.0, z=5.0)

    north = StraightLineTrajectory(
        start_position=origin,
        speed_mps=2.0,
        heading_rad=0.0,
    )
    east = StraightLineTrajectory(
        start_position=origin,
        speed_mps=2.0,
        heading_rad=pi / 2.0,
    )

    north_position = north.position_at(SimulationTime(seconds=10.0))
    east_position = east.position_at(SimulationTime(seconds=10.0))

    assert north_position.x == pytest.approx(120.0)
    assert north_position.y == pytest.approx(200.0)
    assert north_position.z == pytest.approx(5.0)

    assert east_position.x == pytest.approx(100.0)
    assert east_position.y == pytest.approx(220.0)
    assert east_position.z == pytest.approx(5.0)


def test_harmonic_signal_uses_declared_amplitude_period_phase_and_offset() -> None:
    signal = HarmonicSignal(
        amplitude=2.0,
        period_seconds=4.0,
        phase_rad=0.0,
        offset=3.0,
    )

    assert signal.value_at(SimulationTime(seconds=0.0)) == pytest.approx(3.0)
    assert signal.value_at(SimulationTime(seconds=1.0)) == pytest.approx(5.0)
    assert signal.value_at(SimulationTime(seconds=2.0)) == pytest.approx(3.0)
    assert signal.value_at(SimulationTime(seconds=3.0)) == pytest.approx(1.0)


def test_positive_heave_moves_pose_up_in_down_positive_navigation_frame() -> None:
    trajectory = StraightLineTrajectory(
        start_position=Vector3(x=0.0, y=0.0, z=20.0),
        speed_mps=0.0,
        heading_rad=0.0,
    )
    motion = VesselMotionModel(
        trajectory=trajectory,
        heave=HarmonicSignal(amplitude=2.0, period_seconds=4.0),
    )

    pose = motion.pose_at(SimulationTime(seconds=1.0))

    assert pose.position.z == pytest.approx(18.0)


def test_vessel_motion_composes_mean_heading_with_yaw_deviation() -> None:
    trajectory = StraightLineTrajectory(
        start_position=Vector3(x=0.0, y=0.0, z=0.0),
        speed_mps=1.0,
        heading_rad=pi / 4.0,
    )
    motion = VesselMotionModel(
        trajectory=trajectory,
        roll=HarmonicSignal(amplitude=0.1, period_seconds=4.0),
        pitch=HarmonicSignal(amplitude=0.2, period_seconds=8.0),
        yaw_deviation=HarmonicSignal(amplitude=0.05, period_seconds=4.0),
    )

    pose = motion.pose_at(SimulationTime(seconds=1.0))

    assert pose.attitude.roll == pytest.approx(0.1)
    assert pose.attitude.pitch == pytest.approx(0.2 * (2.0**0.5) / 2.0)
    assert pose.attitude.yaw == pytest.approx(pi / 4.0 + 0.05)


def test_generate_pose_time_series_includes_interval_end_when_not_on_sample_grid() -> None:
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=0.0),
            speed_mps=2.0,
            heading_rad=0.0,
        )
    )
    config = MotionSamplingConfig(
        interval=TimeInterval(
            start=SimulationTime(seconds=0.0),
            end=SimulationTime(seconds=2.5),
        ),
        sample_period_seconds=1.0,
        include_end=True,
    )

    series = generate_pose_time_series(motion, config)

    assert [sample.time.seconds for sample in series.samples] == [0.0, 1.0, 2.0, 2.5]
    assert series.samples[-1].pose.position.x == pytest.approx(5.0)
    assert series.pose_at(SimulationTime(seconds=1.5)).position.x == pytest.approx(3.0)


def test_motion_sampling_can_leave_end_off_regular_grid_when_requested() -> None:
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=0.0),
            speed_mps=0.0,
            heading_rad=0.0,
        )
    )
    config = MotionSamplingConfig(
        interval=TimeInterval(
            start=SimulationTime(seconds=0.0),
            end=SimulationTime(seconds=2.5),
        ),
        sample_period_seconds=1.0,
        include_end=False,
    )

    series = generate_pose_time_series(motion, config)

    assert [sample.time.seconds for sample in series.samples] == [0.0, 1.0, 2.0]

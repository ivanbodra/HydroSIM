from math import isclose, pi

import pytest

from hydrosim.acquisition import PingSchedule, generate_acquisition_sequence
from hydrosim.geometry import Vector3
from hydrosim.motion import (
    HarmonicSignal,
    MotionSamplingConfig,
    StraightLineTrajectory,
    VesselMotionModel,
    generate_pose_time_series,
)
from hydrosim.timing import SimulationTime, TimeInterval


def _poses():
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=10.0),
            speed_mps=2.0,
            heading_rad=0.0,
        ),
        roll=HarmonicSignal(amplitude=0.1, period_seconds=4.0),
        heave=HarmonicSignal(amplitude=1.0, period_seconds=4.0),
    )
    return generate_pose_time_series(
        motion,
        MotionSamplingConfig(
            interval=TimeInterval(
                start=SimulationTime(seconds=0.0),
                end=SimulationTime(seconds=5.0),
            ),
            sample_period_seconds=0.05,
        ),
    )


def test_acquisition_samples_distinct_tx_and_rx_truth_states():
    sequence = generate_acquisition_sequence(
        _poses(),
        PingSchedule(
            start_time=SimulationTime(seconds=0.0),
            end_time=SimulationTime(seconds=2.0),
            ping_period_seconds=1.0,
            trigger_to_tx_seconds=0.1,
            receive_start_delay_seconds=0.2,
            receive_window_seconds=0.4,
        ),
    )

    assert len(sequence.pings) == 3
    ping = sequence.pings[0]
    assert ping.timing.trigger_time.seconds == 0.0
    assert ping.timing.tx_time.seconds == 0.1
    assert ping.timing.rx_start_time.seconds == 0.3
    assert isclose(ping.timing.rx_end_time.seconds, 0.7)
    assert ping.tx_pose.position.x < ping.rx_start_pose.position.x < ping.rx_end_pose.position.x
    assert ping.tx_pose.attitude.roll != ping.rx_end_pose.attitude.roll
    assert ping.tx_pose.position.z != ping.rx_end_pose.position.z


def test_ping_period_controls_transmit_sequence():
    sequence = generate_acquisition_sequence(
        _poses(),
        PingSchedule(
            start_time=SimulationTime(seconds=0.0),
            end_time=SimulationTime(seconds=2.0),
            ping_period_seconds=0.5,
        ),
    )
    assert [ping.timing.tx_time.seconds for ping in sequence.pings] == [0.0, 0.5, 1.0, 1.5, 2.0]


def test_acquisition_rejects_missing_motion_support_for_rx_window():
    with pytest.raises(ValueError, match="outside pose-series support"):
        generate_acquisition_sequence(
            _poses(),
            PingSchedule(
                start_time=SimulationTime(seconds=4.9),
                end_time=SimulationTime(seconds=4.9),
                ping_period_seconds=1.0,
                receive_window_seconds=0.2,
            ),
        )

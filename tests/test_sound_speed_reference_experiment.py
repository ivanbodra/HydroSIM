from math import radians

import pytest

from hydrosim.acquisition.sound_speed_reference_experiment import (
    run_sound_speed_at_transducer_reference_experiment,
)
from hydrosim.acquisition.sound_speed_sensor import SoundSpeedSensorAtTransducer
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def test_zero_sensor_error_closes_truth_and_reconstruction() -> None:
    result = run_sound_speed_at_transducer_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=radians(35.0),
        true_local_sound_speed_mps=1500.0,
    )

    assert result.sound_speed_used_by_sonar.sound_speed_mps == pytest.approx(1500.0)
    assert result.transmit_truth.physical_angle_rad == pytest.approx(radians(35.0))
    assert result.receive_angle_estimate.estimated_angle_rad == pytest.approx(radians(35.0))
    assert result.calculated_sounding.point.is_close(result.truth_bottom_point, atol=1e-9)
    assert result.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)


def test_sensor_bias_changes_physical_tx_but_rx_maps_wavefront_back_under_same_used_c() -> None:
    configured = radians(35.0)
    result = run_sound_speed_at_transducer_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=configured,
        true_local_sound_speed_mps=1500.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=-20.0),
    )

    assert result.sound_speed_used_by_sonar.sound_speed_mps == pytest.approx(1480.0)
    assert result.transmit_truth.physical_angle_rad > configured
    assert result.receive_angle_estimate.estimated_angle_rad == pytest.approx(configured)
    assert result.sounding_error_norm_m > 0.0
    assert not result.calculated_sounding.point.is_close(result.truth_bottom_point, atol=1e-6)


def test_reference_experiment_keeps_truth_out_of_sonar_states() -> None:
    result = run_sound_speed_at_transducer_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=80.0),
        configured_across_track_angle_rad=radians(25.0),
        true_local_sound_speed_mps=1495.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=5.0),
    )

    assert not hasattr(result.sensor_measurement, "true_local_sound_speed_mps")
    assert not hasattr(result.sound_speed_used_by_sonar, "true_local_sound_speed_mps")
    assert result.observation.detected_across_track_angle_rad == pytest.approx(
        result.receive_angle_estimate.estimated_angle_rad
    )

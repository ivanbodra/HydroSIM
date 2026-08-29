from math import radians, sqrt

import pytest

from hydrosim.acquisition import (
    DetectedAcousticObservation,
    reconstruct_constant_sound_speed_sounding,
)
from hydrosim.geometry import Attitude, Pose, Vector3


def _observation(*, across_track_angle_rad: float | None) -> DetectedAcousticObservation:
    return DetectedAcousticObservation(
        parent_beam_index=3,
        detection_method="phase_zero_crossing",
        twtt_seconds=0.100,
        detected_across_track_angle_rad=across_track_angle_rad,
        quality=0.9,
    )


def _sensor_pose(*, yaw_rad: float = 0.0) -> Pose:
    return Pose(
        position=Vector3(x=10.0, y=20.0, z=5.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=yaw_rad),
        frame="N",
    )


def test_nadir_reconstruction_applies_half_twtt_range_downward() -> None:
    sounding = reconstruct_constant_sound_speed_sounding(
        _observation(across_track_angle_rad=0.0),
        sensor_pose=_sensor_pose(),
        along_track_angle_rad=0.0,
        sound_speed_mps=1500.0,
    )

    assert sounding.range_interpretation.reciprocal_one_way_range_m == pytest.approx(75.0)
    assert sounding.point.x == pytest.approx(10.0)
    assert sounding.point.y == pytest.approx(20.0)
    assert sounding.point.z == pytest.approx(80.0)
    assert sounding.reconstruction_assumption == "stationary_reciprocal_straight_ray_constant_sound_speed"


def test_mills_cross_angles_define_full_sensor_frame_direction() -> None:
    angle = radians(45.0)
    sounding = reconstruct_constant_sound_speed_sounding(
        _observation(across_track_angle_rad=angle),
        sensor_pose=Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            frame="N",
        ),
        along_track_angle_rad=angle,
        sound_speed_mps=1500.0,
    )

    component = 1.0 / sqrt(3.0)
    assert sounding.direction_sensor_frame.x == pytest.approx(component)
    assert sounding.direction_sensor_frame.y == pytest.approx(-component)
    assert sounding.direction_sensor_frame.z == pytest.approx(component)
    assert sounding.point.x == pytest.approx(75.0 * component)
    assert sounding.point.y == pytest.approx(-75.0 * component)
    assert sounding.point.z == pytest.approx(75.0 * component)


def test_sensor_pose_rotates_reconstructed_direction_to_destination_frame() -> None:
    sounding = reconstruct_constant_sound_speed_sounding(
        _observation(across_track_angle_rad=0.0),
        sensor_pose=_sensor_pose(yaw_rad=radians(90.0)),
        along_track_angle_rad=radians(45.0),
        sound_speed_mps=1500.0,
    )

    component = 1.0 / sqrt(2.0)
    assert sounding.direction_destination_frame.x == pytest.approx(0.0, abs=1e-12)
    assert sounding.direction_destination_frame.y == pytest.approx(component)
    assert sounding.direction_destination_frame.z == pytest.approx(component)


def test_cartesian_reconstruction_requires_detected_across_track_angle() -> None:
    with pytest.raises(ValueError, match="detected across-track angle is required"):
        reconstruct_constant_sound_speed_sounding(
            _observation(across_track_angle_rad=None),
            sensor_pose=_sensor_pose(),
            along_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
        )

from math import radians, sqrt

import pytest

from hydrosim.acquisition import (
    DetectedAcousticObservation,
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    reconstruct_constant_sound_speed_sounding,
    reconstruct_layered_sound_speed_sounding,
    reconstruct_layered_sound_speed_sounding_from_initial_direction,
    sensor_angular_direction,
)
from hydrosim.geometry import Attitude, Pose, Vector3


def _observation(*, across_track_angle_rad: float | None, twtt_seconds: float = 0.100) -> DetectedAcousticObservation:
    return DetectedAcousticObservation(
        parent_beam_index=3,
        detection_method="phase_zero_crossing",
        twtt_seconds=twtt_seconds,
        detected_across_track_angle_rad=across_track_angle_rad,
        quality=0.9,
    )


def _sensor_pose(*, yaw_rad: float = 0.0) -> Pose:
    return Pose(
        position=Vector3(x=10.0, y=20.0, z=5.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=yaw_rad),
        frame="N",
    )


def _layered_profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=50.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=50.0, bottom_depth_m=120.0, sound_speed_mps=1600.0),
        )
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


def test_mills_cross_angles_define_full_sensor_frame_direction() -> None:
    angle = radians(45.0)
    sounding = reconstruct_constant_sound_speed_sounding(
        _observation(across_track_angle_rad=angle),
        sensor_pose=Pose(position=Vector3(x=0.0, y=0.0, z=0.0), attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0), frame="N"),
        along_track_angle_rad=angle,
        sound_speed_mps=1500.0,
    )
    component = 1.0 / sqrt(3.0)
    assert sounding.direction_sensor_frame.x == pytest.approx(component)
    assert sounding.direction_sensor_frame.y == pytest.approx(-component)
    assert sounding.direction_sensor_frame.z == pytest.approx(component)


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


def test_layered_nadir_reconstruction_stops_on_measured_twtt_not_average_speed() -> None:
    one_way_time = 50.0 / 1500.0 + 25.0 / 1600.0
    sounding = reconstruct_layered_sound_speed_sounding(
        _observation(across_track_angle_rad=0.0, twtt_seconds=2.0 * one_way_time),
        sensor_pose=Pose(position=Vector3(x=0.0, y=0.0, z=10.0), attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0), frame="N"),
        along_track_angle_rad=0.0,
        profile=_layered_profile(),
        profile_start_depth_m=0.0,
    )
    assert sounding.one_way_travel_time_seconds == pytest.approx(one_way_time)
    assert sounding.ray_path.target_depth_m == pytest.approx(75.0)
    assert len(sounding.ray_path.segments) == 2
    assert sounding.point.z == pytest.approx(85.0)


def test_layered_reconstruction_preserves_horizontal_azimuth_while_ray_bends() -> None:
    sounding = reconstruct_layered_sound_speed_sounding(
        _observation(across_track_angle_rad=radians(20.0), twtt_seconds=0.08),
        sensor_pose=Pose(position=Vector3(x=0.0, y=0.0, z=0.0), attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0), frame="N"),
        along_track_angle_rad=radians(10.0),
        profile=_layered_profile(),
        profile_start_depth_m=0.0,
    )
    assert len(sounding.ray_path.segments) == 2
    assert sounding.ray_path.segments[1].angle_from_vertical_rad > sounding.ray_path.segments[0].angle_from_vertical_rad
    assert sounding.point.x > 0.0
    assert sounding.point.y < 0.0
    assert sounding.point.z > 0.0


def test_initial_direction_helper_is_processing_only() -> None:
    observation = _observation(across_track_angle_rad=radians(25.0), twtt_seconds=0.08)
    direction = sensor_angular_direction(radians(10.0), radians(25.0))
    sounding = reconstruct_layered_sound_speed_sounding_from_initial_direction(
        observation,
        sensor_pose=Pose(position=Vector3(x=0.0, y=0.0, z=0.0), attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0), frame="N"),
        initial_direction_sensor_frame=direction,
        profile=_layered_profile(),
        profile_start_depth_m=0.0,
        along_track_angle_rad=radians(10.0),
        across_track_angle_rad=radians(25.0),
    )
    assert sounding.initial_direction_sensor_frame.is_close(direction, atol=1e-12)
    assert not hasattr(sounding, "true_local_sound_speed_mps")
    assert not hasattr(sounding, "sound_speed_at_transducer")


def test_layered_reconstruction_rejects_nonpositive_twtt() -> None:
    with pytest.raises(ValueError, match="positive TWTT"):
        reconstruct_layered_sound_speed_sounding(
            _observation(across_track_angle_rad=0.0, twtt_seconds=0.0),
            sensor_pose=_sensor_pose(),
            along_track_angle_rad=0.0,
            profile=_layered_profile(),
            profile_start_depth_m=0.0,
        )

from math import radians

import pytest

from hydrosim.acquisition import (
    DetectedAcousticObservation,
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    reconstruct_layered_sound_speed_sounding_from_sonar_state,
    resolve_layered_reconstruction_initial_direction,
    sensor_angular_direction,
    use_manual_sound_speed_at_transducer,
)
from hydrosim.geometry import Attitude, Pose, Vector3


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=120.0, sound_speed_mps=1550.0),
        )
    )


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def test_equal_used_and_profile_start_sound_speed_preserves_detected_direction() -> None:
    detected = sensor_angular_direction(radians(10.0), radians(25.0))
    result = resolve_layered_reconstruction_initial_direction(
        detected_direction_sensor_frame=detected,
        sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1500.0),
        profile=_profile(),
        profile_start_depth_m=0.0,
    )
    assert result.profile_initial_direction_sensor_frame.is_close(detected, atol=1e-12)
    assert result.profile_boundary.sound_speed_mps == pytest.approx(1500.0)
    assert result.profile_boundary.source == "sound_speed_at_transducer"


def test_profile_entry_direction_preserves_boundary_tangential_slowness() -> None:
    detected = sensor_angular_direction(radians(10.0), radians(25.0))
    profile = _profile()
    result = resolve_layered_reconstruction_initial_direction(
        detected_direction_sensor_frame=detected,
        sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1480.0),
        profile=profile,
        profile_start_depth_m=0.0,
    )
    profile_direction = result.profile_initial_direction_sensor_frame
    assert result.profile_boundary.sound_speed_mps == pytest.approx(1480.0)
    assert profile_direction.x / 1500.0 == pytest.approx(detected.x / 1480.0)
    assert profile_direction.y / 1500.0 == pytest.approx(detected.y / 1480.0)
    assert abs(profile_direction.x) > abs(detected.x)
    assert abs(profile_direction.y) > abs(detected.y)
    # The zero-thickness boundary must not overwrite the finite profile layer.
    assert profile.layer_at_depth(0.0).sound_speed_mps == pytest.approx(1500.0)


def test_layered_sonar_state_reconstruction_uses_slowness_not_raw_detected_angle() -> None:
    detected_angle = radians(30.0)
    observation = DetectedAcousticObservation(
        parent_beam_index=2,
        detection_method="phase_zero_crossing",
        twtt_seconds=0.08,
        detected_across_track_angle_rad=detected_angle,
        quality=1.0,
    )
    result = reconstruct_layered_sound_speed_sounding_from_sonar_state(
        observation,
        sensor_pose=_pose(),
        along_track_angle_rad=0.0,
        profile=_profile(),
        profile_start_depth_m=0.0,
        sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1480.0),
    )
    detected = sensor_angular_direction(0.0, detected_angle)
    resolution = result.initial_direction_resolution
    profile_direction = resolution.profile_initial_direction_sensor_frame
    assert resolution.profile_boundary.source == "sound_speed_at_transducer"
    assert profile_direction.y / 1500.0 == pytest.approx(detected.y / 1480.0)
    assert result.sounding.ray_path.ray_parameter_seconds_per_m == pytest.approx(
        abs(detected.y) / 1480.0
    )
    assert not hasattr(result, "true_local_sound_speed_mps")
    assert not hasattr(resolution, "true_local_sound_speed_mps")


def test_nonpropagating_profile_entry_state_is_rejected() -> None:
    detected = sensor_angular_direction(0.0, radians(80.0))
    high_speed_profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=100.0, sound_speed_mps=1700.0),
        )
    )
    with pytest.raises(ValueError, match="non-propagating"):
        resolve_layered_reconstruction_initial_direction(
            detected_direction_sensor_frame=detected,
            sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1400.0),
            profile=high_speed_profile,
            profile_start_depth_m=0.0,
        )

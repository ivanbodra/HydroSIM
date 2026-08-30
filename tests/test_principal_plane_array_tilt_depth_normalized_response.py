from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.principal_plane_array_tilt_depth_normalized_response import (
    run_principal_plane_array_tilt_depth_normalized_response,
)
from hydrosim.geometry import Attitude, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _constant_profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=600.0, sound_speed_mps=1500.0),)
    )


def _layered_profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=150.0, sound_speed_mps=1540.0),
            SoundSpeedLayer(top_depth_m=150.0, bottom_depth_m=600.0, sound_speed_mps=1510.0),
        )
    )


def test_constant_profile_normalized_response_is_depth_invariant() -> None:
    response = run_principal_plane_array_tilt_depth_normalized_response(
        sensor_pose=_pose(),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(20.0,),
        principal_plane_array_tilts_rad=(radians(8.0),),
        bottom_depths_m=(50.0, 100.0, 200.0, 400.0),
        true_profile=_constant_profile(),
        profile_start_depth_m=0.0,
    )

    assert len(response.points) == 4
    reference = response.points[0]
    for point in response.points[1:]:
        assert point.across_track_error_per_depth == pytest.approx(
            reference.across_track_error_per_depth, rel=1e-10, abs=1e-12
        )
        assert point.vertical_error_per_depth == pytest.approx(
            reference.vertical_error_per_depth, rel=1e-10, abs=1e-12
        )
        assert point.sounding_error_norm_per_depth == pytest.approx(
            reference.sounding_error_norm_per_depth, rel=1e-10, abs=1e-12
        )


def test_layered_profile_is_not_forced_to_have_depth_invariant_normalized_error() -> None:
    response = run_principal_plane_array_tilt_depth_normalized_response(
        sensor_pose=_pose(),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(20.0,),
        principal_plane_array_tilts_rad=(radians(8.0),),
        bottom_depths_m=(100.0, 300.0),
        true_profile=_layered_profile(),
        profile_start_depth_m=0.0,
    )

    shallow, deep = response.points
    assert shallow.sounding_error_norm_m > 0.0
    assert deep.sounding_error_norm_m > shallow.sounding_error_norm_m
    assert shallow.sounding_error_norm_per_depth != pytest.approx(
        deep.sounding_error_norm_per_depth, rel=1e-6, abs=1e-12
    )


def test_zero_bias_or_zero_tilt_closes_after_normalization() -> None:
    response = run_principal_plane_array_tilt_depth_normalized_response(
        sensor_pose=_pose(),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(0.0, 20.0),
        principal_plane_array_tilts_rad=(0.0, radians(8.0)),
        bottom_depths_m=(100.0, 200.0),
        true_profile=_constant_profile(),
        profile_start_depth_m=0.0,
    )

    for point in response.points:
        if (
            abs(float(point.transducer_sensor_bias_mps)) < 1e-15
            or abs(float(point.principal_plane_array_tilt_rad)) < 1e-15
        ):
            assert point.across_track_error_per_depth == pytest.approx(0.0, abs=1e-11)
            assert point.vertical_error_per_depth == pytest.approx(0.0, abs=1e-11)
            assert point.sounding_error_norm_per_depth == pytest.approx(0.0, abs=1e-11)


def test_order_is_angle_bias_tilt_depth() -> None:
    angles = (radians(10.0), radians(20.0))
    biases = (-5.0, 5.0)
    tilts = (radians(-2.0), radians(2.0))
    depths = (50.0, 100.0)
    response = run_principal_plane_array_tilt_depth_normalized_response(
        sensor_pose=_pose(),
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        principal_plane_array_tilts_rad=tilts,
        bottom_depths_m=depths,
        true_profile=_constant_profile(),
        profile_start_depth_m=0.0,
    )

    coordinates = [
        (
            float(point.configured_across_track_angle_rad),
            float(point.transducer_sensor_bias_mps),
            float(point.principal_plane_array_tilt_rad),
            float(point.bottom_depth_m),
        )
        for point in response.points
    ]
    assert coordinates == [
        (angle, bias, tilt, depth)
        for angle in angles
        for bias in biases
        for tilt in tilts
        for depth in depths
    ]


def test_rejects_empty_depth_axis_and_bottom_above_sensor() -> None:
    common = dict(
        sensor_pose=_pose(),
        configured_across_track_angles_rad=(radians(20.0),),
        transducer_sensor_biases_mps=(20.0,),
        principal_plane_array_tilts_rad=(radians(2.0),),
        true_profile=_constant_profile(),
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="bottom_depths_m must not be empty"):
        run_principal_plane_array_tilt_depth_normalized_response(bottom_depths_m=(), **common)
    with pytest.raises(ValueError, match="below the sensor"):
        run_principal_plane_array_tilt_depth_normalized_response(
            bottom_depths_m=(0.0,), **common
        )

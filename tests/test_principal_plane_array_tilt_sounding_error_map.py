from math import asin, cos, radians, sin

import pytest

from hydrosim.acquisition import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
)
from hydrosim.acquisition.principal_plane_array_tilt_sounding_error_map import (
    run_principal_plane_array_tilt_sounding_error_map,
)
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=140.0, sound_speed_mps=1550.0),
        )
    )


def test_map_matches_independent_closed_form_ray_parameter_mismatch() -> None:
    angles = (radians(20.0), radians(35.0))
    biases = (-10.0, 20.0)
    tilts = (radians(-8.0), 0.0, radians(8.0))
    study = run_principal_plane_array_tilt_sounding_error_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        principal_plane_array_tilts_rad=tilts,
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    assert len(study.points) == len(angles) * len(biases) * len(tilts)
    for point in study.points:
        theta = float(point.configured_across_track_angle_rad)
        bias = float(point.transducer_sensor_bias_mps)
        tau = float(point.principal_plane_array_tilt_rad)
        c_true = 1500.0
        c_used = c_true + bias
        theta_phys = asin((c_true / c_used) * sin(theta))
        expected_k = cos(theta) / c_used - cos(theta_phys) / c_true
        expected_delta = expected_k * sin(tau)

        assert point.analytical_tilt_sensitivity_seconds_per_m_per_rad == pytest.approx(
            expected_k, abs=1e-15
        )
        assert point.analytical_ray_parameter_mismatch_seconds_per_m == pytest.approx(
            expected_delta, abs=1e-15
        )
        assert point.numerical_ray_parameter_mismatch_seconds_per_m == pytest.approx(
            expected_delta, abs=1e-15
        )
        assert point.ray_parameter_mismatch_residual_seconds_per_m == pytest.approx(
            0.0, abs=1e-15
        )


def test_zero_tilt_or_zero_bias_preserves_controlled_sounding_closure() -> None:
    study = run_principal_plane_array_tilt_sounding_error_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(0.0, 20.0),
        principal_plane_array_tilts_rad=(0.0, radians(8.0)),
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    for point in study.points:
        if (
            abs(float(point.principal_plane_array_tilt_rad)) < 1e-15
            or abs(float(point.transducer_sensor_bias_mps)) < 1e-15
        ):
            assert point.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)
            assert point.across_track_error_m == pytest.approx(0.0, abs=1e-9)
            assert point.vertical_error_m == pytest.approx(0.0, abs=1e-9)


def test_nonzero_tilt_and_bias_produce_resolved_sounding_components() -> None:
    study = run_principal_plane_array_tilt_sounding_error_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(20.0,),
        principal_plane_array_tilts_rad=(radians(-8.0), radians(8.0)),
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    negative, positive = study.points
    assert negative.sounding_error_norm_m > 0.01
    assert positive.sounding_error_norm_m > 0.01
    assert abs(float(negative.across_track_error_m)) > 0.001
    assert abs(float(positive.across_track_error_m)) > 0.001
    assert negative.numerical_ray_parameter_mismatch_seconds_per_m == pytest.approx(
        -float(positive.numerical_ray_parameter_mismatch_seconds_per_m), abs=1e-15
    )
    # Final sounding-error component symmetry is intentionally not asserted.


def test_map_order_is_angle_then_bias_then_tilt() -> None:
    angles = (radians(10.0), radians(20.0))
    biases = (-5.0, 5.0)
    tilts = (radians(-2.0), radians(2.0))
    study = run_principal_plane_array_tilt_sounding_error_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=80.0),
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        principal_plane_array_tilts_rad=tilts,
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    coordinates = [
        (
            float(point.configured_across_track_angle_rad),
            float(point.transducer_sensor_bias_mps),
            float(point.principal_plane_array_tilt_rad),
        )
        for point in study.points
    ]
    assert coordinates == [
        (angle, bias, tilt)
        for angle in angles
        for bias in biases
        for tilt in tilts
    ]


def test_map_rejects_empty_axes() -> None:
    common = dict(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="angles.*must not be empty"):
        run_principal_plane_array_tilt_sounding_error_map(
            configured_across_track_angles_rad=(),
            transducer_sensor_biases_mps=(20.0,),
            principal_plane_array_tilts_rad=(0.0,),
            **common,
        )
    with pytest.raises(ValueError, match="biases.*must not be empty"):
        run_principal_plane_array_tilt_sounding_error_map(
            configured_across_track_angles_rad=(radians(30.0),),
            transducer_sensor_biases_mps=(),
            principal_plane_array_tilts_rad=(0.0,),
            **common,
        )
    with pytest.raises(ValueError, match="tilts.*must not be empty"):
        run_principal_plane_array_tilt_sounding_error_map(
            configured_across_track_angles_rad=(radians(30.0),),
            transducer_sensor_biases_mps=(20.0,),
            principal_plane_array_tilts_rad=(),
            **common,
        )

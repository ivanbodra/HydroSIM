from math import asin, cos, radians, sin

import pytest

from hydrosim.acquisition import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    run_principal_plane_array_tilt_sensitivity_study,
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


def test_tilt_sensitivity_matches_independent_closed_form_ray_parameter_curve() -> None:
    configured = radians(35.0)
    bias = 20.0
    c_true = 1500.0
    c_used = c_true + bias
    tilts = (radians(-8.0), 0.0, radians(8.0))

    study = run_principal_plane_array_tilt_sensitivity_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=configured,
        transducer_sensor_bias_mps=bias,
        principal_plane_array_tilts_rad=tilts,
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    physical_array_angle = asin((c_true / c_used) * sin(configured))
    coefficient = cos(configured) / c_used - cos(physical_array_angle) / c_true

    assert study.principal_plane_array_tilts_rad == pytest.approx(tilts)
    assert len(study.points) == 3
    for point, tilt in zip(study.points, tilts, strict=True):
        expected_truth = sin(tilt + physical_array_angle) / c_true
        expected_processing = sin(tilt + configured) / c_used
        expected_mismatch = coefficient * sin(tilt)

        assert point.truth_ray_parameter_seconds_per_m == pytest.approx(expected_truth)
        assert point.processing_ray_parameter_seconds_per_m == pytest.approx(expected_processing)
        assert point.ray_parameter_mismatch_seconds_per_m == pytest.approx(expected_mismatch)

    negative, aligned, positive = study.points
    assert aligned.ray_parameter_mismatch_seconds_per_m == pytest.approx(0.0, abs=1e-15)
    assert aligned.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)
    assert negative.ray_parameter_mismatch_seconds_per_m == pytest.approx(
        -positive.ray_parameter_mismatch_seconds_per_m,
        abs=1e-15,
    )
    assert negative.sounding_error_norm_m > 0.01
    assert positive.sounding_error_norm_m > 0.01


def test_tilt_sensitivity_small_angle_slope_matches_independent_derivative() -> None:
    configured = radians(35.0)
    bias = 20.0
    c_true = 1500.0
    c_used = c_true + bias
    epsilon = 1.0e-5

    study = run_principal_plane_array_tilt_sensitivity_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=configured,
        transducer_sensor_bias_mps=bias,
        principal_plane_array_tilts_rad=(-epsilon, epsilon),
        true_profile=_profile(),
        profile_start_depth_m=0.0,
    )

    physical_array_angle = asin((c_true / c_used) * sin(configured))
    expected_slope = cos(configured) / c_used - cos(physical_array_angle) / c_true
    negative, positive = study.points
    centered_slope = (
        positive.ray_parameter_mismatch_seconds_per_m
        - negative.ray_parameter_mismatch_seconds_per_m
    ) / (2.0 * epsilon)

    assert centered_slope == pytest.approx(expected_slope, rel=1e-9, abs=1e-15)


def test_tilt_sensitivity_rejects_empty_tilt_axis() -> None:
    with pytest.raises(ValueError, match="tilts.*must not be empty"):
        run_principal_plane_array_tilt_sensitivity_study(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angle_rad=radians(35.0),
            transducer_sensor_bias_mps=20.0,
            principal_plane_array_tilts_rad=(),
            true_profile=_profile(),
            profile_start_depth_m=0.0,
        )

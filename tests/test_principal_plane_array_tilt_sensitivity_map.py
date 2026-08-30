from math import asin, cos, radians, sin

import pytest

from hydrosim.acquisition.principal_plane_array_tilt_sensitivity_map import (
    principal_plane_array_tilt_sensitivity_coefficient,
    run_principal_plane_array_tilt_sensitivity_map,
)


def _independent_coefficient(theta_rad: float, bias_mps: float, c_true: float) -> float:
    c_used = c_true + bias_mps
    theta_phys = asin((c_true / c_used) * sin(theta_rad))
    return cos(theta_rad) / c_used - cos(theta_phys) / c_true


def test_sensitivity_coefficient_matches_independent_closed_form() -> None:
    theta = radians(42.0)
    bias = 18.0
    c_true = 1492.0
    point = principal_plane_array_tilt_sensitivity_coefficient(
        configured_across_track_angle_rad=theta,
        transducer_sensor_bias_mps=bias,
        true_local_sound_speed_mps=c_true,
    )

    expected_theta_phys = asin((c_true / (c_true + bias)) * sin(theta))
    expected = _independent_coefficient(theta, bias, c_true)
    assert point.physical_array_angle_rad == pytest.approx(expected_theta_phys)
    assert point.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad == pytest.approx(expected)


def test_zero_bias_has_zero_tilt_sensitivity_for_all_tested_beam_angles() -> None:
    study = run_principal_plane_array_tilt_sensitivity_map(
        configured_across_track_angles_rad=(radians(-60.0), radians(-20.0), 0.0, radians(35.0)),
        transducer_sensor_biases_mps=(0.0,),
        true_local_sound_speed_mps=1500.0,
    )
    assert all(
        point.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad == pytest.approx(0.0, abs=1e-15)
        for point in study.points
    )


def test_sensitivity_is_even_in_beam_angle_for_fixed_bias() -> None:
    positive = principal_plane_array_tilt_sensitivity_coefficient(
        configured_across_track_angle_rad=radians(50.0),
        transducer_sensor_bias_mps=20.0,
        true_local_sound_speed_mps=1500.0,
    )
    negative = principal_plane_array_tilt_sensitivity_coefficient(
        configured_across_track_angle_rad=radians(-50.0),
        transducer_sensor_bias_mps=20.0,
        true_local_sound_speed_mps=1500.0,
    )
    assert negative.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad == pytest.approx(
        positive.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad,
        abs=1e-15,
    )


def test_bias_sign_reverses_sensitivity_sign_in_controlled_case() -> None:
    positive_bias = principal_plane_array_tilt_sensitivity_coefficient(
        configured_across_track_angle_rad=radians(40.0),
        transducer_sensor_bias_mps=20.0,
        true_local_sound_speed_mps=1500.0,
    )
    negative_bias = principal_plane_array_tilt_sensitivity_coefficient(
        configured_across_track_angle_rad=radians(40.0),
        transducer_sensor_bias_mps=-20.0,
        true_local_sound_speed_mps=1500.0,
    )
    assert positive_bias.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad < 0.0
    assert negative_bias.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad > 0.0


def test_map_order_is_angle_outer_bias_inner_and_outer_beams_are_more_sensitive_here() -> None:
    angles = (0.0, radians(30.0), radians(60.0))
    biases = (-20.0, 20.0)
    study = run_principal_plane_array_tilt_sensitivity_map(
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        true_local_sound_speed_mps=1500.0,
    )
    assert len(study.points) == 6
    assert [point.configured_across_track_angle_rad for point in study.points] == pytest.approx(
        (angles[0], angles[0], angles[1], angles[1], angles[2], angles[2])
    )
    assert [point.transducer_sensor_bias_mps for point in study.points] == pytest.approx(
        (biases[0], biases[1], biases[0], biases[1], biases[0], biases[1])
    )

    positive_bias_points = [point for point in study.points if point.transducer_sensor_bias_mps > 0.0]
    magnitudes = [
        abs(point.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad)
        for point in positive_bias_points
    ]
    assert magnitudes[0] < magnitudes[1] < magnitudes[2]


def test_map_rejects_empty_axes_and_non_propagating_states() -> None:
    with pytest.raises(ValueError, match="angles.*must not be empty"):
        run_principal_plane_array_tilt_sensitivity_map(
            configured_across_track_angles_rad=(),
            transducer_sensor_biases_mps=(20.0,),
            true_local_sound_speed_mps=1500.0,
        )
    with pytest.raises(ValueError, match="biases.*must not be empty"):
        run_principal_plane_array_tilt_sensitivity_map(
            configured_across_track_angles_rad=(radians(30.0),),
            transducer_sensor_biases_mps=(),
            true_local_sound_speed_mps=1500.0,
        )
    with pytest.raises(ValueError, match="non-propagating"):
        principal_plane_array_tilt_sensitivity_coefficient(
            configured_across_track_angle_rad=radians(80.0),
            transducer_sensor_bias_mps=-100.0,
            true_local_sound_speed_mps=1500.0,
        )

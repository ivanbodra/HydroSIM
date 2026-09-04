import math

import pytest

from hydrosim.app.uncertainty_scalar_api import (
    D18ScalarUncertaintyRequest,
    prepare_d18_scalar_uncertainty_response,
)


def _response(**updates):
    return prepare_d18_scalar_uncertainty_response(D18ScalarUncertaintyRequest(**updates))


def test_d18_scalar_zero_input_closure():
    response = _response()

    assert response.standard_uncertainty_m == pytest.approx((0.0, 0.0, 0.0))
    assert response.thu_m == pytest.approx(0.0)
    assert response.tvu_m == pytest.approx(0.0)
    assert response.combined_3d_standard_uncertainty_m == pytest.approx(0.0)


def test_d18_scalar_nadir_range_and_sound_speed_are_vertical_only():
    response = _response(
        slant_range_m=30.0,
        sound_speed_mps=1500.0,
        across_track_angle_rad=0.0,
        u_range_m=0.4,
        u_sound_speed_mps=2.0,
    )

    expected_sound_speed = (response.twtt_seconds / 2.0) * 2.0
    expected_down = math.hypot(0.4, expected_sound_speed)
    assert response.standard_uncertainty_m[0] == pytest.approx(0.0)
    assert response.standard_uncertainty_m[1] == pytest.approx(0.0)
    assert response.standard_uncertainty_m[2] == pytest.approx(expected_down)


def test_d18_scalar_nadir_roll_across_sensitivity_is_range():
    response = _response(
        slant_range_m=42.0,
        across_track_angle_rad=0.0,
        u_attitude_roll_rad=0.01,
    )

    assert response.standard_uncertainty_m == pytest.approx((0.0, 0.42, 0.0))


def test_d18_scalar_timing_maps_to_along_with_absolute_speed_magnitude():
    positive = _response(vessel_speed_mps=4.0, u_timing_s=0.025)
    negative = _response(vessel_speed_mps=-4.0, u_timing_s=0.025)

    assert positive.standard_uncertainty_m[0] == pytest.approx(0.1)
    assert negative.standard_uncertainty_m[0] == pytest.approx(0.1)


def test_d18_scalar_port_starboard_variance_symmetry_for_isolated_range():
    port = _response(across_track_angle_rad=0.5, u_range_m=0.3)
    starboard = _response(across_track_angle_rad=-0.5, u_range_m=0.3)

    assert port.standard_uncertainty_m == pytest.approx(starboard.standard_uncertainty_m)
    assert port.covariance_m2[1][1] == pytest.approx(starboard.covariance_m2[1][1])
    assert port.covariance_m2[2][2] == pytest.approx(starboard.covariance_m2[2][2])


def test_d18_scalar_offset_is_one_for_one_across_at_nadir():
    response = _response(across_track_angle_rad=0.0, u_offset_across_m=0.25)

    assert response.standard_uncertainty_m == pytest.approx((0.0, 0.25, 0.0))


def test_d18_scalar_doubling_isolated_input_doubles_standard_and_quadruples_variance():
    first = _response(u_water_level_m=0.2)
    second = _response(u_water_level_m=0.4)

    assert second.tvu_m == pytest.approx(2.0 * first.tvu_m)
    assert second.covariance_m2[2][2] == pytest.approx(4.0 * first.covariance_m2[2][2])

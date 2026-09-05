from math import cos, isclose, radians, sin, sqrt

from hydrosim.acquisition import array_factor
from hydrosim.geometry import TransducerArray, Vector3


def _direction(angle_deg: float) -> Vector3:
    angle = radians(angle_deg)
    return Vector3(x=0.0, y=-sin(angle), z=cos(angle))


def _two_element_array(*, spacing_m: float) -> TransducerArray:
    return TransducerArray(
        name="rx_two",
        role="rx",
        n_x=1,
        n_y=2,
        d_x=0.0,
        d_y=spacing_m,
        element_longitudinal_size=0.001,
        element_transverse_size=0.001,
    )


def test_matched_source_and_steering_give_unity_response():
    result = array_factor(
        array=_two_element_array(spacing_m=0.005),
        source_direction_array_frame=_direction(37.0),
        steering_direction_array_frame=_direction(37.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.wavelength_m, 0.01, abs_tol=1e-15)
    assert isclose(result.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(result.normalized_power, 1.0, abs_tol=1e-12)


def test_two_elements_half_wavelength_match_closed_form_at_thirty_degrees():
    result = array_factor(
        array=_two_element_array(spacing_m=0.005),
        source_direction_array_frame=_direction(30.0),
        steering_direction_array_frame=_direction(0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.normalized_magnitude, sqrt(2.0) / 2.0, rel_tol=1e-12)
    assert isclose(result.normalized_power, 0.5, rel_tol=1e-12)


def test_opposite_thirty_degree_directions_cancel_for_half_wavelength_pair():
    result = array_factor(
        array=_two_element_array(spacing_m=0.005),
        source_direction_array_frame=_direction(30.0),
        steering_direction_array_frame=_direction(-30.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.normalized_magnitude, 0.0, abs_tol=1e-12)
    assert isclose(result.normalized_power, 0.0, abs_tol=1e-12)


def test_one_wavelength_spacing_creates_visible_grating_lobe_at_endfire():
    result = array_factor(
        array=_two_element_array(spacing_m=0.01),
        source_direction_array_frame=_direction(90.0),
        steering_direction_array_frame=_direction(0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(result.normalized_power, 1.0, abs_tol=1e-12)


def test_complex_weights_are_normalized_by_sum_of_weight_magnitudes():
    result = array_factor(
        array=_two_element_array(spacing_m=0.005),
        source_direction_array_frame=_direction(0.0),
        steering_direction_array_frame=_direction(0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        weights=(2.0 + 0.0j, 1.0 + 0.0j),
    )

    assert isclose(result.normalization, 3.0, abs_tol=1e-15)
    assert isclose(result.normalized_magnitude, 1.0, abs_tol=1e-12)


def test_array_factor_can_skip_detail_objects_without_changing_response():
    kwargs = dict(
        array=_two_element_array(spacing_m=0.005),
        source_direction_array_frame=_direction(25.0),
        steering_direction_array_frame=_direction(0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    detailed = array_factor(**kwargs)
    compact = array_factor(**kwargs, include_element_contributions=False)

    assert len(detailed.element_contributions) == 2
    assert compact.element_contributions == ()
    assert compact.coherent_real == detailed.coherent_real
    assert compact.coherent_imag == detailed.coherent_imag
    assert compact.normalized_power == detailed.normalized_power

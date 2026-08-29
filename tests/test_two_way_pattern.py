from math import isclose, sqrt

from hydrosim.acquisition.beam_pattern import across_track_direction
from hydrosim.acquisition.two_way_pattern import two_way_beam_pattern
from hydrosim.geometry import TransducerArray, Vector3


def _linear_array(*, name: str, count: int, spacing: float, element_size: float = 1e-6) -> TransducerArray:
    return TransducerArray(
        name=name,
        n_x=1,
        n_y=count,
        d_x=0.0,
        d_y=spacing,
        element_longitudinal_size=element_size,
        element_transverse_size=element_size,
    )


def test_matched_tx_and_rx_have_unity_two_way_response():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=4, spacing=wavelength / 2.0)
    rx = _linear_array(name="rx", count=8, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=broadside,
        receive_direction_array_frame=broadside,
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(response.normalized_amplitude, 1.0, abs_tol=1e-12)
    assert isclose(response.normalized_power, 1.0, abs_tol=1e-12)


def test_two_way_amplitude_is_product_of_independent_one_way_amplitudes():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=1, spacing=0.0)
    rx = _linear_array(name="rx", count=2, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)
    source = across_track_direction(3.141592653589793 / 6.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=source,
        receive_direction_array_frame=source,
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    expected_rx = sqrt(2.0) / 2.0
    assert isclose(response.transmit_response.normalized_amplitude, 1.0, rel_tol=1e-8)
    assert isclose(response.receive_response.normalized_amplitude, expected_rx, rel_tol=1e-8)
    assert isclose(response.normalized_amplitude, expected_rx, rel_tol=1e-8)
    assert isclose(
        response.normalized_power,
        response.normalized_amplitude * response.normalized_amplitude,
        abs_tol=1e-15,
    )


def test_tx_and_rx_directions_are_independent_local_frame_representations():
    # This is the architectural anchor for Mills Cross: the same physical direction
    # need not have the same coordinates in two differently oriented aperture frames.
    wavelength = 0.01
    tx = _linear_array(name="tx", count=2, spacing=wavelength / 2.0)
    rx = _linear_array(name="rx", count=2, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=Vector3(x=0.0, y=-0.5, z=sqrt(3.0) / 2.0),
        receive_direction_array_frame=Vector3(x=0.0, y=0.0, z=1.0),
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert response.transmit_response.normalized_amplitude < 1.0
    assert isclose(response.receive_response.normalized_amplitude, 1.0, abs_tol=1e-12)
    assert response.normalized_amplitude < 1.0

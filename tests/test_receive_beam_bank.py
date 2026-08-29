from math import isclose

import pytest

from hydrosim.acquisition import evaluate_mills_cross_receive_beam_bank
from hydrosim.geometry import make_reference_mills_cross


def _configuration():
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=8,
        receive_count=16,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="receive_beam_bank_test",
    )


def test_matched_receive_beam_is_strongest_for_source_direction():
    steering = (-0.30, -0.15, 0.0, 0.15, 0.30)
    response = evaluate_mills_cross_receive_beam_bank(
        configuration=_configuration(),
        source_along_track_angle_rad=0.0,
        source_across_track_angle_rad=0.15,
        receive_steering_across_track_angles_rad=steering,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert response.strongest_beam_index == 3
    assert isclose(response.beams[3].receive_amplitude, 1.0, abs_tol=1e-12)
    assert isclose(response.beams[3].normalized_power, 1.0, rel_tol=1e-8)
    assert response.beams[2].normalized_power < response.beams[3].normalized_power
    assert response.beams[4].normalized_power < response.beams[3].normalized_power


def test_tx_response_is_common_while_rx_steering_changes():
    response = evaluate_mills_cross_receive_beam_bank(
        configuration=_configuration(),
        source_along_track_angle_rad=0.10,
        source_across_track_angle_rad=0.0,
        receive_steering_across_track_angles_rad=(-0.2, 0.0, 0.2),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    tx_amplitudes = [beam.transmit_amplitude for beam in response.beams]
    assert all(isclose(value, tx_amplitudes[0], abs_tol=1e-12) for value in tx_amplitudes)
    assert response.strongest_beam_index == 1


def test_receive_beam_bank_requires_at_least_one_beam():
    with pytest.raises(ValueError, match="must not be empty"):
        evaluate_mills_cross_receive_beam_bank(
            configuration=_configuration(),
            source_along_track_angle_rad=0.0,
            source_across_track_angle_rad=0.0,
            receive_steering_across_track_angles_rad=(),
            frequency_hz=150_000.0,
            sound_speed_mps=1500.0,
        )

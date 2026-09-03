import pytest

from hydrosim.app.beamforming_api import D7BeamformingRequest, prepare_d7_beamforming_response


def test_d7_coherent_source_at_steer_angle_aligns_residual_phases() -> None:
    response = prepare_d7_beamforming_response(
        D7BeamformingRequest(steering_angle_deg=25.0, source_angle_deg=25.0)
    )

    assert response.evaluated_array_factor_magnitude == pytest.approx(1.0, abs=1e-12)
    assert response.evaluated_array_factor_power == pytest.approx(1.0, abs=1e-12)
    assert all(abs(element.residual_phase_rad) < 1e-12 for element in response.elements)


def test_d7_preserves_port_positive_steering_direction() -> None:
    positive = prepare_d7_beamforming_response(
        D7BeamformingRequest(steering_angle_deg=30.0, source_angle_deg=30.0)
    )
    negative = prepare_d7_beamforming_response(
        D7BeamformingRequest(steering_angle_deg=-30.0, source_angle_deg=-30.0)
    )

    assert positive.steering_direction_array_frame.y < 0.0
    assert negative.steering_direction_array_frame.y > 0.0
    assert positive.metadata["positive_angle_direction"] == "Port (-Y)"


def test_d7_broadside_reproduces_normalized_d6_pattern_boundary() -> None:
    response = prepare_d7_beamforming_response(
        D7BeamformingRequest(steering_angle_deg=0.0, source_angle_deg=0.0)
    )

    assert response.peak_angle_deg == pytest.approx(0.0, abs=1e-12)
    assert response.peak_normalized_power == pytest.approx(1.0)
    assert max(response.array_factor_pattern.normalized_power) == pytest.approx(1.0)
    assert max(response.physical_beam_pattern.normalized_power) == pytest.approx(1.0)


def test_d7_two_element_half_wavelength_documented_anchor() -> None:
    response = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            element_count=2,
            element_spacing_m=0.00375,
            element_face_m=0.001,
            steering_angle_deg=0.0,
            source_angle_deg=30.0,
        )
    )

    assert response.wavelength_m == pytest.approx(0.0075)
    assert response.evaluated_array_factor_magnitude == pytest.approx(2**-0.5, rel=1e-10)
    assert response.evaluated_array_factor_power == pytest.approx(0.5, rel=1e-10)


def test_d7_tx_rx_roles_share_same_first_slice_numeric_response() -> None:
    configured = dict(steering_angle_deg=20.0, source_angle_deg=10.0)
    tx = prepare_d7_beamforming_response(D7BeamformingRequest(role="tx", **configured))
    rx = prepare_d7_beamforming_response(D7BeamformingRequest(role="rx", **configured))

    assert tx.role == "tx"
    assert rx.role == "rx"
    assert tx.array_factor_pattern.normalized_power == pytest.approx(
        rx.array_factor_pattern.normalized_power
    )
    assert tx.physical_beam_pattern.normalized_power == pytest.approx(
        rx.physical_beam_pattern.normalized_power
    )


def test_d7_requires_steering_inside_requested_scan() -> None:
    with pytest.raises(ValueError, match="steering_angle_deg"):
        D7BeamformingRequest(steering_angle_deg=70.0, scan_max_deg=60.0)

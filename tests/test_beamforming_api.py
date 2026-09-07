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


def test_d7_relative_timing_uses_explicit_channel_zero_reference() -> None:
    response = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            role="rx",
            element_count=6,
            element_spacing_m=0.00375,
            steering_angle_deg=25.0,
            source_angle_deg=10.0,
        )
    )

    assert response.reference_channel_index == 0
    reference = response.elements[0]
    assert reference.relative_arrival_offset_us == pytest.approx(0.0, abs=1e-12)
    assert reference.relative_compensation_delay_us == pytest.approx(0.0, abs=1e-12)
    assert reference.residual_relative_timing_us == pytest.approx(0.0, abs=1e-12)
    assert reference.residual_relative_phase_rad == pytest.approx(0.0, abs=1e-12)


def test_d7_source_equal_steering_closes_relative_timing_residual() -> None:
    response = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            role="rx",
            element_count=6,
            steering_angle_deg=30.0,
            source_angle_deg=30.0,
        )
    )

    assert all(abs(element.residual_relative_timing_us) < 1e-12 for element in response.elements)
    assert all(abs(element.residual_relative_phase_rad) < 1e-12 for element in response.elements)


def test_d7_delay_gradient_inverse_matches_angle_control() -> None:
    angle_response = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            role="rx",
            element_count=6,
            steering_angle_deg=20.0,
            source_angle_deg=20.0,
        )
    )
    delay_response = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            role="rx",
            element_count=6,
            steering_control_mode="delay_gradient",
            delay_gradient_us_per_element=angle_response.steering_delay_gradient_us_per_element,
            source_angle_deg=20.0,
        )
    )

    assert delay_response.steering_angle_deg == pytest.approx(20.0, abs=1e-10)
    assert delay_response.evaluated_array_factor_power == pytest.approx(1.0, abs=1e-12)


def test_d7_delay_gradient_rejects_nonphysical_mapping() -> None:
    with pytest.raises(ValueError, match="physical steering angle"):
        prepare_d7_beamforming_response(
            D7BeamformingRequest(
                steering_control_mode="delay_gradient",
                delay_gradient_us_per_element=100.0,
            )
        )


def test_d7_reports_unambiguous_and_aliased_regimes() -> None:
    unambiguous = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            element_spacing_m=0.00375,
            steering_angle_deg=20.0,
        )
    )
    aliased = prepare_d7_beamforming_response(
        D7BeamformingRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            element_spacing_m=0.012,
            steering_angle_deg=20.0,
        )
    )

    assert unambiguous.steering_regime == "unambiguous"
    assert unambiguous.grating_lobe_angles_deg == ()
    assert aliased.steering_regime == "aliased"
    assert aliased.grating_lobe_angles_deg

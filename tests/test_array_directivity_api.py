import pytest

from hydrosim.app.array_directivity_api import D6ArrayRequest, prepare_d6_array_response


def test_d6_broadside_pattern_exposes_canonical_geometry_and_peak():
    response = prepare_d6_array_response(
        D6ArrayRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            element_count=8,
            spacing_mm=3.75,
            element_size_mm=3.0,
            sample_count=721,
        )
    )

    assert response.wavelength_m == pytest.approx(0.0075)
    assert response.aperture_m == pytest.approx(0.02925)
    assert len(response.element_positions_m) == 8
    assert response.element_positions_m[0] == pytest.approx(-response.element_positions_m[-1])
    assert response.peak_angle_deg == pytest.approx(0.0, abs=1e-12)
    assert response.peak_normalized_power == pytest.approx(1.0)
    assert response.half_power_beamwidth_deg is not None
    assert response.metadata["state_semantics"] == "Configured inputs; Derived outputs"


def test_d6_returns_separate_element_array_and_combined_patterns():
    response = prepare_d6_array_response(D6ArrayRequest(sample_count=181))

    assert response.element_factor.angle_deg == response.array_factor.angle_deg
    assert response.array_factor.angle_deg == response.combined_pattern.angle_deg
    assert max(response.element_factor.normalized_amplitude) == pytest.approx(1.0)
    assert max(response.array_factor.normalized_amplitude) == pytest.approx(1.0)
    assert max(response.combined_pattern.normalized_power) == pytest.approx(1.0)


def test_d6_lambda_spacing_exposes_endfire_grating_lobe_anchor():
    response = prepare_d6_array_response(
        D6ArrayRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            element_count=8,
            spacing_mm=7.5,
            element_size_mm=1.0,
            sample_count=721,
        )
    )

    assert response.array_factor.normalized_power[0] == pytest.approx(1.0, abs=1e-10)
    assert response.array_factor.normalized_power[-1] == pytest.approx(1.0, abs=1e-10)


def test_d6_does_not_extrapolate_half_power_crossings():
    response = prepare_d6_array_response(
        D6ArrayRequest(scan_start_deg=-1.0, scan_end_deg=1.0, sample_count=101)
    )

    assert response.half_power_beamwidth_deg is None
    assert response.half_power_left_deg is None
    assert response.half_power_right_deg is None


def test_d6_rejects_zero_spacing_for_multiple_elements():
    with pytest.raises(ValueError, match="spacing_mm"):
        prepare_d6_array_response(D6ArrayRequest(element_count=2, spacing_mm=0.0))

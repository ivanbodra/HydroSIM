import pytest

from hydrosim.app.array_api import D6ArrayRequest, prepare_d6_array_response
from hydrosim.geometry import TransducerArray


def test_d6_broadside_response_uses_core_wavelength_geometry_and_pattern() -> None:
    request = D6ArrayRequest(
        frequency_khz=200.0,
        sound_speed_mps=1500.0,
        element_count=8,
        element_spacing_m=0.00375,
        element_face_m=0.003,
        sample_count=321,
    )
    response = prepare_d6_array_response(request)
    expected_array = TransducerArray(
        name="test",
        role="txrx",
        n_x=1,
        n_y=8,
        d_x=0.0,
        d_y=0.00375,
        element_longitudinal_size=0.003,
        element_transverse_size=0.003,
    )

    assert response.wavelength_m == pytest.approx(0.0075)
    assert response.physical_aperture_m == pytest.approx(expected_array.aperture_transverse)
    assert response.element_positions_m == pytest.approx(
        tuple(float(item.position.y) for item in expected_array.elements())
    )
    assert response.peak_angle_deg == pytest.approx(0.0, abs=1e-12)
    assert response.peak_normalized_power == pytest.approx(1.0)
    assert response.half_power_beamwidth_deg is not None
    assert response.metadata["state_semantics"] == "Configured inputs; Derived outputs"


def test_d6_preserves_separate_element_array_and_combined_patterns() -> None:
    response = prepare_d6_array_response(
        D6ArrayRequest(element_count=4, element_spacing_m=0.004, element_face_m=0.006)
    )

    assert response.element_factor.angle_deg == response.array_factor.angle_deg
    assert response.array_factor.angle_deg == response.combined_pattern.angle_deg
    assert len(response.combined_pattern.angle_deg) == 321
    assert max(response.element_factor.normalized_power) == pytest.approx(1.0)
    assert max(response.array_factor.normalized_power) == pytest.approx(1.0)
    assert max(response.combined_pattern.normalized_power) == pytest.approx(1.0)


def test_d6_more_elements_at_fixed_spacing_increase_aperture_and_narrow_beam() -> None:
    small = prepare_d6_array_response(
        D6ArrayRequest(element_count=4, element_spacing_m=0.00375, element_face_m=0.003)
    )
    large = prepare_d6_array_response(
        D6ArrayRequest(element_count=16, element_spacing_m=0.00375, element_face_m=0.003)
    )

    assert large.physical_aperture_m > small.physical_aperture_m
    assert small.half_power_beamwidth_deg is not None
    assert large.half_power_beamwidth_deg is not None
    assert large.half_power_beamwidth_deg < small.half_power_beamwidth_deg


def test_d6_rejects_zero_spacing_for_multi_element_array() -> None:
    with pytest.raises(ValueError, match="element_spacing_m"):
        D6ArrayRequest(element_count=2, element_spacing_m=0.0)

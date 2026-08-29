import math

import pytest

from hydrosim.acquisition import (
    AngularScatteringStrengthSample,
    AngularScatteringStrengthTable,
    ContinuousWavePulse,
    LinearFMPulse,
    angular_matched_filter_scattering_bottom_response,
    angular_scattering_bottom_response,
    integrate_angular_matched_filter_seafloor_backscatter,
    integrate_angular_seafloor_backscatter,
    project_angular_pattern_to_flat_seafloor,
    scan_mills_cross_two_way_pattern_2d,
    scattering_strength_at_incidence,
    weight_projected_pattern_by_matched_filter,
)
from hydrosim.geometry import make_reference_mills_cross


def _illumination(samples: int = 61):
    wavelength = 0.01
    configuration = make_reference_mills_cross(
        transmit_count=12,
        receive_count=12,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="angular_scattering_test",
    )
    scan = scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.20,
        along_track_end_angle_rad=0.20,
        along_track_sample_count=samples,
        across_track_start_angle_rad=-0.20,
        across_track_end_angle_rad=0.20,
        across_track_sample_count=samples,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    return project_angular_pattern_to_flat_seafloor(
        scan=scan,
        vertical_separation_m=50.0,
    )


def _table(s0: float, s1: float):
    return AngularScatteringStrengthTable(
        samples=(
            AngularScatteringStrengthSample(
                incidence_angle_from_normal_rad=0.0,
                scattering_strength_db_per_m2=s0,
            ),
            AngularScatteringStrengthSample(
                incidence_angle_from_normal_rad=0.5,
                scattering_strength_db_per_m2=s1,
            ),
        )
    )


def test_projected_cells_retain_local_flat_bottom_incidence() -> None:
    illumination = _illumination()
    center = min(
        illumination.cells,
        key=lambda cell: abs(float(cell.along_track_angle_rad))
        + abs(float(cell.across_track_angle_rad)),
    )
    edge = max(illumination.cells, key=lambda cell: float(cell.slant_range_m))

    assert center.incidence_angle_from_normal_rad == pytest.approx(0.0, abs=1e-12)
    expected_edge = math.acos(
        float(illumination.vertical_separation_m) / float(edge.slant_range_m)
    )
    assert edge.incidence_angle_from_normal_rad == pytest.approx(expected_edge)
    assert edge.incidence_angle_from_normal_rad > center.incidence_angle_from_normal_rad


def test_explicit_angular_scattering_table_interpolates_in_db() -> None:
    table = _table(-20.0, -40.0)
    assert scattering_strength_at_incidence(table, 0.25) == pytest.approx(-30.0)

    with pytest.raises(ValueError):
        scattering_strength_at_incidence(table, 0.6)


def test_uniform_angular_table_matches_uniform_equivalent_area_formula() -> None:
    illumination = _illumination()
    integration = integrate_angular_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-30.0, -30.0),
    )

    expected = -30.0 + 10.0 * math.log10(
        float(illumination.equivalent_insonified_area_m2)
    )
    assert integration.integrated_backscatter_strength_db == pytest.approx(expected)
    assert integration.minimum_incidence_angle_rad == pytest.approx(0.0, abs=1e-12)
    assert integration.maximum_incidence_angle_rad > 0.0


def test_angle_dependent_strength_changes_integrated_bottom_response() -> None:
    illumination = _illumination()
    uniform = integrate_angular_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-20.0, -20.0),
    )
    weakening = integrate_angular_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-20.0, -50.0),
    )

    assert weakening.integrated_backscatter_strength_db < uniform.integrated_backscatter_strength_db
    response = angular_scattering_bottom_response(weakening)
    assert response.interaction_kind == "seafloor_angular_area"
    assert response.effective_backscatter_strength_db == pytest.approx(
        weakening.integrated_backscatter_strength_db
    )
    assert response.amplitude_ratio == pytest.approx(weakening.amplitude_ratio)


def test_constant_angular_table_matches_matched_filter_equivalent_area_formula() -> None:
    illumination = _illumination(samples=71)
    pulse = LinearFMPulse(
        center_frequency_hz=150_000.0,
        bandwidth_hz=80_000.0,
        duration_seconds=0.001,
    )
    weighted = weight_projected_pattern_by_matched_filter(
        illumination=illumination,
        pulse=pulse,
        center_one_way_range_m=50.0,
        sample_rate_hz=400_000.0,
        sound_speed_mps=1500.0,
    )
    combined = integrate_angular_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-30.0, -30.0),
        pulse=pulse,
        center_one_way_range_m=50.0,
        sample_rate_hz=400_000.0,
        sound_speed_mps=1500.0,
    )

    expected = -30.0 + 10.0 * math.log10(
        float(weighted.equivalent_insonified_area_m2)
    )
    assert combined.integrated_backscatter_strength_db == pytest.approx(expected)
    assert combined.contributing_cell_count == weighted.contributing_cell_count


def test_combined_integration_retains_angular_and_waveform_effects() -> None:
    illumination = _illumination(samples=71)
    pulse = ContinuousWavePulse(
        center_frequency_hz=150_000.0,
        duration_seconds=0.001,
    )
    uniform = integrate_angular_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-20.0, -20.0),
        pulse=pulse,
        center_one_way_range_m=50.0,
        sample_rate_hz=400_000.0,
        sound_speed_mps=1500.0,
    )
    weakening = integrate_angular_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(-20.0, -50.0),
        pulse=pulse,
        center_one_way_range_m=50.0,
        sample_rate_hz=400_000.0,
        sound_speed_mps=1500.0,
    )

    assert weakening.integrated_backscatter_strength_db < uniform.integrated_backscatter_strength_db
    assert weakening.minimum_incidence_angle_rad == pytest.approx(0.0, abs=1e-12)
    assert weakening.maximum_incidence_angle_rad > 0.0

    response = angular_matched_filter_scattering_bottom_response(weakening)
    assert response.interaction_kind == "seafloor_angular_area_matched_filter"
    assert response.effective_backscatter_strength_db == pytest.approx(
        weakening.integrated_backscatter_strength_db
    )
    assert response.amplitude_ratio == pytest.approx(weakening.amplitude_ratio)

import pytest

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LayeredSoundSpeedProfile,
    LinearFMPulse,
    SoundSpeedLayer,
    project_angular_pattern_through_layered_profile,
    scan_mills_cross_two_way_pattern_2d,
    weight_refracted_footprint_by_matched_filter,
)
from hydrosim.geometry import make_reference_mills_cross


def _illumination(samples: int = 41):
    wavelength = 0.01
    configuration = make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="footprint_contribution_test",
    )
    scan = scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.15,
        along_track_end_angle_rad=0.15,
        along_track_sample_count=samples,
        across_track_start_angle_rad=-0.15,
        across_track_end_angle_rad=0.15,
        across_track_sample_count=samples,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=25.0, sound_speed_mps=1480.0),
            SoundSpeedLayer(top_depth_m=25.0, bottom_depth_m=50.0, sound_speed_mps=1530.0),
        )
    )
    return project_angular_pattern_through_layered_profile(
        scan=scan,
        profile=profile,
        target_depth_m=50.0,
    )


def _reference_time(illumination) -> float:
    center = min(
        illumination.cells,
        key=lambda cell: abs(float(cell.along_track_angle_rad))
        + abs(float(cell.across_track_angle_rad)),
    )
    return float(center.one_way_travel_time_seconds)


def test_refracted_footprint_contribution_contains_no_bottom_response_terms() -> None:
    illumination = _illumination()
    result = weight_refracted_footprint_by_matched_filter(
        illumination=illumination,
        pulse=LinearFMPulse(
            center_frequency_hz=150_000.0,
            bandwidth_hz=80_000.0,
            duration_seconds=0.001,
        ),
        reference_one_way_travel_time_seconds=_reference_time(illumination),
        sample_rate_hz=400_000.0,
    )

    assert result.contributing_cell_count > 0
    assert result.equivalent_contributing_area_m2 > 0.0
    assert all(0.0 <= float(cell.spatial_pattern_power_weight) <= 1.0 + 1e-12 for cell in result.cells)
    assert all(0.0 <= float(cell.matched_filter_power_weight) <= 1.0 + 1e-12 for cell in result.cells)
    assert all(
        float(cell.combined_dimensionless_weight)
        == pytest.approx(
            float(cell.spatial_pattern_power_weight) * float(cell.matched_filter_power_weight)
        )
        for cell in result.cells
    )


def test_lfm_compression_reduces_refracted_equivalent_contributing_area_vs_cw() -> None:
    illumination = _illumination(samples=51)
    reference_time = _reference_time(illumination)
    cw = weight_refracted_footprint_by_matched_filter(
        illumination=illumination,
        pulse=ContinuousWavePulse(center_frequency_hz=150_000.0, duration_seconds=0.001),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=500_000.0,
    )
    lfm = weight_refracted_footprint_by_matched_filter(
        illumination=illumination,
        pulse=LinearFMPulse(
            center_frequency_hz=150_000.0,
            bandwidth_hz=100_000.0,
            duration_seconds=0.001,
        ),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=500_000.0,
    )
    assert lfm.equivalent_contributing_area_m2 < cw.equivalent_contributing_area_m2


def test_reference_cell_has_unit_temporal_weight() -> None:
    illumination = _illumination(samples=31)
    reference_time = _reference_time(illumination)
    result = weight_refracted_footprint_by_matched_filter(
        illumination=illumination,
        pulse=LinearFMPulse(
            center_frequency_hz=150_000.0,
            bandwidth_hz=60_000.0,
            duration_seconds=0.001,
        ),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=400_000.0,
    )
    reference_cell = min(
        result.cells,
        key=lambda cell: abs(float(cell.one_way_travel_time_seconds) - reference_time),
    )
    assert reference_cell.matched_filter_power_weight == pytest.approx(1.0, abs=1e-12)

import pytest

from hydrosim.acquisition import (
    AngularScatteringStrengthSample,
    AngularScatteringStrengthTable,
    LayeredSoundSpeedProfile,
    LinearFMPulse,
    SoundSpeedLayer,
    integrate_angular_matched_filter_seafloor_backscatter,
    integrate_refracted_matched_filter_seafloor_backscatter,
    project_angular_pattern_through_layered_profile,
    project_angular_pattern_to_flat_seafloor,
    refracted_matched_filter_scattering_bottom_response,
    scan_mills_cross_two_way_pattern_2d,
)
from hydrosim.geometry import make_reference_mills_cross


def _scan(samples: int = 41):
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
        name="refracted_scattering_test",
    )
    return scan_mills_cross_two_way_pattern_2d(
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


def _profile(c0: float, c1: float):
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=25.0, sound_speed_mps=c0),
            SoundSpeedLayer(top_depth_m=25.0, bottom_depth_m=50.0, sound_speed_mps=c1),
        )
    )


def _table():
    return AngularScatteringStrengthTable(
        samples=(
            AngularScatteringStrengthSample(
                incidence_angle_from_normal_rad=0.0,
                scattering_strength_db_per_m2=-30.0,
            ),
            AngularScatteringStrengthSample(
                incidence_angle_from_normal_rad=0.5,
                scattering_strength_db_per_m2=-30.0,
            ),
        )
    )


def _reference_time(illumination) -> float:
    center = min(
        illumination.cells,
        key=lambda cell: abs(float(cell.along_track_angle_rad))
        + abs(float(cell.across_track_angle_rad)),
    )
    return float(center.one_way_travel_time_seconds)


def test_constant_speed_refracted_time_matches_straight_range_weighting() -> None:
    scan = _scan()
    pulse = LinearFMPulse(
        center_frequency_hz=150_000.0,
        bandwidth_hz=80_000.0,
        duration_seconds=0.001,
    )
    straight = project_angular_pattern_to_flat_seafloor(
        scan=scan,
        vertical_separation_m=50.0,
    )
    refracted = project_angular_pattern_through_layered_profile(
        scan=scan,
        profile=_profile(1500.0, 1500.0),
        target_depth_m=50.0,
    )
    straight_result = integrate_angular_matched_filter_seafloor_backscatter(
        illumination=straight,
        scattering_table=_table(),
        pulse=pulse,
        center_one_way_range_m=50.0,
        sample_rate_hz=400_000.0,
        sound_speed_mps=1500.0,
    )
    refracted_result = integrate_refracted_matched_filter_seafloor_backscatter(
        illumination=refracted,
        scattering_table=_table(),
        pulse=pulse,
        reference_one_way_travel_time_seconds=_reference_time(refracted),
        sample_rate_hz=400_000.0,
    )
    assert refracted_result.integrated_backscatter_strength_db == pytest.approx(
        straight_result.integrated_backscatter_strength_db,
        rel=1e-10,
        abs=1e-10,
    )


def test_refracted_temporal_weight_uses_acoustic_time_not_path_over_single_c() -> None:
    scan = _scan()
    pulse = LinearFMPulse(
        center_frequency_hz=150_000.0,
        bandwidth_hz=100_000.0,
        duration_seconds=0.001,
    )
    illumination = project_angular_pattern_through_layered_profile(
        scan=scan,
        profile=_profile(1450.0, 1550.0),
        target_depth_m=50.0,
    )
    result = integrate_refracted_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(),
        pulse=pulse,
        reference_one_way_travel_time_seconds=_reference_time(illumination),
        sample_rate_hz=500_000.0,
    )
    assert result.contributing_cell_count > 0
    assert result.maximum_one_way_travel_time_seconds > result.minimum_one_way_travel_time_seconds
    assert result.maximum_incidence_angle_rad > result.minimum_incidence_angle_rad


def test_refracted_scattering_exposes_common_bottom_response() -> None:
    illumination = project_angular_pattern_through_layered_profile(
        scan=_scan(samples=31),
        profile=_profile(1500.0, 1550.0),
        target_depth_m=50.0,
    )
    result = integrate_refracted_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(),
        pulse=LinearFMPulse(
            center_frequency_hz=150_000.0,
            bandwidth_hz=80_000.0,
            duration_seconds=0.001,
        ),
        reference_one_way_travel_time_seconds=_reference_time(illumination),
        sample_rate_hz=400_000.0,
    )
    response = refracted_matched_filter_scattering_bottom_response(result)
    assert response.interaction_kind == "seafloor_refracted_angular_area_matched_filter"
    assert response.effective_backscatter_strength_db == pytest.approx(
        result.integrated_backscatter_strength_db
    )
    assert response.amplitude_ratio == pytest.approx(result.amplitude_ratio)

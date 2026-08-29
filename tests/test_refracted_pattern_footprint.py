import math

import pytest

from hydrosim.acquisition import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    project_angular_pattern_through_layered_profile,
    scan_mills_cross_two_way_pattern_2d,
)
from hydrosim.geometry import make_reference_mills_cross


def _scan(samples: int = 31):
    wavelength = 0.01
    configuration = make_reference_mills_cross(
        transmit_count=8, receive_count=8,
        transmit_spacing=wavelength / 2.0, receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6, transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6, receive_element_transverse_size=1e-6,
        name="refracted_projection_test",
    )
    return scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.15, along_track_end_angle_rad=0.15,
        along_track_sample_count=samples,
        across_track_start_angle_rad=-0.15, across_track_end_angle_rad=0.15,
        across_track_sample_count=samples,
        frequency_hz=150_000.0, sound_speed_mps=1500.0,
    )


def _profile(c0: float, c1: float):
    return LayeredSoundSpeedProfile(layers=(
        SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=25.0, sound_speed_mps=c0),
        SoundSpeedLayer(top_depth_m=25.0, bottom_depth_m=50.0, sound_speed_mps=c1),
    ))


def test_constant_speed_refracted_projection_matches_straight_geometry() -> None:
    result = project_angular_pattern_through_layered_profile(
        scan=_scan(), profile=_profile(1500.0, 1500.0), target_depth_m=50.0,
    )
    cell = min(result.cells, key=lambda item: abs(float(item.along_track_angle_rad) - 0.10) + abs(float(item.across_track_angle_rad)))
    angle = float(cell.along_track_angle_rad)
    assert cell.forward_center_m == pytest.approx(50.0 * math.tan(angle), rel=1e-10)
    assert cell.port_center_m == pytest.approx(0.0, abs=1e-10)
    assert cell.incidence_angle_from_normal_rad == pytest.approx(abs(angle), rel=1e-10)
    assert cell.one_way_travel_time_seconds == pytest.approx(float(cell.acoustic_path_length_m) / 1500.0)


def test_increasing_sound_speed_bends_ray_away_from_vertical() -> None:
    scan = _scan()
    uniform = project_angular_pattern_through_layered_profile(
        scan=scan, profile=_profile(1500.0, 1500.0), target_depth_m=50.0,
    )
    increasing = project_angular_pattern_through_layered_profile(
        scan=scan, profile=_profile(1500.0, 1550.0), target_depth_m=50.0,
    )
    key = lambda item: abs(float(item.along_track_angle_rad) - 0.10) + abs(float(item.across_track_angle_rad))
    straight_cell = min(uniform.cells, key=key)
    refracted_cell = min(increasing.cells, key=key)
    assert refracted_cell.horizontal_distance_m > straight_cell.horizontal_distance_m
    assert refracted_cell.incidence_angle_from_normal_rad > straight_cell.incidence_angle_from_normal_rad
    assert refracted_cell.forward_center_m > straight_cell.forward_center_m


def test_refraction_changes_projected_equivalent_area() -> None:
    scan = _scan(samples=41)
    uniform = project_angular_pattern_through_layered_profile(
        scan=scan, profile=_profile(1500.0, 1500.0), target_depth_m=50.0,
    )
    increasing = project_angular_pattern_through_layered_profile(
        scan=scan, profile=_profile(1500.0, 1550.0), target_depth_m=50.0,
    )
    assert increasing.equivalent_insonified_area_m2 > uniform.equivalent_insonified_area_m2

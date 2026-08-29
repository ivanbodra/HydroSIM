import pytest

from hydrosim.acquisition import (
    project_angular_pattern_to_flat_seafloor,
    scan_mills_cross_two_way_pattern_2d,
    seafloor_backscatter_from_projected_pattern,
)
from hydrosim.geometry import make_reference_mills_cross


def _configuration(count: int = 16):
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=count,
        receive_count=count,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name=f"projection_{count}",
    )


def _scan(configuration, *, tx_along=0.0, rx_across=0.0, samples=81):
    return scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.25,
        along_track_end_angle_rad=0.25,
        along_track_sample_count=samples,
        across_track_start_angle_rad=-0.25,
        across_track_end_angle_rad=0.25,
        across_track_sample_count=samples,
        transmit_steering_along_track_angle_rad=tx_along,
        receive_steering_across_track_angle_rad=rx_across,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )


def test_direct_half_power_projection_is_symmetric_at_broadside() -> None:
    footprint = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration()),
        vertical_separation_m=50.0,
    )

    assert footprint.included_cell_count > 0
    assert footprint.effective_area_m2 > 0.0
    assert footprint.forward_min_m == pytest.approx(-float(footprint.forward_max_m), rel=1e-12, abs=1e-12)
    assert footprint.port_min_m == pytest.approx(-float(footprint.port_max_m), rel=1e-12, abs=1e-12)


def test_combined_steering_moves_projected_footprint_forward_and_port() -> None:
    footprint = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration(), tx_along=0.08, rx_across=0.10, samples=101),
        vertical_separation_m=60.0,
    )

    included = [cell for cell in footprint.cells if cell.included]
    mean_forward = sum(float(cell.forward_center_m) for cell in included) / len(included)
    mean_port = sum(float(cell.port_center_m) for cell in included) / len(included)
    assert mean_forward > 0.0
    assert mean_port > 0.0


def test_larger_array_reduces_direct_projected_half_power_area() -> None:
    small = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration(8), samples=101),
        vertical_separation_m=50.0,
    )
    large = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration(24), samples=101),
        vertical_separation_m=50.0,
    )

    assert large.effective_area_m2 < small.effective_area_m2


def test_projected_area_can_feed_existing_seafloor_backscatter_model() -> None:
    footprint = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration()),
        vertical_separation_m=40.0,
    )
    model = seafloor_backscatter_from_projected_pattern(
        scattering_strength_db_per_m2=-30.0,
        footprint=footprint,
        incidence_angle_from_normal_rad=0.0,
    )

    assert float(model.insonified_area_m2) == pytest.approx(float(footprint.effective_area_m2))
    assert float(model.scattering_strength_db_per_m2) == pytest.approx(-30.0)

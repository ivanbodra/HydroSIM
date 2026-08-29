import pytest

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LinearFMPulse,
    gate_projected_pattern_by_rectangular_pulse,
    project_angular_pattern_to_flat_seafloor,
    scan_mills_cross_two_way_pattern_2d,
    waveform_autocorrelation,
    weight_projected_pattern_by_matched_filter,
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


def test_half_power_is_descriptor_not_insonification_boundary() -> None:
    illumination = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration()), vertical_separation_m=50.0
    )
    assert illumination.half_power_cell_count > 0
    assert illumination.half_power_area_m2 > 0.0
    assert illumination.equivalent_insonified_area_m2 > 0.0
    assert illumination.equivalent_insonified_area_m2 < illumination.sampled_grid_area_m2
    outside = [cell for cell in illumination.cells if not cell.inside_half_power_contour]
    assert outside
    assert any(float(cell.equivalent_area_contribution_m2) > 0.0 for cell in outside)
    assert illumination.half_power_forward_min_m == pytest.approx(-float(illumination.half_power_forward_max_m), rel=1e-12, abs=1e-12)
    assert illumination.half_power_port_min_m == pytest.approx(-float(illumination.half_power_port_max_m), rel=1e-12, abs=1e-12)


def test_combined_steering_moves_power_weighted_illumination_forward_and_port() -> None:
    illumination = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration(), tx_along=0.08, rx_across=0.10, samples=101),
        vertical_separation_m=60.0,
    )
    weight_sum = sum(float(cell.equivalent_area_contribution_m2) for cell in illumination.cells)
    mean_forward = sum(float(cell.forward_center_m) * float(cell.equivalent_area_contribution_m2) for cell in illumination.cells) / weight_sum
    mean_port = sum(float(cell.port_center_m) * float(cell.equivalent_area_contribution_m2) for cell in illumination.cells) / weight_sum
    assert mean_forward > 0.0
    assert mean_port > 0.0


def test_larger_array_reduces_pattern_weighted_equivalent_area() -> None:
    small = project_angular_pattern_to_flat_seafloor(scan=_scan(_configuration(8), samples=101), vertical_separation_m=50.0)
    large = project_angular_pattern_to_flat_seafloor(scan=_scan(_configuration(24), samples=101), vertical_separation_m=50.0)
    assert large.equivalent_insonified_area_m2 < small.equivalent_insonified_area_m2


def test_rectangular_pulse_gate_restricts_pattern_weighted_contributing_area() -> None:
    illumination = project_angular_pattern_to_flat_seafloor(scan=_scan(_configuration(), samples=101), vertical_separation_m=50.0)
    short = gate_projected_pattern_by_rectangular_pulse(
        illumination=illumination, center_one_way_range_m=50.0,
        pulse_duration_seconds=0.001, sound_speed_mps=1500.0,
    )
    long = gate_projected_pattern_by_rectangular_pulse(
        illumination=illumination, center_one_way_range_m=50.0,
        pulse_duration_seconds=0.010, sound_speed_mps=1500.0,
    )
    assert short.range_shell_width_m == pytest.approx(0.75)
    assert long.range_shell_width_m == pytest.approx(7.5)
    assert short.contributing_cell_count < long.contributing_cell_count
    assert short.equivalent_insonified_area_m2 < long.equivalent_insonified_area_m2


def test_waveform_autocorrelation_has_unit_zero_lag_power() -> None:
    pulse = LinearFMPulse(center_frequency_hz=150_000.0, bandwidth_hz=100_000.0, duration_seconds=0.001)
    response = waveform_autocorrelation(pulse, sample_rate_hz=500_000.0)
    zero = min(range(len(response.lag_seconds)), key=lambda i: abs(float(response.lag_seconds[i])))
    assert response.normalized_amplitude[zero] == pytest.approx(1.0)
    assert response.normalized_power[zero] == pytest.approx(1.0)


def test_lfm_pulse_compression_reduces_matched_filter_weighted_area_vs_cw() -> None:
    illumination = project_angular_pattern_to_flat_seafloor(
        scan=_scan(_configuration(8), samples=121), vertical_separation_m=50.0
    )
    cw = ContinuousWavePulse(center_frequency_hz=150_000.0, duration_seconds=0.001)
    lfm = LinearFMPulse(center_frequency_hz=150_000.0, bandwidth_hz=100_000.0, duration_seconds=0.001)
    cw_area = weight_projected_pattern_by_matched_filter(
        illumination=illumination, pulse=cw, center_one_way_range_m=50.0,
        sample_rate_hz=500_000.0, sound_speed_mps=1500.0,
    )
    lfm_area = weight_projected_pattern_by_matched_filter(
        illumination=illumination, pulse=lfm, center_one_way_range_m=50.0,
        sample_rate_hz=500_000.0, sound_speed_mps=1500.0,
    )
    assert lfm_area.equivalent_insonified_area_m2 < cw_area.equivalent_insonified_area_m2

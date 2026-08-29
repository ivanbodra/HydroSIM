import pytest

from hydrosim.acquisition import (
    ContinuousWavePulse,
    RefractedPatternIllumination,
    RefractedProjectedPatternCell,
    SplitApertureDefinition,
    build_geometric_phase_ramp,
    compare_geometric_phase_detection_refinement,
)
from hydrosim.geometry import Attitude, TransducerArray


def _array() -> TransducerArray:
    return TransducerArray(
        name="rx_detection_convergence",
        role="rx",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def _cell(ai: int, ci: int, along: float, across: float, time_s: float) -> RefractedProjectedPatternCell:
    return RefractedProjectedPatternCell(
        along_track_index=ai,
        across_track_index=ci,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        normalized_power=1.0,
        relative_power_to_peak=1.0,
        forward_center_m=float(ai),
        port_center_m=float(ci),
        horizontal_distance_m=1.0,
        acoustic_path_length_m=100.0,
        one_way_travel_time_seconds=time_s,
        incidence_angle_from_normal_rad=abs(across),
        projected_area_m2=1.0,
        equivalent_area_contribution_m2=1.0,
    )


def _illumination() -> RefractedPatternIllumination:
    angles = (-0.02, 0.02)
    cells = tuple(
        _cell(ai, ci, along, across, 0.100 + 0.001 * ci)
        for ai, along in enumerate(angles)
        for ci, across in enumerate(angles)
    )
    return RefractedPatternIllumination(
        configuration_name="detection_convergence",
        start_depth_m=0.0,
        target_depth_m=100.0,
        peak_power=1.0,
        sampled_grid_area_m2=4.0,
        equivalent_insonified_area_m2=4.0,
        cells=cells,
    )


def _ramp(sample_rate_hz: float, sample_count: int):
    return build_geometric_phase_ramp(
        illumination=_illumination(),
        receive_array=_array(),
        definition=SplitApertureDefinition(),
        pulse=ContinuousWavePulse(center_frequency_hz=150_000.0, duration_seconds=0.004),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        steering_along_track_angle_rad=0.0,
        steering_across_track_angle_rad=0.0,
        start_reference_one_way_travel_time_seconds=0.099,
        sample_count=sample_count,
        sample_rate_hz=sample_rate_hz,
    )


def test_phase_detected_twtt_converges_under_temporal_refinement() -> None:
    coarse = _ramp(2000.0, 9)
    fine = _ramp(4000.0, 17)

    diagnostic = compare_geometric_phase_detection_refinement(
        coarse=coarse,
        fine=fine,
        search_start_twtt_seconds=0.199,
        search_end_twtt_seconds=0.202,
        fit_half_width_seconds=0.001,
        twtt_tolerance_seconds=2.5e-4,
    )

    assert diagnostic.coarse_detection.detection.twtt_seconds == pytest.approx(0.201, abs=5e-4)
    assert diagnostic.fine_detection.detection.twtt_seconds == pytest.approx(0.201, abs=5e-4)
    assert diagnostic.absolute_twtt_change_seconds <= 2.5e-4
    assert diagnostic.change_in_fine_samples <= 1.0
    assert diagnostic.converged is True


def test_detection_refinement_uses_physical_fit_width() -> None:
    coarse = _ramp(2000.0, 9)
    fine = _ramp(4000.0, 17)

    diagnostic = compare_geometric_phase_detection_refinement(
        coarse=coarse,
        fine=fine,
        search_start_twtt_seconds=0.199,
        search_end_twtt_seconds=0.202,
        fit_half_width_seconds=0.001,
        twtt_tolerance_seconds=1e-3,
    )

    assert diagnostic.coarse_detection.fit.sample_count < diagnostic.fine_detection.fit.sample_count
    assert diagnostic.fine_temporal_spacing_seconds == pytest.approx(1.0 / 4000.0)

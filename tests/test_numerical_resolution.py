from types import SimpleNamespace

import pytest

from hydrosim.acquisition import (
    angular_grid_resolution,
    assess_baseband_sampling,
    compare_refracted_footprint_refinement,
    compare_scalar_refinement,
)


def test_baseband_sampling_reports_nyquist_margin() -> None:
    diagnostic = assess_baseband_sampling(
        sample_rate_hz=100_000.0,
        maximum_absolute_frequency_hz=20_000.0,
    )
    assert diagnostic.meets_nyquist is True
    assert diagnostic.nyquist_frequency_hz == pytest.approx(50_000.0)
    assert diagnostic.nyquist_ratio == pytest.approx(2.5)


def test_zero_bandwidth_sampling_has_no_finite_ratio() -> None:
    diagnostic = assess_baseband_sampling(
        sample_rate_hz=10_000.0,
        maximum_absolute_frequency_hz=0.0,
    )
    assert diagnostic.meets_nyquist is True
    assert diagnostic.nyquist_ratio is None


def test_scalar_refinement_marks_small_relative_change_converged() -> None:
    diagnostic = compare_scalar_refinement(
        quantity_name="equivalent_contributing_area_m2",
        coarse_value=10.02,
        fine_value=10.0,
        relative_tolerance=0.005,
    )
    assert diagnostic.relative_change == pytest.approx(0.002)
    assert diagnostic.converged is True


def test_scalar_refinement_handles_zero_reference_without_infinity() -> None:
    diagnostic = compare_scalar_refinement(
        quantity_name="phase_error_rad",
        coarse_value=0.1,
        fine_value=0.0,
        relative_tolerance=0.01,
    )
    assert diagnostic.relative_change is None
    assert diagnostic.converged is False


def test_angular_grid_resolution_records_continuous_sampled_axes() -> None:
    result = angular_grid_resolution(
        along_track_angles_rad=(-0.2, 0.0, 0.2),
        across_track_angles_rad=(-0.1, 0.0, 0.1),
    )
    assert result.along_track.semantics == "continuous_sampled"
    assert result.along_track.sample_count == 3
    assert result.along_track.nominal_spacing == pytest.approx(0.2)
    assert result.across_track.nominal_spacing == pytest.approx(0.1)


def test_refracted_footprint_refinement_compares_same_physical_domain() -> None:
    coarse = SimpleNamespace(
        configuration_name="reference",
        start_depth_m=0.0,
        target_depth_m=100.0,
        sampled_grid_area_m2=400.4,
        equivalent_insonified_area_m2=100.3,
    )
    fine = SimpleNamespace(
        configuration_name="reference",
        start_depth_m=0.0,
        target_depth_m=100.0,
        sampled_grid_area_m2=400.0,
        equivalent_insonified_area_m2=100.0,
    )
    result = compare_refracted_footprint_refinement(
        coarse_illumination=coarse,
        fine_illumination=fine,
        coarse_along_track_angles_rad=(-0.2, 0.0, 0.2),
        coarse_across_track_angles_rad=(-0.2, 0.0, 0.2),
        fine_along_track_angles_rad=(-0.2, -0.1, 0.0, 0.1, 0.2),
        fine_across_track_angles_rad=(-0.2, -0.1, 0.0, 0.1, 0.2),
        relative_tolerance=0.005,
    )
    assert result.coarse_grid.along_track.nominal_spacing == pytest.approx(0.2)
    assert result.fine_grid.along_track.nominal_spacing == pytest.approx(0.1)
    assert result.sampled_grid_area.converged is True
    assert result.equivalent_insonified_area.converged is True
    assert result.converged is True


def test_refracted_footprint_refinement_rejects_non_refined_grid() -> None:
    coarse = SimpleNamespace(
        configuration_name="reference",
        start_depth_m=0.0,
        target_depth_m=100.0,
        sampled_grid_area_m2=1.0,
        equivalent_insonified_area_m2=1.0,
    )
    fine = SimpleNamespace(**coarse.__dict__)
    with pytest.raises(ValueError, match="fine along-track grid"):
        compare_refracted_footprint_refinement(
            coarse_illumination=coarse,
            fine_illumination=fine,
            coarse_along_track_angles_rad=(-0.1, 0.0, 0.1),
            coarse_across_track_angles_rad=(-0.1, 0.0, 0.1),
            fine_along_track_angles_rad=(-0.1, 0.0, 0.1),
            fine_across_track_angles_rad=(-0.1, 0.0, 0.1),
            relative_tolerance=0.01,
        )

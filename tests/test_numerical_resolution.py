import pytest

from hydrosim.acquisition import (
    assess_baseband_sampling,
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

"""Numerical-resolution metadata for continuous physical models.

HydroSIM distinguishes a continuous scientific model from its discrete numerical
realization. This module provides small reusable diagnostics for that boundary.
It does not choose a scientific model; it records sampling and compares results
under refinement.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

DomainSemantics = Literal[
    "continuous_sampled",
    "piecewise_constant",
    "intrinsically_discrete",
]


class ResolutionAxis(BaseModel):
    """One numerical axis used to realize a physical or geometric domain."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    semantics: DomainSemantics
    sample_count: int = Field(ge=2)
    nominal_spacing: FiniteFloat = Field(gt=0.0)


class SamplingAdequacy(BaseModel):
    """Nyquist-style adequacy diagnostic for a sampled baseband signal."""

    model_config = ConfigDict(frozen=True)

    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    maximum_absolute_frequency_hz: FiniteFloat = Field(ge=0.0)
    nyquist_frequency_hz: FiniteFloat = Field(gt=0.0)
    nyquist_ratio: FiniteFloat | None = Field(default=None, ge=0.0)
    meets_nyquist: bool


class ScalarConvergenceDiagnostic(BaseModel):
    """Change in one scalar quantity under numerical refinement."""

    model_config = ConfigDict(frozen=True)

    quantity_name: str = Field(min_length=1)
    coarse_value: FiniteFloat
    fine_value: FiniteFloat
    absolute_change: FiniteFloat = Field(ge=0.0)
    relative_change: FiniteFloat | None = Field(default=None, ge=0.0)
    relative_tolerance: FiniteFloat = Field(ge=0.0)
    converged: bool


class AngularGridResolution(BaseModel):
    """Resolution metadata for a sampled continuous two-dimensional angular field."""

    model_config = ConfigDict(frozen=True)

    along_track: ResolutionAxis
    across_track: ResolutionAxis


class FootprintConvergenceDiagnostic(BaseModel):
    """Convergence of refracted footprint integrals under angular-grid refinement."""

    model_config = ConfigDict(frozen=True)

    coarse_grid: AngularGridResolution
    fine_grid: AngularGridResolution
    sampled_grid_area: ScalarConvergenceDiagnostic
    equivalent_insonified_area: ScalarConvergenceDiagnostic
    converged: bool


def assess_baseband_sampling(*, sample_rate_hz: float, maximum_absolute_frequency_hz: float) -> SamplingAdequacy:
    """Assess whether a discrete baseband realization satisfies Nyquist.

    The criterion is ``f_s / 2 >= f_max``. Meeting Nyquist only prevents aliasing
    in the ideal sampled representation; it does not guarantee adequate numerical
    resolution for a particular observable. ``nyquist_ratio`` is undefined for a
    zero-bandwidth baseband signal and is then reported as ``None``.
    """

    fs = float(sample_rate_hz)
    fmax = float(maximum_absolute_frequency_hz)
    if fs <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if fmax < 0.0:
        raise ValueError("maximum_absolute_frequency_hz must be non-negative")
    nyquist = 0.5 * fs
    ratio = nyquist / fmax if fmax > 0.0 else None
    return SamplingAdequacy(
        sample_rate_hz=fs,
        maximum_absolute_frequency_hz=fmax,
        nyquist_frequency_hz=nyquist,
        nyquist_ratio=ratio,
        meets_nyquist=nyquist >= fmax,
    )


def compare_scalar_refinement(*, quantity_name: str, coarse_value: float, fine_value: float, relative_tolerance: float) -> ScalarConvergenceDiagnostic:
    """Compare a scalar result from coarse and refined numerical realizations.

    Relative change uses the refined result as the reference scale. It is undefined
    when the refined value is exactly zero and the two results differ; that case is
    reported as ``relative_change=None`` and cannot satisfy a finite relative
    convergence tolerance.
    """

    tolerance = float(relative_tolerance)
    if tolerance < 0.0:
        raise ValueError("relative_tolerance must be non-negative")
    coarse = float(coarse_value)
    fine = float(fine_value)
    change = abs(fine - coarse)
    scale = abs(fine)
    if scale > 0.0:
        relative: float | None = change / scale
        converged = relative <= tolerance
    elif change == 0.0:
        relative = 0.0
        converged = True
    else:
        relative = None
        converged = False
    return ScalarConvergenceDiagnostic(
        quantity_name=quantity_name,
        coarse_value=coarse,
        fine_value=fine,
        absolute_change=change,
        relative_change=relative,
        relative_tolerance=tolerance,
        converged=converged,
    )


def angular_grid_resolution(*, along_track_angles_rad: tuple[float, ...], across_track_angles_rad: tuple[float, ...]) -> AngularGridResolution:
    """Describe the numerical realization of a continuous angular field.

    Both axes must be strictly increasing and uniformly sampled.  The helper is
    intentionally explicit because a sampled angular pattern is a numerical grid,
    not a set of intrinsically discrete physical beams.
    """

    def _axis(name: str, values: tuple[float, ...]) -> ResolutionAxis:
        if len(values) < 2:
            raise ValueError(f"{name} axis requires at least two samples")
        numbers = tuple(float(value) for value in values)
        steps = tuple(numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1))
        if any(step <= 0.0 for step in steps):
            raise ValueError(f"{name} angles must be strictly increasing")
        nominal = steps[0]
        tolerance = max(1e-12, abs(nominal) * 1e-9)
        if any(abs(step - nominal) > tolerance for step in steps[1:]):
            raise ValueError(f"{name} angular grid must be uniformly sampled")
        return ResolutionAxis(
            name=name,
            unit="rad",
            semantics="continuous_sampled",
            sample_count=len(numbers),
            nominal_spacing=nominal,
        )

    return AngularGridResolution(
        along_track=_axis("along_track", along_track_angles_rad),
        across_track=_axis("across_track", across_track_angles_rad),
    )


def compare_refracted_footprint_refinement(
    *,
    coarse_illumination,
    fine_illumination,
    coarse_along_track_angles_rad: tuple[float, ...],
    coarse_across_track_angles_rad: tuple[float, ...],
    fine_along_track_angles_rad: tuple[float, ...],
    fine_across_track_angles_rad: tuple[float, ...],
    relative_tolerance: float,
) -> FootprintConvergenceDiagnostic:
    """Compare refracted footprint integrals computed on two angular grids.

    The scientific quantity is the continuous-area integral. ``coarse`` and
    ``fine`` are two discrete quadrature realizations over the same physical
    angular domain.  This function does not assume convergence merely because the
    fine grid contains more cells; it reports the observed refinement change.
    """

    if coarse_illumination.configuration_name != fine_illumination.configuration_name:
        raise ValueError("footprint refinements must use the same configuration")
    for attribute in ("start_depth_m", "target_depth_m"):
        if abs(float(getattr(coarse_illumination, attribute)) - float(getattr(fine_illumination, attribute))) > 1e-12:
            raise ValueError("footprint refinements must use the same depth geometry")

    coarse_grid = angular_grid_resolution(
        along_track_angles_rad=coarse_along_track_angles_rad,
        across_track_angles_rad=coarse_across_track_angles_rad,
    )
    fine_grid = angular_grid_resolution(
        along_track_angles_rad=fine_along_track_angles_rad,
        across_track_angles_rad=fine_across_track_angles_rad,
    )
    if fine_grid.along_track.nominal_spacing >= coarse_grid.along_track.nominal_spacing:
        raise ValueError("fine along-track grid must have smaller spacing than coarse grid")
    if fine_grid.across_track.nominal_spacing >= coarse_grid.across_track.nominal_spacing:
        raise ValueError("fine across-track grid must have smaller spacing than coarse grid")

    grid_area = compare_scalar_refinement(
        quantity_name="sampled_grid_area_m2",
        coarse_value=float(coarse_illumination.sampled_grid_area_m2),
        fine_value=float(fine_illumination.sampled_grid_area_m2),
        relative_tolerance=relative_tolerance,
    )
    equivalent_area = compare_scalar_refinement(
        quantity_name="equivalent_insonified_area_m2",
        coarse_value=float(coarse_illumination.equivalent_insonified_area_m2),
        fine_value=float(fine_illumination.equivalent_insonified_area_m2),
        relative_tolerance=relative_tolerance,
    )
    return FootprintConvergenceDiagnostic(
        coarse_grid=coarse_grid,
        fine_grid=fine_grid,
        sampled_grid_area=grid_area,
        equivalent_insonified_area=equivalent_area,
        converged=grid_area.converged and equivalent_area.converged,
    )

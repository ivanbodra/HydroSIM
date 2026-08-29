"""Numerical-resolution metadata for continuous physical models.

HydroSIM distinguishes a continuous scientific model from its discrete numerical
realization.  This module provides small reusable diagnostics for that boundary.
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
    nyquist_ratio: FiniteFloat = Field(ge=0.0)
    meets_nyquist: bool


class ScalarConvergenceDiagnostic(BaseModel):
    """Change in one scalar quantity under numerical refinement."""

    model_config = ConfigDict(frozen=True)

    quantity_name: str = Field(min_length=1)
    coarse_value: FiniteFloat
    fine_value: FiniteFloat
    absolute_change: FiniteFloat = Field(ge=0.0)
    relative_change: FiniteFloat = Field(ge=0.0)
    relative_tolerance: FiniteFloat = Field(ge=0.0)
    converged: bool


def assess_baseband_sampling(*, sample_rate_hz: float, maximum_absolute_frequency_hz: float) -> SamplingAdequacy:
    """Assess whether a discrete baseband realization satisfies Nyquist.

    The criterion is ``f_s / 2 >= f_max``.  Meeting Nyquist only prevents aliasing
    in the ideal sampled representation; it does not guarantee adequate numerical
    resolution for a particular observable.
    """

    fs = float(sample_rate_hz)
    fmax = float(maximum_absolute_frequency_hz)
    if fs <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if fmax < 0.0:
        raise ValueError("maximum_absolute_frequency_hz must be non-negative")
    nyquist = 0.5 * fs
    ratio = nyquist / fmax if fmax > 0.0 else float("inf")
    return SamplingAdequacy(
        sample_rate_hz=fs,
        maximum_absolute_frequency_hz=fmax,
        nyquist_frequency_hz=nyquist,
        nyquist_ratio=ratio,
        meets_nyquist=nyquist >= fmax,
    )


def compare_scalar_refinement(*, quantity_name: str, coarse_value: float, fine_value: float, relative_tolerance: float) -> ScalarConvergenceDiagnostic:
    """Compare a scalar result from coarse and refined numerical realizations."""

    tolerance = float(relative_tolerance)
    if tolerance < 0.0:
        raise ValueError("relative_tolerance must be non-negative")
    coarse = float(coarse_value)
    fine = float(fine_value)
    change = abs(fine - coarse)
    scale = abs(fine)
    relative = change / scale if scale > 0.0 else (0.0 if change == 0.0 else float("inf"))
    return ScalarConvergenceDiagnostic(
        quantity_name=quantity_name,
        coarse_value=coarse,
        fine_value=fine,
        absolute_change=change,
        relative_change=relative,
        relative_tolerance=tolerance,
        converged=relative <= tolerance,
    )

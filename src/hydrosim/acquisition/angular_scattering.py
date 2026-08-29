"""Explicit angle-dependent seafloor scattering over projected pattern cells.

HydroSIM does not embed a hidden empirical bottom-scattering law. This module
accepts an explicit user/model supplied table of scattering strength versus
incidence angle and integrates it over the already projected TX×RX power field.

For cell i with scattering strength S_b(theta_i) in dB per square metre and
pattern-weighted equivalent area dA_eq,i, the linear contribution is

    q_i = 10**(S_b(theta_i)/10) * dA_eq,i

and the integrated area-backscatter strength is

    BS = 10 log10(sum_i q_i).

The table is linearly interpolated in dB versus incidence angle. Extrapolation is
not performed: the supplied table must cover every contributing incidence angle.
This keeps the scientific assumption visible and replaceable.
"""

from __future__ import annotations

from bisect import bisect_left
from math import log10

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from .bottom_interaction import BottomInteractionResponse
from .pattern_footprint_2d import ProjectedPatternIllumination


class AngularScatteringStrengthSample(BaseModel):
    """One explicit seafloor scattering-strength sample versus incidence angle."""

    model_config = ConfigDict(frozen=True)

    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0)
    scattering_strength_db_per_m2: FiniteFloat


class AngularScatteringStrengthTable(BaseModel):
    """Piecewise-linear S_b(theta) table with no implicit extrapolation."""

    model_config = ConfigDict(frozen=True)

    samples: tuple[AngularScatteringStrengthSample, ...]

    @model_validator(mode="after")
    def _validate_samples(self) -> "AngularScatteringStrengthTable":
        if len(self.samples) < 2:
            raise ValueError("angular scattering table requires at least two samples")
        angles = [float(item.incidence_angle_from_normal_rad) for item in self.samples]
        if any(right <= left for left, right in zip(angles, angles[1:], strict=False)):
            raise ValueError("angular scattering incidence angles must be strictly increasing")
        return self


class AngularScatteringIntegration(BaseModel):
    """Integrated angle-dependent area backscatter over projected pattern cells."""

    model_config = ConfigDict(frozen=True)

    contributing_cell_count: int = Field(gt=0)
    minimum_incidence_angle_rad: FiniteFloat = Field(ge=0.0)
    maximum_incidence_angle_rad: FiniteFloat = Field(ge=0.0)
    integrated_backscatter_strength_db: FiniteFloat
    amplitude_ratio: FiniteFloat = Field(gt=0.0)


def scattering_strength_at_incidence(
    table: AngularScatteringStrengthTable,
    incidence_angle_from_normal_rad: float,
) -> float:
    """Linearly interpolate the explicit S_b table in dB versus incidence angle."""

    angle = float(incidence_angle_from_normal_rad)
    samples = table.samples
    angles = tuple(float(item.incidence_angle_from_normal_rad) for item in samples)
    if angle < angles[0] or angle > angles[-1]:
        raise ValueError("incidence angle lies outside supplied angular scattering table")
    index = bisect_left(angles, angle)
    if index == 0:
        return float(samples[0].scattering_strength_db_per_m2)
    if index == len(samples):
        return float(samples[-1].scattering_strength_db_per_m2)
    if angles[index] == angle:
        return float(samples[index].scattering_strength_db_per_m2)
    left = samples[index - 1]
    right = samples[index]
    a0 = float(left.incidence_angle_from_normal_rad)
    a1 = float(right.incidence_angle_from_normal_rad)
    s0 = float(left.scattering_strength_db_per_m2)
    s1 = float(right.scattering_strength_db_per_m2)
    fraction = (angle - a0) / (a1 - a0)
    return s0 + fraction * (s1 - s0)


def integrate_angular_seafloor_backscatter(
    *,
    illumination: ProjectedPatternIllumination,
    scattering_table: AngularScatteringStrengthTable,
) -> AngularScatteringIntegration:
    """Integrate explicit S_b(theta) over pattern-weighted projected cells.

    Every sampled cell contributes according to its own flat-bottom incidence
    angle and its existing ``(P/P_peak) dA`` equivalent-area contribution.
    Cells with exactly zero pattern contribution do not require table coverage.
    """

    linear_sum = 0.0
    incidences: list[float] = []
    count = 0
    for cell in illumination.cells:
        equivalent_area = float(cell.equivalent_area_contribution_m2)
        if equivalent_area <= 0.0:
            continue
        incidence = float(cell.incidence_angle_from_normal_rad)
        strength_db = scattering_strength_at_incidence(scattering_table, incidence)
        linear_sum += (10.0 ** (strength_db / 10.0)) * equivalent_area
        incidences.append(incidence)
        count += 1

    if linear_sum <= 0.0 or not incidences:
        raise ValueError("angular scattering integration has no positive contribution")

    strength_db = 10.0 * log10(linear_sum)
    return AngularScatteringIntegration(
        contributing_cell_count=count,
        minimum_incidence_angle_rad=min(incidences),
        maximum_incidence_angle_rad=max(incidences),
        integrated_backscatter_strength_db=strength_db,
        amplitude_ratio=10.0 ** (strength_db / 20.0),
    )


def angular_scattering_bottom_response(
    integration: AngularScatteringIntegration,
) -> BottomInteractionResponse:
    """Expose the angle-resolved integration through the common bottom response."""

    return BottomInteractionResponse(
        interaction_kind="seafloor_angular_area",
        effective_backscatter_strength_db=integration.integrated_backscatter_strength_db,
        amplitude_ratio=integration.amplitude_ratio,
    )

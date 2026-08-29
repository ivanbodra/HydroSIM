"""Backscatter-free contribution weighting for footprint demonstrations.

The acquisition forward model does not require a bottom-scattering or reflectivity
model. This module therefore describes only how transducer pattern, refracted
travel time, and waveform processing shape the part of the seafloor that can
contribute to one matched-filter sample.

For cell i the demonstration weight is

    w_i = (P_i/P_peak) * W_t(2(T_i - T_ref)),

and its area-equivalent contribution is

    dA_eq,i = w_i * dA_i.

No S_b, target strength, sediment class, or reflectivity coefficient appears here.
The result is not received power and must not be interpreted as backscatter.

The continuous-area interpretation is approximated numerically by the projected
angular cells. ``assess_refracted_footprint_convergence`` compares the same
observable under spatial refinement so discretization change is not confused with
physical change.
"""

from __future__ import annotations

from bisect import bisect_left

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .numerical_resolution import ScalarConvergenceDiagnostic, compare_scalar_refinement
from .refracted_pattern_footprint import RefractedPatternIllumination
from .waveform import WaveformAutocorrelation, WaveformPulse, waveform_autocorrelation


class FootprintContributionCell(BaseModel):
    """One refracted seafloor cell with purely geometric/waveform contribution weight."""

    model_config = ConfigDict(frozen=True)

    along_track_index: int = Field(ge=0)
    across_track_index: int = Field(ge=0)
    forward_center_m: FiniteFloat
    port_center_m: FiniteFloat
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0)
    one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    projected_area_m2: FiniteFloat = Field(gt=0.0)
    spatial_pattern_power_weight: FiniteFloat = Field(ge=0.0)
    matched_filter_power_weight: FiniteFloat = Field(ge=0.0)
    combined_dimensionless_weight: FiniteFloat = Field(ge=0.0)
    equivalent_area_contribution_m2: FiniteFloat = Field(ge=0.0)


class RefractedFootprintContribution(BaseModel):
    """Refracted pattern-times-waveform footprint contribution field."""

    model_config = ConfigDict(frozen=True)

    reference_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    total_cell_count: int = Field(gt=0)
    contributing_cell_count: int = Field(ge=0)
    equivalent_contributing_area_m2: FiniteFloat = Field(ge=0.0)
    cells: tuple[FootprintContributionCell, ...]
    autocorrelation: WaveformAutocorrelation


def _autocorrelation_power_at_lag(
    autocorrelation: WaveformAutocorrelation,
    lag_seconds: float,
) -> float:
    lags = tuple(float(value) for value in autocorrelation.lag_seconds)
    powers = tuple(float(value) for value in autocorrelation.normalized_power)
    lag = float(lag_seconds)
    if lag < lags[0] or lag > lags[-1]:
        return 0.0
    index = bisect_left(lags, lag)
    if index == 0:
        return powers[0]
    if index == len(lags):
        return powers[-1]
    l0, l1 = lags[index - 1], lags[index]
    p0, p1 = powers[index - 1], powers[index]
    if l1 == l0:
        return p0
    return p0 + (lag - l0) * (p1 - p0) / (l1 - l0)


def weight_refracted_footprint_by_matched_filter(
    *,
    illumination: RefractedPatternIllumination,
    pulse: WaveformPulse,
    reference_one_way_travel_time_seconds: float,
    sample_rate_hz: float,
) -> RefractedFootprintContribution:
    """Build a footprint contribution field without any bottom-response model.

    ``reference_one_way_travel_time_seconds`` identifies the matched-filter sample
    being demonstrated. Under the current reciprocal stationary-water reference,
    each cell is evaluated at two-way lag ``2 * (T_i - T_ref)``.
    """

    reference_time = float(reference_one_way_travel_time_seconds)
    fs = float(sample_rate_hz)
    if reference_time <= 0.0 or fs <= 0.0:
        raise ValueError("reference travel time and sample rate must be positive")

    autocorrelation = waveform_autocorrelation(pulse, sample_rate_hz=fs)
    cells: list[FootprintContributionCell] = []
    equivalent_area = 0.0
    contributing = 0

    for cell in illumination.cells:
        spatial = float(cell.relative_power_to_peak)
        temporal = _autocorrelation_power_at_lag(
            autocorrelation,
            2.0 * (float(cell.one_way_travel_time_seconds) - reference_time),
        )
        combined = spatial * temporal
        area_contribution = combined * float(cell.projected_area_m2)
        if combined > 0.0:
            contributing += 1
        equivalent_area += area_contribution
        cells.append(
            FootprintContributionCell(
                along_track_index=cell.along_track_index,
                across_track_index=cell.across_track_index,
                forward_center_m=cell.forward_center_m,
                port_center_m=cell.port_center_m,
                incidence_angle_from_normal_rad=cell.incidence_angle_from_normal_rad,
                one_way_travel_time_seconds=cell.one_way_travel_time_seconds,
                projected_area_m2=cell.projected_area_m2,
                spatial_pattern_power_weight=spatial,
                matched_filter_power_weight=temporal,
                combined_dimensionless_weight=combined,
                equivalent_area_contribution_m2=area_contribution,
            )
        )

    return RefractedFootprintContribution(
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=fs,
        total_cell_count=len(cells),
        contributing_cell_count=contributing,
        equivalent_contributing_area_m2=equivalent_area,
        cells=tuple(cells),
        autocorrelation=autocorrelation,
    )


def assess_refracted_footprint_convergence(
    *,
    coarse: RefractedFootprintContribution,
    fine: RefractedFootprintContribution,
    relative_tolerance: float,
) -> ScalarConvergenceDiagnostic:
    """Compare equivalent contributing area under spatial-grid refinement.

    The two results must use the same temporal sample rate and the same reference
    one-way travel time.  This deliberately isolates spatial discretization from
    temporal discretization.  The ``fine`` realization must contain more cells
    than ``coarse``.
    """

    if fine.total_cell_count <= coarse.total_cell_count:
        raise ValueError("fine footprint realization must contain more cells than coarse")
    if abs(float(fine.sample_rate_hz) - float(coarse.sample_rate_hz)) > 1e-12:
        raise ValueError("coarse and fine footprint results must use the same sample rate")
    if abs(
        float(fine.reference_one_way_travel_time_seconds)
        - float(coarse.reference_one_way_travel_time_seconds)
    ) > 1e-12:
        raise ValueError("coarse and fine footprint results must use the same reference travel time")

    return compare_scalar_refinement(
        quantity_name="equivalent_contributing_area_m2",
        coarse_value=float(coarse.equivalent_contributing_area_m2),
        fine_value=float(fine.equivalent_contributing_area_m2),
        relative_tolerance=relative_tolerance,
    )

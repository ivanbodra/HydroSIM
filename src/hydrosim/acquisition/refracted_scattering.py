"""Angle-dependent matched-filter seafloor scattering using refracted travel time.

This module combines the refracted pattern footprint with the existing explicit
S_b(theta) table and waveform autocorrelation. Unlike the straight-ray reference,
temporal delay is derived from the per-cell acoustic travel time produced by the
layered propagation model.

For reciprocal propagation, the relative two-way delay of cell i is

    dt_i = 2 (T_i - T_ref),

where T_i is its one-way refracted travel time. The deterministic incoherent power
contribution is

    q_i = 10**(S_b(theta_i)/10)
          * (P_i/P_peak) dA_i
          * W_t(dt_i),

with W_t the normalized matched-filter power response. No constant effective
sound speed is introduced to convert path length into delay.
"""

from __future__ import annotations

from bisect import bisect_left
from math import log10

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_scattering import AngularScatteringStrengthTable, scattering_strength_at_incidence
from .bottom_interaction import BottomInteractionResponse
from .refracted_pattern_footprint import RefractedPatternIllumination
from .waveform import WaveformAutocorrelation, WaveformPulse, waveform_autocorrelation


class RefractedMatchedFilterScatteringIntegration(BaseModel):
    """Beam, refraction, incidence, waveform and bottom-scattering integration."""

    model_config = ConfigDict(frozen=True)

    reference_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    contributing_cell_count: int = Field(gt=0)
    minimum_incidence_angle_rad: FiniteFloat = Field(ge=0.0)
    maximum_incidence_angle_rad: FiniteFloat = Field(ge=0.0)
    minimum_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    maximum_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    integrated_backscatter_strength_db: FiniteFloat
    amplitude_ratio: FiniteFloat = Field(gt=0.0)
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


def integrate_refracted_matched_filter_seafloor_backscatter(
    *,
    illumination: RefractedPatternIllumination,
    scattering_table: AngularScatteringStrengthTable,
    pulse: WaveformPulse,
    reference_one_way_travel_time_seconds: float,
    sample_rate_hz: float,
) -> RefractedMatchedFilterScatteringIntegration:
    """Integrate refracted travel time, local incidence and waveform per cell.

    The reference is expressed directly as one-way acoustic travel time. Under the
    current reciprocal stationary-water approximation, a cell contributes at lag
    ``2 * (T_i - T_ref)``. This keeps temporal weighting tied to the propagation
    solution instead of reconstructing delay from Euclidean range and one sound
    speed.
    """

    reference_time = float(reference_one_way_travel_time_seconds)
    fs = float(sample_rate_hz)
    if reference_time <= 0.0 or fs <= 0.0:
        raise ValueError("reference travel time and sample rate must be positive")

    autocorrelation = waveform_autocorrelation(pulse, sample_rate_hz=fs)
    linear_sum = 0.0
    incidences: list[float] = []
    travel_times: list[float] = []
    count = 0

    for cell in illumination.cells:
        spatial_area = float(cell.equivalent_area_contribution_m2)
        if spatial_area <= 0.0:
            continue
        travel_time = float(cell.one_way_travel_time_seconds)
        lag = 2.0 * (travel_time - reference_time)
        temporal_power = _autocorrelation_power_at_lag(autocorrelation, lag)
        if temporal_power <= 0.0:
            continue
        incidence = float(cell.incidence_angle_from_normal_rad)
        strength_db = scattering_strength_at_incidence(scattering_table, incidence)
        linear_sum += (10.0 ** (strength_db / 10.0)) * spatial_area * temporal_power
        incidences.append(incidence)
        travel_times.append(travel_time)
        count += 1

    if linear_sum <= 0.0 or not incidences:
        raise ValueError("refracted matched-filter scattering integration has no positive contribution")

    strength_db = 10.0 * log10(linear_sum)
    return RefractedMatchedFilterScatteringIntegration(
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=fs,
        contributing_cell_count=count,
        minimum_incidence_angle_rad=min(incidences),
        maximum_incidence_angle_rad=max(incidences),
        minimum_one_way_travel_time_seconds=min(travel_times),
        maximum_one_way_travel_time_seconds=max(travel_times),
        integrated_backscatter_strength_db=strength_db,
        amplitude_ratio=10.0 ** (strength_db / 20.0),
        autocorrelation=autocorrelation,
    )


def refracted_matched_filter_scattering_bottom_response(
    integration: RefractedMatchedFilterScatteringIntegration,
) -> BottomInteractionResponse:
    """Expose refracted deterministic cell integration through the common response."""

    return BottomInteractionResponse(
        interaction_kind="seafloor_refracted_angular_area_matched_filter",
        effective_backscatter_strength_db=integration.integrated_backscatter_strength_db,
        amplitude_ratio=integration.amplitude_ratio,
    )

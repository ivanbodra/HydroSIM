"""Propagation-weighted refracted seafloor return integration.

This module extends the deterministic refracted bottom-scattering integration by
applying explicit two-way propagation loss to every contributing cell. It remains
separate from ``BottomInteractionResponse`` because propagation loss and bottom
scattering are distinct physical layers in HydroSIM.

For cell i, the linear received-power-relative contribution is

    q_i = 10**(S_b(theta_i)/10)
          * (P_i/P_peak) dA_i
          * W_t(dt_i)
          * G_prop,i,

where ``G_prop,i`` is the reciprocal two-way propagation *power* ratio. The
existing transmission-loss model returns a two-way pressure-amplitude ratio A_i,
so

    G_prop,i = A_i**2 = 10**(-TL_2w,i/10).

The result is referenced to the transmission-loss model's spreading reference
distance and unit source/bottom conventions. It is not an absolute received level:
source level, calibrated transducer sensitivity, receiver gain, noise and
electronics are intentionally absent.
"""

from __future__ import annotations

from bisect import bisect_left
from math import log10

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_scattering import AngularScatteringStrengthTable, scattering_strength_at_incidence
from .refracted_pattern_footprint import RefractedPatternIllumination
from .transmission_loss import PropagationLossModel, reciprocal_transmission_loss
from .waveform import WaveformAutocorrelation, WaveformPulse, waveform_autocorrelation


class RefractedPropagationWeightedReturn(BaseModel):
    """Relative received return after pattern, scattering, time gate and TL."""

    model_config = ConfigDict(frozen=True)

    reference_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    contributing_cell_count: int = Field(gt=0)
    minimum_one_way_path_length_m: FiniteFloat = Field(gt=0.0)
    maximum_one_way_path_length_m: FiniteFloat = Field(gt=0.0)
    minimum_two_way_transmission_loss_db: FiniteFloat
    maximum_two_way_transmission_loss_db: FiniteFloat
    received_power_relative_db: FiniteFloat
    received_power_ratio: FiniteFloat = Field(gt=0.0)
    received_amplitude_ratio: FiniteFloat = Field(gt=0.0)
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


def integrate_refracted_propagation_weighted_return(
    *,
    illumination: RefractedPatternIllumination,
    scattering_table: AngularScatteringStrengthTable,
    pulse: WaveformPulse,
    reference_one_way_travel_time_seconds: float,
    sample_rate_hz: float,
    propagation_loss_model: PropagationLossModel,
) -> RefractedPropagationWeightedReturn:
    """Integrate per-cell pattern, S_b(theta), matched filter and reciprocal TL."""

    reference_time = float(reference_one_way_travel_time_seconds)
    fs = float(sample_rate_hz)
    if reference_time <= 0.0 or fs <= 0.0:
        raise ValueError("reference travel time and sample rate must be positive")

    autocorrelation = waveform_autocorrelation(pulse, sample_rate_hz=fs)
    linear_sum = 0.0
    path_lengths: list[float] = []
    losses_db: list[float] = []
    count = 0

    for cell in illumination.cells:
        spatial_area = float(cell.equivalent_area_contribution_m2)
        if spatial_area <= 0.0:
            continue

        travel_time = float(cell.one_way_travel_time_seconds)
        temporal_power = _autocorrelation_power_at_lag(
            autocorrelation,
            2.0 * (travel_time - reference_time),
        )
        if temporal_power <= 0.0:
            continue

        incidence = float(cell.incidence_angle_from_normal_rad)
        strength_db = scattering_strength_at_incidence(scattering_table, incidence)
        path_length = float(cell.acoustic_path_length_m)
        loss = reciprocal_transmission_loss(
            one_way_path_length_m=path_length,
            model=propagation_loss_model,
        )
        propagation_power_ratio = float(loss.two_way_amplitude_ratio) ** 2

        linear_sum += (
            (10.0 ** (strength_db / 10.0))
            * spatial_area
            * temporal_power
            * propagation_power_ratio
        )
        path_lengths.append(path_length)
        losses_db.append(float(loss.two_way_total_loss_db))
        count += 1

    if linear_sum <= 0.0 or not path_lengths:
        raise ValueError("propagation-weighted refracted integration has no positive contribution")

    received_db = 10.0 * log10(linear_sum)
    return RefractedPropagationWeightedReturn(
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=fs,
        contributing_cell_count=count,
        minimum_one_way_path_length_m=min(path_lengths),
        maximum_one_way_path_length_m=max(path_lengths),
        minimum_two_way_transmission_loss_db=min(losses_db),
        maximum_two_way_transmission_loss_db=max(losses_db),
        received_power_relative_db=received_db,
        received_power_ratio=linear_sum,
        received_amplitude_ratio=linear_sum ** 0.5,
        autocorrelation=autocorrelation,
    )

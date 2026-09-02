"""Reusable scalar metrics derived from canonical waveform responses."""

from __future__ import annotations

from math import isfinite

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .wave_kinematics import monostatic_two_way_range_offset
from .waveform import WaveformAutocorrelation


class AutocorrelationPowerFwhm(BaseModel):
    """FWHM of normalized autocorrelation power.

    Half-power crossings are linearly interpolated between the two adjacent lag
    samples that bracket normalized power = 0.5 on each side of the dominant
    peak. This is therefore a metric of the sampled canonical response, not an
    ideal-bandwidth approximation.
    """

    model_config = ConfigDict(frozen=True)

    left_half_power_lag_seconds: FiniteFloat
    right_half_power_lag_seconds: FiniteFloat
    temporal_width_seconds: FiniteFloat = Field(gt=0.0)
    equivalent_two_way_range_width_m: FiniteFloat | None = Field(default=None, gt=0.0)


def _interpolated_crossing(x0: float, y0: float, x1: float, y1: float) -> float:
    if y1 == y0:
        return 0.5 * (x0 + x1)
    fraction = (0.5 - y0) / (y1 - y0)
    return x0 + fraction * (x1 - x0)


def autocorrelation_power_fwhm(
    response: WaveformAutocorrelation,
    *,
    sound_speed_mps: float | None = None,
) -> AutocorrelationPowerFwhm:
    """Measure full width at half maximum of normalized autocorrelation power."""

    lag = np.asarray(response.lag_seconds, dtype=float)
    power = np.asarray(response.normalized_power, dtype=float)
    if lag.ndim != 1 or power.ndim != 1 or lag.size != power.size or lag.size < 3:
        raise ValueError("autocorrelation response must contain aligned one-dimensional samples")
    if not np.all(np.isfinite(lag)) or not np.all(np.isfinite(power)):
        raise ValueError("autocorrelation response must be finite")

    peak = int(np.argmax(power))
    if power[peak] < 0.5:
        raise ValueError("autocorrelation peak must reach half power")

    left_index = peak
    while left_index > 0 and power[left_index] >= 0.5:
        left_index -= 1
    right_index = peak
    while right_index < power.size - 1 and power[right_index] >= 0.5:
        right_index += 1
    if left_index == 0 and power[left_index] >= 0.5:
        raise ValueError("left half-power crossing is outside sampled lag support")
    if right_index == power.size - 1 and power[right_index] >= 0.5:
        raise ValueError("right half-power crossing is outside sampled lag support")

    left = _interpolated_crossing(
        lag[left_index], power[left_index], lag[left_index + 1], power[left_index + 1]
    )
    right = _interpolated_crossing(
        lag[right_index - 1], power[right_index - 1], lag[right_index], power[right_index]
    )
    width = right - left
    if not isfinite(width) or width <= 0.0:
        raise ValueError("autocorrelation FWHM must be finite and positive")

    range_width = None
    if sound_speed_mps is not None:
        range_width = monostatic_two_way_range_offset(
            lag_seconds=width,
            sound_speed_mps=sound_speed_mps,
        )

    return AutocorrelationPowerFwhm(
        left_half_power_lag_seconds=left,
        right_half_power_lag_seconds=right,
        temporal_width_seconds=width,
        equivalent_two_way_range_width_m=range_width,
    )

"""Reusable scalar metrics derived from canonical waveform responses."""

from __future__ import annotations

from math import isfinite
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .wave_kinematics import monostatic_two_way_range_offset
from .waveform import ContinuousWavePulse, LinearFMPulse, WaveformAutocorrelation, WaveformPulse


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


class D2WaveformReferenceMetrics(BaseModel):
    """Authoritative PED-D2 ideal resolution and normalized pulse-energy reference."""

    model_config = ConfigDict(frozen=True)

    ideal_range_resolution_m: FiniteFloat = Field(gt=0.0)
    range_resolution_basis: Literal["cw_pulse_duration", "lfm_swept_bandwidth"]
    range_resolution_kind: Literal["ideal_analytical_reference"] = "ideal_analytical_reference"
    relative_energy: FiniteFloat = Field(gt=0.0)
    relative_energy_reference_duration_ms: FiniteFloat = Field(gt=0.0)
    relative_energy_kind: Literal["normalized_waveform_energy_proxy"] = (
        "normalized_waveform_energy_proxy"
    )
    sound_speed_mps: FiniteFloat = Field(gt=0.0)


def d2_waveform_reference_metrics(
    pulse: WaveformPulse,
    *,
    sound_speed_mps: float = 1500.0,
    reference_duration_seconds: float = 1e-3,
) -> D2WaveformReferenceMetrics:
    """Return the scientific PED-D2 range-resolution and relative-energy references.

    The energy ratio uses the analytic integral of the configured unit-amplitude
    envelope squared. The common carrier-average factor of one half cancels against
    the rectangular reference pulse, preserving the contract's normalized real-
    passband energy comparison without tying the result to a display sampling rate.
    """

    if sound_speed_mps <= 0.0:
        raise ValueError("sound_speed_mps must be positive")
    if reference_duration_seconds <= 0.0:
        raise ValueError("reference_duration_seconds must be positive")

    duration = float(pulse.duration_seconds)
    if isinstance(pulse, ContinuousWavePulse):
        range_resolution = float(sound_speed_mps) * duration / 2.0
        basis: Literal["cw_pulse_duration", "lfm_swept_bandwidth"] = "cw_pulse_duration"
    elif isinstance(pulse, LinearFMPulse):
        range_resolution = float(sound_speed_mps) / (2.0 * float(pulse.bandwidth_hz))
        basis = "lfm_swept_bandwidth"
    else:  # pragma: no cover - WaveformPulse exhaustiveness guard
        raise TypeError(f"unsupported pulse type: {type(pulse)!r}")

    envelope_energy_factor = 1.0
    if pulse.envelope_model == "tukey" and float(pulse.tukey_alpha) > 0.0:
        envelope_energy_factor = 1.0 - 5.0 * float(pulse.tukey_alpha) / 8.0
    relative_energy = duration * envelope_energy_factor / float(reference_duration_seconds)

    return D2WaveformReferenceMetrics(
        ideal_range_resolution_m=range_resolution,
        range_resolution_basis=basis,
        relative_energy=relative_energy,
        relative_energy_reference_duration_ms=float(reference_duration_seconds) * 1e3,
        sound_speed_mps=float(sound_speed_mps),
    )


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

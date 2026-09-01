"""Analytic transmit-waveform primitives for HydroSIM.

The waveform layer keeps the continuous scientific definition separate from its
numerical realizations. Complex baseband remains the processing representation
used by matched filtering, while passband sampling is exposed explicitly for
scientific/didactic display. No projector transfer function, electronics, noise,
source level, propagation, or calibrated receive amplitude is introduced here.
"""

from __future__ import annotations

from math import pi
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .numerical_resolution import SamplingAdequacy, assess_baseband_sampling


EnvelopeModel = Literal["rectangular", "tukey"]
ChirpDirection = Literal["up", "down"]


class ContinuousWavePulse(BaseModel):
    """Finite-duration continuous-wave pulse."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="cw", min_length=1)
    center_frequency_hz: FiniteFloat = Field(gt=0.0)
    duration_seconds: FiniteFloat = Field(gt=0.0)
    initial_phase_rad: FiniteFloat = 0.0
    envelope_model: EnvelopeModel = "rectangular"
    tukey_alpha: FiniteFloat = Field(default=0.1, ge=0.0, le=1.0)


class LinearFMPulse(BaseModel):
    """Finite-duration symmetric linear-FM pulse around centre frequency."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="lfm", min_length=1)
    center_frequency_hz: FiniteFloat = Field(gt=0.0)
    bandwidth_hz: FiniteFloat = Field(gt=0.0)
    duration_seconds: FiniteFloat = Field(gt=0.0)
    chirp_direction: ChirpDirection = "up"
    initial_phase_rad: FiniteFloat = 0.0
    envelope_model: EnvelopeModel = "rectangular"
    tukey_alpha: FiniteFloat = Field(default=0.1, ge=0.0, le=1.0)

    @property
    def start_frequency_hz(self) -> float:
        half_bandwidth = 0.5 * float(self.bandwidth_hz)
        if self.chirp_direction == "up":
            return float(self.center_frequency_hz) - half_bandwidth
        return float(self.center_frequency_hz) + half_bandwidth

    @property
    def end_frequency_hz(self) -> float:
        half_bandwidth = 0.5 * float(self.bandwidth_hz)
        if self.chirp_direction == "up":
            return float(self.center_frequency_hz) + half_bandwidth
        return float(self.center_frequency_hz) - half_bandwidth

    @property
    def sweep_rate_hz_per_second(self) -> float:
        return (self.end_frequency_hz - self.start_frequency_hz) / float(self.duration_seconds)


WaveformPulse = ContinuousWavePulse | LinearFMPulse


class MatchedFilterSummary(BaseModel):
    """Peak properties of a normalized matched-filter correlation."""

    model_config = ConfigDict(frozen=True)

    peak_index: int = Field(ge=0)
    peak_lag_samples: int
    peak_lag_seconds: FiniteFloat
    normalized_peak_amplitude: FiniteFloat = Field(ge=0.0)


class WaveformAutocorrelation(BaseModel):
    """Normalized matched-filter response of a waveform to delayed copies of itself."""

    model_config = ConfigDict(frozen=True)

    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    lag_seconds: tuple[FiniteFloat, ...]
    normalized_amplitude: tuple[FiniteFloat, ...]
    normalized_power: tuple[FiniteFloat, ...]


def waveform_sampling_adequacy(pulse: WaveformPulse, *, sample_rate_hz: float) -> SamplingAdequacy:
    """Return Nyquist adequacy for the represented complex-baseband pulse."""

    maximum = 0.0 if isinstance(pulse, ContinuousWavePulse) else 0.5 * float(pulse.bandwidth_hz)
    return assess_baseband_sampling(
        sample_rate_hz=sample_rate_hz,
        maximum_absolute_frequency_hz=maximum,
    )


def waveform_passband_sampling_adequacy(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> SamplingAdequacy:
    """Return Nyquist adequacy for a real passband numerical realization."""

    if isinstance(pulse, ContinuousWavePulse):
        maximum = float(pulse.center_frequency_hz)
    else:
        maximum = max(abs(pulse.start_frequency_hz), abs(pulse.end_frequency_hz))
    return assess_baseband_sampling(
        sample_rate_hz=sample_rate_hz,
        maximum_absolute_frequency_hz=maximum,
    )


def _sample_count(duration_seconds: float, sample_rate_hz: float) -> int:
    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    count = int(round(float(duration_seconds) * float(sample_rate_hz)))
    if count < 2:
        raise ValueError("waveform requires at least two samples")
    return count


def _time_samples(pulse: WaveformPulse, sample_rate_hz: float) -> np.ndarray:
    count = _sample_count(float(pulse.duration_seconds), sample_rate_hz)
    return np.arange(count, dtype=float) / float(sample_rate_hz)


def sample_waveform_envelope(pulse: WaveformPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Sample the configured unit-amplitude pulse envelope.

    ``rectangular`` reproduces the previous ideal unit envelope. ``tukey`` is a
    symmetric finite-rise/fall didactic envelope; it is not a projector impulse
    response model.
    """

    count = _sample_count(float(pulse.duration_seconds), sample_rate_hz)
    if pulse.envelope_model == "rectangular" or float(pulse.tukey_alpha) <= 0.0:
        return np.ones(count, dtype=float)

    alpha = float(pulse.tukey_alpha)
    if count == 2:
        return np.zeros(count, dtype=float)

    x = np.arange(count, dtype=float) / float(count - 1)
    window = np.ones(count, dtype=float)
    first = x < alpha / 2.0
    last = x > 1.0 - alpha / 2.0
    window[first] = 0.5 * (1.0 + np.cos(pi * (2.0 * x[first] / alpha - 1.0)))
    window[last] = 0.5 * (
        1.0 + np.cos(pi * (2.0 * x[last] / alpha - 2.0 / alpha + 1.0))
    )
    return window


def sample_waveform_instantaneous_frequency(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> np.ndarray:
    """Sample the physical instantaneous frequency over pulse support."""

    t = _time_samples(pulse, sample_rate_hz)
    if isinstance(pulse, ContinuousWavePulse):
        return np.full(t.size, float(pulse.center_frequency_hz), dtype=float)
    return pulse.start_frequency_hz + float(pulse.sweep_rate_hz_per_second) * t


def sample_cw_baseband(pulse: ContinuousWavePulse, *, sample_rate_hz: float) -> np.ndarray:
    """Return complex baseband samples for a finite CW pulse."""

    envelope = sample_waveform_envelope(pulse, sample_rate_hz=sample_rate_hz)
    phase = float(pulse.initial_phase_rad)
    return envelope.astype(np.complex128) * np.exp(1j * phase)


def sample_lfm_baseband(pulse: LinearFMPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Return complex centred-baseband samples for a signed LFM pulse."""

    adequacy = waveform_sampling_adequacy(pulse, sample_rate_hz=sample_rate_hz)
    if not adequacy.meets_nyquist:
        raise ValueError(
            "sample_rate_hz is below the Nyquist rate for the represented LFM baseband bandwidth"
        )
    t = _time_samples(pulse, sample_rate_hz)
    duration = float(pulse.duration_seconds)
    tau = t - 0.5 * duration
    phase = pi * float(pulse.sweep_rate_hz_per_second) * tau * tau + float(pulse.initial_phase_rad)
    envelope = sample_waveform_envelope(pulse, sample_rate_hz=sample_rate_hz)
    return envelope.astype(np.complex128) * np.exp(1j * phase)


def sample_waveform_baseband(pulse: WaveformPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Sample either supported complex-baseband pulse."""

    if isinstance(pulse, ContinuousWavePulse):
        return sample_cw_baseband(pulse, sample_rate_hz=sample_rate_hz)
    return sample_lfm_baseband(pulse, sample_rate_hz=sample_rate_hz)


def sample_waveform_passband(pulse: WaveformPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Return the real unit-amplitude acoustic/passband waveform realization.

    This numerical trace is intended for scientific/didactic passband display.
    Its sample rate is independent of the lower processing/baseband sample rate.
    """

    adequacy = waveform_passband_sampling_adequacy(pulse, sample_rate_hz=sample_rate_hz)
    if not adequacy.meets_nyquist:
        raise ValueError("sample_rate_hz is below the Nyquist rate for the passband waveform")

    t = _time_samples(pulse, sample_rate_hz)
    envelope = sample_waveform_envelope(pulse, sample_rate_hz=sample_rate_hz)
    if isinstance(pulse, ContinuousWavePulse):
        phase = 2.0 * pi * float(pulse.center_frequency_hz) * t + float(pulse.initial_phase_rad)
    else:
        k = float(pulse.sweep_rate_hz_per_second)
        phase = 2.0 * pi * (pulse.start_frequency_hz * t + 0.5 * k * t * t) + float(
            pulse.initial_phase_rad
        )
    return envelope * np.cos(phase)


def waveform_autocorrelation(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> WaveformAutocorrelation:
    """Return the normalized matched-filter autocorrelation envelope and power."""

    reference = sample_waveform_baseband(pulse, sample_rate_hz=sample_rate_hz)
    raw = np.correlate(reference, reference, mode="full")
    zero_lag_index = reference.size - 1
    peak = float(abs(raw[zero_lag_index]))
    if peak <= 0.0:
        raise ValueError("waveform autocorrelation has zero peak")
    amplitude = np.abs(raw) / peak
    power = amplitude * amplitude
    lag_samples = np.arange(-(reference.size - 1), reference.size, dtype=int)
    lags = lag_samples.astype(float) / float(sample_rate_hz)
    return WaveformAutocorrelation(
        sample_rate_hz=sample_rate_hz,
        lag_seconds=tuple(float(value) for value in lags),
        normalized_amplitude=tuple(float(value) for value in amplitude),
        normalized_power=tuple(float(value) for value in power),
    )


def matched_filter(
    received: np.ndarray,
    reference: np.ndarray,
    *,
    sample_rate_hz: float,
) -> tuple[np.ndarray, MatchedFilterSummary]:
    """Correlate a received analytic signal with a known reference waveform."""

    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    received_array = np.asarray(received, dtype=np.complex128)
    reference_array = np.asarray(reference, dtype=np.complex128)
    if received_array.ndim != 1 or reference_array.ndim != 1:
        raise ValueError("matched_filter expects one-dimensional signals")
    if received_array.size == 0 or reference_array.size == 0:
        raise ValueError("matched_filter signals must not be empty")

    energy = float(np.vdot(reference_array, reference_array).real)
    if energy <= 0.0:
        raise ValueError("reference waveform must have positive energy")

    correlation = np.correlate(received_array, reference_array, mode="full") / energy
    peak_index = int(np.argmax(np.abs(correlation)))
    lag_samples = peak_index - (reference_array.size - 1)
    summary = MatchedFilterSummary(
        peak_index=peak_index,
        peak_lag_samples=lag_samples,
        peak_lag_seconds=lag_samples / float(sample_rate_hz),
        normalized_peak_amplitude=float(abs(correlation[peak_index])),
    )
    return correlation, summary

"""Analytic transmit-waveform primitives for HydroSIM.

The waveform layer is intentionally separate from transducer geometry and sector
steering. It provides deterministic complex analytic/baseband samples suitable
for didactic pulse-compression experiments without introducing electronics,
noise, source level, or calibrated receive amplitude.

Continuous waveform definitions and their discrete numerical realization are kept
separate. Sampling adequacy is checked explicitly for the represented baseband
bandwidth before discrete LFM samples are generated.
"""

from __future__ import annotations

from math import pi

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .numerical_resolution import SamplingAdequacy, assess_baseband_sampling


class ContinuousWavePulse(BaseModel):
    """Finite-duration continuous-wave pulse."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="cw", min_length=1)
    center_frequency_hz: FiniteFloat = Field(gt=0.0)
    duration_seconds: FiniteFloat = Field(gt=0.0)


class LinearFMPulse(BaseModel):
    """Finite-duration linear-FM pulse with symmetric sweep around centre."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="lfm", min_length=1)
    center_frequency_hz: FiniteFloat = Field(gt=0.0)
    bandwidth_hz: FiniteFloat = Field(gt=0.0)
    duration_seconds: FiniteFloat = Field(gt=0.0)

    @property
    def start_frequency_hz(self) -> float:
        return float(self.center_frequency_hz) - 0.5 * float(self.bandwidth_hz)

    @property
    def end_frequency_hz(self) -> float:
        return float(self.center_frequency_hz) + 0.5 * float(self.bandwidth_hz)

    @property
    def sweep_rate_hz_per_second(self) -> float:
        return float(self.bandwidth_hz) / float(self.duration_seconds)


WaveformPulse = ContinuousWavePulse | LinearFMPulse


class MatchedFilterSummary(BaseModel):
    """Peak properties of a normalized matched-filter correlation."""

    model_config = ConfigDict(frozen=True)

    peak_index: int = Field(ge=0)
    peak_lag_samples: int
    peak_lag_seconds: FiniteFloat
    normalized_peak_amplitude: FiniteFloat = Field(ge=0.0)


class WaveformAutocorrelation(BaseModel):
    """Normalized matched-filter response of a waveform to delayed copies of itself.

    ``normalized_amplitude`` is |R_ss(tau)| / R_ss(0). ``normalized_power`` is
    its square. The result is a discrete numerical realization of a continuous
    waveform correlation and therefore records its sample rate explicitly.
    """

    model_config = ConfigDict(frozen=True)

    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    lag_seconds: tuple[FiniteFloat, ...]
    normalized_amplitude: tuple[FiniteFloat, ...]
    normalized_power: tuple[FiniteFloat, ...]


def waveform_sampling_adequacy(pulse: WaveformPulse, *, sample_rate_hz: float) -> SamplingAdequacy:
    """Return the Nyquist diagnostic for the represented complex baseband pulse.

    A baseband CW pulse is constant and therefore has zero represented baseband
    frequency. A symmetric LFM of bandwidth B occupies approximately -B/2..+B/2,
    so the ideal Nyquist condition is ``sample_rate_hz >= B``.
    """

    maximum = 0.0 if isinstance(pulse, ContinuousWavePulse) else 0.5 * float(pulse.bandwidth_hz)
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


def sample_cw_baseband(pulse: ContinuousWavePulse, *, sample_rate_hz: float) -> np.ndarray:
    """Return unit-amplitude complex baseband samples for a CW pulse."""

    count = _sample_count(float(pulse.duration_seconds), sample_rate_hz)
    return np.ones(count, dtype=np.complex128)


def sample_lfm_baseband(pulse: LinearFMPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Return unit-amplitude complex baseband samples for a centred LFM pulse.

    With local time tau measured from pulse centre, the complex baseband phase is

        phi(tau) = pi * k * tau^2,

    where k = bandwidth / duration. The instantaneous baseband frequency is
    k*tau and therefore sweeps from approximately -B/2 to +B/2.
    """

    adequacy = waveform_sampling_adequacy(pulse, sample_rate_hz=sample_rate_hz)
    if not adequacy.meets_nyquist:
        raise ValueError(
            "sample_rate_hz is below the Nyquist rate for the represented LFM baseband bandwidth"
        )
    count = _sample_count(float(pulse.duration_seconds), sample_rate_hz)
    duration = float(pulse.duration_seconds)
    sweep_rate = float(pulse.sweep_rate_hz_per_second)
    t = np.arange(count, dtype=float) / float(sample_rate_hz)
    tau = t - 0.5 * duration
    phase = pi * sweep_rate * tau * tau
    return np.exp(1j * phase)


def sample_waveform_baseband(pulse: WaveformPulse, *, sample_rate_hz: float) -> np.ndarray:
    """Sample either supported analytic/baseband pulse."""

    if isinstance(pulse, ContinuousWavePulse):
        return sample_cw_baseband(pulse, sample_rate_hz=sample_rate_hz)
    return sample_lfm_baseband(pulse, sample_rate_hz=sample_rate_hz)


def waveform_autocorrelation(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> WaveformAutocorrelation:
    """Return the normalized matched-filter autocorrelation envelope and power.

    The result is discrete at the waveform sampling interval. It intentionally
    represents waveform/matched-filter physics only; no receiver bandwidth,
    analogue electronics, sampling jitter, noise or detection threshold is added.
    """

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
    """Correlate a received analytic signal with a known reference waveform.

    The returned correlation is normalized by the reference energy so a perfect,
    unit-amplitude copy has peak amplitude 1. The lag convention follows
    ``numpy.correlate(received, reference, mode='full')``: positive lag means the
    received copy occurs later than the reference origin.
    """

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

"""Prepare waveform and matched-filter state for the Didactic Signal Explorer.

Processing and display sampling are deliberately separate. The processing snapshot
preserves complex-baseband state for matched filtering, while the display trace
exposes passband waveform and physical instantaneous frequency from the same
canonical pulse model. No waveform physics is duplicated in presentation code.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LinearFMPulse,
    WaveformAutocorrelation,
    sample_waveform_baseband,
    sample_waveform_instantaneous_frequency,
    sample_waveform_passband,
    waveform_autocorrelation,
    waveform_passband_sampling_adequacy,
    waveform_sampling_adequacy,
)
from hydrosim.acquisition.numerical_resolution import SamplingAdequacy


WaveformPulse = ContinuousWavePulse | LinearFMPulse


class SignalExplorerSnapshot(BaseModel):
    """Render-ready complex-baseband processing state for one CW or LFM pulse."""

    model_config = ConfigDict(frozen=True)

    pulse: WaveformPulse
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    sampling_adequacy: SamplingAdequacy
    time_seconds: tuple[FiniteFloat, ...]
    baseband_real: tuple[FiniteFloat, ...]
    baseband_imag: tuple[FiniteFloat, ...]
    unwrapped_baseband_phase_rad: tuple[FiniteFloat, ...]
    autocorrelation: WaveformAutocorrelation
    representation: str = "complex_analytic_baseband"


class SignalExplorerDisplayTrace(BaseModel):
    """Passband and instantaneous-frequency state for didactic display."""

    model_config = ConfigDict(frozen=True)

    pulse: WaveformPulse
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    sampling_adequacy: SamplingAdequacy
    time_seconds: tuple[FiniteFloat, ...]
    passband_amplitude: tuple[FiniteFloat, ...]
    instantaneous_frequency_hz: tuple[FiniteFloat, ...]
    representation: str = "real_acoustic_passband"


def prepare_signal_explorer_snapshot(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> SignalExplorerSnapshot:
    """Compose complex-baseband reference calculations into one snapshot."""

    rate = float(sample_rate_hz)
    adequacy = waveform_sampling_adequacy(pulse, sample_rate_hz=rate)
    samples = sample_waveform_baseband(pulse, sample_rate_hz=rate)
    time = np.arange(samples.size, dtype=float) / rate
    phase = np.unwrap(np.angle(samples))
    correlation = waveform_autocorrelation(pulse, sample_rate_hz=rate)

    return SignalExplorerSnapshot(
        pulse=pulse,
        sample_rate_hz=rate,
        sampling_adequacy=adequacy,
        time_seconds=tuple(float(value) for value in time),
        baseband_real=tuple(float(value) for value in samples.real),
        baseband_imag=tuple(float(value) for value in samples.imag),
        unwrapped_baseband_phase_rad=tuple(float(value) for value in phase),
        autocorrelation=correlation,
    )


def prepare_signal_explorer_display_trace(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> SignalExplorerDisplayTrace:
    """Prepare a carrier-resolved passband trace without changing processing rate.

    ``sample_rate_hz`` here is a display/numerical realization rate and must meet
    the passband Nyquist requirement. It is intentionally independent of the
    lower complex-baseband processing rate used by :func:`prepare_signal_explorer_snapshot`.
    """

    rate = float(sample_rate_hz)
    adequacy = waveform_passband_sampling_adequacy(pulse, sample_rate_hz=rate)
    passband = sample_waveform_passband(pulse, sample_rate_hz=rate)
    frequency = sample_waveform_instantaneous_frequency(pulse, sample_rate_hz=rate)
    time = np.arange(passband.size, dtype=float) / rate

    return SignalExplorerDisplayTrace(
        pulse=pulse,
        sample_rate_hz=rate,
        sampling_adequacy=adequacy,
        time_seconds=tuple(float(value) for value in time),
        passband_amplitude=tuple(float(value) for value in passband),
        instantaneous_frequency_hz=tuple(float(value) for value in frequency),
    )

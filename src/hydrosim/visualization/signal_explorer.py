"""Prepare waveform and matched-filter state for the Didactic Signal Explorer.

This module composes existing HydroSIM waveform calculations into a render-ready
snapshot. It adds no acoustic propagation, electronics, noise, or attenuation
physics. The snapshot intentionally exposes complex baseband state; any later
carrier-scale animation is a presentation concern and must not redefine the
waveform model.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LinearFMPulse,
    WaveformAutocorrelation,
    sample_waveform_baseband,
    waveform_autocorrelation,
    waveform_sampling_adequacy,
)
from hydrosim.acquisition.numerical_resolution import SamplingAdequacy


WaveformPulse = ContinuousWavePulse | LinearFMPulse


class SignalExplorerSnapshot(BaseModel):
    """Render-ready deterministic state for one CW or LFM pulse."""

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


def prepare_signal_explorer_snapshot(
    pulse: WaveformPulse,
    *,
    sample_rate_hz: float,
) -> SignalExplorerSnapshot:
    """Compose existing waveform reference calculations into one snapshot.

    The sample-rate adequacy result is exposed rather than hidden so a future UI can
    teach the distinction between the continuous waveform definition and its
    discrete numerical realization. LFM sampling below the represented baseband
    Nyquist rate remains an error in the scientific waveform sampler.
    """

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

import numpy as np
import pytest

from hydrosim.acquisition.waveform import (
    ContinuousWavePulse,
    LinearFMPulse,
    matched_filter,
    sample_cw_baseband,
    sample_lfm_baseband,
)


def test_cw_baseband_is_unit_constant() -> None:
    pulse = ContinuousWavePulse(center_frequency_hz=200_000.0, duration_seconds=0.002)
    samples = sample_cw_baseband(pulse, sample_rate_hz=100_000.0)
    assert samples.size == 200
    assert np.allclose(samples, 1.0 + 0.0j)


def test_lfm_properties_and_constant_envelope() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=300_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.01,
    )
    assert pulse.start_frequency_hz == pytest.approx(290_000.0)
    assert pulse.end_frequency_hz == pytest.approx(310_000.0)
    assert pulse.sweep_rate_hz_per_second == pytest.approx(2_000_000.0)

    samples = sample_lfm_baseband(pulse, sample_rate_hz=100_000.0)
    assert samples.size == 1000
    assert np.allclose(np.abs(samples), 1.0)


def test_matched_filter_recovers_known_sample_delay() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=200_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.005,
    )
    sample_rate = 100_000.0
    reference = sample_lfm_baseband(pulse, sample_rate_hz=sample_rate)
    delay_samples = 137
    received = np.concatenate(
        [np.zeros(delay_samples, dtype=np.complex128), reference]
    )

    _, summary = matched_filter(received, reference, sample_rate_hz=sample_rate)

    assert summary.peak_lag_samples == delay_samples
    assert summary.peak_lag_seconds == pytest.approx(delay_samples / sample_rate)
    assert summary.normalized_peak_amplitude == pytest.approx(1.0)

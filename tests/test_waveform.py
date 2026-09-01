import numpy as np
import pytest

from hydrosim.acquisition.waveform import (
    ContinuousWavePulse,
    LinearFMPulse,
    matched_filter,
    sample_cw_baseband,
    sample_lfm_baseband,
    sample_waveform_envelope,
    sample_waveform_instantaneous_frequency,
    sample_waveform_passband,
    waveform_autocorrelation,
    waveform_sampling_adequacy,
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


def test_down_lfm_reverses_signed_sweep_without_negative_bandwidth() -> None:
    up = LinearFMPulse(
        center_frequency_hz=300_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.01,
        chirp_direction="up",
    )
    down = up.model_copy(update={"chirp_direction": "down"})

    assert up.bandwidth_hz == down.bandwidth_hz == 20_000.0
    assert down.start_frequency_hz == pytest.approx(up.end_frequency_hz)
    assert down.end_frequency_hz == pytest.approx(up.start_frequency_hz)
    assert down.sweep_rate_hz_per_second == pytest.approx(-up.sweep_rate_hz_per_second)
    assert (down.start_frequency_hz + down.end_frequency_hz) / 2.0 == pytest.approx(
        down.center_frequency_hz
    )
    assert abs(down.end_frequency_hz - down.start_frequency_hz) == pytest.approx(
        down.bandwidth_hz
    )


def test_instantaneous_frequency_is_constant_for_cw_and_signed_for_lfm() -> None:
    cw = ContinuousWavePulse(center_frequency_hz=200_000.0, duration_seconds=0.001)
    cw_frequency = sample_waveform_instantaneous_frequency(cw, sample_rate_hz=10_000.0)
    assert np.allclose(cw_frequency, 200_000.0)

    up = LinearFMPulse(
        center_frequency_hz=200_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.001,
        chirp_direction="up",
    )
    down = up.model_copy(update={"chirp_direction": "down"})
    up_frequency = sample_waveform_instantaneous_frequency(up, sample_rate_hz=100_000.0)
    down_frequency = sample_waveform_instantaneous_frequency(down, sample_rate_hz=100_000.0)

    assert up_frequency[0] == pytest.approx(up.start_frequency_hz)
    assert down_frequency[0] == pytest.approx(down.start_frequency_hz)
    assert np.all(np.diff(up_frequency) > 0.0)
    assert np.all(np.diff(down_frequency) < 0.0)


def test_tukey_envelope_has_symmetric_zero_endpoints() -> None:
    pulse = ContinuousWavePulse(
        center_frequency_hz=100_000.0,
        duration_seconds=0.002,
        envelope_model="tukey",
        tukey_alpha=0.1,
    )
    envelope = sample_waveform_envelope(pulse, sample_rate_hz=100_000.0)

    assert envelope[0] == pytest.approx(0.0)
    assert envelope[-1] == pytest.approx(0.0)
    assert np.allclose(envelope, envelope[::-1])
    assert np.max(envelope) == pytest.approx(1.0)


def test_passband_cw_oscillates_and_requires_carrier_rate() -> None:
    pulse = ContinuousWavePulse(center_frequency_hz=100_000.0, duration_seconds=0.001)
    samples = sample_waveform_passband(pulse, sample_rate_hz=1_000_000.0)
    assert not np.allclose(samples, samples[0])
    assert np.max(samples) <= 1.0
    assert np.min(samples) >= -1.0

    with pytest.raises(ValueError, match="passband waveform"):
        sample_waveform_passband(pulse, sample_rate_hz=100_000.0)


def test_lfm_sampling_adequacy_uses_complex_baseband_bandwidth() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=300_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.01,
    )
    adequate = waveform_sampling_adequacy(pulse, sample_rate_hz=100_000.0)
    assert adequate.maximum_absolute_frequency_hz == pytest.approx(10_000.0)
    assert adequate.meets_nyquist is True
    assert adequate.nyquist_ratio == pytest.approx(5.0)

    with pytest.raises(ValueError, match="below the Nyquist rate"):
        sample_lfm_baseband(pulse, sample_rate_hz=10_000.0)


def test_tapered_baseband_and_self_correlation_preserve_zero_lag_peak() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=200_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.005,
        envelope_model="tukey",
        tukey_alpha=0.1,
    )
    samples = sample_lfm_baseband(pulse, sample_rate_hz=100_000.0)
    assert abs(samples[0]) == pytest.approx(0.0)
    assert abs(samples[-1]) == pytest.approx(0.0)

    correlation = waveform_autocorrelation(pulse, sample_rate_hz=100_000.0)
    peak_index = int(np.argmax(correlation.normalized_amplitude))
    assert correlation.lag_seconds[peak_index] == pytest.approx(0.0)
    assert correlation.normalized_amplitude[peak_index] == pytest.approx(1.0)


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

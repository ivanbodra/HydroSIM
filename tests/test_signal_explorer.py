from __future__ import annotations

import math

import pytest

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import prepare_signal_explorer_snapshot


def test_cw_signal_explorer_snapshot_preserves_baseband_reference() -> None:
    pulse = ContinuousWavePulse(center_frequency_hz=100_000.0, duration_seconds=0.001)

    snapshot = prepare_signal_explorer_snapshot(pulse, sample_rate_hz=20_000.0)

    assert snapshot.representation == "complex_analytic_baseband"
    assert snapshot.sampling_adequacy.meets_nyquist
    assert snapshot.sampling_adequacy.nyquist_ratio is None
    assert len(snapshot.time_seconds) == 20
    assert snapshot.baseband_real == pytest.approx((1.0,) * 20)
    assert snapshot.baseband_imag == pytest.approx((0.0,) * 20)
    assert snapshot.unwrapped_baseband_phase_rad == pytest.approx((0.0,) * 20)
    assert max(snapshot.autocorrelation.normalized_amplitude) == pytest.approx(1.0)


def test_lfm_signal_explorer_snapshot_exposes_phase_and_correlation() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=100_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.001,
    )

    snapshot = prepare_signal_explorer_snapshot(pulse, sample_rate_hz=80_000.0)

    assert snapshot.sampling_adequacy.meets_nyquist
    assert len(snapshot.time_seconds) == 80
    assert len(snapshot.baseband_real) == len(snapshot.time_seconds)
    assert len(snapshot.baseband_imag) == len(snapshot.time_seconds)
    assert len(snapshot.unwrapped_baseband_phase_rad) == len(snapshot.time_seconds)
    assert not math.isclose(
        snapshot.unwrapped_baseband_phase_rad[0],
        snapshot.unwrapped_baseband_phase_rad[len(snapshot.unwrapped_baseband_phase_rad) // 2],
        abs_tol=1e-12,
    )
    assert len(snapshot.autocorrelation.lag_seconds) == 2 * len(snapshot.time_seconds) - 1
    assert max(snapshot.autocorrelation.normalized_amplitude) == pytest.approx(1.0)


def test_signal_explorer_retains_waveform_sampling_guard() -> None:
    pulse = LinearFMPulse(
        center_frequency_hz=100_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.001,
    )

    with pytest.raises(ValueError, match="below the Nyquist rate"):
        prepare_signal_explorer_snapshot(pulse, sample_rate_hz=10_000.0)

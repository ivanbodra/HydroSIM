import numpy as np
import pytest

from hydrosim.acquisition import detect_bottom_from_matched_filter


def test_bottom_detection_recovers_arrival_and_twtt() -> None:
    sample_rate = 100_000.0
    reference_count = 20
    arrival_samples = 240
    tx_delay_samples = 40

    correlation = np.zeros(arrival_samples + reference_count + 5, dtype=np.complex128)
    peak_index = arrival_samples + reference_count - 1
    correlation[peak_index] = 1.0 + 0.0j

    detection = detect_bottom_from_matched_filter(
        correlation,
        reference_sample_count=reference_count,
        sample_rate_hz=sample_rate,
        tx_delay_seconds=tx_delay_samples / sample_rate,
    )

    assert detection.detection_method == "amplitude_peak"
    assert detection.peak_lag_samples == arrival_samples
    assert detection.arrival_offset_seconds == pytest.approx(arrival_samples / sample_rate)
    assert detection.twtt_seconds == pytest.approx((arrival_samples - tx_delay_samples) / sample_rate)
    assert detection.normalized_amplitude == pytest.approx(1.0)


def test_bottom_detection_rejects_arrival_before_transmit_epoch() -> None:
    sample_rate = 10_000.0
    reference_count = 10
    arrival_samples = 5
    correlation = np.zeros(30, dtype=np.complex128)
    correlation[arrival_samples + reference_count - 1] = 1.0

    with pytest.raises(ValueError, match="precedes the sector transmit epoch"):
        detect_bottom_from_matched_filter(
            correlation,
            reference_sample_count=reference_count,
            sample_rate_hz=sample_rate,
            tx_delay_seconds=0.01,
        )

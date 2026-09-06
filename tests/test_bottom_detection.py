import numpy as np
import pytest

from hydrosim.acquisition import detect_bottom_from_matched_filter
from hydrosim.acquisition.bottom_detection import detect_bottom_candidates_from_matched_filter


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


def test_candidate_detector_threshold_and_multiple_retention_are_deterministic() -> None:
    correlation = np.asarray((0.0, 1.0, 0.2, 0.6, 0.1, 0.6, 0.0), dtype=np.complex128)

    single = detect_bottom_candidates_from_matched_filter(
        correlation,
        reference_sample_count=1,
        sample_rate_hz=1000.0,
        threshold=0.5,
        multiple_detection=False,
    )
    multiple = detect_bottom_candidates_from_matched_filter(
        correlation,
        reference_sample_count=1,
        sample_rate_hz=1000.0,
        threshold=0.5,
        multiple_detection=True,
    )

    assert [item.peak_lag_samples for item in single] == [1]
    assert [item.peak_lag_samples for item in multiple] == [1, 3, 5]
    assert [item.normalized_amplitude for item in multiple] == pytest.approx([1.0, 0.6, 0.6])


def test_candidate_detector_uses_one_representative_for_flat_plateau() -> None:
    correlation = np.asarray((0.0, 0.8, 0.8, 0.8, 0.1), dtype=np.complex128)

    detections = detect_bottom_candidates_from_matched_filter(
        correlation,
        reference_sample_count=1,
        sample_rate_hz=1000.0,
        threshold=0.5,
        multiple_detection=True,
    )

    assert len(detections) == 1
    assert detections[0].peak_lag_samples == 1


def test_candidate_detector_all_zero_response_has_no_detection() -> None:
    detections = detect_bottom_candidates_from_matched_filter(
        np.zeros(8, dtype=np.complex128),
        reference_sample_count=1,
        sample_rate_hz=1000.0,
        threshold=0.0,
        multiple_detection=True,
    )

    assert detections == ()

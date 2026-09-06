import pytest

from hydrosim.app.bottom_detection_api import (
    D9BottomDetectionRequest,
    prepare_d9_bottom_detection_response,
)


def test_d9_adapter_delegates_peak_detection_and_converts_units() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 0.0, 0.2, 0.5, 0.1, 0.0),
            correlation_imag=(0.0, 0.0, 0.0, 0.5, 0.0, 0.0),
            reference_sample_count=2,
            sample_rate_hz=1000.0,
            tx_delay_ms=1.0,
            parent_beam_index=4,
            steering_across_track_angle_deg=30.0,
        )
    )

    assert response.status == "detected"
    assert len(response.candidates) == 1
    assert response.selected_detection == response.candidates[0]
    detection = response.selected_detection
    assert detection is not None
    assert detection.detection_method == "amplitude_peak"
    assert detection.peak_index == 3
    assert detection.peak_lag_samples == 2
    assert detection.arrival_offset_ms == pytest.approx(2.0)
    assert detection.tx_delay_ms == pytest.approx(1.0)
    assert detection.twtt_ms == pytest.approx(1.0)
    assert detection.detected_across_track_angle_deg == pytest.approx(30.0)
    assert detection.normalized_amplitude == pytest.approx(1.0)
    assert response.correlation.lag_us == pytest.approx(
        (-1000.0, 0.0, 1000.0, 2000.0, 3000.0, 4000.0)
    )


def test_d9_detection_window_restricts_peak_search_without_changing_trace() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 0.1, 0.9, 0.2, 0.7, 0.1),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            detection_window_start_ms=3.0,
            detection_window_end_ms=5.0,
        )
    )

    detection = response.selected_detection
    assert detection is not None
    assert detection.peak_index == 4
    assert detection.peak_lag_samples == 4
    assert detection.arrival_offset_ms == pytest.approx(4.0)
    assert response.correlation.magnitude == pytest.approx((0.0, 0.1, 0.9, 0.2, 0.7, 0.1))
    assert response.metadata["detection_window_start_ms"] == pytest.approx(3.0)
    assert response.metadata["detection_window_end_ms"] == pytest.approx(5.0)


def test_d9_detection_window_rejects_invalid_or_empty_range() -> None:
    with pytest.raises(ValueError, match="greater than or equal"):
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            detection_window_start_ms=2.0,
            detection_window_end_ms=1.0,
        )

    with pytest.raises(ValueError, match="does not include any"):
        prepare_d9_bottom_detection_response(
            D9BottomDetectionRequest(
                correlation_real=(0.0, 1.0),
                reference_sample_count=1,
                sample_rate_hz=1000.0,
                detection_window_start_ms=10.0,
                detection_window_end_ms=20.0,
            )
        )


def test_d9_threshold_and_multiple_mode_return_render_ready_comparison() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0, 0.1, 0.65, 0.1, 0.4, 0.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            threshold=0.5,
            multiple_detection=True,
        )
    )

    assert [item.peak_lag_samples for item in response.eligible_candidates] == [1, 3]
    assert [item.peak_lag_samples for item in response.retained_detections] == [1, 3]
    assert response.comparison.eligible_candidate_count == 2
    assert response.comparison.single_detection_count == 1
    assert response.comparison.multiple_detection_count == 2
    assert response.comparison.retained_detection_count == 2
    assert response.comparison.detection_separation_samples == (2,)
    assert response.comparison.detection_separation_ms == pytest.approx((2.0,))

    single = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0, 0.1, 0.65, 0.1, 0.4, 0.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            threshold=0.5,
            multiple_detection=False,
        )
    )
    assert len(single.retained_detections) == 1
    assert single.comparison.multiple_detection_count == 2


def test_d9_truth_classification_reports_true_false_and_missed() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0, 0.1, 0.7, 0.1, 0.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            threshold=0.5,
            multiple_detection=True,
            truth_echo_lag_samples=(1, 5),
            truth_match_tolerance_samples=0,
        )
    )

    assert [item.classification for item in response.classifications] == [
        "true_detection",
        "false_detection",
        "missed_detection",
    ]
    assert response.classifications[0].detection_lag_samples == 1
    assert response.classifications[0].truth_lag_samples == 1
    assert response.classifications[1].detection_lag_samples == 3
    assert response.classifications[2].truth_lag_samples == 5


def test_d9_does_not_emit_false_missed_labels_without_truth_reference() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0, 0.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
        )
    )
    assert response.classifications == ()


def test_d9_adapter_reports_phase_detector_as_explicitly_unsupported() -> None:
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 1.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            detection_method="phase_zero_crossing",
        )
    )

    assert response.status == "unsupported"
    assert response.candidates == ()
    assert response.selected_detection is None
    assert "no canonical matched-filter detector" in (response.unsupported_reason or "")


def test_d9_adapter_rejects_mismatched_complex_sample_lengths() -> None:
    with pytest.raises(ValueError, match="same sample count"):
        prepare_d9_bottom_detection_response(
            D9BottomDetectionRequest(
                correlation_real=(0.0, 1.0),
                correlation_imag=(0.0,),
                reference_sample_count=1,
                sample_rate_hz=1000.0,
            )
        )

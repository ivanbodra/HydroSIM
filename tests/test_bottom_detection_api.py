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
    assert detection.normalized_amplitude == pytest.approx(2**-0.5)
    assert response.correlation.lag_us == pytest.approx((-1000.0, 0.0, 1000.0, 2000.0, 3000.0, 4000.0))


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

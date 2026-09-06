"""Application adapter for the PED-D9 bottom-detection learner slice.

Scientific detection remains owned by ``hydrosim.acquisition.bottom_detection``.
This module validates/serializes learner controls, Truth-relative didactic
classification, and render-ready comparison quantities for the production React
application.
"""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition import DetectionMethod
from hydrosim.acquisition.bottom_detection import detect_bottom_candidates_from_matched_filter


class D9BottomDetectionRequest(BaseModel):
    """Configured matched-filter samples and detector controls for PED-D9."""

    model_config = ConfigDict(extra="forbid")

    correlation_real: tuple[float, ...] = Field(min_length=1, max_length=16384)
    correlation_imag: tuple[float, ...] | None = Field(default=None, max_length=16384)
    reference_sample_count: int = Field(ge=1)
    sample_rate_hz: float = Field(gt=0.0)
    tx_delay_ms: float = Field(default=0.0, ge=0.0)
    parent_beam_index: int | None = Field(default=None, ge=0)
    steering_across_track_angle_deg: float | None = None
    detection_method: DetectionMethod = "amplitude_peak"
    detection_window_start_ms: float | None = None
    detection_window_end_ms: float | None = None
    threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    multiple_detection: bool = False
    truth_echo_lag_samples: tuple[int, ...] | None = None
    truth_match_tolerance_samples: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_detection_window(self) -> "D9BottomDetectionRequest":
        if (
            self.detection_window_start_ms is not None
            and self.detection_window_end_ms is not None
            and self.detection_window_end_ms < self.detection_window_start_ms
        ):
            raise ValueError(
                "detection_window_end_ms must be greater than or equal to detection_window_start_ms"
            )
        if self.truth_echo_lag_samples is not None and any(
            lag < 0 for lag in self.truth_echo_lag_samples
        ):
            raise ValueError("truth_echo_lag_samples must contain non-negative arrival lags")
        return self


class D9CorrelationTrace(BaseModel):
    """Render-ready matched-filter magnitude using acoustic lag as x-axis."""

    model_config = ConfigDict(frozen=True)

    lag_us: tuple[float, ...]
    magnitude: tuple[float, ...]
    normalized_magnitude: tuple[float, ...]


class D9DetectionCandidate(BaseModel):
    """Render-ready serialization of one canonical ``BottomDetection``."""

    model_config = ConfigDict(frozen=True)

    detection_method: DetectionMethod
    peak_index: int | None
    peak_lag_samples: int | None
    arrival_offset_ms: float
    tx_delay_ms: float
    twtt_ms: float
    detected_across_track_angle_deg: float | None
    normalized_amplitude: float | None
    quality: float | None


class D9DetectionClassification(BaseModel):
    """Truth-relative didactic classification; never a detection probability."""

    model_config = ConfigDict(frozen=True)

    classification: Literal["true_detection", "false_detection", "missed_detection"]
    detection_lag_samples: int | None
    truth_lag_samples: int | None


class D9DetectionComparison(BaseModel):
    """Render-ready single-versus-multiple retention summary."""

    model_config = ConfigDict(frozen=True)

    eligible_candidate_count: int = Field(ge=0)
    single_detection_count: int = Field(ge=0)
    multiple_detection_count: int = Field(ge=0)
    retained_detection_count: int = Field(ge=0)
    detection_separation_samples: tuple[int, ...]
    detection_separation_ms: tuple[float, ...]


class D9BottomDetectionResponse(BaseModel):
    """Stable production contract for PED-D9."""

    model_config = ConfigDict(frozen=True)

    status: Literal["detected", "unsupported"]
    correlation: D9CorrelationTrace
    candidates: tuple[D9DetectionCandidate, ...]
    eligible_candidates: tuple[D9DetectionCandidate, ...]
    retained_detections: tuple[D9DetectionCandidate, ...]
    selected_detection: D9DetectionCandidate | None
    classifications: tuple[D9DetectionClassification, ...]
    comparison: D9DetectionComparison
    unsupported_reason: str | None = None
    metadata: dict[str, float | int | str | bool]


def _correlation_from_request(request: D9BottomDetectionRequest) -> np.ndarray:
    real = np.asarray(request.correlation_real, dtype=np.float64)
    if request.correlation_imag is None:
        imag = np.zeros(real.shape, dtype=np.float64)
    else:
        imag = np.asarray(request.correlation_imag, dtype=np.float64)
        if imag.shape != real.shape:
            raise ValueError("correlation_imag must have the same sample count as correlation_real")
    if not np.all(np.isfinite(real)) or not np.all(np.isfinite(imag)):
        raise ValueError("correlation samples must be finite")
    return real.astype(np.complex128) + 1j * imag


def _normalized_magnitude(correlation: np.ndarray) -> tuple[float, ...]:
    magnitude = np.abs(correlation)
    maximum = float(np.max(magnitude))
    if maximum <= 0.0:
        return tuple(0.0 for _ in magnitude)
    return tuple(float(value / maximum) for value in magnitude)


def _trace(
    correlation: np.ndarray, *, reference_sample_count: int, sample_rate_hz: float
) -> D9CorrelationTrace:
    lag_samples = np.arange(correlation.size, dtype=np.float64) - (reference_sample_count - 1)
    return D9CorrelationTrace(
        lag_us=tuple(float(value * 1e6 / sample_rate_hz) for value in lag_samples),
        magnitude=tuple(float(value) for value in np.abs(correlation)),
        normalized_magnitude=_normalized_magnitude(correlation),
    )


def _apply_detection_window(
    correlation: np.ndarray,
    *,
    reference_sample_count: int,
    sample_rate_hz: float,
    start_ms: float | None,
    end_ms: float | None,
) -> np.ndarray:
    """Restrict the detector search domain without changing the full render trace."""

    if start_ms is None and end_ms is None:
        return correlation
    lag_ms = (
        np.arange(correlation.size, dtype=np.float64) - (reference_sample_count - 1)
    ) * 1e3 / sample_rate_hz
    mask = np.ones(correlation.size, dtype=bool)
    if start_ms is not None:
        mask &= lag_ms >= start_ms
    if end_ms is not None:
        mask &= lag_ms <= end_ms
    if not np.any(mask):
        raise ValueError("detection window does not include any correlation samples")
    restricted = np.zeros_like(correlation)
    restricted[mask] = correlation[mask]
    return restricted


def _candidate_from_detection(detection) -> D9DetectionCandidate:
    angle_deg = None
    if detection.detected_across_track_angle_rad is not None:
        angle_deg = math.degrees(float(detection.detected_across_track_angle_rad))
    return D9DetectionCandidate(
        detection_method=detection.detection_method,
        peak_index=detection.peak_index,
        peak_lag_samples=detection.peak_lag_samples,
        arrival_offset_ms=float(detection.arrival_offset_seconds) * 1e3,
        tx_delay_ms=float(detection.tx_delay_seconds) * 1e3,
        twtt_ms=float(detection.twtt_seconds) * 1e3,
        detected_across_track_angle_deg=angle_deg,
        normalized_amplitude=detection.normalized_amplitude,
        quality=detection.quality,
    )


def _classify_against_truth(
    detections: tuple[D9DetectionCandidate, ...],
    truth_lags: tuple[int, ...] | None,
    tolerance_samples: int,
) -> tuple[D9DetectionClassification, ...]:
    if truth_lags is None:
        return ()

    detection_lags = tuple(
        int(item.peak_lag_samples)
        for item in detections
        if item.peak_lag_samples is not None
    )
    possible = sorted(
        (
            (abs(detection_lag - truth_lag), detection_lag, truth_lag, detection_index, truth_index)
            for detection_index, detection_lag in enumerate(detection_lags)
            for truth_index, truth_lag in enumerate(truth_lags)
            if abs(detection_lag - truth_lag) <= tolerance_samples
        ),
        key=lambda item: (item[0], item[1], item[2]),
    )
    matched_detections: dict[int, int] = {}
    matched_truth: set[int] = set()
    for _, _, _, detection_index, truth_index in possible:
        if detection_index in matched_detections or truth_index in matched_truth:
            continue
        matched_detections[detection_index] = truth_index
        matched_truth.add(truth_index)

    result: list[D9DetectionClassification] = []
    for detection_index, detection_lag in enumerate(detection_lags):
        truth_index = matched_detections.get(detection_index)
        if truth_index is None:
            result.append(
                D9DetectionClassification(
                    classification="false_detection",
                    detection_lag_samples=detection_lag,
                    truth_lag_samples=None,
                )
            )
        else:
            result.append(
                D9DetectionClassification(
                    classification="true_detection",
                    detection_lag_samples=detection_lag,
                    truth_lag_samples=truth_lags[truth_index],
                )
            )
    for truth_index, truth_lag in enumerate(truth_lags):
        if truth_index not in matched_truth:
            result.append(
                D9DetectionClassification(
                    classification="missed_detection",
                    detection_lag_samples=None,
                    truth_lag_samples=truth_lag,
                )
            )
    return tuple(result)


def _comparison(
    eligible: tuple[D9DetectionCandidate, ...], retained_count: int, sample_rate_hz: float
) -> D9DetectionComparison:
    lags = sorted(
        int(item.peak_lag_samples)
        for item in eligible
        if item.peak_lag_samples is not None
    )
    separations = tuple(lags[index + 1] - lags[index] for index in range(len(lags) - 1))
    return D9DetectionComparison(
        eligible_candidate_count=len(eligible),
        single_detection_count=min(1, len(eligible)),
        multiple_detection_count=len(eligible),
        retained_detection_count=retained_count,
        detection_separation_samples=separations,
        detection_separation_ms=tuple(value * 1e3 / sample_rate_hz for value in separations),
    )


def prepare_d9_bottom_detection_response(
    request: D9BottomDetectionRequest,
) -> D9BottomDetectionResponse:
    """Delegate PED-D9 detection to the authoritative deterministic detector."""

    correlation = _correlation_from_request(request)
    trace = _trace(
        correlation,
        reference_sample_count=request.reference_sample_count,
        sample_rate_hz=request.sample_rate_hz,
    )
    metadata: dict[str, float | int | str | bool] = {
        "reference_sample_count": request.reference_sample_count,
        "sample_rate_hz": request.sample_rate_hz,
        "threshold": request.threshold,
        "multiple_detection": request.multiple_detection,
        "threshold_semantics": "normalized matched-filter magnitude within detection window",
        "candidate_policy": "local maxima; descending normalized magnitude; earlier lag tie-break",
        "state_semantics": "Configured controls; Observed detections; Derived ranking/classification",
    }
    if request.detection_window_start_ms is not None:
        metadata["detection_window_start_ms"] = request.detection_window_start_ms
    if request.detection_window_end_ms is not None:
        metadata["detection_window_end_ms"] = request.detection_window_end_ms

    empty_comparison = _comparison((), 0, request.sample_rate_hz)
    if request.detection_method != "amplitude_peak":
        return D9BottomDetectionResponse(
            status="unsupported",
            correlation=trace,
            candidates=(),
            eligible_candidates=(),
            retained_detections=(),
            selected_detection=None,
            classifications=(),
            comparison=empty_comparison,
            unsupported_reason=(
                "phase_zero_crossing is represented by the Core data model but has no "
                "canonical matched-filter detector in this PED-D9 slice"
            ),
            metadata=metadata,
        )

    steering_rad = None
    if request.steering_across_track_angle_deg is not None:
        steering_rad = math.radians(request.steering_across_track_angle_deg)

    detector_correlation = _apply_detection_window(
        correlation,
        reference_sample_count=request.reference_sample_count,
        sample_rate_hz=request.sample_rate_hz,
        start_ms=request.detection_window_start_ms,
        end_ms=request.detection_window_end_ms,
    )
    detections = detect_bottom_candidates_from_matched_filter(
        detector_correlation,
        reference_sample_count=request.reference_sample_count,
        sample_rate_hz=request.sample_rate_hz,
        threshold=request.threshold,
        multiple_detection=True,
        tx_delay_seconds=request.tx_delay_ms * 1e-3,
        parent_beam_index=request.parent_beam_index,
        steering_across_track_angle_rad=steering_rad,
    )
    eligible = tuple(_candidate_from_detection(item) for item in detections)
    retained = eligible if request.multiple_detection else eligible[:1]
    selected = retained[0] if retained else None
    classifications = _classify_against_truth(
        retained,
        request.truth_echo_lag_samples,
        request.truth_match_tolerance_samples,
    )
    comparison = _comparison(eligible, len(retained), request.sample_rate_hz)
    return D9BottomDetectionResponse(
        status="detected",
        correlation=trace,
        candidates=retained,
        eligible_candidates=eligible,
        retained_detections=retained,
        selected_detection=selected,
        classifications=classifications,
        comparison=comparison,
        metadata=metadata,
    )

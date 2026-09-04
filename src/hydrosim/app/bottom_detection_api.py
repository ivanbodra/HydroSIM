"""Application adapter for the PED-D9 bottom-detection learner slice.

Scientific detection remains owned by ``hydrosim.acquisition.bottom_detection``.
This module only validates/serializes learner controls and converts units for the
production React application.
"""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition import DetectionMethod, detect_bottom_from_matched_filter


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


class D9CorrelationTrace(BaseModel):
    """Render-ready matched-filter magnitude using acoustic lag as x-axis."""

    model_config = ConfigDict(frozen=True)

    lag_us: tuple[float, ...]
    magnitude: tuple[float, ...]


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


class D9BottomDetectionResponse(BaseModel):
    """Stable production contract for PED-D9."""

    model_config = ConfigDict(frozen=True)

    status: Literal["detected", "unsupported"]
    correlation: D9CorrelationTrace
    candidates: tuple[D9DetectionCandidate, ...]
    selected_detection: D9DetectionCandidate | None
    unsupported_reason: str | None = None
    metadata: dict[str, float | int | str]


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


def _trace(
    correlation: np.ndarray, *, reference_sample_count: int, sample_rate_hz: float
) -> D9CorrelationTrace:
    lag_samples = np.arange(correlation.size, dtype=np.float64) - (reference_sample_count - 1)
    return D9CorrelationTrace(
        lag_us=tuple(float(value * 1e6 / sample_rate_hz) for value in lag_samples),
        magnitude=tuple(float(value) for value in np.abs(correlation)),
    )


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


def prepare_d9_bottom_detection_response(
    request: D9BottomDetectionRequest,
) -> D9BottomDetectionResponse:
    """Delegate PED-D9 detection to the canonical amplitude detector."""

    correlation = _correlation_from_request(request)
    trace = _trace(
        correlation,
        reference_sample_count=request.reference_sample_count,
        sample_rate_hz=request.sample_rate_hz,
    )
    metadata: dict[str, float | int | str] = {
        "reference_sample_count": request.reference_sample_count,
        "sample_rate_hz": request.sample_rate_hz,
        "state_semantics": "Configured input; Derived detection",
    }

    if request.detection_method != "amplitude_peak":
        return D9BottomDetectionResponse(
            status="unsupported",
            correlation=trace,
            candidates=(),
            selected_detection=None,
            unsupported_reason=(
                "phase_zero_crossing is represented by the Core data model but has no "
                "canonical matched-filter detector in this PED-D9 slice"
            ),
            metadata=metadata,
        )

    steering_rad = None
    if request.steering_across_track_angle_deg is not None:
        steering_rad = math.radians(request.steering_across_track_angle_deg)

    detection = detect_bottom_from_matched_filter(
        correlation,
        reference_sample_count=request.reference_sample_count,
        sample_rate_hz=request.sample_rate_hz,
        tx_delay_seconds=request.tx_delay_ms * 1e-3,
        parent_beam_index=request.parent_beam_index,
        steering_across_track_angle_rad=steering_rad,
    )
    candidate = _candidate_from_detection(detection)
    return D9BottomDetectionResponse(
        status="detected",
        correlation=trace,
        candidates=(candidate,),
        selected_detection=candidate,
        metadata=metadata,
    )

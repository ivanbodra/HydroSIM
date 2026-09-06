"""Bottom-detection data model and reference amplitude detector.

Beam spacing and detection are deliberately independent. A receive beam may
produce zero, one, or multiple ``BottomDetection`` objects. This permits later
phase-ramp and high-density strategies without assuming one beam equals one
sounding.

The legacy reference detector returns the strongest matched-filter magnitude.
The deterministic candidate detector additionally implements the vendor-neutral
threshold and local-peak retention policy defined for PED-D9.
"""

from __future__ import annotations

from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

DetectionMethod = Literal["amplitude_peak", "phase_zero_crossing"]


class BottomDetection(BaseModel):
    """One timing/angle observation extracted from a receive beam."""

    model_config = ConfigDict(frozen=True)

    parent_beam_index: int | None = Field(default=None, ge=0)
    detection_index: int = Field(default=0, ge=0)
    detection_method: DetectionMethod
    peak_index: int | None = Field(default=None, ge=0)
    peak_lag_samples: int | None = Field(default=None, ge=0)
    arrival_offset_seconds: FiniteFloat = Field(ge=0.0)
    tx_delay_seconds: FiniteFloat = Field(ge=0.0)
    twtt_seconds: FiniteFloat = Field(ge=0.0)
    detected_across_track_angle_rad: FiniteFloat | None = None
    normalized_amplitude: FiniteFloat | None = Field(default=None, ge=0.0)
    quality: FiniteFloat | None = Field(default=None, ge=0.0, le=1.0)


class BeamDetections(BaseModel):
    """All detections associated with one receive beam."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    steering_across_track_angle_rad: FiniteFloat
    detections: tuple[BottomDetection, ...] = ()


def _validate_detector_inputs(
    correlation: np.ndarray,
    *,
    reference_sample_count: int,
    sample_rate_hz: float,
    tx_delay_seconds: float,
) -> np.ndarray:
    values = np.asarray(correlation, dtype=np.complex128)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("correlation must be a non-empty one-dimensional signal")
    if reference_sample_count < 1:
        raise ValueError("reference_sample_count must be positive")
    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if tx_delay_seconds < 0.0:
        raise ValueError("tx_delay_seconds must be non-negative")
    return values


def _plateau_peak_indices(magnitude: np.ndarray) -> tuple[int, ...]:
    """Return one deterministic (earliest) index for each positive local-max plateau."""

    peaks: list[int] = []
    index = 0
    size = int(magnitude.size)
    while index < size:
        end = index
        value = float(magnitude[index])
        while end + 1 < size and float(magnitude[end + 1]) == value:
            end += 1
        left = float(magnitude[index - 1]) if index > 0 else float("-inf")
        right = float(magnitude[end + 1]) if end + 1 < size else float("-inf")
        if value > 0.0 and value >= left and value >= right:
            peaks.append(index)
        index = end + 1
    return tuple(peaks)


def detect_bottom_candidates_from_matched_filter(
    correlation: np.ndarray,
    *,
    reference_sample_count: int,
    sample_rate_hz: float,
    threshold: float = 0.0,
    multiple_detection: bool = False,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
    steering_across_track_angle_rad: float | None = None,
) -> tuple[BottomDetection, ...]:
    """Return deterministic threshold-eligible local maxima for PED-D9.

    The supplied correlation is assumed to have already been restricted to the
    configured detection window. Magnitude is normalized by the strongest sample.
    Candidates are sorted by descending normalized magnitude, then earlier arrival
    lag. Flat maxima emit only their earliest sample. This is a didactic retention
    policy, not a manufacturer bottom-detector model.
    """

    values = _validate_detector_inputs(
        correlation,
        reference_sample_count=reference_sample_count,
        sample_rate_hz=sample_rate_hz,
        tx_delay_seconds=tx_delay_seconds,
    )
    tau = float(threshold)
    if not 0.0 <= tau <= 1.0:
        raise ValueError("threshold must be between 0 and 1")

    magnitude = np.abs(values)
    maximum = float(np.max(magnitude))
    if maximum <= 0.0:
        return ()
    normalized = magnitude / maximum
    tolerance = 0.5 / float(sample_rate_hz)

    eligible: list[tuple[float, int, int]] = []
    for peak_index in _plateau_peak_indices(magnitude):
        lag_samples = peak_index - (reference_sample_count - 1)
        if lag_samples < 0 or float(normalized[peak_index]) < tau:
            continue
        arrival = lag_samples / float(sample_rate_hz)
        if arrival - float(tx_delay_seconds) < -tolerance:
            continue
        eligible.append((-float(normalized[peak_index]), lag_samples, peak_index))

    eligible.sort()
    if not multiple_detection and eligible:
        eligible = eligible[:1]

    detections: list[BottomDetection] = []
    for detection_index, (_, lag_samples, peak_index) in enumerate(eligible):
        arrival = lag_samples / float(sample_rate_hz)
        twtt = arrival - float(tx_delay_seconds)
        detections.append(
            BottomDetection(
                parent_beam_index=parent_beam_index,
                detection_index=detection_index,
                detection_method="amplitude_peak",
                peak_index=peak_index,
                peak_lag_samples=lag_samples,
                arrival_offset_seconds=arrival,
                tx_delay_seconds=tx_delay_seconds,
                twtt_seconds=max(0.0, twtt),
                detected_across_track_angle_rad=steering_across_track_angle_rad,
                normalized_amplitude=float(normalized[peak_index]),
            )
        )
    return tuple(detections)


def detect_bottom_from_matched_filter(
    correlation: np.ndarray,
    *,
    reference_sample_count: int,
    sample_rate_hz: float,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
    steering_across_track_angle_rad: float | None = None,
) -> BottomDetection:
    """Detect the strongest matched-filter magnitude and recover acoustic TWTT."""

    values = _validate_detector_inputs(
        correlation,
        reference_sample_count=reference_sample_count,
        sample_rate_hz=sample_rate_hz,
        tx_delay_seconds=tx_delay_seconds,
    )

    peak_index = int(np.argmax(np.abs(values)))
    lag_samples = peak_index - (reference_sample_count - 1)
    if lag_samples < 0:
        raise ValueError("bottom detector requires a non-negative arrival lag")

    arrival = lag_samples / float(sample_rate_hz)
    twtt = arrival - float(tx_delay_seconds)
    tolerance = 0.5 / float(sample_rate_hz)
    if twtt < -tolerance:
        raise ValueError("detected arrival precedes the sector transmit epoch")

    return BottomDetection(
        parent_beam_index=parent_beam_index,
        detection_method="amplitude_peak",
        peak_index=peak_index,
        peak_lag_samples=lag_samples,
        arrival_offset_seconds=arrival,
        tx_delay_seconds=tx_delay_seconds,
        twtt_seconds=max(0.0, twtt),
        detected_across_track_angle_rad=steering_across_track_angle_rad,
        normalized_amplitude=float(abs(values[peak_index])),
    )

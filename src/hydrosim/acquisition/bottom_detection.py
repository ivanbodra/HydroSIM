"""Bottom-detection data model and reference amplitude detector.

Beam spacing and detection are deliberately independent. A receive beam may
produce zero, one, or multiple ``BottomDetection`` objects. This permits later
phase-ramp and high-density strategies without assuming one beam equals one
sounding.

The current reference detector uses the strongest matched-filter magnitude. It
contains no threshold, noise, sediment response, or proprietary vendor logic.
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

    values = np.asarray(correlation, dtype=np.complex128)
    if values.ndim != 1 or values.size == 0:
        raise ValueError("correlation must be a non-empty one-dimensional signal")
    if reference_sample_count < 1:
        raise ValueError("reference_sample_count must be positive")
    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if tx_delay_seconds < 0.0:
        raise ValueError("tx_delay_seconds must be non-negative")

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

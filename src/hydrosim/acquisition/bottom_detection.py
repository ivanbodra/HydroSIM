"""Deterministic bottom detection from matched-filter output.

This module deliberately starts with the simplest scientifically explicit detector:
the detected bottom time is the lag of the strongest matched-filter magnitude.
No threshold, noise model, amplitude model, sediment response, or proprietary
vendor detector is implied.

The detector separates two quantities that are easy to conflate:

* ``arrival_offset_seconds``: elapsed time from the common ping time to the
  detected return, including any transmit-sector delay;
* ``twtt_seconds``: acoustic two-way travel time measured from the actual sector
  transmit epoch.

Therefore

    TWTT = detected_arrival_offset - tx_delay.

The conversion from TWTT to range is intentionally not performed here because a
single ``c * TWTT / 2`` is not generally valid for refracted propagation. Range
reconstruction belongs to the configured propagation/reconstruction model.
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class BottomDetection(BaseModel):
    """Detected bottom timing from one matched-filtered receive signal."""

    model_config = ConfigDict(frozen=True)

    peak_index: int = Field(ge=0)
    peak_lag_samples: int = Field(ge=0)
    arrival_offset_seconds: FiniteFloat = Field(ge=0.0)
    tx_delay_seconds: FiniteFloat = Field(ge=0.0)
    twtt_seconds: FiniteFloat = Field(ge=0.0)
    normalized_peak_amplitude: FiniteFloat = Field(ge=0.0)
    detection_method: str = Field(default="matched_filter_peak", min_length=1)


def detect_bottom_from_matched_filter(
    correlation: np.ndarray,
    *,
    reference_sample_count: int,
    sample_rate_hz: float,
    tx_delay_seconds: float = 0.0,
) -> BottomDetection:
    """Detect the strongest matched-filter peak and recover acoustic TWTT.

    ``correlation`` must follow the lag convention of
    ``numpy.correlate(received, reference, mode='full')``. Positive lag means the
    received copy occurs after the reference origin.
    """

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
    twtt = max(0.0, twtt)

    return BottomDetection(
        peak_index=peak_index,
        peak_lag_samples=lag_samples,
        arrival_offset_seconds=arrival,
        tx_delay_seconds=tx_delay_seconds,
        twtt_seconds=twtt,
        normalized_peak_amplitude=float(abs(values[peak_index])),
    )

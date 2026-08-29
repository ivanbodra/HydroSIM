"""Reference split-aperture phase-ramp bottom detection.

This module implements the signal-processing part of a phase detector without
assuming any proprietary MBES algorithm. It expects two complex time series from
independently beamformed receive subapertures A and B.

The differential phase is

    dphi(t) = arg(z_A(t) * conj(z_B(t))).

Inside a user-supplied search window, the phase is locally unwrapped and a linear
least-squares fit is made over samples surrounding a sign change. The fitted zero
crossing provides a sub-sample estimate of the return arrival epoch.

Signal generation for the two subapertures is deliberately separate. This module
does not invent bottom reflectivity, backscatter, noise, or vendor-specific
quality logic.
"""

from __future__ import annotations

from math import pi

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .bottom_detection import BottomDetection


class PhaseRampFit(BaseModel):
    """Diagnostics for one local split-aperture phase-ramp fit."""

    model_config = ConfigDict(frozen=True)

    first_sample_index: int = Field(ge=0)
    last_sample_index: int = Field(ge=0)
    sample_count: int = Field(ge=2)
    slope_rad_per_second: FiniteFloat
    intercept_rad: FiniteFloat
    zero_crossing_seconds: FiniteFloat
    rms_residual_rad: FiniteFloat = Field(ge=0.0)


class PhaseDetectionResult(BaseModel):
    """Phase detection plus the local phase-ramp diagnostics used to obtain it."""

    model_config = ConfigDict(frozen=True)

    detection: BottomDetection
    fit: PhaseRampFit


def differential_phase(subaperture_a: np.ndarray, subaperture_b: np.ndarray) -> np.ndarray:
    """Return wrapped A-minus-B phase from two complex subaperture series."""

    a = np.asarray(subaperture_a, dtype=np.complex128)
    b = np.asarray(subaperture_b, dtype=np.complex128)
    if a.ndim != 1 or b.ndim != 1 or a.size == 0 or b.size == 0:
        raise ValueError("subaperture signals must be non-empty one-dimensional arrays")
    if a.size != b.size:
        raise ValueError("subaperture signals must have equal sample counts")
    return np.angle(a * np.conjugate(b))


def detect_bottom_from_phase_ramp(
    subaperture_a: np.ndarray,
    subaperture_b: np.ndarray,
    *,
    sample_rate_hz: float,
    search_start_sample: int,
    search_end_sample: int,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
    steering_across_track_angle_rad: float | None = None,
    fit_half_width_samples: int = 2,
) -> PhaseDetectionResult:
    """Estimate bottom arrival from a split-aperture differential-phase zero crossing.

    The strongest valid sign change in the search window is chosen by maximizing
    the local product ``|z_A| |z_B|``. A linear phase fit around that crossing
    yields a sub-sample zero-crossing time.
    """

    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if tx_delay_seconds < 0.0:
        raise ValueError("tx_delay_seconds must be non-negative")
    if fit_half_width_samples < 1:
        raise ValueError("fit_half_width_samples must be at least one")

    a = np.asarray(subaperture_a, dtype=np.complex128)
    b = np.asarray(subaperture_b, dtype=np.complex128)
    phase = differential_phase(a, b)
    n = phase.size
    if search_start_sample < 0 or search_end_sample >= n or search_end_sample <= search_start_sample:
        raise ValueError("invalid phase-detection search window")

    local = np.unwrap(phase[search_start_sample : search_end_sample + 1])
    candidates: list[tuple[float, int]] = []
    for j in range(local.size - 1):
        p0 = float(local[j])
        p1 = float(local[j + 1])
        if p0 == 0.0 or p1 == 0.0 or p0 * p1 < 0.0:
            i = search_start_sample + j
            strength = float(abs(a[i]) * abs(b[i]) + abs(a[i + 1]) * abs(b[i + 1]))
            candidates.append((strength, i))
    if not candidates:
        raise ValueError("no differential-phase zero crossing in search window")

    _, crossing_index = max(candidates, key=lambda item: item[0])
    first = max(search_start_sample, crossing_index - fit_half_width_samples)
    last = min(search_end_sample, crossing_index + 1 + fit_half_width_samples)
    indices = np.arange(first, last + 1, dtype=float)
    times = indices / float(sample_rate_hz)
    phases = np.unwrap(phase[first : last + 1])

    slope, intercept = np.polyfit(times, phases, 1)
    if abs(float(slope)) <= 1e-15:
        raise ValueError("phase-ramp fit has effectively zero slope")
    zero = -float(intercept) / float(slope)
    if zero < times[0] or zero > times[-1]:
        raise ValueError("fitted phase zero crossing lies outside the fit interval")

    fitted = slope * times + intercept
    rms = float(np.sqrt(np.mean((phases - fitted) ** 2)))
    arrival = zero
    twtt = arrival - float(tx_delay_seconds)
    tolerance = 0.5 / float(sample_rate_hz)
    if twtt < -tolerance:
        raise ValueError("phase-detected arrival precedes the sector transmit epoch")

    midpoint = 0.5 * (first + last)
    representative_index = int(round(midpoint))
    normalized_amplitude = float(
        np.sqrt(abs(a[representative_index]) * abs(b[representative_index]))
    )
    # A simple deterministic fit-quality indicator: 1 at zero residual, decreasing
    # monotonically with residual on a pi-radian scale. It is diagnostic only.
    quality = 1.0 / (1.0 + rms / pi)

    detection = BottomDetection(
        parent_beam_index=parent_beam_index,
        detection_method="phase_zero_crossing",
        peak_index=None,
        peak_lag_samples=None,
        arrival_offset_seconds=arrival,
        tx_delay_seconds=tx_delay_seconds,
        twtt_seconds=max(0.0, twtt),
        detected_across_track_angle_rad=steering_across_track_angle_rad,
        normalized_amplitude=normalized_amplitude,
        quality=quality,
    )
    return PhaseDetectionResult(
        detection=detection,
        fit=PhaseRampFit(
            first_sample_index=first,
            last_sample_index=last,
            sample_count=last - first + 1,
            slope_rad_per_second=float(slope),
            intercept_rad=float(intercept),
            zero_crossing_seconds=zero,
            rms_residual_rad=rms,
        ),
    )

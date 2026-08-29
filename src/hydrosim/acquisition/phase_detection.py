"""Reference split-aperture phase-ramp bottom detection.

This module implements the signal-processing part of a phase detector without
assuming any proprietary MBES algorithm. It supports either two complex
subaperture time series or an already-derived sampled differential-phase series.

The physical differential phase is

    dphi(t) = arg(z_A(t) * conj(z_B(t))).

A sampled realization is locally unwrapped inside a user-supplied search window.
A linear least-squares fit around a sign change estimates the continuous zero
crossing. The fitted epoch is therefore not restricted to the discrete sample
grid.

Signal generation remains separate. This module does not invent bottom
reflectivity, backscatter, noise, or vendor-specific quality logic.
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


def detect_bottom_from_sampled_phase(
    phase_rad: np.ndarray,
    *,
    sample_times_seconds: np.ndarray,
    strength: np.ndarray | None = None,
    search_start_sample: int,
    search_end_sample: int,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
    steering_across_track_angle_rad: float | None = None,
    fit_half_width_samples: int = 2,
) -> PhaseDetectionResult:
    """Estimate a continuous zero crossing from discretely sampled phase.

    ``sample_times_seconds`` supplies the physical epoch of every phase sample and
    may therefore represent a non-zero origin or a non-unit sample spacing.
    ``strength`` is used only to select among multiple valid zero crossings; when
    omitted, every sample has unit strength. A sign change with zero support on
    both adjacent samples is ignored. The local phase fit itself remains
    unweighted and diagnostic.
    """

    phase_values = np.asarray(phase_rad, dtype=float)
    times = np.asarray(sample_times_seconds, dtype=float)
    if phase_values.ndim != 1 or times.ndim != 1 or phase_values.size == 0:
        raise ValueError("phase and sample times must be non-empty one-dimensional arrays")
    if phase_values.size != times.size:
        raise ValueError("phase and sample times must have equal sample counts")
    if not np.all(np.isfinite(phase_values)) or not np.all(np.isfinite(times)):
        raise ValueError("phase and sample times must be finite")
    if np.any(np.diff(times) <= 0.0):
        raise ValueError("sample times must be strictly increasing")
    if tx_delay_seconds < 0.0:
        raise ValueError("tx_delay_seconds must be non-negative")
    if fit_half_width_samples < 1:
        raise ValueError("fit_half_width_samples must be at least one")

    n = phase_values.size
    if search_start_sample < 0 or search_end_sample >= n or search_end_sample <= search_start_sample:
        raise ValueError("invalid phase-detection search window")

    if strength is None:
        strengths = np.ones(n, dtype=float)
    else:
        strengths = np.asarray(strength, dtype=float)
        if strengths.ndim != 1 or strengths.size != n:
            raise ValueError("strength must be one-dimensional and match phase sample count")
        if not np.all(np.isfinite(strengths)) or np.any(strengths < 0.0):
            raise ValueError("strength values must be finite and non-negative")

    local = np.unwrap(phase_values[search_start_sample : search_end_sample + 1])
    candidates: list[tuple[float, int]] = []
    for j in range(local.size - 1):
        p0 = float(local[j])
        p1 = float(local[j + 1])
        if p0 == 0.0 or p1 == 0.0 or p0 * p1 < 0.0:
            i = search_start_sample + j
            crossing_strength = float(strengths[i] + strengths[i + 1])
            if crossing_strength > 0.0:
                candidates.append((crossing_strength, i))
    if not candidates:
        raise ValueError("no differential-phase zero crossing in search window")

    _, crossing_index = max(candidates, key=lambda item: item[0])
    first = max(search_start_sample, crossing_index - fit_half_width_samples)
    last = min(search_end_sample, crossing_index + 1 + fit_half_width_samples)
    fit_times = times[first : last + 1]
    fit_phases = np.unwrap(phase_values[first : last + 1])

    slope, intercept = np.polyfit(fit_times, fit_phases, 1)
    if abs(float(slope)) <= 1e-15:
        raise ValueError("phase-ramp fit has effectively zero slope")
    zero = -float(intercept) / float(slope)
    if zero < fit_times[0] or zero > fit_times[-1]:
        raise ValueError("fitted phase zero crossing lies outside the fit interval")

    fitted = slope * fit_times + intercept
    rms = float(np.sqrt(np.mean((fit_phases - fitted) ** 2)))
    twtt = zero - float(tx_delay_seconds)
    local_spacing = float(np.min(np.diff(times)))
    tolerance = 0.5 * local_spacing
    if twtt < -tolerance:
        raise ValueError("phase-detected arrival precedes the sector transmit epoch")

    representative_index = int(round(0.5 * (first + last)))
    representative_strength = float(strengths[representative_index])
    quality = 1.0 / (1.0 + rms / pi)

    detection = BottomDetection(
        parent_beam_index=parent_beam_index,
        detection_method="phase_zero_crossing",
        peak_index=None,
        peak_lag_samples=None,
        arrival_offset_seconds=zero,
        tx_delay_seconds=tx_delay_seconds,
        twtt_seconds=max(0.0, twtt),
        detected_across_track_angle_rad=steering_across_track_angle_rad,
        normalized_amplitude=representative_strength,
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
    """Estimate bottom arrival from two sampled split-aperture complex series."""

    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    a = np.asarray(subaperture_a, dtype=np.complex128)
    b = np.asarray(subaperture_b, dtype=np.complex128)
    phase_values = differential_phase(a, b)
    times = np.arange(phase_values.size, dtype=float) / float(sample_rate_hz)
    strengths = np.sqrt(np.abs(a) * np.abs(b))
    return detect_bottom_from_sampled_phase(
        phase_values,
        sample_times_seconds=times,
        strength=strengths,
        search_start_sample=search_start_sample,
        search_end_sample=search_end_sample,
        tx_delay_seconds=tx_delay_seconds,
        parent_beam_index=parent_beam_index,
        steering_across_track_angle_rad=steering_across_track_angle_rad,
        fit_half_width_samples=fit_half_width_samples,
    )

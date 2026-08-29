"""Convergence diagnostics for geometric phase-ramp bottom detection.

This layer compares the final detected TWTT produced from coarse and refined
geometric phase-ramp realizations. Search and fit windows are specified in physical
time, not sample counts, so changing temporal sampling does not silently change the
scientific interval being evaluated.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .geometric_phase_ramp import GeometricPhaseRamp, detect_bottom_from_geometric_phase_ramp
from .phase_detection import PhaseDetectionResult


class PhaseDetectionConvergenceDiagnostic(BaseModel):
    """Change in phase-detected TWTT under numerical refinement."""

    model_config = ConfigDict(frozen=True)

    coarse_detection: PhaseDetectionResult
    fine_detection: PhaseDetectionResult
    absolute_twtt_change_seconds: FiniteFloat = Field(ge=0.0)
    twtt_tolerance_seconds: FiniteFloat = Field(ge=0.0)
    fine_temporal_spacing_seconds: FiniteFloat = Field(gt=0.0)
    change_in_fine_samples: FiniteFloat = Field(ge=0.0)
    converged: bool


def _twtt_samples(ramp: GeometricPhaseRamp) -> tuple[float, ...]:
    return tuple(2.0 * float(sample.reference_one_way_travel_time_seconds) for sample in ramp.samples)


def _window_indices(
    ramp: GeometricPhaseRamp,
    *,
    start_twtt_seconds: float,
    end_twtt_seconds: float,
) -> tuple[int, int]:
    start = float(start_twtt_seconds)
    end = float(end_twtt_seconds)
    if start < 0.0 or end <= start:
        raise ValueError("invalid physical TWTT search window")
    times = _twtt_samples(ramp)
    indices = [i for i, time in enumerate(times) if start <= time <= end]
    if len(indices) < 2:
        raise ValueError("TWTT search window must contain at least two ramp samples")
    return indices[0], indices[-1]


def _fit_half_width_samples(ramp: GeometricPhaseRamp, fit_half_width_seconds: float) -> int:
    width = float(fit_half_width_seconds)
    if width <= 0.0:
        raise ValueError("fit_half_width_seconds must be positive")
    dt = float(ramp.temporal_resolution.nominal_spacing)
    return max(1, int(round(width / dt)))


def _validate_refinement(coarse: GeometricPhaseRamp, fine: GeometricPhaseRamp) -> None:
    if coarse.array_name != fine.array_name:
        raise ValueError("phase-detection refinements must use the same receive array")
    scalar_pairs = (
        (coarse.frequency_hz, fine.frequency_hz, "frequency_hz"),
        (coarse.sound_speed_mps, fine.sound_speed_mps, "sound_speed_mps"),
        (coarse.steering_along_track_angle_rad, fine.steering_along_track_angle_rad, "along-track steering"),
        (coarse.steering_across_track_angle_rad, fine.steering_across_track_angle_rad, "across-track steering"),
    )
    for coarse_value, fine_value, name in scalar_pairs:
        if abs(float(coarse_value) - float(fine_value)) > 1e-12:
            raise ValueError(f"phase-detection refinements must use the same {name}")

    coarse_axes = (
        coarse.along_track_resolution,
        coarse.across_track_resolution,
        coarse.temporal_resolution,
    )
    fine_axes = (
        fine.along_track_resolution,
        fine.across_track_resolution,
        fine.temporal_resolution,
    )
    refined_any = False
    for coarse_axis, fine_axis in zip(coarse_axes, fine_axes, strict=True):
        coarse_spacing = float(coarse_axis.nominal_spacing)
        fine_spacing = float(fine_axis.nominal_spacing)
        if fine_spacing > coarse_spacing + 1e-15:
            raise ValueError("fine phase-detection realization must not be coarser on any axis")
        if fine_spacing < coarse_spacing - 1e-15:
            refined_any = True
    if not refined_any:
        raise ValueError("fine phase-detection realization must refine at least one axis")


def compare_geometric_phase_detection_refinement(
    *,
    coarse: GeometricPhaseRamp,
    fine: GeometricPhaseRamp,
    search_start_twtt_seconds: float,
    search_end_twtt_seconds: float,
    fit_half_width_seconds: float,
    twtt_tolerance_seconds: float,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
) -> PhaseDetectionConvergenceDiagnostic:
    """Compare final phase-detected TWTT using common physical windows.

    Both search bounds and local-fit half-width are specified in seconds. Each
    realization converts those physical windows to its own sample indices, so a
    temporal refinement changes numerical resolution without changing the intended
    physical interval. ``change_in_fine_samples`` is diagnostic only: it expresses
    the remaining TWTT change relative to the refined sampling interval.
    """

    tolerance = float(twtt_tolerance_seconds)
    if tolerance < 0.0:
        raise ValueError("twtt_tolerance_seconds must be non-negative")
    _validate_refinement(coarse, fine)

    coarse_start, coarse_end = _window_indices(
        coarse,
        start_twtt_seconds=search_start_twtt_seconds,
        end_twtt_seconds=search_end_twtt_seconds,
    )
    fine_start, fine_end = _window_indices(
        fine,
        start_twtt_seconds=search_start_twtt_seconds,
        end_twtt_seconds=search_end_twtt_seconds,
    )

    coarse_detection = detect_bottom_from_geometric_phase_ramp(
        coarse,
        search_start_sample=coarse_start,
        search_end_sample=coarse_end,
        tx_delay_seconds=tx_delay_seconds,
        parent_beam_index=parent_beam_index,
        fit_half_width_samples=_fit_half_width_samples(coarse, fit_half_width_seconds),
    )
    fine_detection = detect_bottom_from_geometric_phase_ramp(
        fine,
        search_start_sample=fine_start,
        search_end_sample=fine_end,
        tx_delay_seconds=tx_delay_seconds,
        parent_beam_index=parent_beam_index,
        fit_half_width_samples=_fit_half_width_samples(fine, fit_half_width_seconds),
    )

    change = abs(
        float(fine_detection.detection.twtt_seconds)
        - float(coarse_detection.detection.twtt_seconds)
    )
    fine_dt = float(fine.temporal_resolution.nominal_spacing)
    return PhaseDetectionConvergenceDiagnostic(
        coarse_detection=coarse_detection,
        fine_detection=fine_detection,
        absolute_twtt_change_seconds=change,
        twtt_tolerance_seconds=tolerance,
        fine_temporal_spacing_seconds=fine_dt,
        change_in_fine_samples=change / fine_dt,
        converged=change <= tolerance,
    )

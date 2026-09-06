"""Reference phase-based High Density bottom detection for PED-D9.

This module implements the minimum vendor-neutral contract in
``docs/science/ped_d9_high_density_phase_contract.md``. It operates on a supplied,
locally unwrapped split-aperture differential-phase trajectory and never aliases
High Density to generic multi-peak amplitude detection.
"""

from __future__ import annotations

from math import pi, sin, cos, sqrt
from typing import Literal, Sequence

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Vector3

from .phase_detection import detect_bottom_from_sampled_phase


HighDensityStatus = Literal["disabled", "available", "unavailable"]


class HighDensityDetection(BaseModel):
    """One retained phase-derived time/angle observation and reference bottom point."""

    model_config = ConfigDict(frozen=True)

    detection_index: int = Field(ge=0)
    parent_beam_index: int | None = Field(default=None, ge=0)
    method: Literal["phase_high_density"] = "phase_high_density"
    source_sample_index: int = Field(ge=0)
    source_phase_rad: FiniteFloat
    arrival_offset_seconds: FiniteFloat = Field(ge=0.0)
    twtt_seconds: FiniteFloat = Field(ge=0.0)
    detected_across_track_angle_rad: FiniteFloat
    local_bottom_point_m: Vector3


class HighDensityResult(BaseModel):
    """Canonical High Density result for one receive beam."""

    model_config = ConfigDict(frozen=True)

    status: HighDensityStatus
    ordinary_detection_arrival_seconds: FiniteFloat | None = None
    ordinary_detection_angle_rad: FiniteFloat | None = None
    candidate_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    target_spacing_m: FiniteFloat | None = Field(default=None, gt=0.0)
    detections: tuple[HighDensityDetection, ...] = ()
    unavailable_reason: str | None = None


def _direction(angle_rad: float) -> Vector3:
    """HydroSIM across-track convention: positive Port (-Y), negative Starboard (+Y)."""

    angle = float(angle_rad)
    return Vector3(x=0.0, y=-sin(angle), z=cos(angle))


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def phase_for_split_aperture_angle(
    angle_rad: float,
    *,
    steering_angle_rad: float,
    baseline_m: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
) -> float:
    """Evaluate the authoritative residual split-aperture phase relation."""

    k = 2.0 * pi * float(frequency_hz) / float(sound_speed_mps)
    source = _direction(angle_rad)
    steering = _direction(steering_angle_rad)
    delta = Vector3(
        x=float(source.x) - float(steering.x),
        y=float(source.y) - float(steering.y),
        z=float(source.z) - float(steering.z),
    )
    return k * _dot(delta, baseline_m)


def invert_split_aperture_phase_angle(
    phase_rad: float,
    *,
    steering_angle_rad: float,
    support_min_angle_rad: float,
    support_max_angle_rad: float,
    baseline_m: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
) -> float | None:
    """Solve the bounded one-dimensional phase relation and require a unique root."""

    if frequency_hz <= 0.0 or sound_speed_mps <= 0.0:
        raise ValueError("frequency_hz and sound_speed_mps must be positive")
    lo = float(support_min_angle_rad)
    hi = float(support_max_angle_rad)
    if hi <= lo:
        raise ValueError("support_max_angle_rad must exceed support_min_angle_rad")
    if sqrt(_dot(baseline_m, baseline_m)) <= 1e-15:
        raise ValueError("split-aperture baseline must be non-zero")

    target = float(phase_rad)

    def residual(angle: float) -> float:
        return phase_for_split_aperture_angle(
            angle,
            steering_angle_rad=steering_angle_rad,
            baseline_m=baseline_m,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
        ) - target

    grid = np.linspace(lo, hi, 257)
    values = [residual(float(angle)) for angle in grid]
    roots: list[tuple[float, float]] = []
    tolerance = 1e-12
    for index, value in enumerate(values):
        if abs(value) <= tolerance:
            angle = float(grid[index])
            roots.append((angle, angle))
        if index == 0:
            continue
        previous = values[index - 1]
        if previous * value < 0.0:
            roots.append((float(grid[index - 1]), float(grid[index])))

    merged: list[tuple[float, float]] = []
    for bracket in roots:
        center = 0.5 * (bracket[0] + bracket[1])
        if merged and abs(center - 0.5 * (merged[-1][0] + merged[-1][1])) < 1e-8:
            continue
        merged.append(bracket)
    if len(merged) != 1:
        return None

    left, right = merged[0]
    if left == right:
        return left
    f_left = residual(left)
    for _ in range(64):
        middle = 0.5 * (left + right)
        f_middle = residual(middle)
        if abs(f_middle) <= 1e-13 or abs(right - left) <= 1e-12:
            return middle
        if f_left * f_middle <= 0.0:
            right = middle
        else:
            left = middle
            f_left = f_middle
    return 0.5 * (left + right)


def _distance(a: Vector3, b: Vector3) -> float:
    return sqrt(
        (float(a.x) - float(b.x)) ** 2
        + (float(a.y) - float(b.y)) ** 2
        + (float(a.z) - float(b.z)) ** 2
    )


def detect_high_density_from_phase(
    *,
    high_density_enabled: bool,
    sample_times_seconds: Sequence[float],
    differential_phase_rad: Sequence[float],
    support_magnitude: Sequence[float],
    steering_angle_rad: float,
    support_min_angle_rad: float,
    support_max_angle_rad: float,
    baseline_m: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
    reference_footprint_width_m: float,
    tx_delay_seconds: float = 0.0,
    parent_beam_index: int | None = None,
) -> HighDensityResult:
    """Return spatially decimated phase-derived detections for one beam footprint."""

    if not high_density_enabled:
        return HighDensityResult(status="disabled", candidate_count=0, retained_count=0)
    times = np.asarray(tuple(sample_times_seconds), dtype=np.float64)
    phases = np.asarray(tuple(differential_phase_rad), dtype=np.float64)
    support = np.asarray(tuple(support_magnitude), dtype=np.float64)
    if times.ndim != 1 or times.size < 2 or phases.shape != times.shape or support.shape != times.shape:
        raise ValueError("phase time, phase, and support series must have equal length >= 2")
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(phases)) or not np.all(np.isfinite(support)):
        raise ValueError("phase time, phase, and support series must be finite")
    if np.any(np.diff(times) <= 0.0):
        raise ValueError("sample_times_seconds must be strictly increasing")
    if tx_delay_seconds < 0.0:
        raise ValueError("tx_delay_seconds must be non-negative")
    if reference_footprint_width_m <= 0.0:
        raise ValueError("reference_footprint_width_m must be positive")

    valid = support > 0.0
    if np.count_nonzero(valid) < 2:
        return HighDensityResult(
            status="unavailable",
            candidate_count=0,
            retained_count=0,
            unavailable_reason="insufficient non-zero phase support",
        )

    try:
        ordinary = detect_bottom_from_sampled_phase(
            phases,
            sample_times_seconds=times,
            strength=np.where(valid, support, 0.0),
            search_start_sample=0,
            search_end_sample=len(times) - 1,
            tx_delay_seconds=tx_delay_seconds,
            parent_beam_index=parent_beam_index,
            steering_across_track_angle_rad=steering_angle_rad,
        )
    except ValueError:
        return HighDensityResult(
            status="unavailable",
            candidate_count=0,
            retained_count=0,
            unavailable_reason="ordinary phase-centre detection is unavailable",
        )

    candidates: list[HighDensityDetection] = []
    for index, (time_value, phase_value, support_value) in enumerate(
        zip(times, phases, support, strict=True)
    ):
        if support_value <= 0.0 or time_value < tx_delay_seconds:
            continue
        angle = invert_split_aperture_phase_angle(
            float(phase_value),
            steering_angle_rad=steering_angle_rad,
            support_min_angle_rad=support_min_angle_rad,
            support_max_angle_rad=support_max_angle_rad,
            baseline_m=baseline_m,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
        )
        if angle is None:
            continue
        twtt = float(time_value) - float(tx_delay_seconds)
        radius = float(sound_speed_mps) * twtt / 2.0
        direction = _direction(angle)
        point = Vector3(
            x=radius * float(direction.x),
            y=radius * float(direction.y),
            z=radius * float(direction.z),
        )
        candidates.append(
            HighDensityDetection(
                detection_index=0,
                parent_beam_index=parent_beam_index,
                source_sample_index=index,
                source_phase_rad=float(phase_value),
                arrival_offset_seconds=float(time_value),
                twtt_seconds=twtt,
                detected_across_track_angle_rad=angle,
                local_bottom_point_m=point,
            )
        )

    if not candidates:
        return HighDensityResult(
            status="unavailable",
            ordinary_detection_arrival_seconds=float(ordinary.detection.arrival_offset_seconds),
            ordinary_detection_angle_rad=steering_angle_rad,
            candidate_count=0,
            retained_count=0,
            unavailable_reason="no phase sample has a unique in-support angle solution",
        )

    centre = min(
        candidates,
        key=lambda item: abs(
            float(item.arrival_offset_seconds) - float(ordinary.detection.arrival_offset_seconds)
        ),
    )
    target_spacing = float(reference_footprint_width_m) / 2.0
    retained = [centre]
    for side in (-1, 1):
        side_candidates = [
            item
            for item in candidates
            if side * (float(item.detected_across_track_angle_rad) - steering_angle_rad) > 0.0
        ]
        side_candidates.sort(
            key=lambda item: _distance(item.local_bottom_point_m, centre.local_bottom_point_m)
        )
        previous = centre
        for item in side_candidates:
            if _distance(item.local_bottom_point_m, previous.local_bottom_point_m) + 1e-12 < target_spacing:
                continue
            retained.append(item)
            previous = item

    retained.sort(key=lambda item: float(item.detected_across_track_angle_rad), reverse=True)
    indexed = tuple(item.model_copy(update={"detection_index": index}) for index, item in enumerate(retained))
    return HighDensityResult(
        status="available",
        ordinary_detection_arrival_seconds=float(ordinary.detection.arrival_offset_seconds),
        ordinary_detection_angle_rad=steering_angle_rad,
        candidate_count=len(candidates),
        retained_count=len(indexed),
        target_spacing_m=target_spacing,
        detections=indexed,
    )

"""Immutable synthetic acquisition evidence for Patch Test P3.

The forward geometry is delegated to the canonical P1 scenario.  This module
adds acquisition identity, time ordering and provenance without estimating a
patch correction or mutating the generated observations.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Literal

import numpy as np

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.scenarios.patch_test_signatures import (
    PatchErrorFamily,
    PatchSignatureConfig,
    run_patch_signature_scenario,
)


class PatchAcquisitionConfig(PatchSignatureConfig):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ping_period_seconds: FiniteFloat = Field(default=0.25, gt=0.0, le=10.0)
    sonar_id: str = Field(default="hydrosim-mbes-01", min_length=1, max_length=80)
    deterministic_seed: int = Field(default=0, ge=0)
    executed_overlap_fraction: FiniteFloat = Field(default=1.0, ge=0.0, le=1.0)
    steering_error_m: FiniteFloat = Field(default=0.0, ge=0.0, le=1000.0)


class ObservedSample(BaseModel):
    """Locked measurement and its acquisition epoch; no hidden Truth fields."""

    model_config = ConfigDict(frozen=True)

    sample_index: int = Field(ge=0)
    ping_time_seconds: FiniteFloat = Field(ge=0.0)
    measured_x_m: FiniteFloat
    measured_y_m: FiniteFloat
    measured_z_m: FiniteFloat


class DerivedSounding(BaseModel):
    model_config = ConfigDict(frozen=True)

    sample_index: int = Field(ge=0)
    x_m: FiniteFloat
    y_m: FiniteFloat
    z_m: FiniteFloat


class AcquisitionRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    line_id: str
    heading_deg: FiniteFloat
    speed_mps: FiniteFloat
    observation_state: Literal["Observed/locked"] = "Observed/locked"
    observed: tuple[ObservedSample, ...]
    derived_soundings: tuple[DerivedSounding, ...]
    configuration_snapshot: dict[str, float | int | str]


class GeometryBounds(BaseModel):
    model_config = ConfigDict(frozen=True)

    min_x_m: FiniteFloat
    max_x_m: FiniteFloat
    min_y_m: FiniteFloat
    max_y_m: FiniteFloat


class CommonSupportGeometry(BaseModel):
    model_config = ConfigDict(frozen=True)

    axis: Literal["x", "y"]
    interval_m: tuple[FiniteFloat, FiniteFloat] | None
    bounds: GeometryBounds | None


class PatchAcquisitionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    acquisition_id: str
    error_family: PatchErrorFamily
    runs: tuple[AcquisitionRun, AcquisitionRun]
    fitness: Literal["usable", "marginal", "reacquire"]
    fitness_reasons: tuple[str, ...]
    common_support_fraction: FiniteFloat = Field(ge=0.0, le=1.0)
    common_support_geometry: CommonSupportGeometry
    residual_axis: Literal["x", "y"]
    residual_preview: tuple[dict[str, float], ...]
    truth_reference: str = Field(exclude=True)
    state_semantics: str = (
        "Truth reference hidden; measurements Observed/locked; configuration "
        "snapshot Configured; navigation-frame soundings and preview Derived; no estimate"
    )


def _coordinate(point, axis: Literal["x", "y"], *, configured: bool) -> float:
    prefix = "configured" if configured else "true"
    return float(getattr(point, f"{prefix}_{axis}_m"))


def _executed_points(signature, config: PatchAcquisitionConfig):
    """Apply execution-only coverage and steering to the second acquired run."""

    axis = signature.dataset_residual_axis
    executed = [
        list(enumerate(signature.runs[0].points)),
        list(enumerate(signature.runs[1].points)),
    ]
    second = executed[1]
    if float(config.executed_overlap_fraction) == 0.0:
        second = []
    elif float(config.executed_overlap_fraction) < 1.0:
        coordinates = np.asarray([_coordinate(point, axis, configured=True) for _, point in second])
        centre = 0.5 * (float(coordinates.min()) + float(coordinates.max()))
        half_width = 0.5 * float(np.ptp(coordinates)) * float(config.executed_overlap_fraction)
        second = [
            indexed_point
            for indexed_point, coordinate in zip(second, coordinates, strict=True)
            if centre - half_width - 1e-9 <= coordinate <= centre + half_width + 1e-9
        ]
        if not second and config.executed_overlap_fraction > 0.0:
            second = [executed[1][int(np.argmin(np.abs(coordinates - centre)))]]

    shift = float(config.steering_error_m)
    if shift:
        shifted = []
        for source_index, point in second:
            updates = {
                f"true_{axis}_m": _coordinate(point, axis, configured=False) + shift,
                f"configured_{axis}_m": _coordinate(point, axis, configured=True) + shift,
            }
            shifted.append((source_index, point.model_copy(update=updates)))
        second = shifted
    executed[1] = second
    return executed


def _bounds(points) -> GeometryBounds | None:
    if not points:
        return None
    xs = [float(point.configured_x_m) for _, point in points]
    ys = [float(point.configured_y_m) for _, point in points]
    return GeometryBounds(min_x_m=min(xs), max_x_m=max(xs), min_y_m=min(ys), max_y_m=max(ys))


def _common_support(signature, executed):
    axis = signature.dataset_residual_axis

    def interval(points):
        values = [_coordinate(point, axis, configured=True) for _, point in points]
        return (min(values), max(values)) if values else None

    base_intervals = [interval(enumerate(run.points)) for run in signature.runs]
    executed_intervals = [interval(points) for points in executed]
    base_lower = max(item[0] for item in base_intervals)
    base_upper = min(item[1] for item in base_intervals)
    lower = max(item[0] for item in executed_intervals if item is not None)
    upper = min(item[1] for item in executed_intervals if item is not None)
    if upper < lower or any(item is None for item in executed_intervals):
        return 0.0, None, ()

    base_span = max(base_upper - base_lower, 0.0)
    span = max(upper - lower, 0.0)
    fraction = (
        1.0 if base_span <= 1e-12 and span <= 1e-12 else min(span / max(base_span, 1e-12), 1.0)
    )

    def profile(points):
        coordinates = np.asarray([_coordinate(point, axis, configured=True) for _, point in points])
        depths = np.asarray([float(point.configured_z_m) for _, point in points])
        order = np.argsort(coordinates)
        coordinates, depths = coordinates[order], depths[order]
        unique, inverse = np.unique(coordinates, return_inverse=True)
        sums, counts = np.zeros_like(unique), np.zeros_like(unique)
        np.add.at(sums, inverse, depths)
        np.add.at(counts, inverse, 1.0)
        return unique, sums / counts

    coordinate_a, depth_a = profile(executed[0])
    coordinate_b, depth_b = profile(executed[1])
    sample_count = max(1, min(len(coordinate_a), len(coordinate_b)))
    common = np.linspace(lower, upper, sample_count) if upper > lower else np.asarray([lower])
    residuals = tuple(
        {
            "coordinate_m": float(coordinate),
            "vertical_difference_m": float(z_a - z_b),
        }
        for coordinate, z_a, z_b in zip(
            common,
            np.interp(common, coordinate_a, depth_a),
            np.interp(common, coordinate_b, depth_b),
            strict=True,
        )
    )
    return fraction, (lower, upper), residuals


def run_patch_acquisition(config: PatchAcquisitionConfig) -> PatchAcquisitionResult:
    """Acquire a deterministic pair and freeze observations plus provenance."""

    signature = run_patch_signature_scenario(
        PatchSignatureConfig(
            **config.model_dump(
                exclude={
                    "ping_period_seconds",
                    "sonar_id",
                    "deterministic_seed",
                    "executed_overlap_fraction",
                    "steering_error_m",
                }
            )
        )
    )
    config_hash = sha256(config.model_dump_json().encode()).hexdigest()[:12]
    executed = _executed_points(signature, config)
    runs = []
    for run_number, (source, indexed_points) in enumerate(
        zip(signature.runs, executed, strict=True), start=1
    ):
        observed = tuple(
            ObservedSample(
                sample_index=source_index,
                ping_time_seconds=source_index * float(config.ping_period_seconds),
                measured_x_m=point.true_x_m,
                measured_y_m=point.true_y_m,
                measured_z_m=point.true_z_m,
            )
            for source_index, point in indexed_points
        )
        derived = tuple(
            DerivedSounding(
                sample_index=source_index,
                x_m=point.configured_x_m,
                y_m=point.configured_y_m,
                z_m=point.configured_z_m,
            )
            for source_index, point in indexed_points
        )
        runs.append(
            AcquisitionRun(
                run_id=f"{config_hash}-{run_number}",
                line_id=source.id,
                heading_deg=source.heading_deg,
                speed_mps=source.speed_mps,
                observed=observed,
                derived_soundings=derived,
                configuration_snapshot={
                    "sonar_id": config.sonar_id,
                    "ping_period_seconds": float(config.ping_period_seconds),
                    "deterministic_seed": config.deterministic_seed,
                    "configured_alignment_deg": 0.0,
                    "configured_latency_ms": 0.0,
                    "executed_steering_offset_m": float(config.steering_error_m)
                    if run_number == 2
                    else 0.0,
                },
            )
        )

    support, support_interval, residual_preview = _common_support(signature, executed)
    bounds_a, bounds_b = _bounds(executed[0]), _bounds(executed[1])
    common_bounds = None
    if support_interval is not None and bounds_a is not None and bounds_b is not None:
        if signature.dataset_residual_axis == "x":
            common_bounds = GeometryBounds(
                min_x_m=support_interval[0],
                max_x_m=support_interval[1],
                min_y_m=max(bounds_a.min_y_m, bounds_b.min_y_m),
                max_y_m=min(bounds_a.max_y_m, bounds_b.max_y_m),
            )
        else:
            common_bounds = GeometryBounds(
                min_x_m=max(bounds_a.min_x_m, bounds_b.min_x_m),
                max_x_m=min(bounds_a.max_x_m, bounds_b.max_x_m),
                min_y_m=support_interval[0],
                max_y_m=support_interval[1],
            )
    reasons: list[str] = []
    if not signature.evidence_sufficient:
        reasons.append("target signature is not identifiable in the executed geometry")
    if support <= 0.0:
        reasons.append("paired runs have no executed common support")
    elif support < 0.5:
        reasons.append("executed common support is weak")
    if float(config.steering_error_m) > float(config.line_offset_m):
        reasons.append("line steering error exceeds the planned offset scale")

    if not signature.evidence_sufficient or support <= 0.0:
        fitness = "reacquire"
    elif support < 0.5 or reasons:
        fitness = "marginal"
    else:
        fitness = "usable"

    return PatchAcquisitionResult(
        acquisition_id=f"p3-{config_hash}",
        error_family=config.error_family,
        runs=(runs[0], runs[1]),
        fitness=fitness,
        fitness_reasons=tuple(reasons),
        common_support_fraction=support,
        common_support_geometry=CommonSupportGeometry(
            axis=signature.dataset_residual_axis,
            interval_m=support_interval,
            bounds=common_bounds,
        ),
        residual_axis=signature.dataset_residual_axis,
        residual_preview=residual_preview,
        truth_reference=f"hidden:{config_hash}",
    )


__all__ = ["PatchAcquisitionConfig", "PatchAcquisitionResult", "run_patch_acquisition"]

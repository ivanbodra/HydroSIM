"""Deterministic forward signatures for Patch Test P1.

P1 is a recognition lesson: it exposes the geometric consequence of one residual
without estimating a correction.  Every sounding is generated through the shared
Truth-versus-Configured sounding pipeline.
"""

from __future__ import annotations

from math import radians, tan
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import (
    Attitude,
    FlatTerrain,
    PlaneTerrain,
    Pose,
    TransducerArray,
    Vector3,
    compare_true_and_configured_state_sounding,
    generate_ideal_fan_degrees,
)

PatchErrorFamily = Literal["roll", "pitch", "yaw", "latency", "confounded"]


class PatchSignatureConfig(BaseModel):
    """Controlled P1 inputs in API-facing units."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    error_family: PatchErrorFamily = "roll"
    angular_residual_deg: FiniteFloat = Field(default=1.0, ge=-5.0, le=5.0)
    latency_residual_ms: FiniteFloat = Field(default=100.0, ge=-500.0, le=500.0)
    water_depth_m: FiniteFloat = Field(default=50.0, gt=5.0, le=1000.0)
    terrain_slope_deg: FiniteFloat = Field(default=15.0, ge=0.0, lt=45.0)
    slow_speed_mps: FiniteFloat = Field(default=2.0, gt=0.0, le=20.0)
    fast_speed_mps: FiniteFloat = Field(default=6.0, gt=0.0, le=20.0)
    line_offset_m: FiniteFloat = Field(default=15.0, gt=0.0, le=200.0)
    sample_count: int = Field(default=41, ge=9, le=201)
    beam_count: int = Field(default=31, ge=5, le=101)
    swath_angle_deg: FiniteFloat = Field(default=100.0, gt=10.0, lt=170.0)


class PatchSignaturePoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    true_x_m: FiniteFloat
    true_y_m: FiniteFloat
    true_z_m: FiniteFloat
    configured_x_m: FiniteFloat
    configured_y_m: FiniteFloat
    configured_z_m: FiniteFloat
    horizontal_residual_m: FiniteFloat = Field(ge=0.0)
    vertical_residual_m: FiniteFloat


class PatchSignatureRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    heading_deg: FiniteFloat
    speed_mps: FiniteFloat
    points: tuple[PatchSignaturePoint, ...]


class PatchDatasetResidualPoint(BaseModel):
    """Run-to-run vertical disagreement on common navigation-frame support."""

    model_config = ConfigDict(frozen=True)

    coordinate_m: FiniteFloat
    run_a_z_m: FiniteFloat
    run_b_z_m: FiniteFloat
    vertical_difference_m: FiniteFloat


class PatchSignatureResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    error_family: PatchErrorFamily
    likely_classification: Literal["roll", "pitch", "yaw", "latency", "confounded"]
    evidence_sufficient: bool
    comparison_region: Literal["outer_swath", "near_nadir", "common_outer_swath"]
    geometry_description: str
    runs: tuple[PatchSignatureRun, ...]
    dataset_residual_axis: Literal["x", "y"]
    dataset_residuals: tuple[PatchDatasetResidualPoint, ...]
    state_semantics: str = (
        "Truth hidden; observations reconstructed with Configured state; "
        "run-to-run residuals Derived; Truth-comparison diagnostics separate"
    )


def _fan(config: PatchSignatureConfig, *, nadir_only: bool = False):
    array = TransducerArray(
        name="patch_p1_rx",
        role="rx",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.01,
        element_transverse_size=0.01,
    )
    return generate_ideal_fan_degrees(
        array,
        beam_count=1 if nadir_only else config.beam_count,
        total_swath_angle_degrees=0.0 if nadir_only else float(config.swath_angle_deg),
        role="rx",
    ).beams


def _point(comparison) -> PatchSignaturePoint:
    return PatchSignaturePoint(
        true_x_m=comparison.true.point.x,
        true_y_m=comparison.true.point.y,
        true_z_m=comparison.true.point.z,
        configured_x_m=comparison.configured.point.x,
        configured_y_m=comparison.configured.point.y,
        configured_z_m=comparison.configured.point.z,
        horizontal_residual_m=comparison.horizontal_error,
        vertical_residual_m=comparison.vertical_error,
    )


def _terrain(config: PatchSignatureConfig, *, slope_axis: Literal["x", "y", "none"]):
    if slope_axis == "none":
        return FlatTerrain(depth=float(config.water_depth_m))
    slope = tan(radians(float(config.terrain_slope_deg)))
    return PlaneTerrain(
        point=Vector3(x=0.0, y=0.0, z=float(config.water_depth_m)),
        normal=Vector3(x=-slope if slope_axis == "x" else 0.0, y=-slope if slope_axis == "y" else 0.0, z=1.0),
    )


def _alignment_run(
    config: PatchSignatureConfig,
    *,
    run_id: str,
    heading_deg: float,
    y_m: float,
    terrain,
    true_alignment: Attitude,
    nadir_only: bool,
) -> PatchSignatureRun:
    points = []
    x_positions = np.linspace(-25.0, 25.0, config.sample_count) if nadir_only else (0.0,)
    for x_m in x_positions:
        pose = Pose(
            position=Vector3(x=float(x_m), y=y_m, z=0.0),
            attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=heading_deg),
            frame="N",
        )
        for beam in _fan(config, nadir_only=nadir_only):
            points.append(
                _point(
                    compare_true_and_configured_state_sounding(
                        vessel_truth_pose=pose,
                        vessel_configured_pose=pose,
                        true_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
                        configured_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
                        true_sensor_alignment=true_alignment,
                        configured_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
                        beam=beam,
                        terrain=terrain,
                    )
                )
            )
    return PatchSignatureRun(id=run_id, heading_deg=heading_deg, speed_mps=4.0, points=tuple(points))


def _latency_run(config: PatchSignatureConfig, *, run_id: str, speed_mps: float) -> PatchSignatureRun:
    terrain = _terrain(config, slope_axis="x")
    latency_s = float(config.latency_residual_ms) * 1e-3
    beam = _fan(config, nadir_only=True)[0]
    points = []
    for x_m in np.linspace(-25.0, 25.0, config.sample_count):
        truth_pose = Pose(
            position=Vector3(x=float(x_m), y=0.0, z=0.0),
            attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            frame="N",
        )
        configured_pose = truth_pose.model_copy(
            update={"position": Vector3(x=float(x_m) - speed_mps * latency_s, y=0.0, z=0.0)}
        )
        points.append(
            _point(
                compare_true_and_configured_state_sounding(
                    vessel_truth_pose=truth_pose,
                    vessel_configured_pose=configured_pose,
                    true_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
                    configured_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
                    true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
                    configured_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
                    beam=beam,
                    terrain=terrain,
                )
            )
        )
    return PatchSignatureRun(id=run_id, heading_deg=0.0, speed_mps=speed_mps, points=tuple(points))


def _dataset_residuals(
    runs: tuple[PatchSignatureRun, PatchSignatureRun],
    *,
    axis: Literal["x", "y"],
    sample_count: int,
) -> tuple[PatchDatasetResidualPoint, ...]:
    """Interpolate both Configured datasets onto their common navigation support."""

    def profile(run: PatchSignatureRun) -> tuple[np.ndarray, np.ndarray]:
        coordinates = np.asarray(
            [
                point.configured_x_m if axis == "x" else point.configured_y_m
                for point in run.points
            ],
            dtype=float,
        )
        depths = np.asarray([point.configured_z_m for point in run.points], dtype=float)
        order = np.argsort(coordinates)
        coordinates = coordinates[order]
        depths = depths[order]
        unique_coordinates, inverse = np.unique(coordinates, return_inverse=True)
        depth_sums = np.zeros_like(unique_coordinates)
        counts = np.zeros_like(unique_coordinates)
        np.add.at(depth_sums, inverse, depths)
        np.add.at(counts, inverse, 1.0)
        return unique_coordinates, depth_sums / counts

    coordinate_a, depth_a = profile(runs[0])
    coordinate_b, depth_b = profile(runs[1])
    lower = max(float(coordinate_a[0]), float(coordinate_b[0]))
    upper = min(float(coordinate_a[-1]), float(coordinate_b[-1]))
    if upper < lower:
        return ()

    common = np.linspace(lower, upper, sample_count) if upper > lower else np.asarray([lower])
    interpolated_a = np.interp(common, coordinate_a, depth_a)
    interpolated_b = np.interp(common, coordinate_b, depth_b)
    return tuple(
        PatchDatasetResidualPoint(
            coordinate_m=float(coordinate),
            run_a_z_m=float(z_a),
            run_b_z_m=float(z_b),
            vertical_difference_m=float(z_a - z_b),
        )
        for coordinate, z_a, z_b in zip(common, interpolated_a, interpolated_b, strict=True)
    )


def run_patch_signature_scenario(config: PatchSignatureConfig) -> PatchSignatureResult:
    """Generate the controlled P1 forward signature selected by ``error_family``."""

    angle = float(config.angular_residual_deg)
    if config.error_family in {"roll", "confounded"}:
        alignment = Attitude.from_degrees(
            roll=angle,
            pitch=angle * 0.65 if config.error_family == "confounded" else 0.0,
            yaw=0.0,
        )
        runs = (
            _alignment_run(config, run_id="A", heading_deg=0.0, y_m=0.0, terrain=_terrain(config, slope_axis="none"), true_alignment=alignment, nadir_only=False),
            _alignment_run(config, run_id="B", heading_deg=180.0, y_m=0.0, terrain=_terrain(config, slope_axis="none"), true_alignment=alignment, nadir_only=False),
        )
        return PatchSignatureResult(
            error_family=config.error_family,
            likely_classification="confounded" if config.error_family == "confounded" else "roll",
            evidence_sufficient=config.error_family != "confounded",
            comparison_region="outer_swath",
            geometry_description="reciprocal coincident lines over a flat seabed",
            runs=runs,
            dataset_residual_axis="y",
            dataset_residuals=_dataset_residuals(
                runs, axis="y", sample_count=config.beam_count
            ),
        )

    if config.error_family == "pitch":
        alignment = Attitude.from_degrees(roll=0.0, pitch=angle, yaw=0.0)
        terrain = _terrain(config, slope_axis="x")
        runs = (
            _alignment_run(config, run_id="A", heading_deg=0.0, y_m=0.0, terrain=terrain, true_alignment=alignment, nadir_only=True),
            _alignment_run(config, run_id="B", heading_deg=180.0, y_m=0.0, terrain=terrain, true_alignment=alignment, nadir_only=True),
        )
        return PatchSignatureResult(
            error_family="pitch",
            likely_classification="pitch",
            evidence_sufficient=float(config.terrain_slope_deg) > 0.0,
            comparison_region="near_nadir",
            geometry_description="reciprocal coincident lines over an along-track slope",
            runs=runs,
            dataset_residual_axis="x",
            dataset_residuals=_dataset_residuals(
                runs, axis="x", sample_count=config.sample_count
            ),
        )

    if config.error_family == "yaw":
        alignment = Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=angle)
        terrain = _terrain(config, slope_axis="y")
        offset = float(config.line_offset_m)
        runs = (
            _alignment_run(config, run_id="A", heading_deg=0.0, y_m=-offset / 2.0, terrain=terrain, true_alignment=alignment, nadir_only=False),
            _alignment_run(config, run_id="B", heading_deg=0.0, y_m=offset / 2.0, terrain=terrain, true_alignment=alignment, nadir_only=False),
        )
        return PatchSignatureResult(
            error_family="yaw",
            likely_classification="yaw",
            evidence_sufficient=float(config.terrain_slope_deg) > 0.0,
            comparison_region="common_outer_swath",
            geometry_description="same-direction offset parallel lines over a cross-track feature/slope",
            runs=runs,
            dataset_residual_axis="y",
            dataset_residuals=_dataset_residuals(
                runs, axis="y", sample_count=config.beam_count
            ),
        )

    runs = (
        _latency_run(config, run_id="slow", speed_mps=float(config.slow_speed_mps)),
        _latency_run(config, run_id="fast", speed_mps=float(config.fast_speed_mps)),
    )
    return PatchSignatureResult(
        error_family="latency",
        likely_classification="latency",
        evidence_sufficient=float(config.terrain_slope_deg) > 0.0 and abs(float(config.fast_speed_mps) - float(config.slow_speed_mps)) > 1e-9,
        comparison_region="near_nadir",
        geometry_description="same-direction lines at different speeds over an along-track slope",
        runs=runs,
        dataset_residual_axis="x",
        dataset_residuals=_dataset_residuals(
            runs, axis="x", sample_count=config.sample_count
        ),
    )

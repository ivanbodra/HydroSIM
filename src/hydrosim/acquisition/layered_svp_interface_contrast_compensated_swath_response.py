"""Evaluate full-swath error along the SVP zero-curvature compensation curve.

The compensation curve constrains only the edge-minus-nadir vertical curvature metric.
This diagnostic re-evaluates every compensated depth/contrast pair over the complete
configured beam fan and reports beamwise and aggregate calculated-minus-Truth errors.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_svp_interface_contrast_compensation_curve import (
    LayeredSvpInterfaceContrastCompensationCurve,
    LayeredSvpInterfaceContrastCompensationPoint,
    run_layered_svp_interface_contrast_compensation_curve,
)
from .layered_svp_interface_contrast_map import run_layered_svp_interface_contrast_map
from .layered_svp_swath_curvature import LayeredSvpSwathCurvature


class LayeredSvpCompensatedSwathResponsePoint(BaseModel):
    """Full-swath response at one zero-curvature compensation-curve coordinate."""

    model_config = ConfigDict(frozen=True)

    compensation_point: LayeredSvpInterfaceContrastCompensationPoint
    swath_curvature: LayeredSvpSwathCurvature
    max_abs_across_track_error_m: FiniteFloat = Field(ge=0.0)
    rms_across_track_error_m: FiniteFloat = Field(ge=0.0)
    max_abs_vertical_error_m: FiniteFloat = Field(ge=0.0)
    rms_vertical_error_m: FiniteFloat = Field(ge=0.0)
    max_sounding_error_norm_m: FiniteFloat = Field(ge=0.0)
    rms_sounding_error_norm_m: FiniteFloat = Field(ge=0.0)


class LayeredSvpCompensatedSwathResponse(BaseModel):
    """Beamwise hidden error evaluated along a scalar zero-curvature contour."""

    model_config = ConfigDict(frozen=True)

    compensation_curve: LayeredSvpInterfaceContrastCompensationCurve
    points: tuple[LayeredSvpCompensatedSwathResponsePoint, ...]


def run_layered_svp_compensated_swath_response(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    processing_interface_depths_m: Iterable[float],
    contrast_bracket_mps: tuple[float, float],
    profile_start_depth_m: float,
    local_interface_depth_step_m: float,
    local_sound_speed_contrast_step_mps: float,
    curvature_tolerance_m: float = 1e-9,
    contrast_tolerance_mps: float = 1e-9,
    max_iterations: int = 80,
) -> LayeredSvpCompensatedSwathResponse:
    """Evaluate complete beamwise error after scalar edge-curvature compensation.

    The supplied interface-depth order is preserved. Every returned swath is evaluated
    at the numerical contrast root located by the existing compensation-curve model.
    Aggregate RMS values are simple deterministic summaries over the configured beam
    samples; they are not stochastic uncertainty estimates.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    depths = tuple(float(value) for value in processing_interface_depths_m)

    curve = run_layered_svp_interface_contrast_compensation_curve(
        sensor_pose=sensor_pose,
        terrain=terrain,
        configured_across_track_angles_rad=angles,
        true_profile=true_profile,
        interface_index=interface_index,
        processing_interface_depths_m=depths,
        contrast_bracket_mps=contrast_bracket_mps,
        profile_start_depth_m=profile_start_depth_m,
        local_interface_depth_step_m=local_interface_depth_step_m,
        local_sound_speed_contrast_step_mps=local_sound_speed_contrast_step_mps,
        curvature_tolerance_m=curvature_tolerance_m,
        contrast_tolerance_mps=contrast_tolerance_mps,
        max_iterations=max_iterations,
    )

    response_points = []
    for compensation_point in curve.points:
        response = run_layered_svp_interface_contrast_map(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angles_rad=angles,
            true_profile=true_profile,
            interface_index=interface_index,
            processing_interface_depths_m=(float(compensation_point.interface_depth_m),),
            processing_sound_speed_contrasts_mps=(
                float(compensation_point.compensated_sound_speed_contrast_mps),
            ),
            profile_start_depth_m=profile_start_depth_m,
        )
        swath = response.points[0].swath_curvature
        n = len(swath.points)
        across = tuple(float(point.across_track_error_m) for point in swath.points)
        vertical = tuple(float(point.vertical_error_m) for point in swath.points)
        norms = tuple(float(point.sounding_error_norm_m) for point in swath.points)

        response_points.append(
            LayeredSvpCompensatedSwathResponsePoint(
                compensation_point=compensation_point,
                swath_curvature=swath,
                max_abs_across_track_error_m=max(abs(value) for value in across),
                rms_across_track_error_m=sqrt(sum(value * value for value in across) / n),
                max_abs_vertical_error_m=max(abs(value) for value in vertical),
                rms_vertical_error_m=sqrt(sum(value * value for value in vertical) / n),
                max_sounding_error_norm_m=max(norms),
                rms_sounding_error_norm_m=sqrt(sum(value * value for value in norms) / n),
            )
        )

    return LayeredSvpCompensatedSwathResponse(
        compensation_curve=curve,
        points=tuple(response_points),
    )

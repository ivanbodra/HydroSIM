"""Depth-normalized response for the controlled principal-plane array-tilt experiment.

This module evaluates the existing sounding-error map at multiple flat-bottom depths
and reports calculated-minus-Truth errors both in metres and normalized by the
sensor-to-bottom vertical separation. The normalization is diagnostic: it tests
whether the response scales approximately with depth for a fixed sound-speed profile
and controlled geometry. It is not an uncertainty metric and does not imply that
sound-speed errors are generally depth-linear.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .principal_plane_array_tilt_sounding_error_map import (
    run_principal_plane_array_tilt_sounding_error_map,
)


class PrincipalPlaneArrayTiltDepthNormalizedResponsePoint(BaseModel):
    """One angle-bias-tilt-depth response normalized by vertical separation."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    transducer_sensor_bias_mps: FiniteFloat
    principal_plane_array_tilt_rad: FiniteFloat
    bottom_depth_m: FiniteFloat
    vertical_separation_m: FiniteFloat = Field(gt=0.0)
    analytical_tilt_sensitivity_seconds_per_m_per_rad: FiniteFloat
    analytical_ray_parameter_mismatch_seconds_per_m: FiniteFloat
    across_track_error_m: FiniteFloat
    vertical_error_m: FiniteFloat
    sounding_error_norm_m: FiniteFloat
    across_track_error_per_depth: FiniteFloat
    vertical_error_per_depth: FiniteFloat
    sounding_error_norm_per_depth: FiniteFloat = Field(ge=0.0)


class PrincipalPlaneArrayTiltDepthNormalizedResponse(BaseModel):
    """Deterministic depth sweep of normalized controlled sounding errors."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angles_rad: tuple[FiniteFloat, ...]
    transducer_sensor_biases_mps: tuple[FiniteFloat, ...]
    principal_plane_array_tilts_rad: tuple[FiniteFloat, ...]
    bottom_depths_m: tuple[FiniteFloat, ...]
    points: tuple[PrincipalPlaneArrayTiltDepthNormalizedResponsePoint, ...]


def run_principal_plane_array_tilt_depth_normalized_response(
    *,
    sensor_pose: Pose,
    configured_across_track_angles_rad: Iterable[float],
    transducer_sensor_biases_mps: Iterable[float],
    principal_plane_array_tilts_rad: Iterable[float],
    bottom_depths_m: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> PrincipalPlaneArrayTiltDepthNormalizedResponse:
    """Sweep flat-bottom depth and normalize final sounding errors by depth.

    Ordering is angle, bias, tilt, then depth. A common sound-speed profile is used
    for every depth; callers must therefore provide a profile that covers every
    requested target depth. The denominator is the physical vertical separation
    between sensor and flat bottom, not absolute NED Z and not slant range.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    biases = tuple(float(value) for value in transducer_sensor_biases_mps)
    tilts = tuple(float(value) for value in principal_plane_array_tilts_rad)
    depths = tuple(float(value) for value in bottom_depths_m)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")
    if not biases:
        raise ValueError("transducer_sensor_biases_mps must not be empty")
    if not tilts:
        raise ValueError("principal_plane_array_tilts_rad must not be empty")
    if not depths:
        raise ValueError("bottom_depths_m must not be empty")

    sensor_z = float(sensor_pose.position.z)
    for depth in depths:
        if depth <= sensor_z:
            raise ValueError("every bottom depth must lie below the sensor in +Z/down")

    # Run one depth at a time, then re-order the results into angle-bias-tilt-depth
    # order so each controlled geometry can be inspected as a depth-response curve.
    by_depth = []
    for depth in depths:
        response = run_principal_plane_array_tilt_sounding_error_map(
            sensor_pose=sensor_pose,
            terrain=FlatTerrain(depth=depth),
            configured_across_track_angles_rad=angles,
            transducer_sensor_biases_mps=biases,
            principal_plane_array_tilts_rad=tilts,
            true_profile=true_profile,
            profile_start_depth_m=profile_start_depth_m,
        )
        by_depth.append(response)

    points = []
    points_per_depth = len(angles) * len(biases) * len(tilts)
    for point_index in range(points_per_depth):
        for depth_index, depth in enumerate(depths):
            source = by_depth[depth_index].points[point_index]
            vertical_separation = depth - sensor_z
            points.append(
                PrincipalPlaneArrayTiltDepthNormalizedResponsePoint(
                    configured_across_track_angle_rad=source.configured_across_track_angle_rad,
                    transducer_sensor_bias_mps=source.transducer_sensor_bias_mps,
                    principal_plane_array_tilt_rad=source.principal_plane_array_tilt_rad,
                    bottom_depth_m=depth,
                    vertical_separation_m=vertical_separation,
                    analytical_tilt_sensitivity_seconds_per_m_per_rad=(
                        source.analytical_tilt_sensitivity_seconds_per_m_per_rad
                    ),
                    analytical_ray_parameter_mismatch_seconds_per_m=(
                        source.analytical_ray_parameter_mismatch_seconds_per_m
                    ),
                    across_track_error_m=source.across_track_error_m,
                    vertical_error_m=source.vertical_error_m,
                    sounding_error_norm_m=source.sounding_error_norm_m,
                    across_track_error_per_depth=(
                        float(source.across_track_error_m) / vertical_separation
                    ),
                    vertical_error_per_depth=(
                        float(source.vertical_error_m) / vertical_separation
                    ),
                    sounding_error_norm_per_depth=(
                        float(source.sounding_error_norm_m) / vertical_separation
                    ),
                )
            )

    return PrincipalPlaneArrayTiltDepthNormalizedResponse(
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        principal_plane_array_tilts_rad=tilts,
        bottom_depths_m=depths,
        points=tuple(points),
    )

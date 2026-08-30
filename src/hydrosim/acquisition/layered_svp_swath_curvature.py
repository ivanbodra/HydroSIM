"""Controlled flat-bottom swath-curvature diagnostic for processing-SVP error.

The diagnostic keeps Truth geometry and the transducer sound-speed measurement ideal,
changes only the finite-thickness processing profile, and evaluates a full signed
across-track fan. It quantifies the familiar smile/frown-like bathymetric signature
without treating that informal terminology as a physical model.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_sound_speed_reference_experiment import run_layered_sound_speed_error_isolation_matrix


class LayeredSvpSwathCurvaturePoint(BaseModel):
    """One calculated-minus-Truth sounding in a controlled signed swath."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    across_track_error_m: FiniteFloat
    vertical_error_m: FiniteFloat
    sounding_error_norm_m: FiniteFloat


class LayeredSvpSwathCurvature(BaseModel):
    """Flat-bottom response to finite-thickness processing-profile mismatch."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angles_rad: tuple[FiniteFloat, ...]
    points: tuple[LayeredSvpSwathCurvaturePoint, ...]
    nadir_vertical_error_m: FiniteFloat
    port_edge_vertical_error_m: FiniteFloat
    starboard_edge_vertical_error_m: FiniteFloat
    mean_edge_minus_nadir_vertical_error_m: FiniteFloat


def run_layered_svp_swath_curvature(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSvpSwathCurvature:
    """Evaluate profile-only sounding error across a signed beam fan.

    The supplied angle axis must contain zero and at least one negative and one
    positive angle. The edge-curvature scalar is the mean vertical error of the
    outermost port/starboard samples minus the nadir vertical error. Its sign follows
    HydroSIM's +Z/down convention and is intentionally not labelled "smile" or
    "frown" because display conventions and informal usage vary.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")
    if not any(abs(angle) <= 1e-15 for angle in angles):
        raise ValueError("configured_across_track_angles_rad must include nadir (0 rad)")
    negative = tuple(angle for angle in angles if angle < -1e-15)
    positive = tuple(angle for angle in angles if angle > 1e-15)
    if not negative or not positive:
        raise ValueError("configured_across_track_angles_rad must span port and starboard")

    points = []
    for angle in angles:
        matrix = run_layered_sound_speed_error_isolation_matrix(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angle_rad=angle,
            true_profile=true_profile,
            perturbed_processing_profile=processing_profile,
            profile_start_depth_m=profile_start_depth_m,
            transducer_sensor_bias_mps=0.0,
            principal_plane_array_tilt_rad=0.0,
        )
        result = matrix.profile_only
        points.append(
            LayeredSvpSwathCurvaturePoint(
                configured_across_track_angle_rad=angle,
                across_track_error_m=result.sounding_error.y,
                vertical_error_m=result.sounding_error.z,
                sounding_error_norm_m=result.sounding_error_norm_m,
            )
        )

    def point_at(target: float) -> LayeredSvpSwathCurvaturePoint:
        return min(points, key=lambda point: abs(float(point.configured_across_track_angle_rad) - target))

    nadir = point_at(0.0)
    port = point_at(min(negative))
    starboard = point_at(max(positive))
    mean_edge = 0.5 * (float(port.vertical_error_m) + float(starboard.vertical_error_m))

    return LayeredSvpSwathCurvature(
        configured_across_track_angles_rad=angles,
        points=tuple(points),
        nadir_vertical_error_m=nadir.vertical_error_m,
        port_edge_vertical_error_m=port.vertical_error_m,
        starboard_edge_vertical_error_m=starboard.vertical_error_m,
        mean_edge_minus_nadir_vertical_error_m=mean_edge - float(nadir.vertical_error_m),
    )

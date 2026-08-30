"""Controlled sensitivity diagnostics for principal-plane array tilt.

This module adds no new propagation physics. It samples the existing layered
sound-speed A/B/C/D experiment at fixed beam angle and transducer-sensor bias while
varying only the explicit principal-plane array tilt. The primary diagnostic is the
signed scalar mismatch between the Truth and processing Snell ray parameters in the
horizontal-profile frame.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import sin

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose, Vector3

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_sound_speed_reference_experiment import run_layered_sound_speed_error_isolation_matrix


class PrincipalPlaneArrayTiltSensitivityPoint(BaseModel):
    """One transducer-only sounding result at an explicit array tilt."""

    model_config = ConfigDict(frozen=True)

    principal_plane_array_tilt_rad: FiniteFloat
    truth_ray_parameter_seconds_per_m: FiniteFloat
    processing_ray_parameter_seconds_per_m: FiniteFloat
    ray_parameter_mismatch_seconds_per_m: FiniteFloat
    sounding_error: Vector3
    sounding_error_norm_m: FiniteFloat


class PrincipalPlaneArrayTiltSensitivityStudy(BaseModel):
    """Tilt sweep with beam angle and transducer-sensor bias held fixed."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    transducer_sensor_bias_mps: FiniteFloat
    principal_plane_array_tilts_rad: tuple[FiniteFloat, ...]
    points: tuple[PrincipalPlaneArrayTiltSensitivityPoint, ...]


def run_principal_plane_array_tilt_sensitivity_study(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angle_rad: float,
    transducer_sensor_bias_mps: float,
    principal_plane_array_tilts_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> PrincipalPlaneArrayTiltSensitivityStudy:
    """Sample transducer-only error versus principal-plane array tilt.

    The finite-thickness processing profile is kept equal to Truth so the returned
    sounding error isolates the interaction between transducer sound-speed bias and
    array tilt. Each point reuses the existing A/B/C/D matrix; no alternate acoustic
    solution is introduced here.

    ``truth_ray_parameter_seconds_per_m`` and
    ``processing_ray_parameter_seconds_per_m`` are signed scalar principal-plane
    quantities under the angle convention used by the controlled experiment. They
    are diagnostic scalars, not a replacement for the vector tangential-slowness
    state used by the general processing path.
    """

    tilts = tuple(float(value) for value in principal_plane_array_tilts_rad)
    if not tilts:
        raise ValueError("principal_plane_array_tilts_rad must not be empty")

    points = []
    for tilt in tilts:
        matrix = run_layered_sound_speed_error_isolation_matrix(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angle_rad=configured_across_track_angle_rad,
            true_profile=true_profile,
            perturbed_processing_profile=true_profile,
            profile_start_depth_m=profile_start_depth_m,
            transducer_sensor_bias_mps=transducer_sensor_bias_mps,
            principal_plane_array_tilt_rad=tilt,
        )
        result = matrix.transducer_only
        c_true = float(result.true_local_sound_speed_mps)
        c_used = float(result.sound_speed_used_by_sonar.sound_speed_mps)
        p_truth = sin(float(result.physical_launch_angle_profile_frame_rad)) / c_true
        p_processing = sin(float(result.estimated_receive_angle_profile_frame_rad)) / c_used

        points.append(
            PrincipalPlaneArrayTiltSensitivityPoint(
                principal_plane_array_tilt_rad=tilt,
                truth_ray_parameter_seconds_per_m=p_truth,
                processing_ray_parameter_seconds_per_m=p_processing,
                ray_parameter_mismatch_seconds_per_m=p_processing - p_truth,
                sounding_error=result.sounding_error,
                sounding_error_norm_m=float(result.sounding_error_norm_m),
            )
        )

    return PrincipalPlaneArrayTiltSensitivityStudy(
        configured_across_track_angle_rad=float(configured_across_track_angle_rad),
        transducer_sensor_bias_mps=float(transducer_sensor_bias_mps),
        principal_plane_array_tilts_rad=tilts,
        points=tuple(points),
    )

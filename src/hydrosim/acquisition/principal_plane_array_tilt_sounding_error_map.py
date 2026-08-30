"""Numerical sounding-error map for the controlled principal-plane tilt experiment.

This module links the independent analytical tilt-sensitivity coefficient to the
existing layered Truth-versus-processing reference experiment. It introduces no new
propagation physics. For each configured beam angle, transducer sound-speed bias,
and explicit principal-plane array tilt, it records both the analytical Snell
ray-parameter mismatch and the resulting calculated-minus-Truth sounding error.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import sin

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_sound_speed_reference_experiment import run_layered_sound_speed_reference_experiment
from .principal_plane_array_tilt_sensitivity_map import (
    principal_plane_array_tilt_sensitivity_coefficient,
)
from .sound_speed_sensor import SoundSpeedSensorAtTransducer


class PrincipalPlaneArrayTiltSoundingErrorMapPoint(BaseModel):
    """One controlled angle-bias-tilt response point."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    transducer_sensor_bias_mps: FiniteFloat
    principal_plane_array_tilt_rad: FiniteFloat
    analytical_tilt_sensitivity_seconds_per_m_per_rad: FiniteFloat
    analytical_ray_parameter_mismatch_seconds_per_m: FiniteFloat
    numerical_ray_parameter_mismatch_seconds_per_m: FiniteFloat
    ray_parameter_mismatch_residual_seconds_per_m: FiniteFloat
    across_track_error_m: FiniteFloat
    vertical_error_m: FiniteFloat
    sounding_error_norm_m: FiniteFloat


class PrincipalPlaneArrayTiltSoundingErrorMap(BaseModel):
    """Deterministic Cartesian map linking analytical sensitivity to sounding error."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angles_rad: tuple[FiniteFloat, ...]
    transducer_sensor_biases_mps: tuple[FiniteFloat, ...]
    principal_plane_array_tilts_rad: tuple[FiniteFloat, ...]
    points: tuple[PrincipalPlaneArrayTiltSoundingErrorMapPoint, ...]


def run_principal_plane_array_tilt_sounding_error_map(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    transducer_sensor_biases_mps: Iterable[float],
    principal_plane_array_tilts_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> PrincipalPlaneArrayTiltSoundingErrorMap:
    """Map analytical ray-parameter sensitivity and final sounding error.

    The finite-thickness processing profile is held equal to Truth so this diagnostic
    isolates the interaction between transducer sound-speed bias and explicit array
    tilt. Angle is the outer loop, bias the middle loop, and tilt the inner loop.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    biases = tuple(float(value) for value in transducer_sensor_biases_mps)
    tilts = tuple(float(value) for value in principal_plane_array_tilts_rad)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")
    if not biases:
        raise ValueError("transducer_sensor_biases_mps must not be empty")
    if not tilts:
        raise ValueError("principal_plane_array_tilts_rad must not be empty")

    start_depth = float(profile_start_depth_m)
    c_true = float(true_profile.layer_at_depth(start_depth).sound_speed_mps)
    points = []

    for angle in angles:
        for bias in biases:
            sensitivity = principal_plane_array_tilt_sensitivity_coefficient(
                configured_across_track_angle_rad=angle,
                transducer_sensor_bias_mps=bias,
                true_local_sound_speed_mps=c_true,
            )
            coefficient = float(
                sensitivity.ray_parameter_tilt_sensitivity_seconds_per_m_per_rad
            )
            sensor = SoundSpeedSensorAtTransducer(bias_mps=bias)

            for tilt in tilts:
                result = run_layered_sound_speed_reference_experiment(
                    sensor_pose=sensor_pose,
                    terrain=terrain,
                    configured_across_track_angle_rad=angle,
                    true_profile=true_profile,
                    processing_profile=true_profile,
                    profile_start_depth_m=start_depth,
                    sensor=sensor,
                    principal_plane_array_tilt_rad=tilt,
                )
                c_used = float(result.sound_speed_used_by_sonar.sound_speed_mps)
                p_truth = sin(float(result.physical_launch_angle_profile_frame_rad)) / c_true
                p_processing = (
                    sin(float(result.estimated_receive_angle_profile_frame_rad)) / c_used
                )
                numerical_delta = p_processing - p_truth
                analytical_delta = coefficient * sin(tilt)
                error = result.sounding_error

                points.append(
                    PrincipalPlaneArrayTiltSoundingErrorMapPoint(
                        configured_across_track_angle_rad=angle,
                        transducer_sensor_bias_mps=bias,
                        principal_plane_array_tilt_rad=tilt,
                        analytical_tilt_sensitivity_seconds_per_m_per_rad=coefficient,
                        analytical_ray_parameter_mismatch_seconds_per_m=analytical_delta,
                        numerical_ray_parameter_mismatch_seconds_per_m=numerical_delta,
                        ray_parameter_mismatch_residual_seconds_per_m=(
                            numerical_delta - analytical_delta
                        ),
                        across_track_error_m=float(error.y),
                        vertical_error_m=float(error.z),
                        sounding_error_norm_m=float(result.sounding_error_norm_m),
                    )
                )

    return PrincipalPlaneArrayTiltSoundingErrorMap(
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        principal_plane_array_tilts_rad=tilts,
        points=tuple(points),
    )

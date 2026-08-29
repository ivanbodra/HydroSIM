"""Reconstruct sounding geometry from detected acoustic observations.

This module belongs to the sonar-processing side of HydroSIM. It consumes
measurement-space observables such as TWTT and detected beam angle together with
explicit processing assumptions. It does not access simulation Truth.

Truth-side consequences of an erroneous sound-speed-at-transducer measurement are
generated upstream in ``sound_speed_at_transducer``. In particular, reconstruction
must not compare the sound speed used by the sonar with the true local sound speed.

Two reference reconstructions are provided:

* stationary reciprocal straight-ray propagation at constant sound speed; and
* stationary reciprocal propagation through a horizontally layered sound-speed
  profile, using measured TWTT as the ray-tracing stopping condition.

The layered reconstruction never replaces the profile with an average sound speed.
An optional zero-thickness ``SoundSpeedProfileBoundary`` can establish the initial
ray parameter independently of the first finite-thickness profile layer.
"""

from __future__ import annotations

from math import atan2, hypot

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Pose, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy

from .angular_pattern_2d import sensor_angular_direction
from .layered_propagation import (
    LayeredRayPath,
    LayeredSoundSpeedProfile,
    trace_layered_ray_for_travel_time,
)
from .sound_speed_profile_boundary import SoundSpeedProfileBoundary
from .sounding_observation import (
    ConstantSoundSpeedRangeObservation,
    DetectedAcousticObservation,
    interpret_observation_constant_sound_speed,
)


class ConstantSoundSpeedSounding(BaseModel):
    """Cartesian sounding reconstructed under the explicit constant-c reference model."""

    model_config = ConfigDict(frozen=True)

    observation: DetectedAcousticObservation
    sensor_pose: Pose
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    direction_sensor_frame: Vector3
    direction_destination_frame: Vector3
    range_interpretation: ConstantSoundSpeedRangeObservation
    point: Vector3
    reconstruction_assumption: str = "stationary_reciprocal_straight_ray_constant_sound_speed"


class LayeredSoundSpeedSounding(BaseModel):
    """Cartesian sounding reconstructed by TWTT-driven layered ray tracing."""

    model_config = ConfigDict(frozen=True)

    observation: DetectedAcousticObservation
    sensor_pose: Pose
    profile_start_depth_m: FiniteFloat = Field(ge=0.0)
    profile_boundary: SoundSpeedProfileBoundary | None = None
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    initial_direction_sensor_frame: Vector3
    initial_direction_destination_frame: Vector3
    one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    ray_path: LayeredRayPath
    point: Vector3
    reconstruction_assumption: str = "stationary_reciprocal_layered_sound_speed_twtt_ray_trace"


def reconstruct_constant_sound_speed_sounding(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    along_track_angle_rad: float,
    sound_speed_mps: float,
) -> ConstantSoundSpeedSounding:
    """Reconstruct one Cartesian sounding from TWTT and Mills-Cross angles."""

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for Cartesian reconstruction")

    along = float(along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    direction_sensor = sensor_angular_direction(along, across)
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    direction_destination = rotate_vector(rotation, direction_sensor)

    interpreted = interpret_observation_constant_sound_speed(
        observation,
        sound_speed_mps=sound_speed_mps,
    )
    distance = float(interpreted.reciprocal_one_way_range_m)
    point = Vector3(
        x=float(sensor_pose.position.x) + distance * float(direction_destination.x),
        y=float(sensor_pose.position.y) + distance * float(direction_destination.y),
        z=float(sensor_pose.position.z) + distance * float(direction_destination.z),
    )

    return ConstantSoundSpeedSounding(
        observation=observation,
        sensor_pose=sensor_pose,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        direction_sensor_frame=direction_sensor,
        direction_destination_frame=direction_destination,
        range_interpretation=interpreted,
        point=point,
    )


def reconstruct_layered_sound_speed_sounding_from_initial_direction(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    initial_direction_sensor_frame: Vector3,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    along_track_angle_rad: float,
    across_track_angle_rad: float,
    profile_boundary: SoundSpeedProfileBoundary | None = None,
) -> LayeredSoundSpeedSounding:
    """Reconstruct from an estimated direction and optional explicit start boundary.

    The supplied direction and optional boundary are processing state, not Truth
    state. If ``profile_boundary`` is supplied, the direction is interpreted at that
    zero-thickness boundary and the ray tracer establishes tangential slowness using
    the boundary sound speed before entering the first finite-thickness profile layer.
    Without a boundary, legacy behavior is preserved and the first profile-layer
    sound speed establishes the ray parameter.
    """

    if float(observation.twtt_seconds) <= 0.0:
        raise ValueError("positive TWTT is required for layered reconstruction")
    start_depth = float(profile_start_depth_m)
    if start_depth < 0.0:
        raise ValueError("profile_start_depth_m must be non-negative")

    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    direction_destination = rotate_vector(rotation, initial_direction_sensor_frame)
    horizontal_norm = hypot(float(direction_destination.x), float(direction_destination.y))
    down = float(direction_destination.z)
    if down <= 0.0:
        raise ValueError("initial acoustic direction must point downward in the profile frame")
    launch_angle = atan2(horizontal_norm, down)

    one_way_time = 0.5 * float(observation.twtt_seconds)
    path = trace_layered_ray_for_travel_time(
        profile=profile,
        launch_angle_from_vertical_rad=launch_angle,
        travel_time_seconds=one_way_time,
        start_depth_m=start_depth,
        start_boundary=profile_boundary,
    )

    horizontal_distance = float(path.horizontal_distance_m)
    if horizontal_norm > 1e-15:
        horizontal_x = horizontal_distance * float(direction_destination.x) / horizontal_norm
        horizontal_y = horizontal_distance * float(direction_destination.y) / horizontal_norm
    else:
        horizontal_x = 0.0
        horizontal_y = 0.0
    vertical_down = float(path.target_depth_m) - start_depth

    point = Vector3(
        x=float(sensor_pose.position.x) + horizontal_x,
        y=float(sensor_pose.position.y) + horizontal_y,
        z=float(sensor_pose.position.z) + vertical_down,
    )

    return LayeredSoundSpeedSounding(
        observation=observation,
        sensor_pose=sensor_pose,
        profile_start_depth_m=start_depth,
        profile_boundary=profile_boundary,
        along_track_angle_rad=float(along_track_angle_rad),
        across_track_angle_rad=float(across_track_angle_rad),
        initial_direction_sensor_frame=initial_direction_sensor_frame,
        initial_direction_destination_frame=direction_destination,
        one_way_travel_time_seconds=one_way_time,
        ray_path=path,
        point=point,
    )


def reconstruct_layered_sound_speed_sounding(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    along_track_angle_rad: float,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSoundSpeedSounding:
    """Reconstruct a sounding from measured TWTT, detected angle, and processing SVP.

    This function deliberately has no simulation-Truth sound-speed input. Any effect
    of a sound-speed-at-transducer sensor error on the physical acquisition must be
    generated upstream; the sonar reconstruction consumes the observables that
    result from that acquisition.
    """

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for layered reconstruction")

    along = float(along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    direction_sensor = sensor_angular_direction(along, across)
    return reconstruct_layered_sound_speed_sounding_from_initial_direction(
        observation,
        sensor_pose=sensor_pose,
        initial_direction_sensor_frame=direction_sensor,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
    )

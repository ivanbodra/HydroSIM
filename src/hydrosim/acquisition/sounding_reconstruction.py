"""Reconstruct sounding geometry from detected acoustic observations.

This module is deliberately downstream of bottom detection. A detector supplies
measurement-space observables such as TWTT and an across-track receive angle. The
reconstruction layer combines those observables with explicit propagation and
steering assumptions.

Three reference reconstructions are provided:

* stationary reciprocal straight-ray propagation at constant sound speed;
* stationary reciprocal propagation through a horizontally layered sound-speed
  profile, using measured TWTT as the ray-tracing stopping condition; and
* the same layered reconstruction preceded by an explicit sound-speed-at-transducer
  steering correction that preserves the imposed 3-D tangential slowness law.

The layered reconstructions never replace the profile with an average sound speed.
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
from .sound_speed_at_transducer import (
    SoundSpeedAtTransducerDirection,
    resolve_sound_speed_at_transducer_direction,
)
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
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    initial_direction_sensor_frame: Vector3
    initial_direction_destination_frame: Vector3
    one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    ray_path: LayeredRayPath
    point: Vector3
    reconstruction_assumption: str = "stationary_reciprocal_layered_sound_speed_twtt_ray_trace"


class SoundSpeedAtTransducerLayeredSounding(BaseModel):
    """Layered sounding whose physical launch direction includes local-c steering."""

    model_config = ConfigDict(frozen=True)

    observation: DetectedAcousticObservation
    sensor_pose: Pose
    profile_start_depth_m: FiniteFloat = Field(ge=0.0)
    configured_along_track_angle_rad: FiniteFloat
    configured_across_track_angle_rad: FiniteFloat
    configured_direction_sensor_frame: Vector3
    sound_speed_at_transducer: SoundSpeedAtTransducerDirection
    physical_initial_direction_destination_frame: Vector3
    one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    ray_path: LayeredRayPath
    point: Vector3
    reconstruction_assumption: str = "stationary_reciprocal_sound_speed_at_transducer_then_layered_twtt_ray_trace"


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


def _reconstruct_layered_from_physical_direction(
    *,
    observation: DetectedAcousticObservation,
    sensor_pose: Pose,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    physical_direction_destination_frame: Vector3,
) -> tuple[float, LayeredRayPath, Vector3]:
    start_depth = float(profile_start_depth_m)
    if start_depth < 0.0:
        raise ValueError("profile_start_depth_m must be non-negative")

    horizontal_norm = hypot(
        float(physical_direction_destination_frame.x),
        float(physical_direction_destination_frame.y),
    )
    down = float(physical_direction_destination_frame.z)
    if down <= 0.0:
        raise ValueError("initial acoustic direction must point downward in the profile frame")
    launch_angle = atan2(horizontal_norm, down)

    one_way_time = 0.5 * float(observation.twtt_seconds)
    path = trace_layered_ray_for_travel_time(
        profile=profile,
        launch_angle_from_vertical_rad=launch_angle,
        travel_time_seconds=one_way_time,
        start_depth_m=start_depth,
    )

    horizontal_distance = float(path.horizontal_distance_m)
    if horizontal_norm > 1e-15:
        horizontal_x = horizontal_distance * float(physical_direction_destination_frame.x) / horizontal_norm
        horizontal_y = horizontal_distance * float(physical_direction_destination_frame.y) / horizontal_norm
    else:
        horizontal_x = 0.0
        horizontal_y = 0.0
    vertical_down = float(path.target_depth_m) - start_depth

    point = Vector3(
        x=float(sensor_pose.position.x) + horizontal_x,
        y=float(sensor_pose.position.y) + horizontal_y,
        z=float(sensor_pose.position.z) + vertical_down,
    )
    return one_way_time, path, point


def reconstruct_layered_sound_speed_sounding(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    along_track_angle_rad: float,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSoundSpeedSounding:
    """Reconstruct a sounding by tracing the measured TWTT through the full SVP.

    This function assumes the supplied Mills-Cross angles already represent the
    physical launch direction at the transducer. Use
    ``reconstruct_layered_sounding_with_sound_speed_at_transducer`` when configured
    steering angles must first be converted to the physical direction using an
    explicit sound speed at the transducer.
    """

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for layered reconstruction")
    if float(observation.twtt_seconds) <= 0.0:
        raise ValueError("positive TWTT is required for layered reconstruction")

    along = float(along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    direction_sensor = sensor_angular_direction(along, across)
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    direction_destination = rotate_vector(rotation, direction_sensor)
    one_way_time, path, point = _reconstruct_layered_from_physical_direction(
        observation=observation,
        sensor_pose=sensor_pose,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
        physical_direction_destination_frame=direction_destination,
    )

    return LayeredSoundSpeedSounding(
        observation=observation,
        sensor_pose=sensor_pose,
        profile_start_depth_m=float(profile_start_depth_m),
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        initial_direction_sensor_frame=direction_sensor,
        initial_direction_destination_frame=direction_destination,
        one_way_travel_time_seconds=one_way_time,
        ray_path=path,
        point=point,
    )


def reconstruct_layered_sounding_with_sound_speed_at_transducer(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    configured_along_track_angle_rad: float,
    configured_sound_speed_at_transducer_mps: float,
    physical_sound_speed_at_transducer_mps: float,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> SoundSpeedAtTransducerLayeredSounding:
    """Apply sound speed at transducer, then trace measured TWTT through the SVP.

    The detected across-track angle and supplied along-track angle are interpreted
    as configured/processing steering angles. They first define one 3-D configured
    sensor-frame direction. The configured and physical sound speeds at the
    transducer then preserve the imposed tangential slowness to recover the physical
    launch direction. Only after that local steering step is the direction rotated
    into the profile frame and propagated through the full SVP.
    """

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for layered reconstruction")
    if float(observation.twtt_seconds) <= 0.0:
        raise ValueError("positive TWTT is required for layered reconstruction")

    along = float(configured_along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    configured_direction = sensor_angular_direction(along, across)
    resolved = resolve_sound_speed_at_transducer_direction(
        configured_direction_array_frame=configured_direction,
        configured_sound_speed_at_transducer_mps=configured_sound_speed_at_transducer_mps,
        physical_sound_speed_at_transducer_mps=physical_sound_speed_at_transducer_mps,
    )
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    physical_destination = rotate_vector(rotation, resolved.physical_direction_array_frame)
    one_way_time, path, point = _reconstruct_layered_from_physical_direction(
        observation=observation,
        sensor_pose=sensor_pose,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
        physical_direction_destination_frame=physical_destination,
    )

    return SoundSpeedAtTransducerLayeredSounding(
        observation=observation,
        sensor_pose=sensor_pose,
        profile_start_depth_m=float(profile_start_depth_m),
        configured_along_track_angle_rad=along,
        configured_across_track_angle_rad=across,
        configured_direction_sensor_frame=configured_direction,
        sound_speed_at_transducer=resolved,
        physical_initial_direction_destination_frame=physical_destination,
        one_way_travel_time_seconds=one_way_time,
        ray_path=path,
        point=point,
    )

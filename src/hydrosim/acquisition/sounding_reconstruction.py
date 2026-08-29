"""Reconstruct sounding geometry from detected acoustic observations.

This module is deliberately downstream of bottom detection. A detector supplies
measurement-space observables such as TWTT and an across-track receive angle. The
reconstruction layer combines those observables with an explicit propagation
assumption and the missing along-track transmit angle needed to define a 3-D Mills
Cross direction.

Two reference reconstructions are provided:

* stationary reciprocal straight-ray propagation at constant sound speed; and
* stationary reciprocal propagation through a horizontally layered sound-speed
  profile, using measured TWTT as the ray-tracing stopping condition.

The layered reconstruction never replaces the profile with an average sound speed.
"""

from __future__ import annotations

from math import atan2, hypot

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import Pose, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy

from .angular_pattern_2d import sensor_angular_direction
from .layered_propagation import (
    LayeredRayPath,
    LayeredSoundSpeedProfile,
    trace_layered_ray_for_travel_time,
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
    profile_start_depth_m: FiniteFloat = FiniteFloat(0.0)
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    initial_direction_sensor_frame: Vector3
    initial_direction_destination_frame: Vector3
    one_way_travel_time_seconds: FiniteFloat
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
    """Reconstruct one Cartesian sounding from TWTT and Mills-Cross angles.

    The across-track angle must be present in ``observation``. The along-track
    angle is a separate required input because a receive detection alone does not
    encode the transmit-sector steering needed to define the full 3-D direction.

    ``sensor_pose`` is the pose of the acoustic reference point in the destination
    Cartesian frame at the reconstruction epoch. Motion compensation, lever-arm
    application, latency, and sensor alignment belong upstream when constructing
    that pose; they are not silently introduced here.
    """

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


def reconstruct_layered_sound_speed_sounding(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    along_track_angle_rad: float,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSoundSpeedSounding:
    """Reconstruct a sounding by tracing the measured TWTT through the full SVP.

    The current reference model assumes stationary reciprocal propagation, so the
    one-way propagation time is ``TWTT/2``. The initial Mills-Cross direction is
    rotated into the destination frame before refraction is evaluated because the
    sound-speed layers are horizontal in that frame, not in the tilted sensor
    frame. Therefore ``sensor_pose.frame`` must use +Z as the profile-depth/down
    axis for this helper.

    Horizontal azimuth is conserved by the horizontally layered model. The total
    launch angle from vertical is derived from the full 3-D initial direction; it
    is not obtained by independently refracting the along- and across-track angles.
    No average sound speed is used.
    """

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for layered reconstruction")
    if float(observation.twtt_seconds) <= 0.0:
        raise ValueError("positive TWTT is required for layered reconstruction")

    start_depth = float(profile_start_depth_m)
    if start_depth < 0.0:
        raise ValueError("profile_start_depth_m must be non-negative")

    along = float(along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    direction_sensor = sensor_angular_direction(along, across)
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    direction_destination = rotate_vector(rotation, direction_sensor)

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
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        initial_direction_sensor_frame=direction_sensor,
        initial_direction_destination_frame=direction_destination,
        one_way_travel_time_seconds=one_way_time,
        ray_path=path,
        point=point,
    )

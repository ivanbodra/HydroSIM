"""Reconstruct sounding geometry from detected acoustic observations.

This module is deliberately downstream of bottom detection. A detector supplies
measurement-space observables such as TWTT and an across-track receive angle. The
reconstruction layer combines those observables with an explicit propagation
assumption and the missing along-track transmit angle needed to define a 3-D Mills
Cross direction.

The first reference implementation is intentionally narrow: a stationary,
reciprocal, straight-ray, constant-sound-speed model. Under that assumption,

    range = c * TWTT / 2,

and the HydroSIM sensor-frame direction follows the canonical angular convention
already used by the 2-D beam-pattern model,

    v = normalize([tan(along), -tan(across), 1]).

Positive along-track is Forward (+X); positive across-track is Port (-Y); +Z is
Down. The sensor pose rotates that direction into its destination frame before the
range is applied. This helper must not be used as a silent substitute for layered
or refracted inversion.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import Pose, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy

from .angular_pattern_2d import sensor_angular_direction
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

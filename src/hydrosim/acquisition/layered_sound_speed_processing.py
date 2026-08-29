"""Layered reconstruction boundary between beam-angle estimation and ray tracing.

A receive beam angle is an estimate formed under the sound speed used by the sonar.
A layered ray tracer, however, needs a propagation direction consistent with the
configured processing profile. The invariant carried between those two models is
tangential slowness, not the angle itself.

HydroSIM represents the transducer-depth value as an explicit zero-thickness
``SoundSpeedProfileBoundary``. This keeps a point/boundary observation distinct from
the first finite-thickness profile layer while making the interface refraction
semantics visible and traceable.

For a detected unit direction ``u_est`` and boundary sound speed ``c_boundary``::

    p_x = u_est.x / c_boundary
    p_y = u_est.y / c_boundary

At the first finite-thickness profile layer, with sound speed ``c_profile``::

    u_profile.x = c_profile * p_x
    u_profile.y = c_profile * p_y
    u_profile.z = sqrt(1 - u_profile.x**2 - u_profile.y**2)

All inputs in this module are sonar-processing state. Simulation Truth is neither
required nor exposed.
"""

from __future__ import annotations

from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Pose, Vector3

from .angular_pattern_2d import sensor_angular_direction
from .layered_propagation import LayeredSoundSpeedProfile
from .sound_speed_processing import SoundSpeedAtTransducerUse
from .sound_speed_profile_boundary import (
    SoundSpeedProfileBoundary,
    profile_boundary_from_sound_speed_at_transducer,
)
from .sounding_observation import DetectedAcousticObservation
from .sounding_reconstruction import (
    LayeredSoundSpeedSounding,
    reconstruct_layered_sound_speed_sounding_from_initial_direction,
)


class LayeredReconstructionInitialDirection(BaseModel):
    """Processing conversion from detected direction to profile-consistent direction."""

    model_config = ConfigDict(frozen=True)

    detected_direction_sensor_frame: Vector3
    sound_speed_at_transducer: SoundSpeedAtTransducerUse
    profile_boundary: SoundSpeedProfileBoundary
    profile_start_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    tangential_slowness_x_seconds_per_m: FiniteFloat
    tangential_slowness_y_seconds_per_m: FiniteFloat
    profile_initial_direction_sensor_frame: Vector3


class LayeredSoundSpeedAtTransducerSounding(BaseModel):
    """Layered sounding with explicit sound-speed-at-transducer processing state."""

    model_config = ConfigDict(frozen=True)

    initial_direction_resolution: LayeredReconstructionInitialDirection
    sounding: LayeredSoundSpeedSounding
    reconstruction_assumption: str = (
        "stationary_reciprocal_layered_sound_speed_explicit_transducer_boundary_tangential_slowness"
    )


def resolve_layered_reconstruction_initial_direction(
    *,
    detected_direction_sensor_frame: Vector3,
    sound_speed_at_transducer: SoundSpeedAtTransducerUse,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredReconstructionInitialDirection:
    """Map a detected direction across the explicit boundary into the profile.

    The transducer value is a zero-thickness boundary state. It is not written into
    the finite-thickness profile. Tangential slowness is preserved across the
    boundary/profile interface, which makes the array-face-to-profile direction
    change explicit without inventing a layer thickness.
    """

    ux = float(detected_direction_sensor_frame.x)
    uy = float(detected_direction_sensor_frame.y)
    uz = float(detected_direction_sensor_frame.z)
    norm = sqrt(ux * ux + uy * uy + uz * uz)
    if abs(norm - 1.0) > 1e-9:
        raise ValueError("detected_direction_sensor_frame must be a unit vector")
    if uz <= 0.0:
        raise ValueError("detected_direction_sensor_frame must point toward +Z/down")

    start_depth = float(profile_start_depth_m)
    boundary = profile_boundary_from_sound_speed_at_transducer(
        sound_speed_at_transducer=sound_speed_at_transducer,
        depth_m=start_depth,
    )
    boundary_c = float(boundary.sound_speed_mps)
    profile_c = float(profile.layer_at_depth(start_depth).sound_speed_mps)
    px = ux / boundary_c
    py = uy / boundary_c
    profile_x = profile_c * px
    profile_y = profile_c * py
    tangential_squared = profile_x * profile_x + profile_y * profile_y
    if tangential_squared >= 1.0:
        raise ValueError(
            "detected tangential slowness is non-propagating at the configured profile start"
        )
    profile_z = sqrt(1.0 - tangential_squared)

    return LayeredReconstructionInitialDirection(
        detected_direction_sensor_frame=detected_direction_sensor_frame,
        sound_speed_at_transducer=sound_speed_at_transducer,
        profile_boundary=boundary,
        profile_start_sound_speed_mps=profile_c,
        tangential_slowness_x_seconds_per_m=px,
        tangential_slowness_y_seconds_per_m=py,
        profile_initial_direction_sensor_frame=Vector3(
            x=profile_x,
            y=profile_y,
            z=profile_z,
        ),
    )


def reconstruct_layered_sound_speed_sounding_from_sonar_state(
    observation: DetectedAcousticObservation,
    *,
    sensor_pose: Pose,
    along_track_angle_rad: float,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    sound_speed_at_transducer: SoundSpeedAtTransducerUse,
) -> LayeredSoundSpeedAtTransducerSounding:
    """Reconstruct using measured TWTT, detected angle, boundary c, and processing SVP.

    The detected direction belongs to the explicit transducer-depth boundary state.
    The ray tracer therefore receives that detected direction together with the
    zero-thickness boundary itself. ``profile_initial_direction_sensor_frame`` is
    retained as a diagnostic representation of the refracted direction immediately
    inside the first finite-thickness profile layer; it is no longer used as a
    substitute for the boundary state.
    """

    if observation.detected_across_track_angle_rad is None:
        raise ValueError("detected across-track angle is required for layered reconstruction")

    along = float(along_track_angle_rad)
    across = float(observation.detected_across_track_angle_rad)
    detected_direction = sensor_angular_direction(along, across)
    resolution = resolve_layered_reconstruction_initial_direction(
        detected_direction_sensor_frame=detected_direction,
        sound_speed_at_transducer=sound_speed_at_transducer,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
    )
    sounding = reconstruct_layered_sound_speed_sounding_from_initial_direction(
        observation,
        sensor_pose=sensor_pose,
        initial_direction_sensor_frame=detected_direction,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        profile_boundary=resolution.profile_boundary,
    )
    return LayeredSoundSpeedAtTransducerSounding(
        initial_direction_resolution=resolution,
        sounding=sounding,
    )

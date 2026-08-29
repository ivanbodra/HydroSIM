"""Layered reconstruction boundary between beam-angle estimation and ray tracing.

A receive beam angle is an estimate formed under the sound speed used by the sonar.
A layered ray tracer, however, needs a propagation direction consistent with the
configured processing profile. The invariant carried between those two models is
tangential slowness, not the angle itself.

For a detected unit direction ``u_est`` and sonar-used sound speed ``c_used``::

    p_x = u_est.x / c_used
    p_y = u_est.y / c_used

At the profile start, with configured profile sound speed ``c_profile``::

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
        "stationary_reciprocal_layered_sound_speed_tangential_slowness_from_sonar_state"
    )


def resolve_layered_reconstruction_initial_direction(
    *,
    detected_direction_sensor_frame: Vector3,
    sound_speed_at_transducer: SoundSpeedAtTransducerUse,
    profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredReconstructionInitialDirection:
    """Map a detected direction into the configured profile using slowness continuity."""

    ux = float(detected_direction_sensor_frame.x)
    uy = float(detected_direction_sensor_frame.y)
    uz = float(detected_direction_sensor_frame.z)
    norm = sqrt(ux * ux + uy * uy + uz * uz)
    if abs(norm - 1.0) > 1e-9:
        raise ValueError("detected_direction_sensor_frame must be a unit vector")
    if uz <= 0.0:
        raise ValueError("detected_direction_sensor_frame must point toward +Z/down")

    c_used = float(sound_speed_at_transducer.sound_speed_mps)
    profile_c = float(profile.layer_at_depth(float(profile_start_depth_m)).sound_speed_mps)
    px = ux / c_used
    py = uy / c_used
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
    """Reconstruct using measured TWTT, detected angle, c-used, and processing SVP.

    Unlike the simpler reference wrapper in ``sounding_reconstruction``, this
    function does not silently interpret the detected beam angle as a physical
    launch angle in the first profile layer. It carries the tangential slowness
    implied by the sonar-used sound speed into the configured profile.
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
        initial_direction_sensor_frame=resolution.profile_initial_direction_sensor_frame,
        profile=profile,
        profile_start_depth_m=profile_start_depth_m,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
    )
    return LayeredSoundSpeedAtTransducerSounding(
        initial_direction_resolution=resolution,
        sounding=sounding,
    )

"""Sound speed at the transducer used by array steering.

Sound speed at the transducer and the water-column sound-speed profile have
different roles. Array steering converts an intended direction into an
inter-element delay/slowness law using the configured sound speed at the
transducer. The physical wavefront in the actual water satisfies that same imposed
tangential slowness law but with the physical local sound speed.

For a principal-plane steering angle theta measured from the array normal,

    p_t = sin(theta_configured) / c_configured

and therefore

    sin(theta_physical) = p_t * c_physical.

For a full 3-D unit direction u = (u_x, u_y, u_z) expressed in an array-local frame
whose +Z axis is the array normal, the imposed tangential slowness vector is

    p_t = (u_x, u_y) / c_configured.

The physical tangential direction components are then

    (u_x, u_y)_physical = c_physical * p_t,

while the downward normal component is recovered from unit length:

    u_z,physical = sqrt(1 - u_x,physical^2 - u_y,physical^2).

This keeps sound speed at the transducer separate from water-column ray tracing.
Once the physical launch/arrival direction at the transducer is established, the
full SVP controls subsequent refraction.
"""

from __future__ import annotations

from math import asin, pi, sin, sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Vector3


class SoundSpeedAtTransducerSteering(BaseModel):
    """Principal-plane steering under configured and physical sound speed at transducer."""

    model_config = ConfigDict(frozen=True)

    configured_angle_rad: FiniteFloat
    configured_sound_speed_at_transducer_mps: FiniteFloat = Field(gt=0.0)
    physical_sound_speed_at_transducer_mps: FiniteFloat = Field(gt=0.0)
    imposed_tangential_slowness_seconds_per_m: FiniteFloat
    physical_angle_rad: FiniteFloat
    angle_error_rad: FiniteFloat


class SoundSpeedAtTransducerDirection(BaseModel):
    """Full 3-D direction implied by a steering law and physical local sound speed."""

    model_config = ConfigDict(frozen=True)

    configured_direction_array_frame: Vector3
    physical_direction_array_frame: Vector3
    configured_sound_speed_at_transducer_mps: FiniteFloat = Field(gt=0.0)
    physical_sound_speed_at_transducer_mps: FiniteFloat = Field(gt=0.0)
    imposed_tangential_slowness_x_seconds_per_m: FiniteFloat
    imposed_tangential_slowness_y_seconds_per_m: FiniteFloat


def _validate_sound_speeds(
    configured_sound_speed_at_transducer_mps: float,
    physical_sound_speed_at_transducer_mps: float,
) -> tuple[float, float]:
    configured_c = float(configured_sound_speed_at_transducer_mps)
    physical_c = float(physical_sound_speed_at_transducer_mps)
    if configured_c <= 0.0:
        raise ValueError("configured_sound_speed_at_transducer_mps must be positive")
    if physical_c <= 0.0:
        raise ValueError("physical_sound_speed_at_transducer_mps must be positive")
    return configured_c, physical_c


def resolve_sound_speed_at_transducer_steering(
    *,
    configured_angle_rad: float,
    configured_sound_speed_at_transducer_mps: float,
    physical_sound_speed_at_transducer_mps: float,
) -> SoundSpeedAtTransducerSteering:
    """Resolve the physical principal-plane angle produced by array steering."""

    angle = float(configured_angle_rad)
    if not (-0.5 * pi < angle < 0.5 * pi):
        raise ValueError("configured steering angle must satisfy -pi/2 < angle < pi/2")

    configured_c, physical_c = _validate_sound_speeds(
        configured_sound_speed_at_transducer_mps,
        physical_sound_speed_at_transducer_mps,
    )
    imposed_slowness = sin(angle) / configured_c
    physical_sine = imposed_slowness * physical_c
    if abs(physical_sine) >= 1.0:
        raise ValueError("configured steering law is non-propagating at the physical sound speed at transducer")

    physical_angle = asin(physical_sine)
    return SoundSpeedAtTransducerSteering(
        configured_angle_rad=angle,
        configured_sound_speed_at_transducer_mps=configured_c,
        physical_sound_speed_at_transducer_mps=physical_c,
        imposed_tangential_slowness_seconds_per_m=imposed_slowness,
        physical_angle_rad=physical_angle,
        angle_error_rad=physical_angle - angle,
    )


def resolve_sound_speed_at_transducer_direction(
    *,
    configured_direction_array_frame: Vector3,
    configured_sound_speed_at_transducer_mps: float,
    physical_sound_speed_at_transducer_mps: float,
) -> SoundSpeedAtTransducerDirection:
    """Resolve a full 3-D physical direction from the imposed tangential slowness.

    The configured direction must be a downward-pointing unit vector in an
    array-local frame whose +Z axis is the array normal. Only tangential slowness is
    imposed by a planar aperture; the physical +Z component is recovered from the
    unit-vector constraint. This avoids independently correcting along- and
    across-track angles when both are non-zero.
    """

    configured_c, physical_c = _validate_sound_speeds(
        configured_sound_speed_at_transducer_mps,
        physical_sound_speed_at_transducer_mps,
    )
    ux = float(configured_direction_array_frame.x)
    uy = float(configured_direction_array_frame.y)
    uz = float(configured_direction_array_frame.z)
    norm = sqrt(ux * ux + uy * uy + uz * uz)
    if abs(norm - 1.0) > 1e-9:
        raise ValueError("configured_direction_array_frame must be a unit vector")
    if uz <= 0.0:
        raise ValueError("configured_direction_array_frame must point toward +Z/down from the array")

    px = ux / configured_c
    py = uy / configured_c
    physical_x = physical_c * px
    physical_y = physical_c * py
    tangential_squared = physical_x * physical_x + physical_y * physical_y
    if tangential_squared >= 1.0:
        raise ValueError("configured 3-D steering law is non-propagating at the physical sound speed at transducer")

    physical_z = sqrt(1.0 - tangential_squared)
    return SoundSpeedAtTransducerDirection(
        configured_direction_array_frame=configured_direction_array_frame,
        physical_direction_array_frame=Vector3(x=physical_x, y=physical_y, z=physical_z),
        configured_sound_speed_at_transducer_mps=configured_c,
        physical_sound_speed_at_transducer_mps=physical_c,
        imposed_tangential_slowness_x_seconds_per_m=px,
        imposed_tangential_slowness_y_seconds_per_m=py,
    )

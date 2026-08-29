"""Surface sound speed used by transducer steering.

Surface/transducer sound speed and the water-column sound-speed profile have
different roles.  Array steering converts an intended angle into an inter-element
delay/slowness law using the configured sound speed at the transducer.  The physical
wavefront in the actual water satisfies the same imposed delay law but with the
physical local sound speed.

For a principal-plane steering angle theta measured from the array normal,

    p = sin(theta_configured) / c_configured

is the imposed horizontal slowness.  The corresponding physical angle at the
transducer is therefore

    sin(theta_physical) = p * c_physical
                        = (c_physical / c_configured) * sin(theta_configured).

This is deliberately separate from water-column ray tracing.  Once the physical
launch/arrival direction at the transducer is established, the full SVP controls
subsequent refraction.
"""

from __future__ import annotations

from math import asin, pi, sin

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class SurfaceSoundSpeedSteering(BaseModel):
    """Principal-plane steering interpretation under configured and physical SSS."""

    model_config = ConfigDict(frozen=True)

    configured_angle_rad: FiniteFloat
    configured_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    physical_surface_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    imposed_slowness_seconds_per_m: FiniteFloat
    physical_angle_rad: FiniteFloat
    angle_error_rad: FiniteFloat


def resolve_surface_sound_speed_steering(
    *,
    configured_angle_rad: float,
    configured_sound_speed_mps: float,
    physical_surface_sound_speed_mps: float,
) -> SurfaceSoundSpeedSteering:
    """Resolve the physical principal-plane angle produced by a steering SSS.

    ``configured_sound_speed_mps`` is the value used to calculate the array delay
    law. ``physical_surface_sound_speed_mps`` is the actual sound speed local to the
    transducer.  The function preserves the signed HydroSIM angle convention.

    If the imposed slowness would require ``abs(sin(theta_physical)) >= 1``, the
    requested steering law is not physically propagating in this simple plane-wave
    model and is rejected explicitly rather than clamped.
    """

    angle = float(configured_angle_rad)
    if not (-0.5 * pi < angle < 0.5 * pi):
        raise ValueError("configured steering angle must satisfy -pi/2 < angle < pi/2")

    configured_c = float(configured_sound_speed_mps)
    physical_c = float(physical_surface_sound_speed_mps)
    if configured_c <= 0.0:
        raise ValueError("configured_sound_speed_mps must be positive")
    if physical_c <= 0.0:
        raise ValueError("physical_surface_sound_speed_mps must be positive")

    imposed_slowness = sin(angle) / configured_c
    physical_sine = imposed_slowness * physical_c
    if abs(physical_sine) >= 1.0:
        raise ValueError("configured steering law is non-propagating at the physical surface sound speed")

    physical_angle = asin(physical_sine)
    return SurfaceSoundSpeedSteering(
        configured_angle_rad=angle,
        configured_sound_speed_mps=configured_c,
        physical_surface_sound_speed_mps=physical_c,
        imposed_slowness_seconds_per_m=imposed_slowness,
        physical_angle_rad=physical_angle,
        angle_error_rad=physical_angle - angle,
    )

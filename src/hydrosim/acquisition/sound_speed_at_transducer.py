"""Array steering consequences of sound speed at the transducer.

This module deliberately separates two domains:

* ``sound_speed_used_by_sonar_mps`` is processing state available to the sonar,
  normally originating from the sound-speed sensor at the transducer; and
* ``true_local_sound_speed_mps`` belongs to the synthetic Truth model and is used
  only to determine what physical wavefront the imposed delay law actually creates.

The sonar never needs access to Truth to form its delay law. HydroSIM compares the
processing law with Truth only because a simulator must generate the physical
consequence of a possibly erroneous measurement.
"""

from __future__ import annotations

from math import asin, pi, sin, sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Vector3


class SteeringTruthComparison(BaseModel):
    """Simulation diagnostic comparing sonar steering state with physical Truth."""

    model_config = ConfigDict(frozen=True)

    configured_direction_array_frame: Vector3
    physical_direction_array_frame: Vector3
    sound_speed_used_by_sonar_mps: FiniteFloat = Field(gt=0.0)
    true_local_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    imposed_tangential_slowness_x_seconds_per_m: FiniteFloat
    imposed_tangential_slowness_y_seconds_per_m: FiniteFloat


class PrincipalPlaneSteeringTruthComparison(BaseModel):
    """Principal-plane form of the simulation steering/Truth comparison."""

    model_config = ConfigDict(frozen=True)

    configured_angle_rad: FiniteFloat
    sound_speed_used_by_sonar_mps: FiniteFloat = Field(gt=0.0)
    true_local_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    imposed_tangential_slowness_seconds_per_m: FiniteFloat
    physical_angle_rad: FiniteFloat
    angle_error_rad: FiniteFloat


def _validate_sound_speeds(sound_speed_used_by_sonar_mps: float, true_local_sound_speed_mps: float) -> tuple[float, float]:
    sonar_c = float(sound_speed_used_by_sonar_mps)
    true_c = float(true_local_sound_speed_mps)
    if sonar_c <= 0.0:
        raise ValueError("sound_speed_used_by_sonar_mps must be positive")
    if true_c <= 0.0:
        raise ValueError("true_local_sound_speed_mps must be positive")
    return sonar_c, true_c


def compare_principal_plane_steering_with_truth(
    *,
    configured_angle_rad: float,
    sound_speed_used_by_sonar_mps: float,
    true_local_sound_speed_mps: float,
) -> PrincipalPlaneSteeringTruthComparison:
    """Generate the physical principal-plane direction produced in simulation Truth."""

    angle = float(configured_angle_rad)
    if not (-0.5 * pi < angle < 0.5 * pi):
        raise ValueError("configured steering angle must satisfy -pi/2 < angle < pi/2")
    sonar_c, true_c = _validate_sound_speeds(sound_speed_used_by_sonar_mps, true_local_sound_speed_mps)
    imposed_slowness = sin(angle) / sonar_c
    physical_sine = imposed_slowness * true_c
    if abs(physical_sine) >= 1.0:
        raise ValueError("sonar steering law is non-propagating at the true local sound speed")
    physical_angle = asin(physical_sine)
    return PrincipalPlaneSteeringTruthComparison(
        configured_angle_rad=angle,
        sound_speed_used_by_sonar_mps=sonar_c,
        true_local_sound_speed_mps=true_c,
        imposed_tangential_slowness_seconds_per_m=imposed_slowness,
        physical_angle_rad=physical_angle,
        angle_error_rad=physical_angle - angle,
    )


def compare_steering_direction_with_truth(
    *,
    configured_direction_array_frame: Vector3,
    sound_speed_used_by_sonar_mps: float,
    true_local_sound_speed_mps: float,
) -> SteeringTruthComparison:
    """Generate the physical 3-D direction produced by a sonar steering law.

    The configured direction is the direction the sonar intends under the sound
    speed available to its processing chain. The synthetic Truth model then applies
    the same imposed tangential slowness at the actual local sound speed. This
    function is therefore a simulator boundary, not an operation a real sonar could
    perform from its own observations alone.
    """

    sonar_c, true_c = _validate_sound_speeds(sound_speed_used_by_sonar_mps, true_local_sound_speed_mps)
    ux = float(configured_direction_array_frame.x)
    uy = float(configured_direction_array_frame.y)
    uz = float(configured_direction_array_frame.z)
    norm = sqrt(ux * ux + uy * uy + uz * uz)
    if abs(norm - 1.0) > 1e-9:
        raise ValueError("configured_direction_array_frame must be a unit vector")
    if uz <= 0.0:
        raise ValueError("configured_direction_array_frame must point toward +Z/down from the array")

    px = ux / sonar_c
    py = uy / sonar_c
    physical_x = true_c * px
    physical_y = true_c * py
    tangential_squared = physical_x * physical_x + physical_y * physical_y
    if tangential_squared >= 1.0:
        raise ValueError("sonar 3-D steering law is non-propagating at the true local sound speed")
    physical_z = sqrt(1.0 - tangential_squared)
    return SteeringTruthComparison(
        configured_direction_array_frame=configured_direction_array_frame,
        physical_direction_array_frame=Vector3(x=physical_x, y=physical_y, z=physical_z),
        sound_speed_used_by_sonar_mps=sonar_c,
        true_local_sound_speed_mps=true_c,
        imposed_tangential_slowness_x_seconds_per_m=px,
        imposed_tangential_slowness_y_seconds_per_m=py,
    )

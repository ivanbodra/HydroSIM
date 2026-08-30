"""Analytical angle-bias map for principal-plane array-tilt sensitivity.

This module contains only the closed-form local sensitivity implied by the
controlled principal-plane array-tilt experiment. It does not call the layered
ray tracer and does not estimate final sounding error.

For configured array-frame angle ``theta_cfg``, true local sound speed ``c_true``
and sonar-used sound speed ``c_used``::

    theta_phys = asin((c_true / c_used) * sin(theta_cfg))

The exact ray-parameter mismatch produced by principal-plane array tilt ``tau`` is::

    Delta_p(tau) = K * sin(tau)

with::

    K = cos(theta_cfg) / c_used - cos(theta_phys) / c_true

``K`` is therefore the derivative d(Delta_p)/d(tau) at zero tilt and is the
analytical sensitivity coordinate mapped here over beam angle and transducer
sound-speed bias.
"""

from __future__ import annotations

from collections.abc import Iterable
from math import asin, cos, pi, sin

from pydantic import BaseModel, ConfigDict, FiniteFloat


class PrincipalPlaneArrayTiltSensitivityMapPoint(BaseModel):
    """Closed-form zero-tilt sensitivity at one beam-angle / sound-speed-bias pair."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    transducer_sensor_bias_mps: FiniteFloat
    true_local_sound_speed_mps: FiniteFloat
    sound_speed_used_by_sonar_mps: FiniteFloat
    physical_array_angle_rad: FiniteFloat
    ray_parameter_tilt_sensitivity_seconds_per_m_per_rad: FiniteFloat


class PrincipalPlaneArrayTiltSensitivityMap(BaseModel):
    """Deterministic Cartesian map of analytical tilt sensitivity K(theta, bias)."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angles_rad: tuple[FiniteFloat, ...]
    transducer_sensor_biases_mps: tuple[FiniteFloat, ...]
    true_local_sound_speed_mps: FiniteFloat
    points: tuple[PrincipalPlaneArrayTiltSensitivityMapPoint, ...]


def principal_plane_array_tilt_sensitivity_coefficient(
    *,
    configured_across_track_angle_rad: float,
    transducer_sensor_bias_mps: float,
    true_local_sound_speed_mps: float,
) -> PrincipalPlaneArrayTiltSensitivityMapPoint:
    """Evaluate the independent closed-form sensitivity coefficient K.

    The configured angle is measured in the array principal plane. The sensor bias
    is added to the true local sound speed to obtain the value used by the sonar.
    The function rejects non-positive sonar sound speed and steering states that are
    non-propagating in Truth.
    """

    theta = float(configured_across_track_angle_rad)
    if not (-0.5 * pi < theta < 0.5 * pi):
        raise ValueError("configured steering angle must satisfy -pi/2 < angle < pi/2")

    c_true = float(true_local_sound_speed_mps)
    if c_true <= 0.0:
        raise ValueError("true_local_sound_speed_mps must be positive")
    bias = float(transducer_sensor_bias_mps)
    c_used = c_true + bias
    if c_used <= 0.0:
        raise ValueError("biased sound speed used by sonar must be positive")

    physical_sine = (c_true / c_used) * sin(theta)
    if abs(physical_sine) >= 1.0:
        raise ValueError("sonar steering law is non-propagating at the true local sound speed")
    theta_phys = asin(physical_sine)
    coefficient = cos(theta) / c_used - cos(theta_phys) / c_true

    return PrincipalPlaneArrayTiltSensitivityMapPoint(
        configured_across_track_angle_rad=theta,
        transducer_sensor_bias_mps=bias,
        true_local_sound_speed_mps=c_true,
        sound_speed_used_by_sonar_mps=c_used,
        physical_array_angle_rad=theta_phys,
        ray_parameter_tilt_sensitivity_seconds_per_m_per_rad=coefficient,
    )


def run_principal_plane_array_tilt_sensitivity_map(
    *,
    configured_across_track_angles_rad: Iterable[float],
    transducer_sensor_biases_mps: Iterable[float],
    true_local_sound_speed_mps: float,
) -> PrincipalPlaneArrayTiltSensitivityMap:
    """Map the analytical coefficient over beam angle and sensor bias.

    Angle is the outer loop and bias is the inner loop. Inputs are materialized once
    so ordering remains deterministic for generators as well as concrete sequences.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    biases = tuple(float(value) for value in transducer_sensor_biases_mps)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")
    if not biases:
        raise ValueError("transducer_sensor_biases_mps must not be empty")

    points = tuple(
        principal_plane_array_tilt_sensitivity_coefficient(
            configured_across_track_angle_rad=angle,
            transducer_sensor_bias_mps=bias,
            true_local_sound_speed_mps=true_local_sound_speed_mps,
        )
        for angle in angles
        for bias in biases
    )
    return PrincipalPlaneArrayTiltSensitivityMap(
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        true_local_sound_speed_mps=float(true_local_sound_speed_mps),
        points=points,
    )

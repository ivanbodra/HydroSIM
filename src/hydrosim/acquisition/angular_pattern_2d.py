"""Two-dimensional sensor-frame angular scans for TX/RX beam patterns.

This module provides the first explicit integration between a validated
``MillsCrossConfiguration`` and HydroSIM's generic two-way beam-pattern model.
It intentionally remains a normalized far-field narrowband angular response; it
is not yet a complete MBES sounding simulator.

The sensor-frame angular parameterization uses along-track and across-track slope
angles relative to the sensor +Z normal. Positive along-track is +X (Forward) and
positive across-track is -Y (Port), consistent with HydroSIM conventions. A unit
direction is obtained from

    v = (tan(alpha_along), -tan(alpha_across), 1)
    u = v / ||v||

This parameterization reduces exactly to the existing one-dimensional angular
conventions on either principal plane and avoids embedding a vendor-specific
sector convention in the generic scan.
"""

from __future__ import annotations

from math import sqrt, tan
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import MillsCrossConfiguration, Vector3

from .two_way_pattern import two_way_beam_pattern_sensor_frame


class AngularPattern2DSample(BaseModel):
    """One normalized two-way response sample in sensor angular coordinates."""

    model_config = ConfigDict(frozen=True)

    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    direction_sensor_frame: Vector3
    transmit_amplitude: FiniteFloat = Field(ge=0.0)
    receive_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_power: FiniteFloat = Field(ge=0.0)


class AngularPattern2DScan(BaseModel):
    """Rectangular angular grid of a normalized Mills-Cross two-way response."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    along_track_angles_rad: tuple[FiniteFloat, ...]
    across_track_angles_rad: tuple[FiniteFloat, ...]
    samples: tuple[AngularPattern2DSample, ...]
    peak_along_track_angle_rad: FiniteFloat
    peak_across_track_angle_rad: FiniteFloat
    peak_power: FiniteFloat = Field(ge=0.0)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)


def sensor_angular_direction(
    along_track_angle_rad: float,
    across_track_angle_rad: float,
) -> Vector3:
    """Return a unit sensor-frame direction from along/across angular slopes.

    Positive along-track points Forward (+X). Positive across-track points Port
    (-Y). Zero/zero is the sensor +Z normal.
    """

    x = tan(float(along_track_angle_rad))
    y = -tan(float(across_track_angle_rad))
    z = 1.0
    norm = sqrt(x * x + y * y + z * z)
    return Vector3(x=x / norm, y=y / norm, z=z / norm)


def _angular_grid(start: float, end: float, count: int, *, name: str) -> tuple[float, ...]:
    if count < 2:
        raise ValueError(f"{name}_sample_count must be >= 2")
    start_f = float(start)
    end_f = float(end)
    if end_f <= start_f:
        raise ValueError(f"{name}_end_angle_rad must be greater than {name}_start_angle_rad")
    step = (end_f - start_f) / (count - 1)
    return tuple(start_f + i * step for i in range(count))


def scan_mills_cross_two_way_pattern_2d(
    *,
    configuration: MillsCrossConfiguration,
    along_track_start_angle_rad: float,
    along_track_end_angle_rad: float,
    along_track_sample_count: int,
    across_track_start_angle_rad: float,
    across_track_end_angle_rad: float,
    across_track_sample_count: int,
    transmit_steering_along_track_angle_rad: float = 0.0,
    transmit_steering_across_track_angle_rad: float = 0.0,
    receive_steering_along_track_angle_rad: float = 0.0,
    receive_steering_across_track_angle_rad: float = 0.0,
    frequency_hz: float,
    sound_speed_mps: float,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> AngularPattern2DScan:
    """Evaluate a validated Mills-Cross installation over a 2D angular grid.

    The physical direction is created once in the common sensor frame. The
    existing TX/RX orientation bridge then maps it independently into each array
    frame before evaluating and multiplying the one-way responses.
    """

    along_angles = _angular_grid(
        along_track_start_angle_rad,
        along_track_end_angle_rad,
        along_track_sample_count,
        name="along_track",
    )
    across_angles = _angular_grid(
        across_track_start_angle_rad,
        across_track_end_angle_rad,
        across_track_sample_count,
        name="across_track",
    )

    tx_steering = sensor_angular_direction(
        transmit_steering_along_track_angle_rad,
        transmit_steering_across_track_angle_rad,
    )
    rx_steering = sensor_angular_direction(
        receive_steering_along_track_angle_rad,
        receive_steering_across_track_angle_rad,
    )

    samples: list[AngularPattern2DSample] = []
    for along in along_angles:
        for across in across_angles:
            direction = sensor_angular_direction(along, across)
            response = two_way_beam_pattern_sensor_frame(
                transmit_array=configuration.transmit_array,
                receive_array=configuration.receive_array,
                direction_sensor_frame=direction,
                transmit_steering_direction_sensor_frame=tx_steering,
                receive_steering_direction_sensor_frame=rx_steering,
                frequency_hz=frequency_hz,
                sound_speed_mps=sound_speed_mps,
                transmit_weights=transmit_weights,
                receive_weights=receive_weights,
            )
            samples.append(
                AngularPattern2DSample(
                    along_track_angle_rad=along,
                    across_track_angle_rad=across,
                    direction_sensor_frame=direction,
                    transmit_amplitude=response.transmit_response.normalized_amplitude,
                    receive_amplitude=response.receive_response.normalized_amplitude,
                    normalized_amplitude=response.normalized_amplitude,
                    normalized_power=response.normalized_power,
                )
            )

    peak = max(samples, key=lambda item: float(item.normalized_power))
    return AngularPattern2DScan(
        configuration_name=configuration.name,
        along_track_angles_rad=along_angles,
        across_track_angles_rad=across_angles,
        samples=tuple(samples),
        peak_along_track_angle_rad=peak.along_track_angle_rad,
        peak_across_track_angle_rad=peak.across_track_angle_rad,
        peak_power=peak.normalized_power,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
    )

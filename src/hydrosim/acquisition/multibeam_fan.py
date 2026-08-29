"""Complete receive-fan abstraction for a Mills-Cross multibeam configuration.

This module builds on the receive-beam bank and represents a complete across-track
fan of electronically steered receive beams under one common transmit field.

The fan is still a normalized far-field narrowband model. It does not duplicate
physical receive arrays: one receive aperture forms many steering hypotheses.
"""

from __future__ import annotations

from math import sqrt
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import MillsCrossConfiguration, Vector3

from .angular_pattern_2d import sensor_angular_direction
from .receive_beam_bank import evaluate_mills_cross_receive_beam_bank
from .two_way_pattern import two_way_beam_pattern_sensor_frame


class MultibeamFanBeam(BaseModel):
    """One electronically formed receive beam in the across-track fan."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    receive_steering_across_track_angle_rad: FiniteFloat
    steering_direction_sensor_frame: Vector3
    transmit_amplitude_at_beam_center: FiniteFloat = Field(ge=0.0)
    receive_amplitude_at_beam_center: FiniteFloat = Field(ge=0.0)
    two_way_amplitude_at_beam_center: FiniteFloat = Field(ge=0.0)
    two_way_power_at_beam_center: FiniteFloat = Field(ge=0.0)


class MultibeamFanMatrixSample(BaseModel):
    """Response of one receive beam to one sampled source direction."""

    model_config = ConfigDict(frozen=True)

    source_index: int = Field(ge=0)
    source_across_track_angle_rad: FiniteFloat
    beam_index: int = Field(ge=0)
    beam_steering_across_track_angle_rad: FiniteFloat
    normalized_power: FiniteFloat = Field(ge=0.0)


class MillsCrossMultibeamFan(BaseModel):
    """Complete across-track RX fan under one common TX field."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    transmit_steering_along_track_angle_rad: FiniteFloat
    transmit_steering_across_track_angle_rad: FiniteFloat
    receive_steering_along_track_angle_rad: FiniteFloat
    receive_steering_across_track_angles_rad: tuple[FiniteFloat, ...]
    beams: tuple[MultibeamFanBeam, ...]
    response_matrix: tuple[MultibeamFanMatrixSample, ...]
    strongest_beam_index_by_source: tuple[int, ...]
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)


def _linear_angles(start: float, end: float, count: int) -> tuple[float, ...]:
    if count < 2:
        raise ValueError("beam_count must be >= 2")
    start_f = float(start)
    end_f = float(end)
    if end_f <= start_f:
        raise ValueError("end_across_track_angle_rad must be greater than start_across_track_angle_rad")
    step = (end_f - start_f) / (count - 1)
    return tuple(start_f + i * step for i in range(count))


def simulate_mills_cross_multibeam_fan(
    *,
    configuration: MillsCrossConfiguration,
    start_across_track_angle_rad: float,
    end_across_track_angle_rad: float,
    beam_count: int,
    transmit_steering_along_track_angle_rad: float = 0.0,
    transmit_steering_across_track_angle_rad: float = 0.0,
    receive_steering_along_track_angle_rad: float = 0.0,
    frequency_hz: float,
    sound_speed_mps: float,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> MillsCrossMultibeamFan:
    """Build a complete uniformly spaced Port-to-Starboard receive fan.

    The source samples used for the response matrix coincide with the receive
    steering angles. This yields a deterministic N-by-N characterization of beam
    localization and overlap while preserving one common physical TX field and
    one common physical RX aperture.
    """

    receive_angles = _linear_angles(
        start_across_track_angle_rad,
        end_across_track_angle_rad,
        beam_count,
    )

    tx_steering = sensor_angular_direction(
        transmit_steering_along_track_angle_rad,
        transmit_steering_across_track_angle_rad,
    )

    beams: list[MultibeamFanBeam] = []
    for index, across in enumerate(receive_angles):
        direction = sensor_angular_direction(receive_steering_along_track_angle_rad, across)
        response = two_way_beam_pattern_sensor_frame(
            transmit_array=configuration.transmit_array,
            receive_array=configuration.receive_array,
            direction_sensor_frame=direction,
            transmit_steering_direction_sensor_frame=tx_steering,
            receive_steering_direction_sensor_frame=direction,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
            transmit_weights=transmit_weights,
            receive_weights=receive_weights,
        )
        beams.append(
            MultibeamFanBeam(
                beam_index=index,
                receive_steering_across_track_angle_rad=across,
                steering_direction_sensor_frame=direction,
                transmit_amplitude_at_beam_center=response.transmit_response.normalized_amplitude,
                receive_amplitude_at_beam_center=response.receive_response.normalized_amplitude,
                two_way_amplitude_at_beam_center=response.normalized_amplitude,
                two_way_power_at_beam_center=response.normalized_power,
            )
        )

    matrix: list[MultibeamFanMatrixSample] = []
    strongest_indices: list[int] = []
    for source_index, source_across in enumerate(receive_angles):
        bank = evaluate_mills_cross_receive_beam_bank(
            configuration=configuration,
            source_along_track_angle_rad=receive_steering_along_track_angle_rad,
            source_across_track_angle_rad=source_across,
            receive_steering_across_track_angles_rad=receive_angles,
            transmit_steering_along_track_angle_rad=transmit_steering_along_track_angle_rad,
            transmit_steering_across_track_angle_rad=transmit_steering_across_track_angle_rad,
            receive_steering_along_track_angle_rad=receive_steering_along_track_angle_rad,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
            transmit_weights=transmit_weights,
            receive_weights=receive_weights,
        )
        strongest_indices.append(bank.strongest_beam_index)
        for beam in bank.beams:
            matrix.append(
                MultibeamFanMatrixSample(
                    source_index=source_index,
                    source_across_track_angle_rad=source_across,
                    beam_index=beam.beam_index,
                    beam_steering_across_track_angle_rad=beam.receive_steering_across_track_angle_rad,
                    normalized_power=beam.normalized_power,
                )
            )

    return MillsCrossMultibeamFan(
        configuration_name=configuration.name,
        transmit_steering_along_track_angle_rad=transmit_steering_along_track_angle_rad,
        transmit_steering_across_track_angle_rad=transmit_steering_across_track_angle_rad,
        receive_steering_along_track_angle_rad=receive_steering_along_track_angle_rad,
        receive_steering_across_track_angles_rad=receive_angles,
        beams=tuple(beams),
        response_matrix=tuple(matrix),
        strongest_beam_index_by_source=tuple(strongest_indices),
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
    )

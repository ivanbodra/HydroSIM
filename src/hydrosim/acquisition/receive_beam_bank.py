"""Receive-beam bank for a Mills-Cross multibeam configuration.

This layer represents the important MBES distinction between one transmitted
field and multiple simultaneously evaluated receive steering hypotheses. It is
still a normalized far-field narrowband model: a beam in this module is a
processing/steering hypothesis, not a separate physical receive array.
"""

from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import MillsCrossConfiguration

from .angular_pattern_2d import sensor_angular_direction
from .two_way_pattern import two_way_beam_pattern_sensor_frame


class ReceiveBeamResponse(BaseModel):
    """Two-way response of one receive steering hypothesis to one direction."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    receive_steering_across_track_angle_rad: FiniteFloat
    transmit_amplitude: FiniteFloat = Field(ge=0.0)
    receive_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_power: FiniteFloat = Field(ge=0.0)


class ReceiveBeamBankResponse(BaseModel):
    """Responses of several receive beams to one physical acoustic direction."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    source_along_track_angle_rad: FiniteFloat
    source_across_track_angle_rad: FiniteFloat
    transmit_steering_along_track_angle_rad: FiniteFloat
    transmit_steering_across_track_angle_rad: FiniteFloat
    beams: tuple[ReceiveBeamResponse, ...]
    strongest_beam_index: int = Field(ge=0)
    strongest_beam_power: FiniteFloat = Field(ge=0.0)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)


def evaluate_mills_cross_receive_beam_bank(
    *,
    configuration: MillsCrossConfiguration,
    source_along_track_angle_rad: float,
    source_across_track_angle_rad: float,
    receive_steering_across_track_angles_rad: Sequence[float],
    transmit_steering_along_track_angle_rad: float = 0.0,
    transmit_steering_across_track_angle_rad: float = 0.0,
    receive_steering_along_track_angle_rad: float = 0.0,
    frequency_hz: float,
    sound_speed_mps: float,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> ReceiveBeamBankResponse:
    """Evaluate many RX steering hypotheses against one physical direction.

    The TX steering is common to the whole bank. Each RX beam differs only in
    its steering direction; all beams use the same physical receive aperture.
    This is the appropriate abstraction for a first multibeam receive fan and
    deliberately does not duplicate the receive transducer geometry.
    """

    if not receive_steering_across_track_angles_rad:
        raise ValueError("receive_steering_across_track_angles_rad must not be empty")

    source = sensor_angular_direction(
        source_along_track_angle_rad,
        source_across_track_angle_rad,
    )
    tx_steering = sensor_angular_direction(
        transmit_steering_along_track_angle_rad,
        transmit_steering_across_track_angle_rad,
    )

    beams: list[ReceiveBeamResponse] = []
    for index, across in enumerate(receive_steering_across_track_angles_rad):
        rx_steering = sensor_angular_direction(
            receive_steering_along_track_angle_rad,
            float(across),
        )
        response = two_way_beam_pattern_sensor_frame(
            transmit_array=configuration.transmit_array,
            receive_array=configuration.receive_array,
            direction_sensor_frame=source,
            transmit_steering_direction_sensor_frame=tx_steering,
            receive_steering_direction_sensor_frame=rx_steering,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
            transmit_weights=transmit_weights,
            receive_weights=receive_weights,
        )
        beams.append(
            ReceiveBeamResponse(
                beam_index=index,
                receive_steering_across_track_angle_rad=float(across),
                transmit_amplitude=response.transmit_response.normalized_amplitude,
                receive_amplitude=response.receive_response.normalized_amplitude,
                normalized_amplitude=response.normalized_amplitude,
                normalized_power=response.normalized_power,
            )
        )

    strongest = max(beams, key=lambda beam: float(beam.normalized_power))
    return ReceiveBeamBankResponse(
        configuration_name=configuration.name,
        source_along_track_angle_rad=source_along_track_angle_rad,
        source_across_track_angle_rad=source_across_track_angle_rad,
        transmit_steering_along_track_angle_rad=transmit_steering_along_track_angle_rad,
        transmit_steering_across_track_angle_rad=transmit_steering_across_track_angle_rad,
        beams=tuple(beams),
        strongest_beam_index=strongest.beam_index,
        strongest_beam_power=strongest.normalized_power,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
    )

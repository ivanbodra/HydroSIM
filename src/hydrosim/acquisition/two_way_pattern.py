"""Generic two-way beam-pattern composition.

HydroSIM keeps transmit and receive apertures independent. A Mills-Cross MBES is
therefore one configuration of this model, not a global assumption about MBES or
sonars in general.

For normalized one-way complex field responses B_tx and B_rx evaluated toward the
same physical direction, the reference two-way response is

    B_2w = B_tx * B_rx

and normalized two-way power is |B_2w|^2. TX and RX may use different arrays,
installation orientations, steering directions, and complex element weights.
"""

from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3

from .beam_pattern import OneWayBeamPatternResponse, one_way_beam_pattern


class TwoWayBeamPatternResponse(BaseModel):
    """Normalized TX-times-RX complex field response in one physical direction."""

    model_config = ConfigDict(frozen=True)

    transmit_array_name: str = Field(min_length=1)
    receive_array_name: str = Field(min_length=1)
    direction_sensor_frame: Vector3 | None = None
    direction_navigation_frame: Vector3 | None = None
    transmit_direction_array_frame: Vector3
    receive_direction_array_frame: Vector3
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    transmit_response: OneWayBeamPatternResponse
    receive_response: OneWayBeamPatternResponse
    field_real: FiniteFloat
    field_imag: FiniteFloat
    normalized_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_power: FiniteFloat = Field(ge=0.0)


def two_way_beam_pattern(
    *,
    transmit_array: TransducerArray,
    receive_array: TransducerArray,
    transmit_direction_array_frame: Vector3,
    receive_direction_array_frame: Vector3,
    transmit_steering_direction_array_frame: Vector3,
    receive_steering_direction_array_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
    direction_sensor_frame: Vector3 | None = None,
    direction_navigation_frame: Vector3 | None = None,
) -> TwoWayBeamPatternResponse:
    """Compose independent TX and RX one-way responses from local directions.

    The two direction arguments represent the *same physical field direction*
    expressed separately in the TX-array and RX-array local frames. This low-level
    form is useful when those local components are already available.
    """

    tx = one_way_beam_pattern(
        array=transmit_array,
        source_direction_array_frame=transmit_direction_array_frame,
        steering_direction_array_frame=transmit_steering_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        weights=transmit_weights,
    )
    rx = one_way_beam_pattern(
        array=receive_array,
        source_direction_array_frame=receive_direction_array_frame,
        steering_direction_array_frame=receive_steering_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        weights=receive_weights,
    )

    tx_field = complex(tx.field_real, tx.field_imag)
    rx_field = complex(rx.field_real, rx.field_imag)
    field = tx_field * rx_field
    amplitude = abs(field)

    return TwoWayBeamPatternResponse(
        transmit_array_name=transmit_array.name,
        receive_array_name=receive_array.name,
        direction_sensor_frame=direction_sensor_frame,
        direction_navigation_frame=direction_navigation_frame,
        transmit_direction_array_frame=tx.source_direction_array_frame,
        receive_direction_array_frame=rx.source_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        transmit_response=tx,
        receive_response=rx,
        field_real=field.real,
        field_imag=field.imag,
        normalized_amplitude=amplitude,
        normalized_power=amplitude * amplitude,
    )


def two_way_beam_pattern_sensor_frame(
    *,
    transmit_array: TransducerArray,
    receive_array: TransducerArray,
    direction_sensor_frame: Vector3,
    transmit_steering_direction_sensor_frame: Vector3,
    receive_steering_direction_sensor_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> TwoWayBeamPatternResponse:
    """Evaluate a two-way response from one common sensor-frame direction.

    ``TransducerArray.orientation`` defines ``R_SA``, the fixed array-to-sensor
    rotation. The same physical source direction is transformed independently:

        u_A_tx = R_SA_tx.T @ u_S
        u_A_rx = R_SA_rx.T @ u_S

    Steering directions are transformed by the same rule. This is the explicit
    orientation bridge required for co-aligned, skewed, and orthogonal TX/RX
    installations, including Mills-Cross arrangements.
    """

    tx_direction = transmit_array.direction_from_sensor_frame(direction_sensor_frame)
    rx_direction = receive_array.direction_from_sensor_frame(direction_sensor_frame)
    tx_steering = transmit_array.direction_from_sensor_frame(
        transmit_steering_direction_sensor_frame
    )
    rx_steering = receive_array.direction_from_sensor_frame(
        receive_steering_direction_sensor_frame
    )

    return two_way_beam_pattern(
        transmit_array=transmit_array,
        receive_array=receive_array,
        transmit_direction_array_frame=tx_direction,
        receive_direction_array_frame=rx_direction,
        transmit_steering_direction_array_frame=tx_steering,
        receive_steering_direction_array_frame=rx_steering,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        transmit_weights=transmit_weights,
        receive_weights=receive_weights,
        direction_sensor_frame=direction_sensor_frame,
    )

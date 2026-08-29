"""Vendor-neutral transmit-array delay law.

For a far-field unit direction ``u`` pointing away from the array and element
position ``r_i`` relative to the array centre, equal arrival time at a distant
wavefront requires the relative emission epoch

    dt_i = (u . r_i) / c_used.

``c_used`` is sonar processing state, never simulation Truth. Hardware delays are
reported after subtracting the minimum relative epoch so all applied delays are
non-negative while preserving the same steering law.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3

from .sound_speed_processing import SoundSpeedAtTransducerUse
from .transmit_sectors import TransmitSector


class TransmitElementSteeringDelay(BaseModel):
    """Relative and non-negative hardware delay for one transmit element."""

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    element_position_array_frame: Vector3
    relative_emission_offset_seconds: FiniteFloat
    hardware_delay_seconds: FiniteFloat = Field(ge=0.0)


class TransmitSteeringLaw(BaseModel):
    """Transmit steering law formed entirely from sonar-known state."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    sector_index: int = Field(ge=0)
    steering_direction_array_frame: Vector3
    sound_speed_at_transducer: SoundSpeedAtTransducerUse
    element_delays: tuple[TransmitElementSteeringDelay, ...]


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def ideal_transmit_steering(
    *,
    transmit_array: TransducerArray,
    sector: TransmitSector,
    sound_speed_at_transducer: SoundSpeedAtTransducerUse,
) -> TransmitSteeringLaw:
    """Build the ideal TX element delay law for one sector.

    The current reference implementation assumes the sector steering direction is
    expressed in a frame aligned with the transmit-array local frame. Explicit
    sensor-to-array alignment can be inserted later without changing the sound-speed
    state boundary.
    """

    if transmit_array.role not in {"tx", "txrx"}:
        raise ValueError("transmit_array must have role 'tx' or 'txrx'")

    c_used = float(sound_speed_at_transducer.sound_speed_mps)
    direction = sector.steering_direction_sensor_frame
    raw: list[tuple[object, float]] = []
    for element in transmit_array.elements():
        raw.append((element, _dot(direction, element.position) / c_used))

    minimum = min((offset for _, offset in raw), default=0.0)
    delays = tuple(
        TransmitElementSteeringDelay(
            index_x=element.index_x,
            index_y=element.index_y,
            element_position_array_frame=element.position,
            relative_emission_offset_seconds=offset,
            hardware_delay_seconds=offset - minimum,
        )
        for element, offset in raw
    )
    return TransmitSteeringLaw(
        array_name=transmit_array.name,
        sector_index=sector.sector_index,
        steering_direction_array_frame=direction,
        sound_speed_at_transducer=sound_speed_at_transducer,
        element_delays=delays,
    )

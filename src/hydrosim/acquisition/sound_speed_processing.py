"""Sound speed at transducer as used by sonar processing.

The sensor measurement and the value actually used by the sonar are distinct
states. A system may use the current sensor observation, a manually entered value,
a value derived from a profile, or a previously held value. None of these states
contains simulation Truth.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .sound_speed_sensor import SoundSpeedAtTransducerMeasurement


SoundSpeedAtTransducerSource = Literal[
    "sensor_measurement",
    "manual",
    "profile_interpolation",
    "held_previous",
]


class SoundSpeedAtTransducerUse(BaseModel):
    """Value and provenance available to sonar steering/processing."""

    model_config = ConfigDict(frozen=True)

    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    source: SoundSpeedAtTransducerSource


def use_measured_sound_speed_at_transducer(
    measurement: SoundSpeedAtTransducerMeasurement,
) -> SoundSpeedAtTransducerUse:
    """Select the current sensor measurement as the value used by the sonar."""

    return SoundSpeedAtTransducerUse(
        sound_speed_mps=float(measurement.measured_sound_speed_mps),
        source="sensor_measurement",
    )


def use_manual_sound_speed_at_transducer(sound_speed_mps: float) -> SoundSpeedAtTransducerUse:
    """Represent an explicitly entered processing value without implying Truth."""

    return SoundSpeedAtTransducerUse(sound_speed_mps=float(sound_speed_mps), source="manual")

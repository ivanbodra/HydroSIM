"""Measurement model for the sound-speed sensor at the transducer face.

The synthetic world owns the true local sound speed. The sonar does not have
access to that truth; it receives a sensor measurement, which may contain bias,
noise, quantization, or latency in later extensions.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class SoundSpeedSensorAtTransducer(BaseModel):
    """Reference sensor model for sound speed measured at the transducer face."""

    model_config = ConfigDict(frozen=True)

    bias_mps: FiniteFloat = 0.0


class SoundSpeedAtTransducerMeasurement(BaseModel):
    """Sensor observation available to the sonar processing chain."""

    model_config = ConfigDict(frozen=True)

    measured_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    sensor_bias_mps: FiniteFloat


def measure_sound_speed_at_transducer(
    *,
    true_local_sound_speed_mps: float,
    sensor: SoundSpeedSensorAtTransducer = SoundSpeedSensorAtTransducer(),
) -> SoundSpeedAtTransducerMeasurement:
    """Generate a sensor measurement from simulation truth.

    ``true_local_sound_speed_mps`` belongs to the synthetic Truth state and is
    intentionally not stored in the returned measurement available to sonar
    processing.
    """

    true_c = float(true_local_sound_speed_mps)
    if true_c <= 0.0:
        raise ValueError("true_local_sound_speed_mps must be positive")
    measured_c = true_c + float(sensor.bias_mps)
    if measured_c <= 0.0:
        raise ValueError("sound-speed sensor measurement must be positive")
    return SoundSpeedAtTransducerMeasurement(
        measured_sound_speed_mps=measured_c,
        sensor_bias_mps=float(sensor.bias_mps),
    )

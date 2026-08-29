"""Ideal receive-array steering geometry for HydroSIM.

This module deliberately stops before waveform summation. It converts a hypothesized
source direction into the inter-element arrival-time pattern expected for a plane
wave in a homogeneous medium, then compares that pattern with Truth element arrivals.

For an element position ``r_i`` relative to the array centre and a unit vector ``u``
pointing from the array centre toward the acoustic source, the far-field arrival
offset is

    dt_i = -(u . r_i) / c

because an element displaced toward the source has a shorter propagation path and
therefore receives the wavefront earlier.
"""

from __future__ import annotations

from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3, rotate_vector, rotation_x

from .reception import ArrayTruthReception
from .sound_speed_processing import SoundSpeedAtTransducerUse, use_measured_sound_speed_at_transducer
from .sound_speed_sensor import SoundSpeedAtTransducerMeasurement


class ReceiveElementSteeringDelay(BaseModel):
    """Ideal plane-wave arrival offset predicted for one receive-array element."""

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    element_position_array_frame: Vector3
    predicted_arrival_offset_seconds: FiniteFloat
    compensation_delay_seconds: FiniteFloat


class ReceiveSteeringHypothesis(BaseModel):
    """One ideal receive steering direction and its element delay law."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    across_track_angle_rad: FiniteFloat
    direction_to_source_array_frame: Vector3
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    element_delays: tuple[ReceiveElementSteeringDelay, ...]


class ReceiveSteeringEvaluation(BaseModel):
    """Mismatch between Truth element arrivals and an ideal steering hypothesis."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    array_name: str = Field(min_length=1)
    hypothesis: ReceiveSteeringHypothesis
    residual_seconds: tuple[FiniteFloat, ...]
    rms_residual_seconds: FiniteFloat = Field(ge=0.0)
    max_abs_residual_seconds: FiniteFloat = Field(ge=0.0)


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def _unit(vector: Vector3) -> Vector3:
    norm = sqrt(_dot(vector, vector))
    if norm <= 1e-15:
        raise ValueError("steering direction must be non-zero")
    return Vector3(x=vector.x / norm, y=vector.y / norm, z=vector.z / norm)


def ideal_receive_steering(
    *,
    receive_array: TransducerArray,
    across_track_angle_rad: float,
    sound_speed_mps: float,
) -> ReceiveSteeringHypothesis:
    """Build the far-field plane-wave delay law for one across-track direction.

    HydroSIM across-track convention is preserved: zero is the array-local +Z
    normal, positive angles point Port (-Y), and negative angles point Starboard
    (+Y). ``compensation_delay_seconds`` is the opposite of the predicted physical
    arrival offset and is the time shift that would align that ideal wavefront to
    the array-centre epoch.
    """

    if receive_array.role not in {"rx", "txrx"}:
        raise ValueError("receive_array must have role 'rx' or 'txrx'")
    c = float(sound_speed_mps)
    if c <= 0.0:
        raise ValueError("sound_speed_mps must be > 0")

    normal = Vector3(x=0.0, y=0.0, z=1.0)
    direction = _unit(rotate_vector(rotation_x(float(across_track_angle_rad)), normal))

    delays: list[ReceiveElementSteeringDelay] = []
    for element in receive_array.elements():
        arrival_offset = -_dot(direction, element.position) / c
        delays.append(
            ReceiveElementSteeringDelay(
                index_x=element.index_x,
                index_y=element.index_y,
                element_position_array_frame=element.position,
                predicted_arrival_offset_seconds=arrival_offset,
                compensation_delay_seconds=-arrival_offset,
            )
        )

    return ReceiveSteeringHypothesis(
        array_name=receive_array.name,
        across_track_angle_rad=across_track_angle_rad,
        direction_to_source_array_frame=direction,
        sound_speed_mps=c,
        element_delays=tuple(delays),
    )


def ideal_receive_steering_from_sound_speed_use(
    *,
    receive_array: TransducerArray,
    across_track_angle_rad: float,
    sound_speed_at_transducer: SoundSpeedAtTransducerUse,
) -> ReceiveSteeringHypothesis:
    """Build receive steering from the explicit sound-speed state used by the sonar."""

    return ideal_receive_steering(
        receive_array=receive_array,
        across_track_angle_rad=across_track_angle_rad,
        sound_speed_mps=float(sound_speed_at_transducer.sound_speed_mps),
    )


def ideal_receive_steering_from_sound_speed_measurement(
    *,
    receive_array: TransducerArray,
    across_track_angle_rad: float,
    sound_speed_measurement: SoundSpeedAtTransducerMeasurement,
) -> ReceiveSteeringHypothesis:
    """Convenience wrapper selecting the current sensor measurement for processing."""

    return ideal_receive_steering_from_sound_speed_use(
        receive_array=receive_array,
        across_track_angle_rad=across_track_angle_rad,
        sound_speed_at_transducer=use_measured_sound_speed_at_transducer(sound_speed_measurement),
    )


def evaluate_receive_steering(
    *,
    reception: ArrayTruthReception,
    hypothesis: ReceiveSteeringHypothesis,
) -> ReceiveSteeringEvaluation:
    """Compare Truth inter-element arrivals with one ideal plane-wave hypothesis.

    The comparison is intentionally time-domain and geometric. It does not yet
    calculate phase, array factor, coherent summation, amplitude, sidelobes, or
    detection statistics. A zero residual means the Truth arrival pattern matches
    the ideal far-field delay law exactly.
    """

    if reception.array_name != hypothesis.array_name:
        raise ValueError("reception and steering hypothesis must reference the same array")
    if len(reception.element_arrivals) != len(hypothesis.element_delays):
        raise ValueError("reception and steering hypothesis element counts differ")

    residuals: list[float] = []
    for arrival, predicted in zip(
        reception.element_arrivals, hypothesis.element_delays, strict=True
    ):
        if (arrival.index_x, arrival.index_y) != (predicted.index_x, predicted.index_y):
            raise ValueError("reception and steering hypothesis element ordering differs")
        residuals.append(
            float(arrival.relative_to_array_center_seconds)
            - float(predicted.predicted_arrival_offset_seconds)
        )

    if residuals:
        rms = sqrt(sum(value * value for value in residuals) / len(residuals))
        maximum = max(abs(value) for value in residuals)
    else:
        rms = 0.0
        maximum = 0.0

    return ReceiveSteeringEvaluation(
        beam_index=reception.beam_index,
        array_name=reception.array_name,
        hypothesis=hypothesis,
        residual_seconds=tuple(residuals),
        rms_residual_seconds=rms,
        max_abs_residual_seconds=maximum,
    )

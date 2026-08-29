"""Ideal narrowband array-factor model for HydroSIM.

This module evaluates the phase-coherent response produced only by the spatial
placement and complex weighting of array elements. Element directivity is kept
separate in ``element_factor.py`` so the physical beam pattern can later be formed
explicitly as

    element factor * array factor.

For a source direction ``u`` and steering direction ``u0``, both expressed as unit
vectors pointing from the array centre toward the acoustic source/field direction,
the residual spatial phase at element position ``r_i`` is

    phi_i = k (u - u0) . r_i,

with ``k = 2*pi/lambda``. This sign convention is consistent with HydroSIM's
existing arrival-time and steering-delay definitions.
"""

from __future__ import annotations

from cmath import exp
from math import pi, sqrt
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3


class ArrayFactorElementContribution(BaseModel):
    """Complex contribution of one physical array element."""

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    position_array_frame: Vector3
    weight_real: FiniteFloat
    weight_imag: FiniteFloat
    residual_phase_rad: FiniteFloat
    contribution_real: FiniteFloat
    contribution_imag: FiniteFloat


class ArrayFactorResponse(BaseModel):
    """Normalized one-way complex array factor for one source/steering pair."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    source_direction_array_frame: Vector3
    steering_direction_array_frame: Vector3
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    wavelength_m: FiniteFloat = Field(gt=0.0)
    element_contributions: tuple[ArrayFactorElementContribution, ...]
    coherent_real: FiniteFloat
    coherent_imag: FiniteFloat
    normalization: FiniteFloat = Field(gt=0.0)
    normalized_magnitude: FiniteFloat = Field(ge=0.0, le=1.000000000001)
    normalized_power: FiniteFloat = Field(ge=0.0, le=1.000000000002)


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def _unit(vector: Vector3) -> Vector3:
    norm = sqrt(_dot(vector, vector))
    if norm <= 1e-15:
        raise ValueError("direction vector must be non-zero")
    return Vector3(x=vector.x / norm, y=vector.y / norm, z=vector.z / norm)


def array_factor(
    *,
    array: TransducerArray,
    source_direction_array_frame: Vector3,
    steering_direction_array_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
    weights: Sequence[complex] | None = None,
) -> ArrayFactorResponse:
    """Evaluate the ideal far-field narrowband array factor.

    ``source_direction_array_frame`` and ``steering_direction_array_frame`` both
    point from the array centre toward the source/field direction. Uniform unit
    weights are used when ``weights`` is omitted.

    The response is normalized by the sum of the magnitudes of the complex element
    weights. Therefore a perfectly phase-aligned set of contributions has normalized
    magnitude 1.0 regardless of overall weight scale. This quantity is a normalized
    one-way voltage/pressure-like array response, not absolute acoustic gain.
    """

    frequency = float(frequency_hz)
    sound_speed = float(sound_speed_mps)
    if frequency <= 0.0:
        raise ValueError("frequency_hz must be > 0")
    if sound_speed <= 0.0:
        raise ValueError("sound_speed_mps must be > 0")

    source = _unit(source_direction_array_frame)
    steering = _unit(steering_direction_array_frame)
    elements = array.elements()

    if weights is None:
        element_weights = tuple(1.0 + 0.0j for _ in elements)
    else:
        element_weights = tuple(complex(value) for value in weights)
        if len(element_weights) != len(elements):
            raise ValueError("weights must contain exactly one complex value per array element")

    normalization = sum(abs(weight) for weight in element_weights)
    if normalization <= 0.0:
        raise ValueError("at least one array weight must be non-zero")

    wavelength = sound_speed / frequency
    k = 2.0 * pi / wavelength
    delta = Vector3(
        x=source.x - steering.x,
        y=source.y - steering.y,
        z=source.z - steering.z,
    )

    total = 0j
    contributions: list[ArrayFactorElementContribution] = []
    for element, weight in zip(elements, element_weights, strict=True):
        phase = k * _dot(delta, element.position)
        contribution = weight * exp(1j * phase)
        total += contribution
        contributions.append(
            ArrayFactorElementContribution(
                index_x=element.index_x,
                index_y=element.index_y,
                position_array_frame=element.position,
                weight_real=weight.real,
                weight_imag=weight.imag,
                residual_phase_rad=phase,
                contribution_real=contribution.real,
                contribution_imag=contribution.imag,
            )
        )

    magnitude = abs(total) / normalization
    # Protect the Pydantic bound against insignificant floating overshoot at unity.
    if 1.0 < magnitude < 1.0 + 1e-12:
        magnitude = 1.0

    return ArrayFactorResponse(
        array_name=array.name,
        source_direction_array_frame=source,
        steering_direction_array_frame=steering,
        frequency_hz=frequency,
        sound_speed_mps=sound_speed,
        wavelength_m=wavelength,
        element_contributions=tuple(contributions),
        coherent_real=total.real,
        coherent_imag=total.imag,
        normalization=normalization,
        normalized_magnitude=magnitude,
        normalized_power=magnitude * magnitude,
    )

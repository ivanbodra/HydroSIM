"""Reference split-aperture receive processing.

This module provides the physical-array prerequisite for phase-ramp bottom
detection without assuming a proprietary vendor implementation. It partitions an
existing receive array into two explicit subapertures and independently sums the
already-steered element phasors.

The present result is an instantaneous/narrowband split-aperture response for one
source direction. It does not by itself create the time-varying phase ramp needed
for bottom detection; that requires a sequence of contributions with changing
arrival geometry across the echo footprint.
"""

from __future__ import annotations

from cmath import phase
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3

from .element_signals import CoherentReceiveSum

SplitAxis = Literal["x", "y"]
CenterElementPolicy = Literal["exclude", "negative", "positive", "both"]


class SplitApertureDefinition(BaseModel):
    """Explicit partition rule in the receive-array local frame."""

    model_config = ConfigDict(frozen=True)

    axis: SplitAxis = "y"
    split_coordinate_m: FiniteFloat = 0.0
    center_element_policy: CenterElementPolicy = "exclude"


class SplitAperturePhaseCenters(BaseModel):
    """Geometric phase centres of the two receive subapertures.

    The centres are simple arithmetic centroids of the physical element-centre
    positions selected by ``SplitApertureDefinition``. They are a transparent
    reference geometry, not a claim about any vendor's effective phase-centre
    calibration or frequency-dependent receive electronics.
    """

    model_config = ConfigDict(frozen=True)

    definition: SplitApertureDefinition
    negative_element_count: int = Field(gt=0)
    positive_element_count: int = Field(gt=0)
    negative_center_array_frame: Vector3
    positive_center_array_frame: Vector3
    negative_to_positive_baseline_array_frame: Vector3
    baseline_length_m: FiniteFloat = Field(gt=0.0)


class SubapertureCoherentSum(BaseModel):
    """Coherent complex response of one subaperture."""

    model_config = ConfigDict(frozen=True)

    side: Literal["negative", "positive"]
    element_indices: tuple[tuple[int, int], ...]
    element_count: int = Field(gt=0)
    coherent_real: FiniteFloat
    coherent_imag: FiniteFloat
    coherent_magnitude: FiniteFloat = Field(ge=0.0)
    normalized_magnitude: FiniteFloat = Field(ge=0.0, le=1.000000000001)


class SplitApertureResponse(BaseModel):
    """Two subaperture sums and their differential phase."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    array_name: str = Field(min_length=1)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    definition: SplitApertureDefinition
    negative: SubapertureCoherentSum
    positive: SubapertureCoherentSum
    differential_phase_rad: FiniteFloat


def _coordinate(array: TransducerArray, index_x: int, index_y: int, axis: SplitAxis) -> float:
    for element in array.elements():
        if (element.index_x, element.index_y) == (index_x, index_y):
            return float(element.position.x if axis == "x" else element.position.y)
    raise ValueError("element phasor does not exist in receive array")


def _membership(
    coordinate: float,
    *,
    split: float,
    policy: CenterElementPolicy,
) -> tuple[bool, bool]:
    tolerance = 1e-15
    if coordinate < split - tolerance:
        return True, False
    if coordinate > split + tolerance:
        return False, True
    if policy == "exclude":
        return False, False
    if policy == "negative":
        return True, False
    if policy == "positive":
        return False, True
    return True, True


def _centroid(points: list[Vector3]) -> Vector3:
    count = len(points)
    if count == 0:
        raise ValueError("cannot calculate an empty subaperture phase centre")
    return Vector3(
        x=sum(float(point.x) for point in points) / count,
        y=sum(float(point.y) for point in points) / count,
        z=sum(float(point.z) for point in points) / count,
    )


def split_aperture_phase_centers(
    *,
    receive_array: TransducerArray,
    definition: SplitApertureDefinition = SplitApertureDefinition(),
) -> SplitAperturePhaseCenters:
    """Return the physical-element centroids of the two split subapertures."""

    if receive_array.role not in {"rx", "txrx"}:
        raise ValueError("receive_array must have role 'rx' or 'txrx'")

    negative_points: list[Vector3] = []
    positive_points: list[Vector3] = []
    for element in receive_array.elements():
        coordinate = float(element.position.x if definition.axis == "x" else element.position.y)
        use_negative, use_positive = _membership(
            coordinate,
            split=float(definition.split_coordinate_m),
            policy=definition.center_element_policy,
        )
        if use_negative:
            negative_points.append(element.position)
        if use_positive:
            positive_points.append(element.position)

    negative = _centroid(negative_points)
    positive = _centroid(positive_points)
    baseline = Vector3(
        x=float(positive.x) - float(negative.x),
        y=float(positive.y) - float(negative.y),
        z=float(positive.z) - float(negative.z),
    )
    length = (float(baseline.x) ** 2 + float(baseline.y) ** 2 + float(baseline.z) ** 2) ** 0.5
    if length <= 0.0:
        raise ValueError("split-aperture phase centres must be spatially distinct")

    return SplitAperturePhaseCenters(
        definition=definition,
        negative_element_count=len(negative_points),
        positive_element_count=len(positive_points),
        negative_center_array_frame=negative,
        positive_center_array_frame=positive,
        negative_to_positive_baseline_array_frame=baseline,
        baseline_length_m=length,
    )


def split_coherent_receive_sum(
    *,
    receive_array: TransducerArray,
    coherent_sum: CoherentReceiveSum,
    definition: SplitApertureDefinition = SplitApertureDefinition(),
) -> SplitApertureResponse:
    """Partition and sum the steered element phasors into two subapertures.

    Differential phase follows

        dphi = arg(z_negative * conj(z_positive)).

    The split is defined in array-local coordinates, so installation orientation
    does not silently change which physical elements belong to each half.
    """

    if receive_array.name != coherent_sum.array_name:
        raise ValueError("receive_array and coherent_sum must reference the same array")
    if receive_array.role not in {"rx", "txrx"}:
        raise ValueError("receive_array must have role 'rx' or 'txrx'")

    negative_values: list[complex] = []
    positive_values: list[complex] = []
    negative_indices: list[tuple[int, int]] = []
    positive_indices: list[tuple[int, int]] = []

    for phasor in coherent_sum.element_phasors:
        coordinate = _coordinate(
            receive_array,
            phasor.index_x,
            phasor.index_y,
            definition.axis,
        )
        use_negative, use_positive = _membership(
            coordinate,
            split=float(definition.split_coordinate_m),
            policy=definition.center_element_policy,
        )
        value = complex(float(phasor.real), float(phasor.imag))
        index = (phasor.index_x, phasor.index_y)
        if use_negative:
            negative_values.append(value)
            negative_indices.append(index)
        if use_positive:
            positive_values.append(value)
            positive_indices.append(index)

    if not negative_values or not positive_values:
        raise ValueError("split aperture must contain at least one element on each side")

    negative_sum = sum(negative_values, 0j)
    positive_sum = sum(positive_values, 0j)

    negative = SubapertureCoherentSum(
        side="negative",
        element_indices=tuple(negative_indices),
        element_count=len(negative_values),
        coherent_real=negative_sum.real,
        coherent_imag=negative_sum.imag,
        coherent_magnitude=abs(negative_sum),
        normalized_magnitude=abs(negative_sum) / len(negative_values),
    )
    positive = SubapertureCoherentSum(
        side="positive",
        element_indices=tuple(positive_indices),
        element_count=len(positive_values),
        coherent_real=positive_sum.real,
        coherent_imag=positive_sum.imag,
        coherent_magnitude=abs(positive_sum),
        normalized_magnitude=abs(positive_sum) / len(positive_values),
    )

    differential = phase(negative_sum * positive_sum.conjugate())
    return SplitApertureResponse(
        beam_index=coherent_sum.beam_index,
        array_name=coherent_sum.array_name,
        frequency_hz=coherent_sum.frequency_hz,
        definition=definition,
        negative=negative,
        positive=positive,
        differential_phase_rad=differential,
    )

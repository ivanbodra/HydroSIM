"""One-way narrowband physical beam-pattern composition for HydroSIM.

The first physical beam pattern combines two deliberately separate models:

    beam field = rectangular element factor * array factor

This is a normalized far-field narrowband response. It is not yet a calibrated
source level, receive sensitivity, or two-way sonar response.
"""

from __future__ import annotations

from math import cos, sin
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3

from .array_factor import ArrayFactorResponse, array_factor
from .element_factor import RectangularElementFactor, rectangular_element_factor


class OneWayBeamPatternResponse(BaseModel):
    """Normalized one-way element-times-array field response."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    source_direction_array_frame: Vector3
    steering_direction_array_frame: Vector3
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    element_factor: RectangularElementFactor
    array_factor: ArrayFactorResponse
    field_real: FiniteFloat
    field_imag: FiniteFloat
    normalized_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_power: FiniteFloat = Field(ge=0.0)


class AcrossTrackBeamPatternSample(BaseModel):
    """One angular sample of an across-track beam-pattern scan."""

    model_config = ConfigDict(frozen=True)

    angle_rad: FiniteFloat
    element_factor_power: FiniteFloat = Field(ge=0.0)
    array_factor_power: FiniteFloat = Field(ge=0.0)
    normalized_amplitude: FiniteFloat = Field(ge=0.0)
    normalized_power: FiniteFloat = Field(ge=0.0)


class AcrossTrackBeamPatternScan(BaseModel):
    """Deterministic across-track scan of a one-way beam pattern."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    steering_angle_rad: FiniteFloat
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    wavelength_m: FiniteFloat = Field(gt=0.0)
    samples: tuple[AcrossTrackBeamPatternSample, ...]
    peak_angle_rad: FiniteFloat
    peak_power: FiniteFloat = Field(ge=0.0)
    half_power_left_angle_rad: FiniteFloat | None = None
    half_power_right_angle_rad: FiniteFloat | None = None
    half_power_beamwidth_rad: FiniteFloat | None = Field(default=None, ge=0.0)


def across_track_direction(angle_rad: float) -> Vector3:
    """Return HydroSIM across-track unit direction: +angle is Port (-Y)."""

    angle = float(angle_rad)
    return Vector3(x=0.0, y=-sin(angle), z=cos(angle))


def one_way_beam_pattern(
    *,
    array: TransducerArray,
    source_direction_array_frame: Vector3,
    steering_direction_array_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
    weights: Sequence[complex] | None = None,
    include_element_contributions: bool = True,
) -> OneWayBeamPatternResponse:
    """Combine rectangular element directivity and spatial array factor.

    All array elements currently share the dimensions stored by ``TransducerArray``.
    Therefore the element factor is common to all channels and may be multiplied by
    the normalized complex array factor after coherent summation.
    """

    representative = array.elements()[0]
    element = rectangular_element_factor(
        element=representative,
        direction_array_frame=source_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
    )
    spatial = array_factor(
        array=array,
        source_direction_array_frame=source_direction_array_frame,
        steering_direction_array_frame=steering_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        weights=weights,
        include_element_contributions=include_element_contributions,
    )

    field = complex(spatial.coherent_real, spatial.coherent_imag) / float(spatial.normalization)
    field *= float(element.signed_amplitude)
    amplitude = abs(field)

    return OneWayBeamPatternResponse(
        array_name=array.name,
        source_direction_array_frame=spatial.source_direction_array_frame,
        steering_direction_array_frame=spatial.steering_direction_array_frame,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        element_factor=element,
        array_factor=spatial,
        field_real=field.real,
        field_imag=field.imag,
        normalized_amplitude=amplitude,
        normalized_power=amplitude * amplitude,
    )


def _crossing_angle(a0: float, p0: float, a1: float, p1: float, target: float) -> float:
    """Linearly interpolate an angular threshold crossing."""

    if p1 == p0:
        return 0.5 * (a0 + a1)
    fraction = (target - p0) / (p1 - p0)
    return a0 + fraction * (a1 - a0)


def scan_across_track_beam_pattern(
    *,
    array: TransducerArray,
    steering_angle_rad: float,
    start_angle_rad: float,
    end_angle_rad: float,
    sample_count: int,
    frequency_hz: float,
    sound_speed_mps: float,
    weights: Sequence[complex] | None = None,
) -> AcrossTrackBeamPatternScan:
    """Scan a one-way beam pattern and estimate the local -3 dB beamwidth.

    The scan keeps the element-factor and array-factor powers needed by learner
    views, while suppressing per-element contribution objects that are not consumed
    by an angular scan. The underlying coherent sum and physical response are
    unchanged.
    """

    if sample_count < 3:
        raise ValueError("sample_count must be >= 3")
    start = float(start_angle_rad)
    end = float(end_angle_rad)
    if end <= start:
        raise ValueError("end_angle_rad must be greater than start_angle_rad")

    steering = across_track_direction(steering_angle_rad)
    step = (end - start) / (sample_count - 1)
    samples: list[AcrossTrackBeamPatternSample] = []
    wavelength_m: float | None = None
    for index in range(sample_count):
        angle = start + index * step
        response = one_way_beam_pattern(
            array=array,
            source_direction_array_frame=across_track_direction(angle),
            steering_direction_array_frame=steering,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
            weights=weights,
            include_element_contributions=False,
        )
        if wavelength_m is None:
            wavelength_m = float(response.array_factor.wavelength_m)
        samples.append(
            AcrossTrackBeamPatternSample(
                angle_rad=angle,
                element_factor_power=float(response.element_factor.power),
                array_factor_power=float(response.array_factor.normalized_power),
                normalized_amplitude=response.normalized_amplitude,
                normalized_power=response.normalized_power,
            )
        )

    peak_index = max(range(len(samples)), key=lambda i: float(samples[i].normalized_power))
    peak = samples[peak_index]
    target = 0.5 * float(peak.normalized_power)

    left = None
    for i in range(peak_index, 0, -1):
        inside = float(samples[i].normalized_power)
        outside = float(samples[i - 1].normalized_power)
        if inside >= target and outside < target:
            left = _crossing_angle(
                float(samples[i - 1].angle_rad), outside,
                float(samples[i].angle_rad), inside, target
            )
            break

    right = None
    for i in range(peak_index, len(samples) - 1):
        inside = float(samples[i].normalized_power)
        outside = float(samples[i + 1].normalized_power)
        if inside >= target and outside < target:
            right = _crossing_angle(
                float(samples[i].angle_rad), inside,
                float(samples[i + 1].angle_rad), outside, target
            )
            break

    width = right - left if left is not None and right is not None else None

    return AcrossTrackBeamPatternScan(
        array_name=array.name,
        steering_angle_rad=steering_angle_rad,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        wavelength_m=float(wavelength_m),
        samples=tuple(samples),
        peak_angle_rad=peak.angle_rad,
        peak_power=peak.normalized_power,
        half_power_left_angle_rad=left,
        half_power_right_angle_rad=right,
        half_power_beamwidth_rad=width,
    )

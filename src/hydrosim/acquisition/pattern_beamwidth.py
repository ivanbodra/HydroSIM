"""Derive half-power principal-plane beamwidths from HydroSIM array physics.

This module closes the loop between physical transducer geometry and footprint
models. Rather than accepting nominal beamwidths as independent inputs, it scans
the existing one-way element-times-array response in a common sensor frame and
locates the first half-power crossings around the main-lobe peak.

The scan remains a narrowband far-field approximation. It does not claim that a
single -3 dB width fully describes a real finite-range footprint; it supplies the
same explicit half-power abstraction already used by the flat-seafloor footprint
model, but derives that abstraction from the configured array, steering,
frequency, sound speed and element weights.
"""

from __future__ import annotations

from typing import Literal, Sequence

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import MillsCrossConfiguration, TransducerArray

from .angular_pattern_2d import sensor_angular_direction
from .beam_pattern import one_way_beam_pattern
from .footprint import (
    FlatSeafloorFootprintModel,
    InsonifiedFootprint,
    estimate_flat_seafloor_footprint,
)

PrincipalPlane = Literal["along_track", "across_track"]


class PrincipalPlaneBeamwidth(BaseModel):
    """Half-power width derived from one physical array response."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    plane: PrincipalPlane
    steering_angle_rad: FiniteFloat
    peak_angle_rad: FiniteFloat
    peak_power: FiniteFloat = Field(ge=0.0)
    half_power_left_angle_rad: FiniteFloat
    half_power_right_angle_rad: FiniteFloat
    half_power_beamwidth_rad: FiniteFloat = Field(gt=0.0)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    sample_count: int = Field(ge=3)


def _crossing_angle(a0: float, p0: float, a1: float, p1: float, target: float) -> float:
    if p1 == p0:
        return 0.5 * (a0 + a1)
    return a0 + (target - p0) * (a1 - a0) / (p1 - p0)


def derive_principal_plane_beamwidth(
    *,
    array: TransducerArray,
    plane: PrincipalPlane,
    steering_along_track_angle_rad: float,
    steering_across_track_angle_rad: float,
    start_angle_rad: float,
    end_angle_rad: float,
    sample_count: int,
    frequency_hz: float,
    sound_speed_mps: float,
    weights: Sequence[complex] | None = None,
) -> PrincipalPlaneBeamwidth:
    """Scan one sensor-frame principal plane and derive the local -3 dB width."""

    if sample_count < 3:
        raise ValueError("sample_count must be >= 3")
    start = float(start_angle_rad)
    end = float(end_angle_rad)
    if end <= start:
        raise ValueError("end_angle_rad must be greater than start_angle_rad")

    steering_sensor = sensor_angular_direction(
        steering_along_track_angle_rad,
        steering_across_track_angle_rad,
    )
    steering_local = array.direction_from_sensor_frame(steering_sensor)
    step = (end - start) / (sample_count - 1)
    angles: list[float] = []
    powers: list[float] = []

    for index in range(sample_count):
        angle = start + index * step
        if plane == "along_track":
            direction_sensor = sensor_angular_direction(
                angle,
                steering_across_track_angle_rad,
            )
        elif plane == "across_track":
            direction_sensor = sensor_angular_direction(
                steering_along_track_angle_rad,
                angle,
            )
        else:
            raise ValueError("plane must be 'along_track' or 'across_track'")

        response = one_way_beam_pattern(
            array=array,
            source_direction_array_frame=array.direction_from_sensor_frame(direction_sensor),
            steering_direction_array_frame=steering_local,
            frequency_hz=frequency_hz,
            sound_speed_mps=sound_speed_mps,
            weights=weights,
        )
        angles.append(angle)
        powers.append(float(response.normalized_power))

    peak_index = max(range(sample_count), key=powers.__getitem__)
    peak_power = powers[peak_index]
    target = 0.5 * peak_power

    left = None
    for index in range(peak_index, 0, -1):
        if powers[index] >= target and powers[index - 1] < target:
            left = _crossing_angle(
                angles[index - 1], powers[index - 1], angles[index], powers[index], target
            )
            break

    right = None
    for index in range(peak_index, sample_count - 1):
        if powers[index] >= target and powers[index + 1] < target:
            right = _crossing_angle(
                angles[index], powers[index], angles[index + 1], powers[index + 1], target
            )
            break

    if left is None or right is None:
        raise ValueError("half-power crossings lie outside requested scan interval")

    steering_angle = (
        float(steering_along_track_angle_rad)
        if plane == "along_track"
        else float(steering_across_track_angle_rad)
    )
    return PrincipalPlaneBeamwidth(
        array_name=array.name,
        plane=plane,
        steering_angle_rad=steering_angle,
        peak_angle_rad=angles[peak_index],
        peak_power=peak_power,
        half_power_left_angle_rad=left,
        half_power_right_angle_rad=right,
        half_power_beamwidth_rad=right - left,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        sample_count=sample_count,
    )


class MillsCrossFootprintBeamwidths(BaseModel):
    """Physical TX/RX half-power widths used by a flat-bottom footprint model."""

    model_config = ConfigDict(frozen=True)

    transmit_along_track: PrincipalPlaneBeamwidth
    receive_across_track: PrincipalPlaneBeamwidth
    footprint_model: FlatSeafloorFootprintModel


class PatternDerivedFootprint(BaseModel):
    """Flat-bottom footprint plus the physical beamwidth derivation that produced it."""

    model_config = ConfigDict(frozen=True)

    beamwidths: MillsCrossFootprintBeamwidths
    footprint: InsonifiedFootprint


def derive_mills_cross_footprint_beamwidths(
    *,
    configuration: MillsCrossConfiguration,
    transmit_steering_along_track_angle_rad: float,
    receive_steering_across_track_angle_rad: float,
    frequency_hz: float,
    sound_speed_mps: float,
    scan_half_span_rad: float = 0.35,
    sample_count: int = 2001,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> MillsCrossFootprintBeamwidths:
    """Derive Mills-Cross TX-along and RX-across widths from configured arrays."""

    if scan_half_span_rad <= 0.0:
        raise ValueError("scan_half_span_rad must be positive")

    tx_center = float(transmit_steering_along_track_angle_rad)
    rx_center = float(receive_steering_across_track_angle_rad)
    tx = derive_principal_plane_beamwidth(
        array=configuration.transmit_array,
        plane="along_track",
        steering_along_track_angle_rad=tx_center,
        steering_across_track_angle_rad=0.0,
        start_angle_rad=tx_center - scan_half_span_rad,
        end_angle_rad=tx_center + scan_half_span_rad,
        sample_count=sample_count,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        weights=transmit_weights,
    )
    rx = derive_principal_plane_beamwidth(
        array=configuration.receive_array,
        plane="across_track",
        steering_along_track_angle_rad=0.0,
        steering_across_track_angle_rad=rx_center,
        start_angle_rad=rx_center - scan_half_span_rad,
        end_angle_rad=rx_center + scan_half_span_rad,
        sample_count=sample_count,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        weights=receive_weights,
    )
    model = FlatSeafloorFootprintModel(
        transmit_along_track_beamwidth_rad=tx.half_power_beamwidth_rad,
        receive_across_track_beamwidth_rad=rx.half_power_beamwidth_rad,
    )
    return MillsCrossFootprintBeamwidths(
        transmit_along_track=tx,
        receive_across_track=rx,
        footprint_model=model,
    )


def estimate_mills_cross_pattern_footprint(
    *,
    configuration: MillsCrossConfiguration,
    transmit_steering_along_track_angle_rad: float,
    receive_steering_across_track_angle_rad: float,
    vertical_separation_m: float,
    pulse_duration_seconds: float,
    frequency_hz: float,
    sound_speed_mps: float,
    scan_half_span_rad: float = 0.35,
    sample_count: int = 2001,
    transmit_weights: Sequence[complex] | None = None,
    receive_weights: Sequence[complex] | None = None,
) -> PatternDerivedFootprint:
    """Derive physical -3 dB widths and immediately project their flat-bottom footprint."""

    widths = derive_mills_cross_footprint_beamwidths(
        configuration=configuration,
        transmit_steering_along_track_angle_rad=transmit_steering_along_track_angle_rad,
        receive_steering_across_track_angle_rad=receive_steering_across_track_angle_rad,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        scan_half_span_rad=scan_half_span_rad,
        sample_count=sample_count,
        transmit_weights=transmit_weights,
        receive_weights=receive_weights,
    )
    footprint = estimate_flat_seafloor_footprint(
        model=widths.footprint_model,
        vertical_separation_m=vertical_separation_m,
        transmit_along_track_center_angle_rad=transmit_steering_along_track_angle_rad,
        incidence_angle_from_normal_rad=abs(float(receive_steering_across_track_angle_rad)),
        pulse_duration_seconds=pulse_duration_seconds,
        sound_speed_mps=sound_speed_mps,
    )
    return PatternDerivedFootprint(beamwidths=widths, footprint=footprint)

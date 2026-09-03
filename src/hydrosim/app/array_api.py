"""Application adapter for PED-D6 transducer and array construction.

The adapter validates learner controls and serializes canonical array/beam-pattern
Core outputs. It does not implement array-factor, element-factor, wavelength, or
beamwidth equations.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.beam_pattern import (
    across_track_direction,
    one_way_beam_pattern,
    scan_across_track_beam_pattern,
)
from hydrosim.geometry import TransducerArray


class D6ArrayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    element_count: int = Field(default=16, ge=1, le=256)
    element_spacing_m: float = Field(default=0.00375, ge=0.0)
    element_face_m: float = Field(default=0.003, gt=0.0)
    scan_min_deg: float = Field(default=-80.0, ge=-89.0, lt=0.0)
    scan_max_deg: float = Field(default=80.0, gt=0.0, le=89.0)
    sample_count: int = Field(default=321, ge=33, le=1441)

    @model_validator(mode="after")
    def _validate_spacing_and_scan(self) -> "D6ArrayRequest":
        if self.element_count > 1 and self.element_spacing_m <= 0.0:
            raise ValueError("element_spacing_m must be > 0 when element_count > 1")
        if self.scan_max_deg <= self.scan_min_deg:
            raise ValueError("scan_max_deg must exceed scan_min_deg")
        return self


class D6PatternSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D6ArrayResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    wavelength_m: float
    physical_aperture_m: float
    element_positions_m: tuple[float, ...]
    element_factor: D6PatternSeries
    array_factor: D6PatternSeries
    combined_pattern: D6PatternSeries
    peak_angle_deg: float
    peak_normalized_power: float
    half_power_beamwidth_deg: float | None
    metadata: dict[str, str | float | int]


def _build_array(request: D6ArrayRequest) -> TransducerArray:
    # Across-track is array-local Y, matching the canonical scan convention.
    return TransducerArray(
        name="PED-D6 regular across-track array",
        role="txrx",
        n_x=1,
        n_y=request.element_count,
        d_x=0.0,
        d_y=request.element_spacing_m,
        element_longitudinal_size=request.element_face_m,
        element_transverse_size=request.element_face_m,
    )


def prepare_d6_array_response(request: D6ArrayRequest) -> D6ArrayResponse:
    """Evaluate the PED-D6 learner controls through canonical Core models."""

    array = _build_array(request)
    start = radians(request.scan_min_deg)
    end = radians(request.scan_max_deg)
    scan = scan_across_track_beam_pattern(
        array=array,
        steering_angle_rad=0.0,
        start_angle_rad=start,
        end_angle_rad=end,
        sample_count=request.sample_count,
        frequency_hz=request.frequency_khz * 1e3,
        sound_speed_mps=request.sound_speed_mps,
    )

    angles = tuple(float(sample.angle_rad) for sample in scan.samples)
    responses = tuple(
        one_way_beam_pattern(
            array=array,
            source_direction_array_frame=across_track_direction(angle),
            steering_direction_array_frame=across_track_direction(0.0),
            frequency_hz=request.frequency_khz * 1e3,
            sound_speed_mps=request.sound_speed_mps,
        )
        for angle in angles
    )
    angle_deg = tuple(degrees(angle) for angle in angles)
    element_power = tuple(float(response.element_factor.power) for response in responses)
    array_power = tuple(float(response.array_factor.normalized_power) for response in responses)
    combined_power = tuple(float(sample.normalized_power) for sample in scan.samples)

    # Wavelength is read from the canonical array-factor response, not recomputed here.
    wavelength_m = float(responses[0].array_factor.wavelength_m)
    beamwidth = (
        None
        if scan.half_power_beamwidth_rad is None
        else degrees(float(scan.half_power_beamwidth_rad))
    )

    return D6ArrayResponse(
        wavelength_m=wavelength_m,
        physical_aperture_m=float(array.aperture_transverse),
        element_positions_m=tuple(float(item.position.y) for item in array.elements()),
        element_factor=D6PatternSeries(angle_deg=angle_deg, normalized_power=element_power),
        array_factor=D6PatternSeries(angle_deg=angle_deg, normalized_power=array_power),
        combined_pattern=D6PatternSeries(angle_deg=angle_deg, normalized_power=combined_power),
        peak_angle_deg=degrees(float(scan.peak_angle_rad)),
        peak_normalized_power=float(scan.peak_power),
        half_power_beamwidth_deg=beamwidth,
        metadata={
            "frequency_unit": "kHz",
            "sound_speed_unit": "m/s",
            "distance_unit": "m",
            "angle_unit": "deg",
            "pattern_quantity": "normalized one-way power re peak",
            "array_axis": "across-track Y",
            "positive_angle_direction": "Port (-Y)",
            "negative_angle_direction": "Starboard (+Y)",
            "steering": "fixed broadside",
            "weights": "uniform unit weights",
            "state_semantics": "Configured inputs; Derived outputs",
            "element_count": request.element_count,
        },
    )

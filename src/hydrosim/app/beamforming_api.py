"""Application adapter for PED-D7 beamforming and electronic steering.

The adapter validates learner controls and serializes canonical Scientific Core
outputs. It does not implement steering, phase, array-factor, element-factor or
beam-pattern equations.
"""

from __future__ import annotations

from math import degrees, radians
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.beam_pattern import (
    across_track_direction,
    one_way_beam_pattern,
    scan_across_track_beam_pattern,
)
from hydrosim.geometry import TransducerArray


class D7BeamformingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    element_count: int = Field(default=16, ge=2, le=256)
    element_spacing_m: float = Field(default=0.00375, gt=0.0)
    element_face_m: float = Field(default=0.003, gt=0.0)
    steering_angle_deg: float = Field(default=0.0, ge=-80.0, le=80.0)
    source_angle_deg: float = Field(default=0.0, ge=-89.0, le=89.0)
    scan_min_deg: float = Field(default=-80.0, ge=-89.0, lt=0.0)
    scan_max_deg: float = Field(default=80.0, gt=0.0, le=89.0)
    sample_count: int = Field(default=321, ge=33, le=1441)
    role: Literal["tx", "rx"] = "tx"

    @model_validator(mode="after")
    def _validate_scan(self) -> "D7BeamformingRequest":
        if self.scan_max_deg <= self.scan_min_deg:
            raise ValueError("scan_max_deg must exceed scan_min_deg")
        if not self.scan_min_deg <= self.steering_angle_deg <= self.scan_max_deg:
            raise ValueError("steering_angle_deg must lie inside the scan interval")
        return self


class D7Direction(BaseModel):
    model_config = ConfigDict(frozen=True)

    x: float
    y: float
    z: float


class D7ElementState(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int
    position_y_m: float
    steering_phase_re_broadside_rad: float
    residual_phase_rad: float
    contribution_real: float
    contribution_imag: float


class D7PatternSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D7BeamformingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: Literal["tx", "rx"]
    wavelength_m: float
    steering_angle_deg: float
    source_angle_deg: float
    steering_direction_array_frame: D7Direction
    source_direction_array_frame: D7Direction
    elements: tuple[D7ElementState, ...]
    evaluated_array_factor_magnitude: float
    evaluated_array_factor_power: float
    evaluated_physical_beam_power: float
    coherent_sum_real: float
    coherent_sum_imag: float
    array_factor_pattern: D7PatternSeries
    physical_beam_pattern: D7PatternSeries
    peak_angle_deg: float
    peak_normalized_power: float
    half_power_beamwidth_deg: float | None
    metadata: dict[str, str | float | int]


def _build_array(request: D7BeamformingRequest) -> TransducerArray:
    return TransducerArray(
        name="PED-D7 regular across-track array",
        role="txrx",
        n_x=1,
        n_y=request.element_count,
        d_x=0.0,
        d_y=request.element_spacing_m,
        element_longitudinal_size=request.element_face_m,
        element_transverse_size=request.element_face_m,
    )


def prepare_d7_beamforming_response(request: D7BeamformingRequest) -> D7BeamformingResponse:
    """Evaluate PED-D7 controls exclusively through canonical Core models."""

    array = _build_array(request)
    frequency_hz = request.frequency_khz * 1e3
    steering_rad = radians(request.steering_angle_deg)
    source_rad = radians(request.source_angle_deg)
    steering_direction = across_track_direction(steering_rad)
    source_direction = across_track_direction(source_rad)

    evaluated = one_way_beam_pattern(
        array=array,
        source_direction_array_frame=source_direction,
        steering_direction_array_frame=steering_direction,
        frequency_hz=frequency_hz,
        sound_speed_mps=request.sound_speed_mps,
    )
    steering_reference = one_way_beam_pattern(
        array=array,
        source_direction_array_frame=across_track_direction(0.0),
        steering_direction_array_frame=steering_direction,
        frequency_hz=frequency_hz,
        sound_speed_mps=request.sound_speed_mps,
    )

    scan = scan_across_track_beam_pattern(
        array=array,
        steering_angle_rad=steering_rad,
        start_angle_rad=radians(request.scan_min_deg),
        end_angle_rad=radians(request.scan_max_deg),
        sample_count=request.sample_count,
        frequency_hz=frequency_hz,
        sound_speed_mps=request.sound_speed_mps,
    )

    angle_deg = tuple(degrees(float(sample.angle_rad)) for sample in scan.samples)
    physical_power = tuple(float(sample.normalized_power) for sample in scan.samples)
    array_power = tuple(
        float(
            one_way_beam_pattern(
                array=array,
                source_direction_array_frame=across_track_direction(float(sample.angle_rad)),
                steering_direction_array_frame=steering_direction,
                frequency_hz=frequency_hz,
                sound_speed_mps=request.sound_speed_mps,
            ).array_factor.normalized_power
        )
        for sample in scan.samples
    )

    evaluated_contributions = evaluated.array_factor.element_contributions
    steering_contributions = steering_reference.array_factor.element_contributions
    elements = tuple(
        D7ElementState(
            index=item.index_y,
            position_y_m=float(item.position_array_frame.y),
            steering_phase_re_broadside_rad=float(reference.residual_phase_rad),
            residual_phase_rad=float(item.residual_phase_rad),
            contribution_real=float(item.contribution_real),
            contribution_imag=float(item.contribution_imag),
        )
        for item, reference in zip(
            evaluated_contributions,
            steering_contributions,
            strict=True,
        )
    )

    steering_vector = evaluated.array_factor.steering_direction_array_frame
    source_vector = evaluated.array_factor.source_direction_array_frame
    beamwidth = (
        None
        if scan.half_power_beamwidth_rad is None
        else degrees(float(scan.half_power_beamwidth_rad))
    )

    return D7BeamformingResponse(
        role=request.role,
        wavelength_m=float(evaluated.array_factor.wavelength_m),
        steering_angle_deg=request.steering_angle_deg,
        source_angle_deg=request.source_angle_deg,
        steering_direction_array_frame=D7Direction(
            x=float(steering_vector.x),
            y=float(steering_vector.y),
            z=float(steering_vector.z),
        ),
        source_direction_array_frame=D7Direction(
            x=float(source_vector.x),
            y=float(source_vector.y),
            z=float(source_vector.z),
        ),
        elements=elements,
        evaluated_array_factor_magnitude=float(evaluated.array_factor.normalized_magnitude),
        evaluated_array_factor_power=float(evaluated.array_factor.normalized_power),
        evaluated_physical_beam_power=float(evaluated.normalized_power),
        coherent_sum_real=float(evaluated.array_factor.coherent_real),
        coherent_sum_imag=float(evaluated.array_factor.coherent_imag),
        array_factor_pattern=D7PatternSeries(
            angle_deg=angle_deg,
            normalized_power=array_power,
        ),
        physical_beam_pattern=D7PatternSeries(
            angle_deg=angle_deg,
            normalized_power=physical_power,
        ),
        peak_angle_deg=degrees(float(scan.peak_angle_rad)),
        peak_normalized_power=float(scan.peak_power),
        half_power_beamwidth_deg=beamwidth,
        metadata={
            "frequency_unit": "kHz",
            "sound_speed_unit": "m/s",
            "distance_unit": "m",
            "angle_unit": "deg",
            "phase_unit": "rad",
            "array_axis": "across-track Y",
            "positive_angle_direction": "Port (-Y)",
            "negative_angle_direction": "Starboard (+Y)",
            "weights": "uniform unit weights",
            "beamformer_model": "ideal static one-way reciprocal narrowband far-field",
            "steering_phase_reference": "canonical Core residual phase for broadside source vs selected steering",
            "state_semantics": "Configured inputs; Derived outputs",
            "element_count": request.element_count,
        },
    )

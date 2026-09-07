"""Application adapter for PED-D7 beamforming and electronic steering.

The adapter validates learner controls and serializes canonical Scientific Core
outputs. It does not implement beam-pattern equations. Learner-facing timing and
alias-status quantities follow the authoritative D6 steering disposition.
"""

from __future__ import annotations

from math import asin, degrees, radians, sin
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
    steering_control_mode: Literal["angle", "delay_gradient"] = "angle"
    delay_gradient_us_per_element: float | None = None
    source_angle_deg: float = Field(default=0.0, ge=-89.0, le=89.0)
    scan_min_deg: float = Field(default=-80.0, ge=-89.0, lt=0.0)
    scan_max_deg: float = Field(default=80.0, gt=0.0, le=89.0)
    sample_count: int = Field(default=321, ge=33, le=1441)
    role: Literal["tx", "rx"] = "tx"

    @model_validator(mode="after")
    def _validate_scan_and_control(self) -> "D7BeamformingRequest":
        if self.scan_max_deg <= self.scan_min_deg:
            raise ValueError("scan_max_deg must exceed scan_min_deg")
        if self.steering_control_mode == "angle":
            if self.delay_gradient_us_per_element is not None:
                raise ValueError(
                    "delay_gradient_us_per_element requires steering_control_mode='delay_gradient'"
                )
            if not self.scan_min_deg <= self.steering_angle_deg <= self.scan_max_deg:
                raise ValueError("steering_angle_deg must lie inside the scan interval")
        elif self.delay_gradient_us_per_element is None:
            raise ValueError(
                "delay_gradient_us_per_element is required for delay-gradient steering control"
            )
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
    relative_arrival_offset_us: float
    relative_compensation_delay_us: float
    residual_relative_timing_us: float
    residual_relative_phase_rad: float
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
    steering_control_mode: Literal["angle", "delay_gradient"]
    steering_angle_deg: float
    requested_steering_angle_deg: float | None
    requested_delay_gradient_us_per_element: float | None
    steering_delay_gradient_us_per_element: float
    source_angle_deg: float
    reference_channel_index: int
    reference_channel_convention: str
    steering_regime: Literal["unambiguous", "aliased"]
    grating_lobe_angles_deg: tuple[float, ...]
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


def _effective_steering_angle_deg(request: D7BeamformingRequest) -> float:
    if request.steering_control_mode == "angle":
        return request.steering_angle_deg

    gradient_s = float(request.delay_gradient_us_per_element) * 1e-6
    sine_value = -request.sound_speed_mps * gradient_s / request.element_spacing_m
    if abs(sine_value) > 1.0 + 1e-12:
        raise ValueError("delay gradient does not map to a physical steering angle")
    steering_angle_deg = degrees(asin(max(-1.0, min(1.0, sine_value))))
    if not request.scan_min_deg <= steering_angle_deg <= request.scan_max_deg:
        raise ValueError("delay-gradient steering angle must lie inside the scan interval")
    return steering_angle_deg


def _visible_grating_lobes_deg(
    *,
    steering_angle_deg: float,
    wavelength_m: float,
    element_spacing_m: float,
    scan_min_deg: float,
    scan_max_deg: float,
) -> tuple[float, ...]:
    steering_sine = sin(radians(steering_angle_deg))
    ratio = wavelength_m / element_spacing_m
    max_order = int(2.0 / ratio) + 2
    aliases: list[float] = []
    for order in range(-max_order, max_order + 1):
        if order == 0:
            continue
        candidate_sine = steering_sine + order * ratio
        if candidate_sine < -1.0 or candidate_sine > 1.0:
            continue
        candidate_deg = degrees(asin(candidate_sine))
        if scan_min_deg <= candidate_deg <= scan_max_deg:
            aliases.append(candidate_deg)
    return tuple(sorted(aliases))


def prepare_d7_beamforming_response(request: D7BeamformingRequest) -> D7BeamformingResponse:
    """Evaluate PED-D7 controls exclusively through canonical Core models."""

    array = _build_array(request)
    frequency_hz = request.frequency_khz * 1e3
    effective_steering_deg = _effective_steering_angle_deg(request)
    steering_rad = radians(effective_steering_deg)
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
    reference_channel_index = 0
    reference_item = evaluated_contributions[reference_channel_index]
    reference_position = reference_item.position_array_frame
    source_vector = evaluated.array_factor.source_direction_array_frame
    steering_vector = evaluated.array_factor.steering_direction_array_frame

    def _dot(direction, position) -> float:
        return (
            float(direction.x) * float(position.x)
            + float(direction.y) * float(position.y)
            + float(direction.z) * float(position.z)
        )

    reference_arrival_s = -_dot(source_vector, reference_position) / request.sound_speed_mps
    reference_delay_s = _dot(steering_vector, reference_position) / request.sound_speed_mps
    reference_residual_phase = float(reference_item.residual_phase_rad)

    elements = tuple(
        D7ElementState(
            index=item.index_y,
            position_y_m=float(item.position_array_frame.y),
            steering_phase_re_broadside_rad=float(reference.residual_phase_rad),
            residual_phase_rad=float(item.residual_phase_rad),
            relative_arrival_offset_us=(
                -_dot(source_vector, item.position_array_frame) / request.sound_speed_mps
                - reference_arrival_s
            )
            * 1e6,
            relative_compensation_delay_us=(
                _dot(steering_vector, item.position_array_frame) / request.sound_speed_mps
                - reference_delay_s
            )
            * 1e6,
            residual_relative_timing_us=(
                (
                    -_dot(source_vector, item.position_array_frame)
                    + _dot(steering_vector, item.position_array_frame)
                )
                / request.sound_speed_mps
                - (reference_arrival_s + reference_delay_s)
            )
            * 1e6,
            residual_relative_phase_rad=float(item.residual_phase_rad) - reference_residual_phase,
            contribution_real=float(item.contribution_real),
            contribution_imag=float(item.contribution_imag),
        )
        for item, reference in zip(
            evaluated_contributions,
            steering_contributions,
            strict=True,
        )
    )

    beamwidth = (
        None
        if scan.half_power_beamwidth_rad is None
        else degrees(float(scan.half_power_beamwidth_rad))
    )
    wavelength_m = float(evaluated.array_factor.wavelength_m)
    aliases = _visible_grating_lobes_deg(
        steering_angle_deg=effective_steering_deg,
        wavelength_m=wavelength_m,
        element_spacing_m=request.element_spacing_m,
        scan_min_deg=request.scan_min_deg,
        scan_max_deg=request.scan_max_deg,
    )
    steering_delay_gradient_us_per_element = (
        -request.element_spacing_m * sin(steering_rad) / request.sound_speed_mps * 1e6
    )

    return D7BeamformingResponse(
        role=request.role,
        wavelength_m=wavelength_m,
        steering_control_mode=request.steering_control_mode,
        steering_angle_deg=effective_steering_deg,
        requested_steering_angle_deg=(
            request.steering_angle_deg if request.steering_control_mode == "angle" else None
        ),
        requested_delay_gradient_us_per_element=request.delay_gradient_us_per_element,
        steering_delay_gradient_us_per_element=steering_delay_gradient_us_per_element,
        source_angle_deg=request.source_angle_deg,
        reference_channel_index=reference_channel_index,
        reference_channel_convention="first array element; displayed relative timing/delay is zero at this channel",
        steering_regime="aliased" if aliases else "unambiguous",
        grating_lobe_angles_deg=aliases,
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
            "time_unit": "us",
            "angle_unit": "deg",
            "phase_unit": "rad",
            "array_axis": "across-track Y",
            "positive_angle_direction": "Port (-Y)",
            "negative_angle_direction": "Starboard (+Y)",
            "weights": "uniform unit weights",
            "beamformer_model": "ideal static one-way reciprocal narrowband far-field",
            "steering_phase_reference": "canonical Core residual phase for broadside source vs selected steering",
            "timing_reference": "channel 0 relative timing/delay",
            "state_semantics": "Configured inputs; Derived outputs",
            "element_count": request.element_count,
        },
    )

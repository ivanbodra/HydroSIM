"""Render-ready shared-channel multibeam bridge for the beamforming lesson.

One physical RX snapshot is evaluated through multiple canonical steering laws.
All numerical beamforming remains owned by ``prepare_d7_beamforming_response``;
this module only removes duplicated channel-state data from the HTTP contract.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.app.beamforming_api import (
    D7BeamformingRequest,
    D7PatternSeries,
    prepare_d7_beamforming_response,
)


class D6SharedRxMultibeamRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    element_count: int = Field(default=16, ge=2, le=256)
    element_spacing_m: float = Field(default=0.00375, gt=0.0)
    element_face_m: float = Field(default=0.003, gt=0.0)
    source_angle_deg: float = Field(default=0.0, ge=-89.0, le=89.0)
    steering_angles_deg: tuple[float, ...] = (-30.0, 0.0, 30.0)
    scan_min_deg: float = Field(default=-80.0, ge=-89.0, lt=0.0)
    scan_max_deg: float = Field(default=80.0, gt=0.0, le=89.0)
    sample_count: int = Field(default=321, ge=33, le=1441)

    @model_validator(mode="after")
    def _validate_virtual_beams(self) -> "D6SharedRxMultibeamRequest":
        if self.scan_max_deg <= self.scan_min_deg:
            raise ValueError("scan_max_deg must exceed scan_min_deg")
        if not self.steering_angles_deg:
            raise ValueError("steering_angles_deg must contain at least one virtual beam")
        if len(self.steering_angles_deg) > 31:
            raise ValueError("steering_angles_deg supports at most 31 virtual beams")
        if len(set(self.steering_angles_deg)) != len(self.steering_angles_deg):
            raise ValueError("steering_angles_deg must not contain duplicates")
        for angle in self.steering_angles_deg:
            if not -80.0 <= angle <= 80.0:
                raise ValueError("each steering angle must lie in [-80, 80] deg")
            if not self.scan_min_deg <= angle <= self.scan_max_deg:
                raise ValueError("each steering angle must lie inside the scan interval")
        return self


class D6SharedRxChannel(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int
    position_y_m: float
    relative_arrival_offset_us: float


class D6VirtualRxBeam(BaseModel):
    model_config = ConfigDict(frozen=True)

    steering_angle_deg: float
    steering_delay_gradient_us_per_element: float
    relative_compensation_delays_us: tuple[float, ...]
    evaluated_array_factor_power: float
    evaluated_physical_beam_power: float
    coherent_sum_real: float
    coherent_sum_imag: float
    peak_angle_deg: float
    peak_normalized_power: float
    half_power_beamwidth_deg: float | None
    physical_beam_pattern: D7PatternSeries


class D6SharedRxMultibeamResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_angle_deg: float
    reference_channel_index: int
    shared_channels: tuple[D6SharedRxChannel, ...]
    virtual_beams: tuple[D6VirtualRxBeam, ...]
    metadata: dict[str, str | float | int]


def prepare_d6_shared_rx_multibeam_response(
    request: D6SharedRxMultibeamRequest,
) -> D6SharedRxMultibeamResponse:
    """Apply several canonical steering solutions to one configured RX snapshot."""

    responses = tuple(
        prepare_d7_beamforming_response(
            D7BeamformingRequest(
                frequency_khz=request.frequency_khz,
                sound_speed_mps=request.sound_speed_mps,
                element_count=request.element_count,
                element_spacing_m=request.element_spacing_m,
                element_face_m=request.element_face_m,
                steering_angle_deg=angle,
                source_angle_deg=request.source_angle_deg,
                scan_min_deg=request.scan_min_deg,
                scan_max_deg=request.scan_max_deg,
                sample_count=request.sample_count,
                role="rx",
            )
        )
        for angle in request.steering_angles_deg
    )

    shared = responses[0]
    shared_channels = tuple(
        D6SharedRxChannel(
            index=element.index,
            position_y_m=element.position_y_m,
            relative_arrival_offset_us=element.relative_arrival_offset_us,
        )
        for element in shared.elements
    )

    for response in responses[1:]:
        arrival_offsets = tuple(element.relative_arrival_offset_us for element in response.elements)
        reference_offsets = tuple(channel.relative_arrival_offset_us for channel in shared_channels)
        if arrival_offsets != reference_offsets:  # pragma: no cover - canonical invariant guard
            raise RuntimeError("virtual beams did not share one RX channel snapshot")

    virtual_beams = tuple(
        D6VirtualRxBeam(
            steering_angle_deg=response.steering_angle_deg,
            steering_delay_gradient_us_per_element=response.steering_delay_gradient_us_per_element,
            relative_compensation_delays_us=tuple(
                element.relative_compensation_delay_us for element in response.elements
            ),
            evaluated_array_factor_power=response.evaluated_array_factor_power,
            evaluated_physical_beam_power=response.evaluated_physical_beam_power,
            coherent_sum_real=response.coherent_sum_real,
            coherent_sum_imag=response.coherent_sum_imag,
            peak_angle_deg=response.peak_angle_deg,
            peak_normalized_power=response.peak_normalized_power,
            half_power_beamwidth_deg=response.half_power_beamwidth_deg,
            physical_beam_pattern=response.physical_beam_pattern,
        )
        for response in responses
    )

    return D6SharedRxMultibeamResponse(
        source_angle_deg=request.source_angle_deg,
        reference_channel_index=shared.reference_channel_index,
        shared_channels=shared_channels,
        virtual_beams=virtual_beams,
        metadata={
            "channel_snapshot": "one shared physical RX element snapshot",
            "virtual_beam_operation": "independent canonical steering/delay set per beam",
            "angle_unit": "deg",
            "time_unit": "us",
            "positive_angle_direction": shared.metadata["positive_angle_direction"],
            "state_semantics": "Configured source/steering; Derived virtual-beam outputs",
            "element_count": request.element_count,
            "virtual_beam_count": len(virtual_beams),
        },
    )

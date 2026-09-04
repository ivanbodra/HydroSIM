"""Application adapter for PED-D6 transducer and array construction.

The adapter validates learner controls and serializes canonical array/beam-pattern
Core outputs. It does not implement array-factor, element-factor, wavelength, or
beamwidth equations.
"""

from __future__ import annotations

from math import degrees, hypot, radians
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.aperture_weights import deterministic_aperture_weights
from hydrosim.acquisition.beam_pattern import (
    across_track_direction,
    one_way_beam_pattern,
    scan_across_track_beam_pattern,
)
from hydrosim.geometry import TransducerArray, Vector3, make_reference_mills_cross


class D6MillsCrossRequest(BaseModel):
    """Configured Mills-Cross construction geometry only."""

    model_config = ConfigDict(extra="forbid")

    transmit_count: int = Field(default=8, ge=2, le=256)
    receive_count: int = Field(default=16, ge=2, le=256)
    transmit_spacing_m: float = Field(default=0.00375, gt=0.0)
    receive_spacing_m: float = Field(default=0.00375, gt=0.0)
    transmit_element_face_m: float = Field(default=0.003, gt=0.0)
    receive_element_face_m: float = Field(default=0.003, gt=0.0)


class D6ArrayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    element_count: int = Field(default=16, ge=1, le=256)
    element_spacing_m: float = Field(default=0.00375, ge=0.0)
    element_face_m: float = Field(default=0.003, gt=0.0)
    longitudinal_element_count: int = Field(default=1, ge=1, le=256)
    longitudinal_element_spacing_m: float = Field(default=0.0, ge=0.0)
    weighting: Literal["uniform", "hann"] = "uniform"
    mills_cross: D6MillsCrossRequest | None = None
    tx_reference_position_m: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rx_reference_position_m: tuple[float, float, float] = (0.0, 0.0, 0.0)
    reference_frame: str = Field(default="B", min_length=1)
    scan_min_deg: float = Field(default=-80.0, ge=-89.0, lt=0.0)
    scan_max_deg: float = Field(default=80.0, gt=0.0, le=89.0)
    sample_count: int = Field(default=321, ge=33, le=1441)

    @model_validator(mode="after")
    def _validate_spacing_and_scan(self) -> "D6ArrayRequest":
        if self.element_count > 1 and self.element_spacing_m <= 0.0:
            raise ValueError("element_spacing_m must be > 0 when element_count > 1")
        if self.longitudinal_element_count > 1 and self.longitudinal_element_spacing_m <= 0.0:
            raise ValueError(
                "longitudinal_element_spacing_m must be > 0 when longitudinal_element_count > 1"
            )
        if self.longitudinal_element_count > 1 and self.weighting != "uniform":
            raise ValueError("hann weighting is defined only for the active 1-D PED-D6 aperture")
        if self.scan_max_deg <= self.scan_min_deg:
            raise ValueError("scan_max_deg must exceed scan_min_deg")
        if not self.reference_frame.strip():
            raise ValueError("reference_frame must not be blank")
        return self


class D6PatternSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D6MillsCrossGeometry(BaseModel):
    """Derived TX/RX construction geometry; no two-way response is implied."""

    model_config = ConfigDict(frozen=True)

    transmit_axis_sensor_frame: tuple[float, float, float]
    receive_axis_sensor_frame: tuple[float, float, float]
    transmit_aperture_m: float
    receive_aperture_m: float
    transmit_element_positions_sensor_frame_m: tuple[tuple[float, float, float], ...]
    receive_element_positions_sensor_frame_m: tuple[tuple[float, float, float], ...]


class D6ArrayResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    wavelength_m: float
    physical_aperture_m: float
    physical_aperture_longitudinal_m: float
    physical_aperture_transverse_m: float
    element_positions_m: tuple[float, ...]
    element_positions_array_frame_m: tuple[tuple[float, float, float], ...]
    aperture_weights: tuple[float, ...]
    element_factor: D6PatternSeries
    array_factor: D6PatternSeries
    combined_pattern: D6PatternSeries
    peak_angle_deg: float
    peak_normalized_power: float
    half_power_beamwidth_deg: float | None
    mills_cross: D6MillsCrossGeometry | None
    tx_reference_position_m: tuple[float, float, float]
    rx_reference_position_m: tuple[float, float, float]
    eccentricity_vector_m: tuple[float, float, float]
    eccentricity_magnitude_m: float
    reference_frame: str
    metadata: dict[str, str | float | int]


def _build_array(request: D6ArrayRequest) -> TransducerArray:
    # Across-track is array-local Y, matching the canonical scan convention.
    return TransducerArray(
        name="PED-D6 regular array",
        role="txrx",
        n_x=request.longitudinal_element_count,
        n_y=request.element_count,
        d_x=request.longitudinal_element_spacing_m,
        d_y=request.element_spacing_m,
        element_longitudinal_size=request.element_face_m,
        element_transverse_size=request.element_face_m,
    )


def _xyz(vector: Vector3) -> tuple[float, float, float]:
    return (float(vector.x), float(vector.y), float(vector.z))


def _mills_cross_geometry(request: D6MillsCrossRequest | None) -> D6MillsCrossGeometry | None:
    if request is None:
        return None

    config = make_reference_mills_cross(
        transmit_count=request.transmit_count,
        receive_count=request.receive_count,
        transmit_spacing=request.transmit_spacing_m,
        receive_spacing=request.receive_spacing_m,
        transmit_element_longitudinal_size=request.transmit_element_face_m,
        transmit_element_transverse_size=request.transmit_element_face_m,
        receive_element_longitudinal_size=request.receive_element_face_m,
        receive_element_transverse_size=request.receive_element_face_m,
    )
    return D6MillsCrossGeometry(
        transmit_axis_sensor_frame=_xyz(config.transmit_axis_sensor_frame),
        receive_axis_sensor_frame=_xyz(config.receive_axis_sensor_frame),
        transmit_aperture_m=float(config.transmit_array.aperture_longitudinal),
        receive_aperture_m=float(config.receive_array.aperture_transverse),
        transmit_element_positions_sensor_frame_m=tuple(
            _xyz(position) for position in config.transmit_array.element_positions_sensor_frame()
        ),
        receive_element_positions_sensor_frame_m=tuple(
            _xyz(position) for position in config.receive_array.element_positions_sensor_frame()
        ),
    )


def _eccentricity_geometry(
    request: D6ArrayRequest,
) -> tuple[Vector3, Vector3, Vector3, float]:
    """Return configured TX/RX points and canonical TX->RX separation."""

    tx = Vector3(
        x=request.tx_reference_position_m[0],
        y=request.tx_reference_position_m[1],
        z=request.tx_reference_position_m[2],
    )
    rx = Vector3(
        x=request.rx_reference_position_m[0],
        y=request.rx_reference_position_m[1],
        z=request.rx_reference_position_m[2],
    )
    eccentricity = Vector3(x=rx.x - tx.x, y=rx.y - tx.y, z=rx.z - tx.z)
    magnitude_m = hypot(eccentricity.x, eccentricity.y, eccentricity.z)
    return tx, rx, eccentricity, magnitude_m


def prepare_d6_array_response(request: D6ArrayRequest) -> D6ArrayResponse:
    """Evaluate the PED-D6 learner controls through canonical Core models."""

    array = _build_array(request)
    weights = deterministic_aperture_weights(array.element_count, request.weighting)
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
        weights=weights,
    )

    angles = tuple(float(sample.angle_rad) for sample in scan.samples)
    responses = tuple(
        one_way_beam_pattern(
            array=array,
            source_direction_array_frame=across_track_direction(angle),
            steering_direction_array_frame=across_track_direction(0.0),
            frequency_hz=request.frequency_khz * 1e3,
            sound_speed_mps=request.sound_speed_mps,
            weights=weights,
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
    elements = array.elements()
    tx, rx, eccentricity, eccentricity_magnitude_m = _eccentricity_geometry(request)

    return D6ArrayResponse(
        wavelength_m=wavelength_m,
        physical_aperture_m=float(array.aperture_transverse),
        physical_aperture_longitudinal_m=float(array.aperture_longitudinal),
        physical_aperture_transverse_m=float(array.aperture_transverse),
        element_positions_m=tuple(float(item.position.y) for item in elements),
        element_positions_array_frame_m=tuple(_xyz(item.position) for item in elements),
        aperture_weights=tuple(float(weight.real) for weight in weights),
        element_factor=D6PatternSeries(angle_deg=angle_deg, normalized_power=element_power),
        array_factor=D6PatternSeries(angle_deg=angle_deg, normalized_power=array_power),
        combined_pattern=D6PatternSeries(angle_deg=angle_deg, normalized_power=combined_power),
        peak_angle_deg=degrees(float(scan.peak_angle_rad)),
        peak_normalized_power=float(scan.peak_power),
        half_power_beamwidth_deg=beamwidth,
        mills_cross=_mills_cross_geometry(request.mills_cross),
        tx_reference_position_m=_xyz(tx),
        rx_reference_position_m=_xyz(rx),
        eccentricity_vector_m=_xyz(eccentricity),
        eccentricity_magnitude_m=float(eccentricity_magnitude_m),
        reference_frame=request.reference_frame.strip(),
        metadata={
            "frequency_unit": "kHz",
            "sound_speed_unit": "m/s",
            "distance_unit": "m",
            "eccentricity_unit": "m",
            "eccentricity_frame": request.reference_frame.strip(),
            "angle_unit": "deg",
            "pattern_quantity": "normalized one-way power re peak",
            "array_axis": "across-track Y",
            "positive_angle_direction": "Port (-Y)",
            "negative_angle_direction": "Starboard (+Y)",
            "steering": "fixed broadside",
            "weights": request.weighting,
            "state_semantics": "Configured inputs; Derived outputs",
            "element_count": array.element_count,
        },
    )

"""Application adapter for PED-D6 transducer-array construction.

Scientific quantities are delegated to the canonical geometry/acquisition Core.
This layer only validates controls, converts units, and serializes render-ready
values for the production frontend.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition import array_factor, one_way_beam_pattern, scan_across_track_beam_pattern
from hydrosim.acquisition.beam_pattern import across_track_direction
from hydrosim.geometry import TransducerArray


class D6ArrayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    element_count: int = Field(default=16, ge=1, le=512)
    spacing_mm: float = Field(default=3.75, ge=0.0)
    element_size_mm: float = Field(default=3.0, gt=0.0)
    scan_start_deg: float = Field(default=-90.0, ge=-90.0, lt=90.0)
    scan_end_deg: float = Field(default=90.0, gt=-90.0, le=90.0)
    sample_count: int = Field(default=721, ge=3, le=4097)


class D6PatternSeries(BaseModel):
    model_config = ConfigDict(frozen=True)
    angle_deg: tuple[float, ...]
    normalized_amplitude: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D6ArrayResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    wavelength_m: float
    aperture_m: float
    element_positions_m: tuple[float, ...]
    element_factor: D6PatternSeries
    array_factor: D6PatternSeries
    combined_pattern: D6PatternSeries
    peak_angle_deg: float
    peak_normalized_power: float
    half_power_beamwidth_deg: float | None
    half_power_left_deg: float | None
    half_power_right_deg: float | None
    metadata: dict[str, str | float | int]


def prepare_d6_array_response(request: D6ArrayRequest) -> D6ArrayResponse:
    """Build PED-D6 Derived values exclusively from canonical Core calls."""

    if request.element_count > 1 and request.spacing_mm <= 0.0:
        raise ValueError("spacing_mm must be > 0 when element_count > 1")
    if request.scan_end_deg <= request.scan_start_deg:
        raise ValueError("scan_end_deg must be greater than scan_start_deg")

    spacing_m = request.spacing_mm * 1e-3
    element_size_m = request.element_size_mm * 1e-3
    frequency_hz = request.frequency_khz * 1e3
    array = TransducerArray(
        name="PED-D6 regular array",
        role="txrx",
        n_x=1,
        n_y=request.element_count,
        d_x=0.0,
        d_y=spacing_m if request.element_count > 1 else 0.0,
        element_longitudinal_size=element_size_m,
        element_transverse_size=element_size_m,
    )
    steering = across_track_direction(0.0)
    scan = scan_across_track_beam_pattern(
        array=array,
        steering_angle_rad=0.0,
        start_angle_rad=radians(request.scan_start_deg),
        end_angle_rad=radians(request.scan_end_deg),
        sample_count=request.sample_count,
        frequency_hz=frequency_hz,
        sound_speed_mps=request.sound_speed_mps,
    )

    angles = tuple(degrees(float(sample.angle_rad)) for sample in scan.samples)
    combined_amplitude = tuple(float(sample.normalized_amplitude) for sample in scan.samples)
    combined_power = tuple(float(sample.normalized_power) for sample in scan.samples)
    element_amplitude: list[float] = []
    spatial_amplitude: list[float] = []
    broadside = None
    for sample in scan.samples:
        direction = across_track_direction(float(sample.angle_rad))
        physical = one_way_beam_pattern(
            array=array,
            source_direction_array_frame=direction,
            steering_direction_array_frame=steering,
            frequency_hz=frequency_hz,
            sound_speed_mps=request.sound_speed_mps,
        )
        spatial = array_factor(
            array=array,
            source_direction_array_frame=direction,
            steering_direction_array_frame=steering,
            frequency_hz=frequency_hz,
            sound_speed_mps=request.sound_speed_mps,
        )
        if broadside is None or abs(float(sample.angle_rad)) < abs(broadside[0]):
            broadside = (float(sample.angle_rad), spatial)
        element_amplitude.append(abs(float(physical.element_factor.signed_amplitude)))
        spatial_amplitude.append(float(spatial.normalized_magnitude))

    assert broadside is not None
    wavelength_m = float(broadside[1].wavelength_m)

    def series(amplitude: tuple[float, ...]) -> D6PatternSeries:
        return D6PatternSeries(
            angle_deg=angles,
            normalized_amplitude=amplitude,
            normalized_power=tuple(value * value for value in amplitude),
        )

    return D6ArrayResponse(
        wavelength_m=wavelength_m,
        aperture_m=float(array.aperture_transverse),
        element_positions_m=tuple(float(element.position.y) for element in array.elements()),
        element_factor=series(tuple(element_amplitude)),
        array_factor=series(tuple(spatial_amplitude)),
        combined_pattern=D6PatternSeries(
            angle_deg=angles,
            normalized_amplitude=combined_amplitude,
            normalized_power=combined_power,
        ),
        peak_angle_deg=degrees(float(scan.peak_angle_rad)),
        peak_normalized_power=float(scan.peak_power),
        half_power_beamwidth_deg=degrees(float(scan.half_power_beamwidth_rad)) if scan.half_power_beamwidth_rad is not None else None,
        half_power_left_deg=degrees(float(scan.half_power_left_angle_rad)) if scan.half_power_left_angle_rad is not None else None,
        half_power_right_deg=degrees(float(scan.half_power_right_angle_rad)) if scan.half_power_right_angle_rad is not None else None,
        metadata={
            "frequency_khz": request.frequency_khz,
            "sound_speed_mps": request.sound_speed_mps,
            "element_count": request.element_count,
            "spacing_mm": request.spacing_mm,
            "element_size_mm": request.element_size_mm,
            "steering_deg": 0.0,
            "active_axis": "array-local Y / across-track",
            "angle_convention": "+angle Port (-Y); -angle Starboard (+Y); 0 deg +Z",
            "response": "normalized one-way far-field narrowband",
            "weights": "uniform unit weights",
            "state_semantics": "Configured inputs; Derived outputs",
            "beamwidth_semantics": "local half-power width; null when crossings unavailable",
        },
    )

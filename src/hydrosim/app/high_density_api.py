"""Render-ready PED-D9 High Density bridge.

Phase inversion and spatial decimation remain in the Scientific Core. This adapter
only validates learner-facing units and serializes the canonical result.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.high_density import detect_high_density_from_phase
from hydrosim.geometry import Vector3


class D9HighDensityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    high_density_enabled: bool = False
    phase_sample_time_ms: tuple[float, ...] = Field(min_length=2, max_length=4096)
    differential_phase_rad: tuple[float, ...] = Field(min_length=2, max_length=4096)
    support_magnitude: tuple[float, ...] = Field(min_length=2, max_length=4096)
    steering_across_track_angle_deg: float = Field(ge=-89.0, le=89.0)
    support_min_angle_deg: float = Field(ge=-89.0, le=89.0)
    support_max_angle_deg: float = Field(ge=-89.0, le=89.0)
    split_aperture_baseline_m: tuple[float, float, float]
    frequency_khz: float = Field(gt=0.0)
    sound_speed_mps: float = Field(gt=0.0)
    reference_footprint_width_m: float = Field(gt=0.0)
    tx_delay_ms: float = Field(default=0.0, ge=0.0)
    parent_beam_index: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_series_and_support(self) -> "D9HighDensityRequest":
        count = len(self.phase_sample_time_ms)
        if len(self.differential_phase_rad) != count or len(self.support_magnitude) != count:
            raise ValueError("phase time, differential phase, and support series must have equal length")
        if self.support_max_angle_deg <= self.support_min_angle_deg:
            raise ValueError("support_max_angle_deg must exceed support_min_angle_deg")
        if not self.support_min_angle_deg <= self.steering_across_track_angle_deg <= self.support_max_angle_deg:
            raise ValueError("steering angle must lie inside the configured beam support")
        return self


class D9HighDensityDetection(BaseModel):
    model_config = ConfigDict(frozen=True)

    detection_index: int
    parent_beam_index: int | None
    method: str
    source_sample_index: int
    source_phase_rad: float
    arrival_offset_ms: float
    twtt_ms: float
    detected_across_track_angle_deg: float
    local_bottom_point_m: tuple[float, float, float]


class D9HighDensityComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    ordinary_detection_count: int = Field(ge=0)
    high_density_detection_count: int = Field(ge=0)
    density_multiplier: float = Field(ge=0.0)
    target_spacing_m: float | None
    adjacent_spacing_m: tuple[float, ...]


class D9HighDensityResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    ordinary_detection_arrival_ms: float | None
    ordinary_detection_angle_deg: float | None
    candidate_count: int
    detections: tuple[D9HighDensityDetection, ...]
    comparison: D9HighDensityComparison
    unavailable_reason: str | None
    metadata: dict[str, str | float | int | bool]


def _xyz(vector: Vector3) -> tuple[float, float, float]:
    return (float(vector.x), float(vector.y), float(vector.z))


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum((left - right) ** 2 for left, right in zip(a, b, strict=True)) ** 0.5


def prepare_d9_high_density_response(request: D9HighDensityRequest) -> D9HighDensityResponse:
    result = detect_high_density_from_phase(
        high_density_enabled=request.high_density_enabled,
        sample_times_seconds=tuple(value * 1e-3 for value in request.phase_sample_time_ms),
        differential_phase_rad=request.differential_phase_rad,
        support_magnitude=request.support_magnitude,
        steering_angle_rad=radians(request.steering_across_track_angle_deg),
        support_min_angle_rad=radians(request.support_min_angle_deg),
        support_max_angle_rad=radians(request.support_max_angle_deg),
        baseline_m=Vector3(
            x=request.split_aperture_baseline_m[0],
            y=request.split_aperture_baseline_m[1],
            z=request.split_aperture_baseline_m[2],
        ),
        frequency_hz=request.frequency_khz * 1e3,
        sound_speed_mps=request.sound_speed_mps,
        reference_footprint_width_m=request.reference_footprint_width_m,
        tx_delay_seconds=request.tx_delay_ms * 1e-3,
        parent_beam_index=request.parent_beam_index,
    )
    detections = tuple(
        D9HighDensityDetection(
            detection_index=item.detection_index,
            parent_beam_index=item.parent_beam_index,
            method=item.method,
            source_sample_index=item.source_sample_index,
            source_phase_rad=float(item.source_phase_rad),
            arrival_offset_ms=float(item.arrival_offset_seconds) * 1e3,
            twtt_ms=float(item.twtt_seconds) * 1e3,
            detected_across_track_angle_deg=degrees(float(item.detected_across_track_angle_rad)),
            local_bottom_point_m=_xyz(item.local_bottom_point_m),
        )
        for item in result.detections
    )
    points = [item.local_bottom_point_m for item in detections]
    spacings = tuple(_distance(points[index], points[index + 1]) for index in range(len(points) - 1))
    ordinary_count = 1 if result.ordinary_detection_arrival_seconds is not None else 0
    multiplier = float(len(detections)) / ordinary_count if ordinary_count else 0.0
    return D9HighDensityResponse(
        status=result.status,
        ordinary_detection_arrival_ms=(
            None
            if result.ordinary_detection_arrival_seconds is None
            else float(result.ordinary_detection_arrival_seconds) * 1e3
        ),
        ordinary_detection_angle_deg=(
            None
            if result.ordinary_detection_angle_rad is None
            else degrees(float(result.ordinary_detection_angle_rad))
        ),
        candidate_count=result.candidate_count,
        detections=detections,
        comparison=D9HighDensityComparison(
            ordinary_detection_count=ordinary_count,
            high_density_detection_count=len(detections),
            density_multiplier=multiplier,
            target_spacing_m=result.target_spacing_m,
            adjacent_spacing_m=spacings,
        ),
        unavailable_reason=result.unavailable_reason,
        metadata={
            "frequency_khz": request.frequency_khz,
            "sound_speed_mps": request.sound_speed_mps,
            "reference_footprint_width_m": request.reference_footprint_width_m,
            "phase_model": "split_aperture_bounded_phase_inversion",
            "spatial_decimation": "target spacing W_ref/2",
            "positive_angle_direction": "Port (-Y)",
            "state_semantics": "Configured phase inputs; Observed time/angle detections; Derived Cartesian comparison",
            "high_density_distinct_from_multiple_detection": True,
        },
    )

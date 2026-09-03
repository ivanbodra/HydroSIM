"""Application adapter for the PED-D4 sound-speed/refraction learner experience.

This module performs request validation, unit conversion, state labeling, and
serialization only. Ray geometry and travel-time physics remain in the canonical
layered propagation Scientific Core.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.layered_propagation import (
    LayeredRayPath,
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_for_travel_time,
    trace_layered_ray_to_depth,
)


class D4ProfileLayer(BaseModel):
    """Configured finite piecewise-constant sound-speed layer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    top_depth_m: float = Field(ge=0.0)
    bottom_depth_m: float = Field(gt=0.0)
    sound_speed_mps: float = Field(gt=0.0)

    @model_validator(mode="after")
    def _validate_depth_order(self) -> "D4ProfileLayer":
        if self.bottom_depth_m <= self.top_depth_m:
            raise ValueError("bottom_depth_m must exceed top_depth_m")
        return self


class D4RefractionRequest(BaseModel):
    """Configured PED-D4 inputs for reference and processing-profile rays."""

    model_config = ConfigDict(extra="forbid")

    launch_angle_deg_from_vertical: float = Field(default=30.0, ge=0.0, lt=90.0)
    start_depth_m: float = Field(default=0.0, ge=0.0)
    target_depth_m: float = Field(default=100.0, gt=0.0)
    reference_profile: tuple[D4ProfileLayer, ...] = (
        D4ProfileLayer(top_depth_m=0.0, bottom_depth_m=50.0, sound_speed_mps=1500.0),
        D4ProfileLayer(top_depth_m=50.0, bottom_depth_m=150.0, sound_speed_mps=1520.0),
    )
    processing_profile: tuple[D4ProfileLayer, ...] | None = None

    @model_validator(mode="after")
    def _validate_depths(self) -> "D4RefractionRequest":
        if self.target_depth_m <= self.start_depth_m:
            raise ValueError("target_depth_m must exceed start_depth_m")
        return self


class D4RaySegment(BaseModel):
    model_config = ConfigDict(frozen=True)

    layer_index: int
    start_depth_m: float
    end_depth_m: float
    sound_speed_mps: float
    angle_from_vertical_deg: float
    horizontal_distance_m: float
    path_length_m: float
    travel_time_seconds: float
    ray_parameter_seconds_per_m: float


class D4RayResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    start_depth_m: float
    target_depth_m: float
    launch_angle_deg_from_vertical: float
    ray_parameter_seconds_per_m: float
    horizontal_distance_m: float
    path_length_m: float
    travel_time_seconds: float
    segments: tuple[D4RaySegment, ...]


class D4ProfileComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference: D4RayResult
    processing: D4RayResult
    horizontal_endpoint_error_m: float
    depth_endpoint_error_m: float
    path_length_difference_m: float
    travel_time_difference_seconds: float


class D4RefractionResponse(BaseModel):
    """Stable render-ready PED-D4 contract derived from canonical Core outputs."""

    model_config = ConfigDict(frozen=True)

    reference_ray: D4RayResult
    profile_comparison: D4ProfileComparison | None
    metadata: dict[str, str | float]


def _build_profile(layers: tuple[D4ProfileLayer, ...]) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=tuple(
            SoundSpeedLayer(
                top_depth_m=layer.top_depth_m,
                bottom_depth_m=layer.bottom_depth_m,
                sound_speed_mps=layer.sound_speed_mps,
            )
            for layer in layers
        )
    )


def _serialize_ray(path: LayeredRayPath) -> D4RayResult:
    p = float(path.ray_parameter_seconds_per_m)
    return D4RayResult(
        start_depth_m=float(path.start_depth_m),
        target_depth_m=float(path.target_depth_m),
        launch_angle_deg_from_vertical=degrees(float(path.launch_angle_from_vertical_rad)),
        ray_parameter_seconds_per_m=p,
        horizontal_distance_m=float(path.horizontal_distance_m),
        path_length_m=float(path.path_length_m),
        travel_time_seconds=float(path.travel_time_seconds),
        segments=tuple(
            D4RaySegment(
                layer_index=int(segment.layer_index),
                start_depth_m=float(segment.start_depth_m),
                end_depth_m=float(segment.end_depth_m),
                sound_speed_mps=float(segment.sound_speed_mps),
                angle_from_vertical_deg=degrees(float(segment.angle_from_vertical_rad)),
                horizontal_distance_m=float(segment.horizontal_distance_m),
                path_length_m=float(segment.path_length_m),
                travel_time_seconds=float(segment.travel_time_seconds),
                ray_parameter_seconds_per_m=p,
            )
            for segment in path.segments
        ),
    )


def prepare_d4_refraction_response(request: D4RefractionRequest) -> D4RefractionResponse:
    """Evaluate PED-D4 through the canonical layered propagation Core."""

    angle_rad = radians(request.launch_angle_deg_from_vertical)
    reference_profile = _build_profile(request.reference_profile)
    reference_path = trace_layered_ray_to_depth(
        profile=reference_profile,
        launch_angle_from_vertical_rad=angle_rad,
        target_depth_m=request.target_depth_m,
        start_depth_m=request.start_depth_m,
    )
    reference_ray = _serialize_ray(reference_path)

    comparison = None
    if request.processing_profile is not None:
        processing_profile = _build_profile(request.processing_profile)
        processing_path = trace_layered_ray_for_travel_time(
            profile=processing_profile,
            launch_angle_from_vertical_rad=angle_rad,
            travel_time_seconds=float(reference_path.travel_time_seconds),
            start_depth_m=request.start_depth_m,
        )
        processing_ray = _serialize_ray(processing_path)
        comparison = D4ProfileComparison(
            reference=reference_ray,
            processing=processing_ray,
            horizontal_endpoint_error_m=(
                float(processing_path.horizontal_distance_m)
                - float(reference_path.horizontal_distance_m)
            ),
            depth_endpoint_error_m=(
                float(processing_path.target_depth_m) - float(reference_path.target_depth_m)
            ),
            path_length_difference_m=(
                float(processing_path.path_length_m) - float(reference_path.path_length_m)
            ),
            travel_time_difference_seconds=(
                float(processing_path.travel_time_seconds) - float(reference_path.travel_time_seconds)
            ),
        )

    return D4RefractionResponse(
        reference_ray=reference_ray,
        profile_comparison=comparison,
        metadata={
            "angle_ui_unit": "deg from downward vertical",
            "angle_internal_unit": "rad from downward vertical",
            "distance_unit": "m",
            "sound_speed_unit": "m/s",
            "travel_time_unit": "s",
            "propagation_model": "layered_snell_piecewise_constant",
            "reference_profile_state": "Truth for comparison exercise; otherwise Configured",
            "processing_profile_state": "Configured",
            "ray_outputs_state": "Derived",
        },
    )

"""Application bridge for the PED-D4 Sound Speed & Refraction experience.

This module owns validation, state semantics and serialization only. Layered-ray
physics remains in :mod:`hydrosim.acquisition.layered_propagation`.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition import (
    LayeredRayPath,
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_for_travel_time,
    trace_layered_ray_to_depth,
)


class D4LayerInput(BaseModel):
    """One learner-configured piecewise-constant sound-speed layer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    top_depth_m: float = Field(ge=0.0)
    bottom_depth_m: float = Field(gt=0.0)
    sound_speed_mps: float = Field(gt=0.0)


class D4PropagationRequest(BaseModel):
    """Configured inputs for the minimal PED-D4 ray experiment."""

    model_config = ConfigDict(extra="forbid")

    launch_angle_deg: float = Field(default=30.0, ge=0.0, lt=90.0)
    target_depth_m: float = Field(default=30.0, gt=0.0)
    reference_profile: tuple[D4LayerInput, ...] = (
        D4LayerInput(top_depth_m=0.0, bottom_depth_m=10.0, sound_speed_mps=1480.0),
        D4LayerInput(top_depth_m=10.0, bottom_depth_m=40.0, sound_speed_mps=1520.0),
    )
    processing_profile: tuple[D4LayerInput, ...] | None = None


class D4SegmentOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    layer_index: int
    start_depth_m: float
    end_depth_m: float
    sound_speed_mps: float
    angle_from_vertical_deg: float
    horizontal_distance_m: float
    path_length_m: float
    travel_time_ms: float


class D4RayOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    launch_angle_deg: float
    ray_parameter_s_per_m: float
    endpoint_horizontal_m: float
    endpoint_depth_m: float
    path_length_m: float
    travel_time_ms: float
    polyline_horizontal_m: tuple[float, ...]
    polyline_depth_m: tuple[float, ...]
    segments: tuple[D4SegmentOutput, ...]


class D4ProfileOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    layers: tuple[D4LayerInput, ...]
    state: str


class D4ComparisonOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    processing_ray: D4RayOutput
    horizontal_error_m: float
    depth_error_m: float
    path_length_difference_m: float
    travel_time_difference_ms: float
    state_semantics: str


class D4PropagationResponse(BaseModel):
    """Render-ready PED-D4 canonical ray and optional incorrect-profile comparison."""

    model_config = ConfigDict(frozen=True)

    reference_profile: D4ProfileOutput
    processing_profile: D4ProfileOutput | None
    reference_ray: D4RayOutput
    comparison: D4ComparisonOutput | None
    metadata: dict[str, str]


def _profile(inputs: tuple[D4LayerInput, ...]) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=tuple(
            SoundSpeedLayer(
                top_depth_m=layer.top_depth_m,
                bottom_depth_m=layer.bottom_depth_m,
                sound_speed_mps=layer.sound_speed_mps,
            )
            for layer in inputs
        )
    )


def _serialize_ray(path: LayeredRayPath) -> D4RayOutput:
    horizontal_points = [0.0]
    depth_points = [float(path.start_depth_m)]
    cumulative_horizontal = 0.0
    segments: list[D4SegmentOutput] = []

    for segment in path.segments:
        cumulative_horizontal += float(segment.horizontal_distance_m)
        horizontal_points.append(cumulative_horizontal)
        depth_points.append(float(segment.end_depth_m))
        segments.append(
            D4SegmentOutput(
                layer_index=int(segment.layer_index),
                start_depth_m=float(segment.start_depth_m),
                end_depth_m=float(segment.end_depth_m),
                sound_speed_mps=float(segment.sound_speed_mps),
                angle_from_vertical_deg=degrees(float(segment.angle_from_vertical_rad)),
                horizontal_distance_m=float(segment.horizontal_distance_m),
                path_length_m=float(segment.path_length_m),
                travel_time_ms=float(segment.travel_time_seconds) * 1e3,
            )
        )

    return D4RayOutput(
        launch_angle_deg=degrees(float(path.launch_angle_from_vertical_rad)),
        ray_parameter_s_per_m=float(path.ray_parameter_seconds_per_m),
        endpoint_horizontal_m=float(path.horizontal_distance_m),
        endpoint_depth_m=float(path.target_depth_m),
        path_length_m=float(path.path_length_m),
        travel_time_ms=float(path.travel_time_seconds) * 1e3,
        polyline_horizontal_m=tuple(horizontal_points),
        polyline_depth_m=tuple(depth_points),
        segments=tuple(segments),
    )


def prepare_d4_propagation_response(request: D4PropagationRequest) -> D4PropagationResponse:
    """Delegate PED-D4 scientific evaluation to the canonical layered-ray Core."""

    reference_profile = _profile(request.reference_profile)
    launch_angle_rad = radians(request.launch_angle_deg)
    reference_path = trace_layered_ray_to_depth(
        profile=reference_profile,
        launch_angle_from_vertical_rad=launch_angle_rad,
        target_depth_m=request.target_depth_m,
    )
    reference_ray = _serialize_ray(reference_path)

    processing_profile_output = None
    comparison = None
    if request.processing_profile is not None:
        processing_profile = _profile(request.processing_profile)
        processing_path = trace_layered_ray_for_travel_time(
            profile=processing_profile,
            launch_angle_from_vertical_rad=launch_angle_rad,
            travel_time_seconds=float(reference_path.travel_time_seconds),
        )
        processing_ray = _serialize_ray(processing_path)
        processing_profile_output = D4ProfileOutput(
            layers=request.processing_profile,
            state="Configured processing profile",
        )
        comparison = D4ComparisonOutput(
            processing_ray=processing_ray,
            horizontal_error_m=(
                processing_ray.endpoint_horizontal_m - reference_ray.endpoint_horizontal_m
            ),
            depth_error_m=processing_ray.endpoint_depth_m - reference_ray.endpoint_depth_m,
            path_length_difference_m=processing_ray.path_length_m - reference_ray.path_length_m,
            travel_time_difference_ms=processing_ray.travel_time_ms - reference_ray.travel_time_ms,
            state_semantics="Derived simulation-truth error; not Observed uncertainty",
        )

    return D4PropagationResponse(
        reference_profile=D4ProfileOutput(
            layers=request.reference_profile,
            state="Truth/reference environment for this exercise",
        ),
        processing_profile=processing_profile_output,
        reference_ray=reference_ray,
        comparison=comparison,
        metadata={
            "experience": "PED-D4",
            "model": "hydrosim.propagation.layered_snell_piecewise_constant",
            "angle_convention": "degrees from local downward vertical",
            "horizontal_direction": "positive within the 2-D propagation plane",
            "representation": "piecewise_constant_layer_ray_polyline",
            "state_semantics": "Configured profiles/angle; Derived ray quantities",
            "validity": "2-D downward piecewise-constant layers; no turning/critical branch or extrapolation",
        },
    )

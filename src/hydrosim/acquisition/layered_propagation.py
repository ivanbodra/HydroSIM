"""Piecewise-constant layered sound-speed ray tracing.

This is HydroSIM's first refracting propagation model. It preserves the ray
parameter across horizontal interfaces and traces a downward ray to a requested
depth. The model is intentionally two-dimensional in the vertical propagation
plane; azimuth remains unchanged in a horizontally stratified ocean.

For angle theta measured from local vertical and sound speed c,

    p = sin(theta) / c

is conserved. Within each constant-c layer the ray is straight. Refraction occurs
at interfaces through the updated theta satisfying sin(theta)=p*c.
"""

from __future__ import annotations

from math import asin, cos, sin, sqrt, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator


class SoundSpeedLayer(BaseModel):
    """One horizontal layer with constant sound speed."""

    model_config = ConfigDict(frozen=True)

    top_depth_m: FiniteFloat = Field(ge=0.0)
    bottom_depth_m: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)

    @model_validator(mode="after")
    def _validate_depth_order(self) -> "SoundSpeedLayer":
        if self.bottom_depth_m <= self.top_depth_m:
            raise ValueError("layer bottom_depth_m must exceed top_depth_m")
        return self


class LayeredSoundSpeedProfile(BaseModel):
    """Contiguous piecewise-constant vertical sound-speed profile."""

    model_config = ConfigDict(frozen=True)

    layers: tuple[SoundSpeedLayer, ...]
    continuity_tolerance_m: FiniteFloat = Field(default=1e-9, ge=0.0)

    @model_validator(mode="after")
    def _validate_layers(self) -> "LayeredSoundSpeedProfile":
        if not self.layers:
            raise ValueError("sound-speed profile must contain at least one layer")
        tolerance = float(self.continuity_tolerance_m)
        for previous, current in zip(self.layers, self.layers[1:], strict=False):
            if abs(float(previous.bottom_depth_m) - float(current.top_depth_m)) > tolerance:
                raise ValueError("sound-speed layers must be contiguous and ordered")
        return self

    def layer_at_depth(self, depth_m: float) -> SoundSpeedLayer:
        depth = float(depth_m)
        for index, layer in enumerate(self.layers):
            top = float(layer.top_depth_m)
            bottom = float(layer.bottom_depth_m)
            is_last = index == len(self.layers) - 1
            if top <= depth < bottom or (is_last and top <= depth <= bottom):
                return layer
        raise ValueError("depth lies outside sound-speed profile")


class LayeredRaySegment(BaseModel):
    """One straight ray segment within a constant-sound-speed layer."""

    model_config = ConfigDict(frozen=True)

    layer_index: int = Field(ge=0)
    start_depth_m: FiniteFloat = Field(ge=0.0)
    end_depth_m: FiniteFloat = Field(ge=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    angle_from_vertical_rad: FiniteFloat
    horizontal_distance_m: FiniteFloat = Field(ge=0.0)
    path_length_m: FiniteFloat = Field(ge=0.0)
    travel_time_seconds: FiniteFloat = Field(ge=0.0)


class LayeredRayPath(BaseModel):
    """Integrated refracting ray path to a target depth."""

    model_config = ConfigDict(frozen=True)

    start_depth_m: FiniteFloat = Field(ge=0.0)
    target_depth_m: FiniteFloat = Field(gt=0.0)
    launch_angle_from_vertical_rad: FiniteFloat
    ray_parameter_seconds_per_m: FiniteFloat = Field(ge=0.0)
    horizontal_distance_m: FiniteFloat = Field(ge=0.0)
    path_length_m: FiniteFloat = Field(ge=0.0)
    travel_time_seconds: FiniteFloat = Field(ge=0.0)
    segments: tuple[LayeredRaySegment, ...]


def trace_layered_ray_to_depth(
    *,
    profile: LayeredSoundSpeedProfile,
    launch_angle_from_vertical_rad: float,
    target_depth_m: float,
    start_depth_m: float = 0.0,
) -> LayeredRayPath:
    """Trace a downward refracting ray through horizontal constant-c layers.

    Angles are magnitudes measured from vertical in the propagation plane. The
    first implementation therefore traces horizontal distance magnitude; the
    caller retains the sign/azimuth of the original 3-D steering direction.

    A ray that would require ``p*c >= 1`` in a deeper layer cannot propagate
    downward through that interface in this simple transmitted-ray branch and is
    rejected explicitly rather than silently clamped.
    """

    angle = float(launch_angle_from_vertical_rad)
    if angle < 0.0 or angle >= 0.5 * 3.141592653589793:
        raise ValueError("launch angle must satisfy 0 <= angle < pi/2")

    start = float(start_depth_m)
    target = float(target_depth_m)
    if target <= start:
        raise ValueError("target_depth_m must exceed start_depth_m")

    start_layer = profile.layer_at_depth(start)
    profile.layer_at_depth(target)
    p = sin(angle) / float(start_layer.sound_speed_mps)

    segments: list[LayeredRaySegment] = []
    total_horizontal = 0.0
    total_path = 0.0
    total_time = 0.0
    current_depth = start

    for layer_index, layer in enumerate(profile.layers):
        layer_top = float(layer.top_depth_m)
        layer_bottom = float(layer.bottom_depth_m)
        if current_depth >= target:
            break
        if layer_bottom <= current_depth or layer_top > current_depth + 1e-9:
            continue

        end_depth = min(layer_bottom, target)
        dz = end_depth - current_depth
        if dz <= 0.0:
            continue

        c = float(layer.sound_speed_mps)
        sine_theta = p * c
        if sine_theta >= 1.0:
            raise ValueError("ray reaches a critical/turning condition in the layered profile")
        theta = asin(sine_theta)
        cosine_theta = cos(theta)
        horizontal = dz * tan(theta)
        path_length = dz / cosine_theta
        travel_time = path_length / c

        segments.append(
            LayeredRaySegment(
                layer_index=layer_index,
                start_depth_m=current_depth,
                end_depth_m=end_depth,
                sound_speed_mps=c,
                angle_from_vertical_rad=theta,
                horizontal_distance_m=horizontal,
                path_length_m=path_length,
                travel_time_seconds=travel_time,
            )
        )
        total_horizontal += horizontal
        total_path += path_length
        total_time += travel_time
        current_depth = end_depth

    if abs(current_depth - target) > 1e-9:
        raise ValueError("target depth could not be reached within the sound-speed profile")

    return LayeredRayPath(
        start_depth_m=start,
        target_depth_m=target,
        launch_angle_from_vertical_rad=angle,
        ray_parameter_seconds_per_m=p,
        horizontal_distance_m=total_horizontal,
        path_length_m=total_path,
        travel_time_seconds=total_time,
        segments=tuple(segments),
    )

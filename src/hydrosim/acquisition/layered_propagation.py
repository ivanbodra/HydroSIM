"""Piecewise-constant layered sound-speed ray tracing.

Scientific basis and source traceability for the transducer/profile boundary:
    docs/science/sound_speed_at_transducer.md

For angle theta measured from local vertical and sound speed c, the horizontal ray
parameter is p = sin(theta) / c and is conserved across horizontal interfaces.
HydroSIM may initialize p from an explicit zero-thickness sound-speed boundary at
the transducer and then propagate through the finite-thickness water-column layers.
This represents the snap-back/initial-entry concept without overwriting a whole
profile layer with a point measurement.
"""

from __future__ import annotations

from math import asin, cos, sin, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from .sound_speed_profile_boundary import SoundSpeedProfileBoundary


class SoundSpeedLayer(BaseModel):
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
    model_config = ConfigDict(frozen=True)
    start_depth_m: FiniteFloat = Field(ge=0.0)
    target_depth_m: FiniteFloat = Field(gt=0.0)
    launch_angle_from_vertical_rad: FiniteFloat
    ray_parameter_seconds_per_m: FiniteFloat = Field(ge=0.0)
    horizontal_distance_m: FiniteFloat = Field(ge=0.0)
    path_length_m: FiniteFloat = Field(ge=0.0)
    travel_time_seconds: FiniteFloat = Field(ge=0.0)
    segments: tuple[LayeredRaySegment, ...]


class LayeredRayClosureDiagnostic(BaseModel):
    model_config = ConfigDict(frozen=True)
    depth_driven_path: LayeredRayPath
    time_driven_path: LayeredRayPath
    absolute_depth_closure_m: FiniteFloat = Field(ge=0.0)
    absolute_horizontal_closure_m: FiniteFloat = Field(ge=0.0)
    absolute_path_length_closure_m: FiniteFloat = Field(ge=0.0)
    depth_tolerance_m: FiniteFloat = Field(ge=0.0)
    horizontal_tolerance_m: FiniteFloat = Field(ge=0.0)
    path_length_tolerance_m: FiniteFloat = Field(ge=0.0)
    converged: bool


def _validate_launch_angle(angle_value: float) -> float:
    angle = float(angle_value)
    if angle < 0.0 or angle >= 0.5 * 3.141592653589793:
        raise ValueError("launch angle must satisfy 0 <= angle < pi/2")
    return angle


def _layer_angle(ray_parameter: float, sound_speed_mps: float) -> float:
    sine_theta = float(ray_parameter) * float(sound_speed_mps)
    if sine_theta >= 1.0:
        raise ValueError("ray reaches a critical/turning condition in the layered profile")
    return asin(sine_theta)


def _initial_ray_parameter(*, profile: LayeredSoundSpeedProfile, start_depth_m: float, launch_angle_rad: float, start_boundary: SoundSpeedProfileBoundary | None) -> float:
    if start_boundary is not None:
        if abs(float(start_boundary.depth_m) - float(start_depth_m)) > float(profile.continuity_tolerance_m):
            raise ValueError("start boundary depth must match ray-tracing start depth")
        initial_c = float(start_boundary.sound_speed_mps)
    else:
        initial_c = float(profile.layer_at_depth(start_depth_m).sound_speed_mps)
    return sin(launch_angle_rad) / initial_c


def trace_layered_ray_to_depth(*, profile: LayeredSoundSpeedProfile, launch_angle_from_vertical_rad: float, target_depth_m: float, start_depth_m: float = 0.0, start_boundary: SoundSpeedProfileBoundary | None = None) -> LayeredRayPath:
    angle = _validate_launch_angle(launch_angle_from_vertical_rad)
    start = float(start_depth_m); target = float(target_depth_m)
    if target <= start: raise ValueError("target_depth_m must exceed start_depth_m")
    profile.layer_at_depth(start); profile.layer_at_depth(target)
    p = _initial_ray_parameter(profile=profile, start_depth_m=start, launch_angle_rad=angle, start_boundary=start_boundary)
    segments=[]; total_horizontal=total_path=total_time=0.0; current_depth=start
    for layer_index, layer in enumerate(profile.layers):
        layer_top=float(layer.top_depth_m); layer_bottom=float(layer.bottom_depth_m)
        if current_depth >= target: break
        if layer_bottom <= current_depth or layer_top > current_depth + 1e-9: continue
        end_depth=min(layer_bottom,target); dz=end_depth-current_depth
        if dz <= 0.0: continue
        c=float(layer.sound_speed_mps); theta=_layer_angle(p,c); cosine_theta=cos(theta)
        horizontal=dz*tan(theta); path_length=dz/cosine_theta; travel_time=path_length/c
        segments.append(LayeredRaySegment(layer_index=layer_index,start_depth_m=current_depth,end_depth_m=end_depth,sound_speed_mps=c,angle_from_vertical_rad=theta,horizontal_distance_m=horizontal,path_length_m=path_length,travel_time_seconds=travel_time))
        total_horizontal+=horizontal; total_path+=path_length; total_time+=travel_time; current_depth=end_depth
    if abs(current_depth-target)>1e-9: raise ValueError("target depth could not be reached within the sound-speed profile")
    return LayeredRayPath(start_depth_m=start,target_depth_m=target,launch_angle_from_vertical_rad=angle,ray_parameter_seconds_per_m=p,horizontal_distance_m=total_horizontal,path_length_m=total_path,travel_time_seconds=total_time,segments=tuple(segments))


def trace_layered_ray_for_travel_time(*, profile: LayeredSoundSpeedProfile, launch_angle_from_vertical_rad: float, travel_time_seconds: float, start_depth_m: float = 0.0, start_boundary: SoundSpeedProfileBoundary | None = None) -> LayeredRayPath:
    angle=_validate_launch_angle(launch_angle_from_vertical_rad); requested_time=float(travel_time_seconds)
    if requested_time<=0.0: raise ValueError("travel_time_seconds must be positive")
    start=float(start_depth_m); profile.layer_at_depth(start)
    p=_initial_ray_parameter(profile=profile,start_depth_m=start,launch_angle_rad=angle,start_boundary=start_boundary)
    segments=[]; total_horizontal=total_path=total_time=0.0; current_depth=start; remaining_time=requested_time
    for layer_index,layer in enumerate(profile.layers):
        layer_top=float(layer.top_depth_m); layer_bottom=float(layer.bottom_depth_m)
        if remaining_time<=1e-15: break
        if layer_bottom<=current_depth or layer_top>current_depth+1e-9: continue
        c=float(layer.sound_speed_mps); theta=_layer_angle(p,c); cosine_theta=cos(theta)
        available_dz=layer_bottom-current_depth; full_path_length=available_dz/cosine_theta; full_travel_time=full_path_length/c
        if remaining_time<full_travel_time-1e-15:
            travel_time=remaining_time; path_length=c*travel_time; dz=path_length*cosine_theta; horizontal=path_length*sin(theta); end_depth=current_depth+dz
        else:
            travel_time=full_travel_time; path_length=full_path_length; horizontal=available_dz*tan(theta); end_depth=layer_bottom
        segments.append(LayeredRaySegment(layer_index=layer_index,start_depth_m=current_depth,end_depth_m=end_depth,sound_speed_mps=c,angle_from_vertical_rad=theta,horizontal_distance_m=horizontal,path_length_m=path_length,travel_time_seconds=travel_time))
        total_horizontal+=horizontal; total_path+=path_length; total_time+=travel_time; remaining_time-=travel_time; current_depth=end_depth
    if remaining_time>1e-12: raise ValueError("travel time extends beyond the supplied sound-speed profile")
    return LayeredRayPath(start_depth_m=start,target_depth_m=current_depth,launch_angle_from_vertical_rad=angle,ray_parameter_seconds_per_m=p,horizontal_distance_m=total_horizontal,path_length_m=total_path,travel_time_seconds=total_time,segments=tuple(segments))


def assess_layered_ray_time_depth_closure(*, profile: LayeredSoundSpeedProfile, launch_angle_from_vertical_rad: float, target_depth_m: float, start_depth_m: float=0.0, start_boundary: SoundSpeedProfileBoundary | None=None, depth_tolerance_m: float=1e-9, horizontal_tolerance_m: float=1e-9, path_length_tolerance_m: float=1e-9) -> LayeredRayClosureDiagnostic:
    depth_tol=float(depth_tolerance_m); horizontal_tol=float(horizontal_tolerance_m); path_tol=float(path_length_tolerance_m)
    if depth_tol<0 or horizontal_tol<0 or path_tol<0: raise ValueError("closure tolerances must be non-negative")
    depth_path=trace_layered_ray_to_depth(profile=profile,launch_angle_from_vertical_rad=launch_angle_from_vertical_rad,target_depth_m=target_depth_m,start_depth_m=start_depth_m,start_boundary=start_boundary)
    time_path=trace_layered_ray_for_travel_time(profile=profile,launch_angle_from_vertical_rad=launch_angle_from_vertical_rad,travel_time_seconds=float(depth_path.travel_time_seconds),start_depth_m=start_depth_m,start_boundary=start_boundary)
    depth_error=abs(float(time_path.target_depth_m)-float(depth_path.target_depth_m)); horizontal_error=abs(float(time_path.horizontal_distance_m)-float(depth_path.horizontal_distance_m)); path_error=abs(float(time_path.path_length_m)-float(depth_path.path_length_m))
    return LayeredRayClosureDiagnostic(depth_driven_path=depth_path,time_driven_path=time_path,absolute_depth_closure_m=depth_error,absolute_horizontal_closure_m=horizontal_error,absolute_path_length_closure_m=path_error,depth_tolerance_m=depth_tol,horizontal_tolerance_m=horizontal_tol,path_length_tolerance_m=path_tol,converged=depth_error<=depth_tol and horizontal_error<=horizontal_tol and path_error<=path_tol)

"""Receive-beam spacing strategies.

Beam spacing and bottom detection are orthogonal concerns.  This module decides
where receive beams are steered; detection modules decide how one or more bottom
detections are extracted from each beam.

Two reference strategies are implemented:

* equiangular: constant angular increment;
* equidistant: steering angles are solved so the ray endpoints have constant
  across-track spacing at a target depth for the configured layered sound-speed
  profile.

The equidistant implementation is therefore not limited to the flat,
constant-sound-speed arctangent approximation.
"""

from __future__ import annotations

from math import copysign
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .layered_propagation import LayeredSoundSpeedProfile, trace_layered_ray_to_depth


class BeamSteeringPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    spacing_method: Literal["equiangular", "equidistant"]
    across_track_angles_rad: tuple[FiniteFloat, ...]
    target_across_track_positions_m: tuple[FiniteFloat, ...] | None = None


def make_equiangular_beam_plan(*, minimum_angle_rad: float, maximum_angle_rad: float, beam_count: int) -> BeamSteeringPlan:
    if beam_count < 2:
        raise ValueError("beam_count must be at least two")
    if maximum_angle_rad <= minimum_angle_rad:
        raise ValueError("maximum_angle_rad must exceed minimum_angle_rad")
    step = (maximum_angle_rad - minimum_angle_rad) / (beam_count - 1)
    angles = tuple(minimum_angle_rad + i * step for i in range(beam_count))
    return BeamSteeringPlan(spacing_method="equiangular", across_track_angles_rad=angles)


def _signed_endpoint(profile: LayeredSoundSpeedProfile, angle_rad: float, target_depth_m: float, start_depth_m: float) -> float:
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=abs(angle_rad),
        target_depth_m=target_depth_m,
        start_depth_m=start_depth_m,
    )
    return copysign(float(path.horizontal_distance_m), angle_rad) if angle_rad != 0.0 else 0.0


def _solve_angle_for_endpoint(*, profile: LayeredSoundSpeedProfile, target_position_m: float, target_depth_m: float, start_depth_m: float, maximum_search_angle_rad: float, iterations: int = 60) -> float:
    if target_position_m == 0.0:
        return 0.0
    sign = 1.0 if target_position_m > 0.0 else -1.0
    target = abs(target_position_m)
    lo, hi = 0.0, abs(maximum_search_angle_rad)
    if abs(_signed_endpoint(profile, sign * hi, target_depth_m, start_depth_m)) < target:
        raise ValueError("target across-track position lies outside the searchable angular sector")
    for _ in range(iterations):
        mid = 0.5 * (lo + hi)
        distance = abs(_signed_endpoint(profile, sign * mid, target_depth_m, start_depth_m))
        if distance < target:
            lo = mid
        else:
            hi = mid
    return sign * 0.5 * (lo + hi)


def make_equidistant_beam_plan(*, profile: LayeredSoundSpeedProfile, minimum_angle_rad: float, maximum_angle_rad: float, beam_count: int, target_depth_m: float, start_depth_m: float = 0.0) -> BeamSteeringPlan:
    """Solve beam angles for equally spaced endpoints over the requested sector."""
    if beam_count < 2:
        raise ValueError("beam_count must be at least two")
    if minimum_angle_rad >= 0.0 or maximum_angle_rad <= 0.0:
        raise ValueError("reference equidistant plan currently requires a sector spanning nadir")
    left = _signed_endpoint(profile, minimum_angle_rad, target_depth_m, start_depth_m)
    right = _signed_endpoint(profile, maximum_angle_rad, target_depth_m, start_depth_m)
    step = (right - left) / (beam_count - 1)
    targets = tuple(left + i * step for i in range(beam_count))
    search = max(abs(minimum_angle_rad), abs(maximum_angle_rad))
    angles = tuple(
        _solve_angle_for_endpoint(
            profile=profile,
            target_position_m=target,
            target_depth_m=target_depth_m,
            start_depth_m=start_depth_m,
            maximum_search_angle_rad=search,
        )
        for target in targets
    )
    return BeamSteeringPlan(
        spacing_method="equidistant",
        across_track_angles_rad=angles,
        target_across_track_positions_m=targets,
    )

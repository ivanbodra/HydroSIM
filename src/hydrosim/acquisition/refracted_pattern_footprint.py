"""Project sampled TX×RX angular cells through a layered sound-speed profile.

This module keeps propagation separate from bottom geometry. Each angular sample
is interpreted as a launch direction in the sensor frame. Its magnitude from the
vertical is traced through a horizontally stratified piecewise-constant profile;
azimuth is preserved because horizontal layers do not rotate the propagation
plane.

The resulting bottom position, acoustic path length, travel time, and final ray
angle are retained per cell. Projected cell area is estimated from the four
refracted angular-cell corners, so refraction may change the spatial weighting as
well as the travel-time and incidence-angle fields.
"""

from __future__ import annotations

from math import atan, atan2, cos, hypot, sin

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_pattern_2d import AngularPattern2DScan
from .layered_propagation import LayeredSoundSpeedProfile, trace_layered_ray_to_depth
from .pattern_footprint_2d import _cell_edges


class RefractedProjectedPatternCell(BaseModel):
    """One angular cell after layered propagation to a horizontal bottom."""

    model_config = ConfigDict(frozen=True)

    along_track_index: int = Field(ge=0)
    across_track_index: int = Field(ge=0)
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    normalized_power: FiniteFloat = Field(ge=0.0)
    relative_power_to_peak: FiniteFloat = Field(ge=0.0)
    forward_center_m: FiniteFloat
    port_center_m: FiniteFloat
    horizontal_distance_m: FiniteFloat = Field(ge=0.0)
    acoustic_path_length_m: FiniteFloat = Field(gt=0.0)
    one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0)
    projected_area_m2: FiniteFloat = Field(gt=0.0)
    equivalent_area_contribution_m2: FiniteFloat = Field(ge=0.0)


class RefractedPatternIllumination(BaseModel):
    """Full pattern projection after layered refraction."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    start_depth_m: FiniteFloat = Field(ge=0.0)
    target_depth_m: FiniteFloat = Field(gt=0.0)
    peak_power: FiniteFloat = Field(gt=0.0)
    sampled_grid_area_m2: FiniteFloat = Field(gt=0.0)
    equivalent_insonified_area_m2: FiniteFloat = Field(gt=0.0)
    cells: tuple[RefractedProjectedPatternCell, ...]


def _launch_geometry(along: float, across: float) -> tuple[float, float]:
    """Return launch angle from vertical and horizontal azimuth toward +Port."""

    sx = __import__("math").tan(along)
    sy = __import__("math").tan(across)
    slope = hypot(sx, sy)
    return atan(slope), atan2(sy, sx) if slope > 0.0 else 0.0


def _bottom_point(*, profile: LayeredSoundSpeedProfile, along: float, across: float,
                  start_depth_m: float, target_depth_m: float) -> tuple[float, float, float, float, float]:
    launch, azimuth = _launch_geometry(along, across)
    path = trace_layered_ray_to_depth(
        profile=profile, launch_angle_from_vertical_rad=launch,
        target_depth_m=target_depth_m, start_depth_m=start_depth_m,
    )
    horizontal = float(path.horizontal_distance_m)
    forward = horizontal * cos(azimuth)
    port = horizontal * sin(azimuth)
    incidence = float(path.segments[-1].angle_from_vertical_rad)
    return forward, port, float(path.path_length_m), float(path.travel_time_seconds), incidence


def _quadrilateral_area(points: tuple[tuple[float, float], ...]) -> float:
    area2 = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1], strict=False):
        area2 += x0 * y1 - x1 * y0
    return abs(area2) / 2.0


def project_angular_pattern_through_layered_profile(
    *, scan: AngularPattern2DScan, profile: LayeredSoundSpeedProfile,
    target_depth_m: float, start_depth_m: float = 0.0,
) -> RefractedPatternIllumination:
    """Trace every sampled direction and angular-cell corner to a flat bottom."""

    start, target = float(start_depth_m), float(target_depth_m)
    if target <= start:
        raise ValueError("target_depth_m must exceed start_depth_m")
    along_count = len(scan.along_track_angles_rad)
    across_count = len(scan.across_track_angles_rad)
    if len(scan.samples) != along_count * across_count:
        raise ValueError("AngularPattern2DScan sample layout is inconsistent with its axes")
    peak = float(scan.peak_power)
    if peak <= 0.0:
        raise ValueError("AngularPattern2DScan peak_power must be positive")

    along_edges = _cell_edges(scan.along_track_angles_rad)
    across_edges = _cell_edges(scan.across_track_angles_rad)
    corner_cache: dict[tuple[int, int], tuple[float, float]] = {}
    for ai, along in enumerate(along_edges):
        for ci, across in enumerate(across_edges):
            forward, port, *_ = _bottom_point(
                profile=profile, along=along, across=across,
                start_depth_m=start, target_depth_m=target,
            )
            corner_cache[(ai, ci)] = (forward, port)

    cells: list[RefractedProjectedPatternCell] = []
    grid_area = equivalent_area = 0.0
    for ai, along_value in enumerate(scan.along_track_angles_rad):
        along = float(along_value)
        for ci, across_value in enumerate(scan.across_track_angles_rad):
            across = float(across_value)
            sample = scan.samples[ai * across_count + ci]
            power = float(sample.normalized_power)
            relative = power / peak
            forward, port, path_length, travel_time, incidence = _bottom_point(
                profile=profile, along=along, across=across,
                start_depth_m=start, target_depth_m=target,
            )
            corners = (
                corner_cache[(ai, ci)], corner_cache[(ai + 1, ci)],
                corner_cache[(ai + 1, ci + 1)], corner_cache[(ai, ci + 1)],
            )
            area = _quadrilateral_area(corners)
            if area <= 0.0:
                raise ValueError("refracted angular cell projects to zero area")
            contribution = relative * area
            grid_area += area
            equivalent_area += contribution
            cells.append(RefractedProjectedPatternCell(
                along_track_index=ai, across_track_index=ci,
                along_track_angle_rad=along, across_track_angle_rad=across,
                normalized_power=power, relative_power_to_peak=relative,
                forward_center_m=forward, port_center_m=port,
                horizontal_distance_m=hypot(forward, port),
                acoustic_path_length_m=path_length,
                one_way_travel_time_seconds=travel_time,
                incidence_angle_from_normal_rad=incidence,
                projected_area_m2=area,
                equivalent_area_contribution_m2=contribution,
            ))

    return RefractedPatternIllumination(
        configuration_name=scan.configuration_name, start_depth_m=start,
        target_depth_m=target, peak_power=peak, sampled_grid_area_m2=grid_area,
        equivalent_insonified_area_m2=equivalent_area, cells=tuple(cells),
    )

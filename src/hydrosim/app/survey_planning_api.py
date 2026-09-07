"""Render-ready PED-D16 survey-planning bridge.

The adapter implements the authoritative minimum contract in
``docs/science/ped_d16_survey_planning_contract.md`` and reuses canonical PED-D8
swath geometry. React receives planned geometry and consequences and must not
reimplement planning equations or coverage rules.
"""

from __future__ import annotations

from math import ceil, cos, hypot, radians, sin
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.app.echosounder_api import (
    D8EchosounderRequest,
    prepare_d8_echosounder_response,
)

KNOT_TO_MPS = 0.5144444444444445
_EPS = 1e-9

Point2 = tuple[float, float]


class D16SurveyPlanningRequest(BaseModel):
    """Learner-configured rectangular reference survey and acquisition settings."""

    model_config = ConfigDict(extra="forbid")

    area_length_m: float = Field(gt=0.0)
    area_width_m: float = Field(gt=0.0)
    line_direction_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    overlap_percent: float | None = Field(default=20.0, ge=0.0, lt=100.0)
    line_spacing_m: float | None = Field(default=None, gt=0.0)
    vessel_speed_knots: float = Field(default=5.0, ge=0.0)
    echosounder: D8EchosounderRequest = Field(default_factory=D8EchosounderRequest)

    @model_validator(mode="after")
    def validate_spacing_mode(self) -> "D16SurveyPlanningRequest":
        if self.overlap_percent is None and self.line_spacing_m is None:
            raise ValueError("configure overlap_percent or line_spacing_m")
        if self.overlap_percent is not None and self.line_spacing_m is not None:
            raise ValueError("overlap_percent and line_spacing_m are mutually exclusive")
        return self


class D16ReferenceGeometry(BaseModel):
    model_config = ConfigDict(frozen=True)

    selected_system: Literal["sbes", "mbes"]
    reference_depth_m: float
    usable_swath_width_m: float
    area_length_m: float
    area_width_m: float
    line_direction_deg: float
    vessel_speed_knots: float
    vessel_speed_mps: float
    planning_frame: str


class D16LineSegment(BaseModel):
    model_config = ConfigDict(frozen=True)

    line_index: int
    center_offset_m: float
    start_m: Point2
    end_m: Point2
    length_m: float


class D16CoverageStrip(BaseModel):
    model_config = ConfigDict(frozen=True)

    line_index: int
    polygon_m: tuple[Point2, ...]


class D16SurveyPlanningResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ready"]
    reference_geometry: D16ReferenceGeometry
    spacing_mode: Literal["overlap", "explicit_spacing"]
    configured_overlap_percent: float | None
    configured_line_spacing_m: float | None
    requested_spacing_m: float
    actual_spacing_m: float | None
    projected_cross_line_span_m: float
    planned_lines: tuple[D16LineSegment, ...]
    coverage_strips: tuple[D16CoverageStrip, ...]
    line_count: int
    total_planned_length_m: float
    overlap_width_m: float | None
    gap_width_m: float | None
    coverage_classification: Literal["continuous", "overlapping", "touching", "gapped"]
    idealized_on_line_time_s: float | None
    metadata: dict[str, str]


def _area_vertices(request: D16SurveyPlanningRequest) -> tuple[Point2, ...]:
    half_x = request.area_length_m / 2.0
    half_y = request.area_width_m / 2.0
    return ((-half_x, -half_y), (half_x, -half_y), (half_x, half_y), (-half_x, half_y))


def _axes(direction_deg: float) -> tuple[Point2, Point2]:
    alpha = radians(direction_deg)
    u = (sin(alpha), cos(alpha))
    n = (cos(alpha), -sin(alpha))
    return u, n


def _dot(point: Point2, axis: Point2) -> float:
    return point[0] * axis[0] + point[1] * axis[1]


def _clip_infinite_line_to_rectangle(
    *,
    u: Point2,
    n: Point2,
    offset: float,
    half_x: float,
    half_y: float,
) -> tuple[Point2, Point2]:
    base = (n[0] * offset, n[1] * offset)
    t_min = float("-inf")
    t_max = float("inf")
    for base_coord, direction, bound in (
        (base[0], u[0], half_x),
        (base[1], u[1], half_y),
    ):
        if abs(direction) <= _EPS:
            if base_coord < -bound - _EPS or base_coord > bound + _EPS:
                raise ValueError("planned line does not intersect survey rectangle")
            continue
        low = (-bound - base_coord) / direction
        high = (bound - base_coord) / direction
        if low > high:
            low, high = high, low
        t_min = max(t_min, low)
        t_max = min(t_max, high)
    if not t_max > t_min + _EPS:
        raise ValueError("planned line clipping produced no finite segment")
    return (
        (base[0] + u[0] * t_min, base[1] + u[1] * t_min),
        (base[0] + u[0] * t_max, base[1] + u[1] * t_max),
    )


def _clip_polygon_half_plane(
    polygon: tuple[Point2, ...],
    *,
    n: Point2,
    limit: float,
    keep_less_equal: bool,
) -> tuple[Point2, ...]:
    if not polygon:
        return ()

    def signed(point: Point2) -> float:
        value = _dot(point, n) - limit
        return value if keep_less_equal else -value

    result: list[Point2] = []
    previous = polygon[-1]
    previous_value = signed(previous)
    previous_inside = previous_value <= _EPS
    for current in polygon:
        current_value = signed(current)
        current_inside = current_value <= _EPS
        if current_inside != previous_inside:
            denom = previous_value - current_value
            ratio = 0.0 if abs(denom) <= _EPS else previous_value / denom
            intersection = (
                previous[0] + ratio * (current[0] - previous[0]),
                previous[1] + ratio * (current[1] - previous[1]),
            )
            result.append(intersection)
        if current_inside:
            result.append(current)
        previous = current
        previous_value = current_value
        previous_inside = current_inside
    return tuple(result)


def _coverage_polygon(
    rectangle: tuple[Point2, ...], *, n: Point2, offset: float, swath_width: float
) -> tuple[Point2, ...]:
    half = swath_width / 2.0
    polygon = _clip_polygon_half_plane(
        rectangle,
        n=n,
        limit=offset + half,
        keep_less_equal=True,
    )
    polygon = _clip_polygon_half_plane(
        polygon,
        n=n,
        limit=offset - half,
        keep_less_equal=False,
    )
    return polygon


def prepare_d16_survey_planning_response(
    request: D16SurveyPlanningRequest,
) -> D16SurveyPlanningResponse:
    """Build the authoritative minimum rectangular survey plan."""

    d8 = prepare_d8_echosounder_response(request.echosounder)
    selected = d8.sbes if request.echosounder.selected_system == "sbes" else d8.mbes
    swath = float(selected.geometric_beam_center_swath_width_m)
    if swath <= 0.0:
        raise ValueError("selected sonar configuration must provide a positive usable swath width")

    rectangle = _area_vertices(request)
    u, n = _axes(request.line_direction_deg)
    projections = tuple(_dot(vertex, n) for vertex in rectangle)
    c_min = min(projections)
    c_max = max(projections)
    cross_span = c_max - c_min
    if cross_span <= 0.0:
        raise ValueError("projected cross-line span must be positive")

    spacing_mode: Literal["overlap", "explicit_spacing"]
    if request.overlap_percent is not None:
        spacing_mode = "overlap"
        requested_spacing = swath * (1.0 - request.overlap_percent / 100.0)
    else:
        spacing_mode = "explicit_spacing"
        assert request.line_spacing_m is not None
        requested_spacing = request.line_spacing_m

    if cross_span <= swath + _EPS:
        offsets = ((c_min + c_max) / 2.0,)
        actual_spacing = None
    else:
        center_span = cross_span - swath
        count = max(2, ceil(center_span / requested_spacing) + 1)
        actual_spacing = center_span / (count - 1)
        first = c_min + swath / 2.0
        offsets = tuple(first + index * actual_spacing for index in range(count))

    half_x = request.area_length_m / 2.0
    half_y = request.area_width_m / 2.0
    line_results: list[D16LineSegment] = []
    strip_results: list[D16CoverageStrip] = []
    for index, offset in enumerate(offsets):
        start, end = _clip_infinite_line_to_rectangle(
            u=u,
            n=n,
            offset=offset,
            half_x=half_x,
            half_y=half_y,
        )
        if index % 2 == 1:
            start, end = end, start
        length = hypot(end[0] - start[0], end[1] - start[1])
        line_results.append(
            D16LineSegment(
                line_index=index,
                center_offset_m=offset,
                start_m=start,
                end_m=end,
                length_m=length,
            )
        )
        strip_results.append(
            D16CoverageStrip(
                line_index=index,
                polygon_m=_coverage_polygon(rectangle, n=n, offset=offset, swath_width=swath),
            )
        )

    if actual_spacing is None:
        classification: Literal["continuous", "overlapping", "touching", "gapped"] = "continuous"
        overlap_width = None
        gap_width = None
    elif actual_spacing < swath - _EPS:
        classification = "overlapping"
        overlap_width = swath - actual_spacing
        gap_width = None
    elif actual_spacing > swath + _EPS:
        classification = "gapped"
        overlap_width = None
        gap_width = actual_spacing - swath
    else:
        classification = "touching"
        overlap_width = 0.0
        gap_width = 0.0

    total_length = sum(line.length_m for line in line_results)
    vessel_speed_mps = request.vessel_speed_knots * KNOT_TO_MPS
    on_line_time = None if vessel_speed_mps <= 0.0 else total_length / vessel_speed_mps

    return D16SurveyPlanningResponse(
        status="ready",
        reference_geometry=D16ReferenceGeometry(
            selected_system=request.echosounder.selected_system,
            reference_depth_m=d8.target_depth_m,
            usable_swath_width_m=swath,
            area_length_m=request.area_length_m,
            area_width_m=request.area_width_m,
            line_direction_deg=request.line_direction_deg,
            vessel_speed_knots=request.vessel_speed_knots,
            vessel_speed_mps=vessel_speed_mps,
            planning_frame="local metres: +x East-like, +y North-like; heading clockwise from +y",
        ),
        spacing_mode=spacing_mode,
        configured_overlap_percent=request.overlap_percent,
        configured_line_spacing_m=request.line_spacing_m,
        requested_spacing_m=requested_spacing,
        actual_spacing_m=actual_spacing,
        projected_cross_line_span_m=cross_span,
        planned_lines=tuple(line_results),
        coverage_strips=tuple(strip_results),
        line_count=len(line_results),
        total_planned_length_m=total_length,
        overlap_width_m=overlap_width,
        gap_width_m=gap_width,
        coverage_classification=classification,
        idealized_on_line_time_s=on_line_time,
        metadata={
            "state_semantics": "Configured area/sonar/direction/spacing/speed; Derived plan geometry/coverage/time",
            "scientific_contract": "docs/science/ped_d16_survey_planning_contract.md",
            "coverage_boundary": "constant canonical D8 swath; High Density does not widen planning swath",
            "time_boundary": "on-line acquisition only; turns, run-ins and transits excluded",
        },
    )

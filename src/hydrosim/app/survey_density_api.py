"""Render-ready PED-D17 survey coverage and density bridge.

The adapter implements ``docs/science/ped_d17_coverage_density_contract.md`` and
reuses canonical PED-D8 geometry. React supplies learner configuration and, when
available, retained D9/High Density bottom positions; it does not derive spacing,
density, footprint union, or gap rules.
"""

from __future__ import annotations

from math import isfinite
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.app.echosounder_api import D8EchosounderRequest, prepare_d8_echosounder_response

KNOT_TO_MPS = 0.5144444444444445
_MERGE_TOLERANCE_M = 1e-9


class D17Interval(BaseModel):
    model_config = ConfigDict(frozen=True)

    start_m: float
    end_m: float
    width_m: float = Field(ge=0.0)


class D17SurveyDensityRequest(BaseModel):
    """Configured acquisition cadence plus canonical reference sonar geometry."""

    model_config = ConfigDict(extra="forbid")

    ping_rate_hz: float = Field(gt=0.0)
    vessel_speed_knots: float = Field(ge=0.0)
    echosounder: D8EchosounderRequest = Field(default_factory=D8EchosounderRequest)
    retained_across_track_positions_m: tuple[float, ...] | None = None
    high_density_bottom_points_m: tuple[tuple[float, float, float], ...] = ()

    @model_validator(mode="after")
    def _validate_finite_geometry(self) -> "D17SurveyDensityRequest":
        if not isfinite(self.ping_rate_hz) or not isfinite(self.vessel_speed_knots):
            raise ValueError("ping rate and vessel speed must be finite")
        if self.retained_across_track_positions_m is not None and any(
            not isfinite(value) for value in self.retained_across_track_positions_m
        ):
            raise ValueError("retained across-track positions must be finite")
        if any(not all(isfinite(value) for value in point) for point in self.high_density_bottom_points_m):
            raise ValueError("High Density bottom points must be finite")
        return self


class D17AcrossTrackDensity(BaseModel):
    model_config = ConfigDict(frozen=True)

    ordered_positions_m: tuple[float, ...]
    adjacent_spacing_m: tuple[float, ...]
    adjacent_linear_density_per_m: tuple[float | None, ...]
    areal_density_per_m2: tuple[float | None, ...]
    min_spacing_m: float | None
    max_spacing_m: float | None
    mean_spacing_m: float | None


class D17CoverageResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    classification: Literal["continuous", "gapped", "unavailable"]
    footprint_intervals: tuple[D17Interval, ...]
    merged_coverage_intervals: tuple[D17Interval, ...]
    internal_gap_intervals: tuple[D17Interval, ...]
    total_covered_width_m: float | None
    geometric_beam_center_swath_width_m: float | None
    along_track_gap_by_beam_m: tuple[float, ...]
    along_track_classification: Literal["continuous", "gapped", "unavailable"]


class D17SurveyDensityResponse(BaseModel):
    """Stable render-ready PED-D17 O03/O04 consequence contract."""

    model_config = ConfigDict(frozen=True)

    status: Literal["available", "partial"]
    ping_rate_hz: float
    ping_period_s: float
    vessel_speed_knots: float
    vessel_speed_mps: float
    along_track_ping_spacing_m: float
    along_track_ping_density_per_m: float | None
    across_track: D17AcrossTrackDensity
    coverage: D17CoverageResult
    ordinary_sounding_count: int = Field(ge=0)
    retained_sounding_count: int = Field(ge=0)
    high_density_added_count: int = Field(ge=0)
    metadata: dict[str, str | bool]


def _interval(start: float, end: float) -> D17Interval:
    left = min(start, end)
    right = max(start, end)
    return D17Interval(start_m=left, end_m=right, width_m=right - left)


def _merge_intervals(intervals: tuple[D17Interval, ...]) -> tuple[D17Interval, ...]:
    if not intervals:
        return ()
    ordered = sorted(intervals, key=lambda item: (item.start_m, item.end_m))
    merged: list[D17Interval] = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.start_m <= previous.end_m + _MERGE_TOLERANCE_M:
            merged[-1] = _interval(previous.start_m, max(previous.end_m, current.end_m))
        else:
            merged.append(current)
    return tuple(merged)


def _gaps(merged: tuple[D17Interval, ...]) -> tuple[D17Interval, ...]:
    return tuple(
        _interval(left.end_m, right.start_m)
        for left, right in zip(merged, merged[1:], strict=False)
        if right.start_m > left.end_m + _MERGE_TOLERANCE_M
    )


def _across_density(
    positions: tuple[float, ...], *, along_spacing_m: float
) -> D17AcrossTrackDensity:
    ordered = tuple(sorted(positions))
    spacings = tuple(abs(right - left) for left, right in zip(ordered, ordered[1:], strict=False))
    linear_density = tuple(None if spacing <= 0.0 else 1.0 / spacing for spacing in spacings)
    areal_density = tuple(
        None if spacing <= 0.0 or along_spacing_m <= 0.0 else 1.0 / (spacing * along_spacing_m)
        for spacing in spacings
    )
    return D17AcrossTrackDensity(
        ordered_positions_m=ordered,
        adjacent_spacing_m=spacings,
        adjacent_linear_density_per_m=linear_density,
        areal_density_per_m2=areal_density,
        min_spacing_m=min(spacings) if spacings else None,
        max_spacing_m=max(spacings) if spacings else None,
        mean_spacing_m=(sum(spacings) / len(spacings)) if spacings else None,
    )


def prepare_d17_survey_density_response(
    request: D17SurveyDensityRequest,
) -> D17SurveyDensityResponse:
    """Derive PED-D17 spacing, density and finite-footprint coverage consequences."""

    ping_period_s = 1.0 / request.ping_rate_hz
    vessel_speed_mps = request.vessel_speed_knots * KNOT_TO_MPS
    along_spacing_m = vessel_speed_mps * ping_period_s
    along_density = None if vessel_speed_mps <= 0.0 else request.ping_rate_hz / vessel_speed_mps

    d8 = prepare_d8_echosounder_response(request.echosounder)
    system = d8.mbes if request.echosounder.selected_system == "mbes" else d8.sbes

    # D8 scalar endpoint is positive Port; PED-D17 display y is positive Starboard.
    ordinary_positions = tuple(-beam.endpoint_across_track_m for beam in system.beams)
    retained_positions = (
        ordinary_positions
        if request.retained_across_track_positions_m is None
        else request.retained_across_track_positions_m
    )
    hd_positions = tuple(point[1] for point in request.high_density_bottom_points_m)
    all_positions = tuple(retained_positions) + hd_positions
    across = _across_density(all_positions, along_spacing_m=along_spacing_m)

    footprints = tuple(
        _interval(
            -beam.endpoint_across_track_m - beam.footprint.effective_across_track_width_m / 2.0,
            -beam.endpoint_across_track_m + beam.footprint.effective_across_track_width_m / 2.0,
        )
        for beam in system.beams
        if beam.footprint.effective_across_track_width_m > 0.0
    )
    merged = _merge_intervals(footprints)
    gaps = _gaps(merged)
    across_classification: Literal["continuous", "gapped", "unavailable"]
    if not merged:
        across_classification = "unavailable"
    else:
        across_classification = "gapped" if gaps else "continuous"

    along_gaps = tuple(
        max(0.0, along_spacing_m - beam.footprint.beam_limited_along_track_width_m)
        for beam in system.beams
        if beam.footprint.beam_limited_along_track_width_m > 0.0
    )
    if not along_gaps:
        along_classification: Literal["continuous", "gapped", "unavailable"] = "unavailable"
    else:
        along_classification = "gapped" if any(value > _MERGE_TOLERANCE_M for value in along_gaps) else "continuous"

    coverage = D17CoverageResult(
        classification=across_classification,
        footprint_intervals=footprints,
        merged_coverage_intervals=merged,
        internal_gap_intervals=gaps,
        total_covered_width_m=sum(item.width_m for item in merged) if merged else None,
        geometric_beam_center_swath_width_m=system.geometric_beam_center_swath_width_m,
        along_track_gap_by_beam_m=along_gaps,
        along_track_classification=along_classification,
    )

    status: Literal["available", "partial"] = (
        "available" if len(all_positions) >= 2 and across_classification != "unavailable" else "partial"
    )
    return D17SurveyDensityResponse(
        status=status,
        ping_rate_hz=request.ping_rate_hz,
        ping_period_s=ping_period_s,
        vessel_speed_knots=request.vessel_speed_knots,
        vessel_speed_mps=vessel_speed_mps,
        along_track_ping_spacing_m=along_spacing_m,
        along_track_ping_density_per_m=along_density,
        across_track=across,
        coverage=coverage,
        ordinary_sounding_count=len(ordinary_positions),
        retained_sounding_count=len(all_positions),
        high_density_added_count=len(hd_positions),
        metadata={
            "state_semantics": "Configured inputs; Derived spacing/density/coverage consequences",
            "survey_frame": "+x along-track; +y Starboard",
            "coverage_source": "finite canonical D8 footprint union",
            "retained_geometry_source": (
                "caller-supplied canonical D9 positions plus High Density points"
                if request.retained_across_track_positions_m is not None or hd_positions
                else "canonical D8 beam-centre reference positions"
            ),
            "high_density_widens_coverage": False,
            "scientific_contract": "docs/science/ped_d17_coverage_density_contract.md",
        },
    )

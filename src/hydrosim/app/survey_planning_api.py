"""Application adapter for the independent PED-D16 survey-planning slice.

This first bridge deliberately exposes only quantities already authoritative in the
current HydroSIM Core. Planned-line placement and line-to-line coverage rules remain
unavailable until the minimum PED-D16 scientific contract requested in #367 lands.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.app.echosounder_api import (
    D8EchosounderRequest,
    prepare_d8_echosounder_response,
)

KNOT_TO_MPS = 0.5144444444444445


class D16SurveyPlanningRequest(BaseModel):
    """Learner-configured reference survey area and acquisition settings."""

    model_config = ConfigDict(extra="forbid")

    area_length_m: float = Field(gt=0.0)
    area_width_m: float = Field(gt=0.0)
    line_direction_deg: float = Field(default=0.0, ge=0.0, lt=360.0)
    overlap_percent: float | None = Field(default=None, ge=0.0, lt=100.0)
    line_spacing_m: float | None = Field(default=None, gt=0.0)
    vessel_speed_knots: float = Field(default=5.0, ge=0.0)
    echosounder: D8EchosounderRequest = Field(default_factory=D8EchosounderRequest)


class D16ReferenceGeometry(BaseModel):
    model_config = ConfigDict(frozen=True)

    selected_system: Literal["sbes", "mbes"]
    reference_depth_m: float
    geometric_beam_center_swath_width_m: float
    area_length_m: float
    area_width_m: float
    line_direction_deg: float
    vessel_speed_knots: float
    vessel_speed_mps: float


class D16SurveyPlanningResponse(BaseModel):
    """Render-ready first slice with explicit unsupported planning consequences."""

    model_config = ConfigDict(frozen=True)

    status: Literal["partial"]
    reference_geometry: D16ReferenceGeometry
    configured_overlap_percent: float | None
    configured_line_spacing_m: float | None
    planned_lines: tuple[tuple[tuple[float, float], tuple[float, float]], ...]
    line_count: int | None
    total_planned_length_m: float | None
    coverage_classification: str
    unavailable_consequences: tuple[str, ...]
    metadata: dict[str, str]


def prepare_d16_survey_planning_response(
    request: D16SurveyPlanningRequest,
) -> D16SurveyPlanningResponse:
    """Expose D16 inputs and canonical D8 swath without inventing planning rules."""

    d8 = prepare_d8_echosounder_response(request.echosounder)
    selected = d8.sbes if request.echosounder.selected_system == "sbes" else d8.mbes
    vessel_speed_mps = request.vessel_speed_knots * KNOT_TO_MPS

    return D16SurveyPlanningResponse(
        status="partial",
        reference_geometry=D16ReferenceGeometry(
            selected_system=request.echosounder.selected_system,
            reference_depth_m=d8.target_depth_m,
            geometric_beam_center_swath_width_m=selected.geometric_beam_center_swath_width_m,
            area_length_m=request.area_length_m,
            area_width_m=request.area_width_m,
            line_direction_deg=request.line_direction_deg,
            vessel_speed_knots=request.vessel_speed_knots,
            vessel_speed_mps=vessel_speed_mps,
        ),
        configured_overlap_percent=request.overlap_percent,
        configured_line_spacing_m=request.line_spacing_m,
        planned_lines=(),
        line_count=None,
        total_planned_length_m=None,
        coverage_classification="unavailable",
        unavailable_consequences=(
            "planned_line_geometry",
            "line_count",
            "total_planned_length",
            "line_to_line_coverage_gap_overlap",
        ),
        metadata={
            "state_semantics": "Configured planning inputs; Derived D8 reference depth/swath and speed conversion",
            "scientific_boundary": "line placement and inter-line coverage await #367",
            "frame": "reference rectangular survey area; planning frame pending #367",
        },
    )

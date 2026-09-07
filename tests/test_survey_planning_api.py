from __future__ import annotations

import pytest

from hydrosim.app.echosounder_api import D8EchosounderRequest
from hydrosim.app.survey_planning_api import (
    D16SurveyPlanningRequest,
    prepare_d16_survey_planning_response,
)


def test_d16_exposes_canonical_d8_reference_geometry() -> None:
    result = prepare_d16_survey_planning_response(
        D16SurveyPlanningRequest(
            area_length_m=1000.0,
            area_width_m=500.0,
            vessel_speed_knots=6.0,
            echosounder=D8EchosounderRequest(
                selected_system="mbes",
                vertical_separation_m=50.0,
                mbes_beam_count=5,
                minimum_angle_deg=-45.0,
                maximum_angle_deg=45.0,
            ),
        )
    )

    assert result.status == "partial"
    assert result.reference_geometry.reference_depth_m == pytest.approx(50.0)
    assert result.reference_geometry.geometric_beam_center_swath_width_m > 0.0
    assert result.reference_geometry.vessel_speed_mps == pytest.approx(3.0866666667)


def test_d16_does_not_fabricate_planned_lines_before_science_contract() -> None:
    result = prepare_d16_survey_planning_response(
        D16SurveyPlanningRequest(
            area_length_m=1000.0,
            area_width_m=500.0,
            overlap_percent=20.0,
            vessel_speed_knots=5.0,
        )
    )

    assert result.planned_lines == ()
    assert result.line_count is None
    assert result.total_planned_length_m is None
    assert result.coverage_classification == "unavailable"
    assert "planned_line_geometry" in result.unavailable_consequences


def test_d16_validates_area_and_spacing_inputs() -> None:
    with pytest.raises(ValueError):
        D16SurveyPlanningRequest(area_length_m=0.0, area_width_m=100.0)
    with pytest.raises(ValueError):
        D16SurveyPlanningRequest(
            area_length_m=100.0,
            area_width_m=100.0,
            line_spacing_m=0.0,
        )

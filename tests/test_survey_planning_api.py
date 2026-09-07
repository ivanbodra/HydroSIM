from __future__ import annotations

import pytest

from hydrosim.app.echosounder_api import D8EchosounderRequest
from hydrosim.app.survey_planning_api import (
    D16SurveyPlanningRequest,
    prepare_d16_survey_planning_response,
)


def _mbes_request(**kwargs) -> D16SurveyPlanningRequest:
    values = {
        "area_length_m": 1000.0,
        "area_width_m": 500.0,
        "overlap_percent": 20.0,
        "vessel_speed_knots": 6.0,
        "echosounder": D8EchosounderRequest(
            selected_system="mbes",
            vertical_separation_m=50.0,
            mbes_beam_count=5,
            minimum_angle_deg=-45.0,
            maximum_angle_deg=45.0,
        ),
    }
    values.update(kwargs)
    return D16SurveyPlanningRequest(**values)


def test_d16_builds_render_ready_plan_from_canonical_d8_swath() -> None:
    result = prepare_d16_survey_planning_response(_mbes_request())

    assert result.status == "ready"
    assert result.reference_geometry.reference_depth_m == pytest.approx(50.0)
    assert result.reference_geometry.usable_swath_width_m > 0.0
    assert result.reference_geometry.vessel_speed_mps == pytest.approx(3.0866666667)
    assert result.line_count == len(result.planned_lines) == len(result.coverage_strips)
    assert result.total_planned_length_m == pytest.approx(
        sum(line.length_m for line in result.planned_lines)
    )
    assert result.actual_spacing_m is None or result.actual_spacing_m <= result.requested_spacing_m


def test_d16_overlap_mode_uses_requested_spacing_as_maximum() -> None:
    result = prepare_d16_survey_planning_response(_mbes_request())
    swath = result.reference_geometry.usable_swath_width_m

    assert result.spacing_mode == "overlap"
    assert result.requested_spacing_m == pytest.approx(0.8 * swath)
    assert result.coverage_classification in {"continuous", "overlapping", "touching"}
    assert result.gap_width_m in {None, 0.0}


def test_d16_direction_reversal_preserves_plan_metrics() -> None:
    forward = prepare_d16_survey_planning_response(_mbes_request(line_direction_deg=30.0))
    reverse = prepare_d16_survey_planning_response(_mbes_request(line_direction_deg=210.0))

    assert reverse.line_count == forward.line_count
    assert reverse.total_planned_length_m == pytest.approx(forward.total_planned_length_m)
    assert reverse.projected_cross_line_span_m == pytest.approx(forward.projected_cross_line_span_m)
    assert reverse.coverage_classification == forward.coverage_classification


def test_d16_zero_speed_keeps_geometry_but_time_is_unavailable() -> None:
    result = prepare_d16_survey_planning_response(_mbes_request(vessel_speed_knots=0.0))

    assert result.line_count > 0
    assert result.total_planned_length_m > 0.0
    assert result.idealized_on_line_time_s is None


def test_d16_explicit_spacing_can_produce_legitimate_gap() -> None:
    base = _mbes_request()
    reference = prepare_d16_survey_planning_response(base)
    swath = reference.reference_geometry.usable_swath_width_m
    result = prepare_d16_survey_planning_response(
        base.model_copy(update={"overlap_percent": None, "line_spacing_m": 1.5 * swath})
    )

    assert result.spacing_mode == "explicit_spacing"
    assert result.requested_spacing_m == pytest.approx(1.5 * swath)
    if result.actual_spacing_m is not None and result.actual_spacing_m > swath:
        assert result.coverage_classification == "gapped"
        assert result.gap_width_m == pytest.approx(result.actual_spacing_m - swath)


def test_d16_rejects_ambiguous_or_missing_spacing_mode() -> None:
    with pytest.raises(ValueError):
        D16SurveyPlanningRequest(
            area_length_m=100.0,
            area_width_m=100.0,
            overlap_percent=20.0,
            line_spacing_m=50.0,
        )
    with pytest.raises(ValueError):
        D16SurveyPlanningRequest(
            area_length_m=100.0,
            area_width_m=100.0,
            overlap_percent=None,
            line_spacing_m=None,
        )


def test_d16_rejects_sbes_zero_beam_center_swath() -> None:
    with pytest.raises(ValueError, match="positive usable swath"):
        prepare_d16_survey_planning_response(
            D16SurveyPlanningRequest(
                area_length_m=100.0,
                area_width_m=100.0,
                echosounder=D8EchosounderRequest(selected_system="sbes"),
            )
        )


def test_d16_route_is_registered_when_fastapi_is_available() -> None:
    pytest.importorskip("fastapi")
    from hydrosim.app.signal_api import create_fastapi_app

    app = create_fastapi_app()
    paths = {route.path for route in app.routes}
    assert "/api/v1/pedagogical/survey-planning" in paths

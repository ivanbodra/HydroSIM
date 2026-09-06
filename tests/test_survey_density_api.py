from __future__ import annotations

import pytest

from hydrosim.app.echosounder_api import D8EchosounderRequest
from hydrosim.app.survey_density_api import (
    D17SurveyDensityRequest,
    prepare_d17_survey_density_response,
)


def test_d17_along_track_spacing_and_density_anchor() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(
            ping_rate_hz=10.0,
            vessel_speed_knots=5.0 / 0.5144444444444445,
        )
    )

    assert result.ping_period_s == pytest.approx(0.1)
    assert result.vessel_speed_mps == pytest.approx(5.0)
    assert result.along_track_ping_spacing_m == pytest.approx(0.5)
    assert result.along_track_ping_density_per_m == pytest.approx(2.0)


def test_d17_zero_speed_has_zero_spacing_but_no_spatial_density() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(ping_rate_hz=5.0, vessel_speed_knots=0.0)
    )

    assert result.along_track_ping_spacing_m == 0.0
    assert result.along_track_ping_density_per_m is None


def test_d17_across_spacing_uses_actual_retained_positions() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(
            ping_rate_hz=10.0,
            vessel_speed_knots=4.0,
            retained_across_track_positions_m=(-10.0, -2.0, 3.0, 15.0),
        )
    )

    assert result.across_track.adjacent_spacing_m == pytest.approx((8.0, 5.0, 12.0))
    assert result.across_track.min_spacing_m == pytest.approx(5.0)
    assert result.across_track.max_spacing_m == pytest.approx(12.0)


def test_d17_high_density_adds_points_without_widening_coverage() -> None:
    base = D17SurveyDensityRequest(
        ping_rate_hz=10.0,
        vessel_speed_knots=4.0,
        echosounder=D8EchosounderRequest(mbes_beam_count=5),
    )
    ordinary = prepare_d17_survey_density_response(base)
    high_density = prepare_d17_survey_density_response(
        base.model_copy(
            update={
                "high_density_bottom_points_m": (
                    (0.0, -1.0, 100.0),
                    (0.0, 1.0, 100.0),
                )
            }
        )
    )

    assert high_density.retained_sounding_count == ordinary.retained_sounding_count + 2
    assert high_density.high_density_added_count == 2
    assert high_density.coverage.total_covered_width_m == pytest.approx(
        ordinary.coverage.total_covered_width_m
    )
    assert high_density.coverage.merged_coverage_intervals == ordinary.coverage.merged_coverage_intervals


def test_d17_coverage_union_does_not_double_count_overlap() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(
            ping_rate_hz=10.0,
            vessel_speed_knots=4.0,
            echosounder=D8EchosounderRequest(
                mbes_beam_count=3,
                minimum_angle_deg=-1.0,
                maximum_angle_deg=1.0,
                receive_across_track_beamwidth_deg=4.0,
            ),
        )
    )

    raw_width = sum(interval.width_m for interval in result.coverage.footprint_intervals)
    assert result.coverage.total_covered_width_m is not None
    assert result.coverage.total_covered_width_m <= raw_width
    assert result.coverage.classification in {"continuous", "gapped"}


def test_d17_rejects_nonpositive_ping_rate() -> None:
    with pytest.raises(ValueError):
        D17SurveyDensityRequest(ping_rate_hz=0.0, vessel_speed_knots=5.0)

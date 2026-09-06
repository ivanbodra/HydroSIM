from __future__ import annotations

import pytest

from hydrosim.app.survey_density_api import (
    D17SurveyDensityRequest,
    prepare_d17_survey_density_response,
)


def test_d17_along_track_spacing_from_speed_and_ping_rate() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(ping_rate_hz=10.0, vessel_speed_knots=6.0)
    )

    assert result.ping_period_s == pytest.approx(0.1)
    assert result.vessel_speed_mps == pytest.approx(3.0866666667)
    assert result.along_track_ping_spacing_m == pytest.approx(0.3086666667)
    assert result.status == "partial"
    assert result.unsupported_consequences == ("coverage_gap", "across_track_density")


def test_d17_zero_speed_has_zero_along_track_spacing() -> None:
    result = prepare_d17_survey_density_response(
        D17SurveyDensityRequest(ping_rate_hz=5.0, vessel_speed_knots=0.0)
    )

    assert result.along_track_ping_spacing_m == 0.0


def test_d17_rejects_nonpositive_ping_rate() -> None:
    with pytest.raises(ValueError):
        D17SurveyDensityRequest(ping_rate_hz=0.0, vessel_speed_knots=5.0)

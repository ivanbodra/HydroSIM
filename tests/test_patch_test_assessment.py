import pytest

from hydrosim.app.patch_test_assessment_api import prepare_patch_assessment_response
from hydrosim.scenarios.patch_test_assessment import PatchAssessmentConfig


@pytest.mark.parametrize("family,candidate", [
    ("roll", 1.0), ("pitch", 1.0), ("yaw", 1.0), ("latency", 100.0),
])
def test_correct_candidate_improves_calibration_and_holdout(family, candidate):
    config = PatchAssessmentConfig(
        error_family=family,
        candidate_correction=candidate,
        search_min=-200.0 if family == "latency" else -4.0,
        search_max=200.0 if family == "latency" else 4.0,
    )
    result = prepare_patch_assessment_response(config)
    assert result.assessment == "Adequate"
    assert result.calibration.after_rms_m < result.calibration.before_rms_m
    assert result.holdout.after_rms_m < result.holdout.before_rms_m
    assert result.calibration.runs == prepare_patch_assessment_response(config).calibration.runs
    assert result.estimation_error is None


def test_overcorrection_is_not_accepted():
    result = prepare_patch_assessment_response(PatchAssessmentConfig(
        error_family="roll", angular_residual_deg=1.0, candidate_correction=1.5,
    ))
    assert result.assessment == "Inadequate"
    assert result.calibration.opposite_sense


def test_non_identifying_geometry_is_never_adequate():
    result = prepare_patch_assessment_response(PatchAssessmentConfig(
        error_family="pitch", terrain_slope_deg=0.0, candidate_correction=1.0,
    ))
    assert result.assessment == "Inadequate"
    assert result.inherited_warnings


def test_truth_error_only_appears_after_submission_and_is_not_rms_or_tpu():
    base = PatchAssessmentConfig(error_family="roll", candidate_correction=0.8)
    hidden = prepare_patch_assessment_response(base).model_dump()
    revealed = prepare_patch_assessment_response(base.model_copy(update={"submitted": True})).model_dump()
    assert hidden["estimation_error"] is None
    assert hidden["estimation_error_semantics"] is None
    assert revealed["estimation_error"] == pytest.approx(-0.2)
    assert "not TPU" in revealed["estimation_error_semantics"]
    assert revealed["estimation_error"] != revealed["calibration"]["after_rms_m"]


def test_http_contract_preserves_observed_and_hides_truth_before_submission():
    from fastapi.testclient import TestClient
    from hydrosim.app.signal_api import create_fastapi_app

    response = TestClient(create_fastapi_app()).post(
        "/api/v1/pedagogical/patch-test/assessment",
        json={"error_family": "roll", "candidate_correction": 1.0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["assessment"] == "Adequate"
    assert payload["estimation_error"] is None
    assert payload["calibration"]["runs"][0]["observation_state"] == "Observed/locked"
    assert payload["holdout"]["evidence_id"] == "holdout_pair"

import pytest

from hydrosim.app.patch_test_manual_calibration_api import prepare_patch_manual_calibration_response
from hydrosim.scenarios.patch_test_manual_calibration import PatchManualCalibrationConfig


@pytest.mark.parametrize("family", ["roll", "pitch", "yaw"])
def test_angular_families_recover_and_close_without_mutating_observed(family):
    base = PatchManualCalibrationConfig(error_family=family, angular_residual_deg=1.0)
    uncorrected = prepare_patch_manual_calibration_response(base)
    corrected = prepare_patch_manual_calibration_response(base.model_copy(update={"candidate_correction": 1.0}))
    assert corrected.objective_rms_m == pytest.approx(0.0, abs=1e-10)
    assert corrected.objective_rms_m < uncorrected.objective_rms_m
    assert uncorrected.estimated_correction == pytest.approx(1.0, abs=0.11)
    assert corrected.runs == uncorrected.runs
    assert all(run.observation_state == "Observed/locked" for run in corrected.runs)


def test_latency_recovery_uses_milliseconds_and_preserves_epochs():
    base = PatchManualCalibrationConfig(
        error_family="latency", latency_residual_ms=100.0,
        search_min=-200.0, search_max=200.0, search_steps=81,
    )
    uncorrected = prepare_patch_manual_calibration_response(base)
    corrected = prepare_patch_manual_calibration_response(base.model_copy(update={"candidate_correction": 100.0}))
    assert corrected.correction_unit == "milliseconds"
    assert corrected.objective_rms_m == pytest.approx(0.0, abs=1e-10)
    assert uncorrected.estimated_correction == pytest.approx(100.0, abs=5.1)
    assert [[p.ping_time_seconds for p in r.observed] for r in corrected.runs] == [[p.ping_time_seconds for p in r.observed] for r in uncorrected.runs]


def test_sign_reversal_reverses_estimated_correction():
    positive = prepare_patch_manual_calibration_response(PatchManualCalibrationConfig(error_family="roll", angular_residual_deg=1.0))
    negative = prepare_patch_manual_calibration_response(PatchManualCalibrationConfig(error_family="roll", angular_residual_deg=-1.0))
    assert positive.estimated_correction == pytest.approx(-negative.estimated_correction, abs=0.11)


def test_degenerate_geometry_does_not_claim_estimate():
    result = prepare_patch_manual_calibration_response(PatchManualCalibrationConfig(error_family="pitch", terrain_slope_deg=0.0))
    assert result.estimate_status == "weak_or_flat"
    assert result.estimated_correction is None


def test_boundary_minimum_is_reported_without_estimate():
    result = prepare_patch_manual_calibration_response(PatchManualCalibrationConfig(
        error_family="roll", angular_residual_deg=2.0,
        search_min=-1.0, search_max=1.0, search_steps=21,
    ))
    assert result.estimate_status == "boundary_minimum"
    assert result.estimated_correction is None


def test_http_route_hides_truth_and_exposes_configured_candidate_and_derived_residual():
    from fastapi.testclient import TestClient
    from hydrosim.app.signal_api import create_fastapi_app

    response = TestClient(create_fastapi_app()).post(
        "/api/v1/pedagogical/patch-test/manual-calibration",
        json={"error_family": "roll", "candidate_correction": 0.5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["candidate_value"] == pytest.approx(0.5)
    assert payload["spatial_residual"]
    assert "truth_reference" not in payload
    assert not any("true" in key.lower() for key in payload)

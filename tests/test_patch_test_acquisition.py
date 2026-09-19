from hydrosim.app.patch_test_acquisition_api import prepare_patch_acquisition_response
from hydrosim.scenarios.patch_test_acquisition import PatchAcquisitionConfig


def test_acquisition_is_deterministic_and_observations_are_locked():
    request = PatchAcquisitionConfig(error_family="roll", deterministic_seed=7)
    first = prepare_patch_acquisition_response(request)
    second = prepare_patch_acquisition_response(request)
    assert first == second
    assert all(run.observation_state == "Observed/locked" for run in first.runs)
    assert first.fitness == "usable"
    assert "no estimate" in first.state_semantics


def test_public_response_hides_truth_reference_and_separates_derived_soundings():
    response = prepare_patch_acquisition_response(PatchAcquisitionConfig(error_family="pitch"))
    payload = response.model_dump(mode="json")
    assert "truth_reference" not in payload
    assert payload["runs"][0]["observed"]
    assert payload["runs"][0]["derived_soundings"]
    assert not any("true" in key.lower() for key in payload["runs"][0]["observed"][0])


def test_execution_evidence_drives_fitness_without_solving_patch():
    marginal = prepare_patch_acquisition_response(PatchAcquisitionConfig(
        error_family="yaw", executed_overlap_fraction=0.25
    ))
    reacquire = prepare_patch_acquisition_response(PatchAcquisitionConfig(
        error_family="latency", executed_overlap_fraction=0.0
    ))
    assert marginal.fitness == "marginal"
    assert reacquire.fitness == "reacquire"
    assert not hasattr(marginal, "estimated_correction")


def test_http_route_exposes_p3_contract():
    from fastapi.testclient import TestClient
    from hydrosim.app.signal_api import create_fastapi_app

    response = TestClient(create_fastapi_app()).post(
        "/api/v1/pedagogical/patch-test/acquisition",
        json={"error_family": "roll"},
    )
    assert response.status_code == 200
    assert response.json()["runs"][0]["observation_state"] == "Observed/locked"
    assert "truth_reference" not in response.json()

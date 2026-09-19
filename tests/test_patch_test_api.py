from __future__ import annotations

from hydrosim.app.patch_test_api import (
    PatchSignatureRequest,
    prepare_patch_signature_response,
)
from fastapi.testclient import TestClient

from hydrosim.app.signal_api import create_fastapi_app


def test_application_adapter_preserves_state_semantics() -> None:
    response = prepare_patch_signature_response(PatchSignatureRequest(error_family="roll"))

    assert response.error_family == "roll"
    assert "Truth hidden" in response.state_semantics
    assert "Configured" in response.state_semantics


def test_http_adapter_exposes_p1_signature_contract() -> None:
    app = create_fastapi_app()
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/pedagogical/patch-test/signatures"
    )
    response = route.endpoint(
        PatchSignatureRequest(error_family="latency", latency_residual_ms=80.0)
    )

    assert response.likely_classification == "latency"
    assert [run.id for run in response.runs] == ["slow", "fast"]


def test_live_http_request_returns_repeated_run_residual() -> None:
    with TestClient(create_fastapi_app()) as client:
        response = client.post(
            "/api/v1/pedagogical/patch-test/signatures",
            json={"error_family": "roll", "angular_residual_deg": 1.0},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["dataset_residual_axis"] == "y"
    assert payload["dataset_residuals"]
    assert max(abs(point["vertical_difference_m"]) for point in payload["dataset_residuals"]) > 0.0

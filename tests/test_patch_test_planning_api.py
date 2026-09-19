from __future__ import annotations

from hydrosim.app.patch_test_planning_api import (
    PatchPlanningRequest,
    prepare_patch_planning_response,
)
from hydrosim.app.signal_api import create_fastapi_app


def test_application_adapter_preserves_p2_boundary() -> None:
    response = prepare_patch_planning_response(
        PatchPlanningRequest(
            target_family="latency",
            heading_b_deg=0.0,
            speed_b_mps=7.0,
            terrain_kind="feature",
        )
    )

    assert response.adequacy == "Adequate"
    assert response.criteria_basis == "scenario_configured_pedagogical_defaults"
    assert "no Estimated correction" in response.state_semantics


def test_http_adapter_exposes_p2_planning_contract() -> None:
    app = create_fastapi_app()
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/pedagogical/patch-test/planning"
    )
    response = route.endpoint(
        PatchPlanningRequest(
            target_family="yaw",
            heading_b_deg=0.0,
            line_offset_m=50.0,
            terrain_kind="feature",
        )
    )

    assert response.target_family == "yaw"
    assert response.adequacy == "Adequate"
    assert response.metrics.common_support_interval_m is not None

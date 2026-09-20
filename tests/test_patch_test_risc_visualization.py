from fastapi.testclient import TestClient
import pytest

from hydrosim.app.patch_test_risc_api import prepare_risc_visualization_response
from hydrosim.app.signal_api import create_fastapi_app
from hydrosim.scenarios.patch_test_risc_visualization import RiscVisualizationConfig


PARAMETERS = ("delta_lx", "delta_ly", "delta_t", "delta_rho", "delta_kappa", "delta_sss")


@pytest.mark.parametrize("parameter", PARAMETERS)
def test_zero_error_closes_for_every_parameter(parameter: str) -> None:
    zero = 1.0 if parameter == "delta_rho" else 0.0
    result = prepare_risc_visualization_response(RiscVisualizationConfig(parameter=parameter, value=zero))
    assert all(point.residual_m == pytest.approx(0.0, abs=1e-12) for point in result.changed)


@pytest.mark.parametrize("parameter", PARAMETERS)
def test_every_default_parameter_has_forward_influence(parameter: str) -> None:
    result = prepare_risc_visualization_response(RiscVisualizationConfig(parameter=parameter))
    assert max(point.residual_m for point in result.changed) > 0.0
    assert len(result.baseline) == len(result.changed) == 41
    assert result.display_scale_m == 2.5


def test_lever_arm_sign_crosswalk_is_visible() -> None:
    positive = prepare_risc_visualization_response(RiscVisualizationConfig(parameter="delta_lx", value=0.4))
    negative = prepare_risc_visualization_response(RiscVisualizationConfig(parameter="delta_lx", value=-0.4))
    assert positive.changed[0].along_m - positive.baseline[0].along_m == pytest.approx(-0.4)
    assert negative.changed[0].along_m - negative.baseline[0].along_m == pytest.approx(0.4)


def test_contract_preserves_scope_provenance_and_reference_role() -> None:
    result = prepare_risc_visualization_response(RiscVisualizationConfig(parameter="delta_sss"))
    assert result.mode == "visualize_only"
    assert result.reference_role == "neutral_estimator_construct"
    assert result.provenance["baseline"] == "post-P1-P5 zero-residual configuration"
    assert any("not an estimate" in item for item in result.limitations)
    assert any("not hidden Truth" in item for item in result.limitations)


def test_runtime_endpoint_and_reset_baseline() -> None:
    client = TestClient(create_fastapi_app())
    changed = client.post("/api/v1/pedagogical/patch-test/risc-visualization", json={"parameter": "delta_t", "value": 0.1})
    reset = client.post("/api/v1/pedagogical/patch-test/risc-visualization", json={"parameter": "delta_t", "value": 0.0})
    assert changed.status_code == 200
    assert max(point["residual_m"] for point in changed.json()["changed"]) > 0.0
    assert reset.status_code == 200
    assert max(point["residual_m"] for point in reset.json()["changed"]) == pytest.approx(0.0)


def test_invalid_scale_is_rejected_by_runtime() -> None:
    response = TestClient(create_fastapi_app()).post(
        "/api/v1/pedagogical/patch-test/risc-visualization",
        json={"parameter": "delta_rho", "value": 0.0},
    )
    assert response.status_code == 422

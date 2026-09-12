import pytest

pytest.importorskip("fastapi")

from hydrosim.app.signal_api import create_fastapi_app


def test_d7_selected_directional_response_route_is_registered() -> None:
    app = create_fastapi_app()
    matching = [
        route
        for route in app.routes
        if getattr(route, "path", None)
        == "/api/v1/pedagogical/echosounders/selected-directional-response"
    ]

    assert len(matching) == 1
    assert "POST" in matching[0].methods

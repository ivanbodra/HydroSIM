import pytest

from hydrosim.app.pu_sensor_api import D13PuSensorRequest, prepare_d13_pu_sensor_response
from hydrosim.integration import ProtocolMessageAcceptance, PuInputProfile, SensorStreamProfile


def _request(*, protocol_id: str = "marine_nav") -> D13PuSensorRequest:
    return D13PuSensorRequest(
        stream=SensorStreamProfile(
            device_class="position_sensor",
            stream_id="GNSS-1",
            transport_kind="serial",
            port_id="COM1",
            baud_rate_baud=38400.0,
            protocol_id=protocol_id,
            message_id="position_fix",
            update_rate_hz=10.0,
            timestamp_source="gnss_utc",
        ),
        pu_input=PuInputProfile(
            input_id="PU-NAV-1",
            accepted_device_classes=("position_sensor",),
            accepted_transport_kinds=("serial",),
            accepted_serial_baud_rates=(38400.0,),
            accepted_protocol_messages=(
                ProtocolMessageAcceptance(
                    protocol_id="marine_nav",
                    message_ids=("position_fix",),
                ),
            ),
            max_update_rate_hz=20.0,
            accepted_timestamp_sources=("gnss_utc",),
        ),
    )


def test_d13_bridge_returns_render_ready_compatible_summary() -> None:
    response = prepare_d13_pu_sensor_response(_request())

    assert response.status == "compatible"
    assert response.reason_codes == ()
    assert response.summary.connection == "COM1 @ 38400 Bd"
    assert response.summary.nominal_update_period_s == pytest.approx(0.1)
    assert "configuration compatibility only" in response.metadata["compatibility_boundary"]


def test_d13_bridge_exposes_reason_codes_without_frontend_rules() -> None:
    response = prepare_d13_pu_sensor_response(_request(protocol_id="unsupported"))

    assert response.status == "incompatible"
    assert response.reason_codes == ("protocol_mismatch",)


def test_d13_http_route_is_registered_when_fastapi_is_available() -> None:
    pytest.importorskip("fastapi")
    from hydrosim.app.signal_api import create_fastapi_app

    app = create_fastapi_app()
    paths = {route.path for route in app.routes}

    assert "/api/v1/pedagogical/pu-sensor" in paths

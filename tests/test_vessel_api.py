import pytest

from hydrosim.app.signal_api import create_fastapi_app
from hydrosim.app.vessel_api import D11VesselRequest, prepare_d11_vessel_response
from hydrosim.geometry.models import Vector3


def test_d11_vessel_bridge_uses_canonical_vertical_geometry() -> None:
    response = prepare_d11_vessel_response(
        D11VesselRequest(
            transducer_lever_arm_m=Vector3(x=1.0, y=-0.5, z=2.4),
            gnss_lever_arm_m=Vector3(x=0.5, y=0.0, z=-3.0),
            imu_lever_arm_m=Vector3(x=0.0, y=0.2, z=-1.0),
            waterline_z_from_vrp_m=0.4,
            static_draft_m=3.0,
            water_level_m_relative_to_datum=1.2,
        )
    )

    assert response.transducer_position_m == Vector3(x=1.0, y=-0.5, z=2.4)
    assert response.gnss_position_m == Vector3(x=0.5, y=0.0, z=-3.0)
    assert response.imu_position_m == Vector3(x=0.0, y=0.2, z=-1.0)
    assert response.keel_z_from_vrp_m == pytest.approx(3.4)
    assert response.transducer_depth_below_waterline_m == pytest.approx(2.0)
    assert response.water_level_m_relative_to_datum == pytest.approx(1.2)


def test_d11_vessel_bridge_rejects_negative_static_draft() -> None:
    with pytest.raises(ValueError):
        prepare_d11_vessel_response(
            D11VesselRequest(
                transducer_lever_arm_m=Vector3(x=0.0, y=0.0, z=1.0),
                waterline_z_from_vrp_m=0.0,
                static_draft_m=-1.0,
                water_level_m_relative_to_datum=0.0,
            )
        )


def test_d11_vessel_route_is_registered() -> None:
    app = create_fastapi_app()
    assert "/api/v1/pedagogical/vessel" in {route.path for route in app.routes}

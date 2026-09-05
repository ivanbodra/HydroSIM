import pytest

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


def test_d11_reference_change_preserves_physical_sensor_positions() -> None:
    response = prepare_d11_vessel_response(
        D11VesselRequest(
            transducer_lever_arm_m=Vector3(x=4.0, y=-1.0, z=2.0),
            gnss_lever_arm_m=Vector3(x=1.0, y=0.0, z=-2.0),
            imu_lever_arm_m=Vector3(x=-0.5, y=0.5, z=-1.0),
            waterline_z_from_vrp_m=0.5,
            static_draft_m=3.0,
            water_level_m_relative_to_datum=1.2,
            vessel_length_m=30.0,
            vessel_beam_m=8.0,
            vessel_height_m=6.0,
            vrp_position_from_envelope_center_m=Vector3(x=1.0, y=0.0, z=0.0),
        )
    )

    assert response.vrp_position_m == Vector3(x=1.0, y=0.0, z=0.0)
    assert response.transducer_lever_arm_from_selected_vrp_m == Vector3(x=3.0, y=-1.0, z=2.0)
    assert response.gnss_lever_arm_from_selected_vrp_m == Vector3(x=0.0, y=0.0, z=-2.0)
    assert response.imu_lever_arm_from_selected_vrp_m == Vector3(x=-1.5, y=0.5, z=-1.0)
    assert response.transducer_position_m == Vector3(x=4.0, y=-1.0, z=2.0)
    assert response.gnss_position_m == Vector3(x=1.0, y=0.0, z=-2.0)
    assert response.imu_position_m == Vector3(x=-0.5, y=0.5, z=-1.0)


def test_d11_vertical_reference_change_preserves_waterline_and_water_level() -> None:
    baseline = prepare_d11_vessel_response(
        D11VesselRequest(
            transducer_lever_arm_m=Vector3(x=0.0, y=0.0, z=2.0),
            waterline_z_from_vrp_m=0.5,
            static_draft_m=3.0,
            water_level_m_relative_to_datum=1.2,
        )
    )
    translated = prepare_d11_vessel_response(
        D11VesselRequest(
            transducer_lever_arm_m=Vector3(x=0.0, y=0.0, z=2.0),
            waterline_z_from_vrp_m=0.5,
            static_draft_m=3.0,
            water_level_m_relative_to_datum=1.2,
            vrp_position_from_envelope_center_m=Vector3(x=0.0, y=0.0, z=0.2),
        )
    )

    assert translated.waterline_z_from_vrp_m == pytest.approx(0.3)
    assert translated.vrp_position_m.z + translated.waterline_z_from_vrp_m == pytest.approx(
        baseline.waterline_z_from_vrp_m
    )
    assert translated.transducer_position_m == baseline.transducer_position_m
    assert translated.water_level_m_relative_to_datum == baseline.water_level_m_relative_to_datum


def test_d11_envelope_dimensions_are_context_only() -> None:
    common = dict(
        transducer_lever_arm_m=Vector3(x=1.0, y=2.0, z=3.0),
        waterline_z_from_vrp_m=0.4,
        static_draft_m=2.0,
        water_level_m_relative_to_datum=0.7,
    )
    small = prepare_d11_vessel_response(
        D11VesselRequest(**common, vessel_length_m=10.0, vessel_beam_m=3.0, vessel_height_m=4.0)
    )
    large = prepare_d11_vessel_response(
        D11VesselRequest(**common, vessel_length_m=50.0, vessel_beam_m=12.0, vessel_height_m=9.0)
    )

    assert small.transducer_position_m == large.transducer_position_m
    assert small.keel_z_from_vrp_m == pytest.approx(large.keel_z_from_vrp_m)
    assert small.water_level_m_relative_to_datum == pytest.approx(large.water_level_m_relative_to_datum)


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


def test_d11_vessel_bridge_rejects_nonpositive_envelope_dimensions() -> None:
    with pytest.raises(ValueError):
        D11VesselRequest(
            transducer_lever_arm_m=Vector3(x=0.0, y=0.0, z=1.0),
            waterline_z_from_vrp_m=0.0,
            static_draft_m=1.0,
            water_level_m_relative_to_datum=0.0,
            vessel_length_m=0.0,
        )

import pytest

from hydrosim.app.motion_lesson_api import (
    D11MotionSnapshotRequest,
    prepare_d11_motion_snapshot_response,
)
from hydrosim.app.vessel_motion_api import D12VesselMotionRequest, prepare_d12_vessel_motion_response
from hydrosim.geometry import Vector3


def test_d11_render_ready_snapshot_keeps_geometry_in_python_core():
    request = D11MotionSnapshotRequest(
        roll_deg=90.0,
        pitch_deg=0.0,
        yaw_deviation_deg=0.0,
        heave_m=1.5,
        vrp_position_n_m=Vector3(x=10.0, y=20.0, z=5.0),
        lever_arm_vrp_to_transducer_b_m=Vector3(x=0.0, y=2.0, z=0.0),
    )

    response = prepare_d11_motion_snapshot_response(request)

    assert response.roll_deg == pytest.approx(90.0)
    assert response.heave_m == pytest.approx(1.5)
    assert response.vrp_position_n_m.z == pytest.approx(3.5)
    assert response.transducer_position_n_m.x == pytest.approx(10.0)
    assert response.transducer_position_n_m.y == pytest.approx(20.0)
    assert response.transducer_position_n_m.z == pytest.approx(5.5)
    assert response.body_forward_axis_n.is_close(Vector3(x=1.0, y=0.0, z=0.0), atol=1e-12)
    assert response.body_starboard_axis_n.is_close(Vector3(x=0.0, y=0.0, z=1.0), atol=1e-12)
    assert response.body_down_axis_n.is_close(Vector3(x=0.0, y=-1.0, z=0.0), atol=1e-12)
    assert response.beam_direction_n.is_close(response.body_down_axis_n, atol=1e-12)
    assert response.metadata["geometry_authority"].startswith("MotionLessonSnapshot")


def test_vessel_motion_http_contract_can_carry_optional_authoritative_snapshot():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            duration_seconds=1.0,
            sample_count=2,
            instantaneous_snapshot=D11MotionSnapshotRequest(
                pitch_deg=10.0,
                heave_m=0.5,
                lever_arm_vrp_to_transducer_b_m=Vector3(x=2.0, y=0.0, z=3.0),
            ),
        )
    )

    snapshot = response.instantaneous_snapshot
    assert snapshot is not None
    assert snapshot.pitch_deg == pytest.approx(10.0)
    assert snapshot.heave_m == pytest.approx(0.5)
    assert snapshot.transducer_position_n_m != snapshot.vrp_position_n_m
    assert response.model_dump(mode="json")["instantaneous_snapshot"]["body_forward_axis_n"]


def test_existing_vessel_motion_contract_remains_backward_compatible():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(duration_seconds=1.0, sample_count=2)
    )

    assert response.instantaneous_snapshot is None
    assert len(response.samples) == 2
    assert len(response.consequences) == 2

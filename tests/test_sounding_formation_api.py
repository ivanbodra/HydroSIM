import pytest

from hydrosim.app.sounding_formation import STAGE_ORDER, SoundingFormationStage
from hydrosim.app.sounding_formation_api import (
    D15SoundingFormationRequest,
    prepare_d15_sounding_formation_response,
)


def test_d15_serializes_canonical_stage_order_and_identity():
    response = prepare_d15_sounding_formation_response(D15SoundingFormationRequest())

    assert response.stages == tuple(stage.value for stage in STAGE_ORDER)
    assert response.active_stage == SoundingFormationStage.TRANSMIT.value
    assert response.stage_index == 0
    assert (response.ping_index, response.beam_index, response.detection_index) == (12, 7, 2)
    assert response.twtt_seconds == pytest.approx(0.04)
    assert response.reconstructed_range_m == pytest.approx(31.30)
    assert response.detected_across_track_angle_rad == pytest.approx(0.3047)


def test_d15_active_stage_changes_focus_without_changing_scientific_state():
    transmit = prepare_d15_sounding_formation_response(D15SoundingFormationRequest())
    reconstruction = prepare_d15_sounding_formation_response(
        D15SoundingFormationRequest(active_stage=SoundingFormationStage.RECONSTRUCTION)
    )

    assert reconstruction.stage_index == STAGE_ORDER.index(SoundingFormationStage.RECONSTRUCTION)
    assert reconstruction.twtt_seconds == transmit.twtt_seconds
    assert reconstruction.truth_sounding == transmit.truth_sounding
    assert reconstruction.reconstructed_sounding == transmit.reconstructed_sounding
    assert reconstruction.truth_minus_reconstructed == transmit.truth_minus_reconstructed


def test_d15_preserves_truth_observed_configured_derived_boundary():
    response = prepare_d15_sounding_formation_response(D15SoundingFormationRequest())

    assert response.semantics["truth"] == "SoundingState"
    assert response.semantics["observed"] == "BottomDetection"
    assert response.semantics["configured"] == "Pose + BeamRay"
    assert response.reconstruction_basis == "configured_geometry_reference"
    assert not hasattr(response, "observed_sounding")


def test_d15_preserves_canonical_reference_points_and_error_vector():
    response = prepare_d15_sounding_formation_response(D15SoundingFormationRequest())

    assert (response.truth_sounding.x, response.truth_sounding.y, response.truth_sounding.z) == pytest.approx(
        (0.0, 9.40, 29.85)
    )
    assert (
        response.reconstructed_sounding.x,
        response.reconstructed_sounding.y,
        response.reconstructed_sounding.z,
    ) == pytest.approx((0.0, 9.30, 29.90))
    assert (
        response.truth_minus_reconstructed.x,
        response.truth_minus_reconstructed.y,
        response.truth_minus_reconstructed.z,
    ) == pytest.approx((0.0, 0.10, -0.05))


def test_d15_configurable_twtt_angle_and_sound_speed_use_canonical_reconstruction():
    response = prepare_d15_sounding_formation_response(
        D15SoundingFormationRequest(
            twtt_seconds=0.02,
            detected_across_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
        )
    )

    assert response.scenario_id == "learner-constant-c-v1"
    assert response.twtt_seconds == pytest.approx(0.02)
    assert response.reconstructed_range_m == pytest.approx(15.0)
    assert response.detected_across_track_angle_rad == pytest.approx(0.0)
    assert (
        response.reconstructed_sounding.x,
        response.reconstructed_sounding.y,
        response.reconstructed_sounding.z,
    ) == pytest.approx((0.0, 0.0, 15.0))
    assert response.reconstruction_basis == "observation_constant_sound_speed"


def test_d15_configurable_pose_and_lever_arm_are_applied_before_reconstruction():
    response = prepare_d15_sounding_formation_response(
        D15SoundingFormationRequest(
            twtt_seconds=0.02,
            detected_across_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
            position_x_m=10.0,
            position_y_m=20.0,
            position_z_m=5.0,
            lever_arm_x_m=1.0,
            lever_arm_y_m=2.0,
            lever_arm_z_m=3.0,
        )
    )

    assert (
        response.associated_pose_position.x,
        response.associated_pose_position.y,
        response.associated_pose_position.z,
    ) == pytest.approx((11.0, 22.0, 8.0))
    assert (
        response.reconstructed_sounding.x,
        response.reconstructed_sounding.y,
        response.reconstructed_sounding.z,
    ) == pytest.approx((11.0, 22.0, 23.0))


def test_d15_configurable_timing_preserves_ping_identity_and_core_ordering():
    response = prepare_d15_sounding_formation_response(
        D15SoundingFormationRequest(
            ping_index=21,
            trigger_time_seconds=1.0,
            tx_time_seconds=1.01,
            rx_start_time_seconds=1.02,
            rx_end_time_seconds=1.10,
        )
    )

    assert response.ping_index == 21

    with pytest.raises(ValueError, match="ping timing must satisfy"):
        prepare_d15_sounding_formation_response(
            D15SoundingFormationRequest(
                trigger_time_seconds=2.0,
                tx_time_seconds=1.0,
            )
        )

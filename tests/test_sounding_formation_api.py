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

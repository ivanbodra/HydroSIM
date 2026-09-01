import pytest

from hydrosim.acquisition.bottom_detection import BottomDetection
from hydrosim.acquisition.models import AcquisitionPing
from hydrosim.app.sounding_formation import (
    STAGE_ORDER,
    SoundingFormationSnapshot,
    SoundingFormationStage,
)
from hydrosim.geometry.beams import BeamDefinition, BeamRay
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.geometry.soundings import SoundingComparison, SoundingState
from hydrosim.timing import PingTiming, SimulationTime


def _snapshot() -> SoundingFormationSnapshot:
    pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )
    timing = PingTiming(
        trigger_time=SimulationTime(seconds=0.0),
        tx_time=SimulationTime(seconds=0.0),
        rx_start_time=SimulationTime(seconds=0.01),
        rx_end_time=SimulationTime(seconds=0.10),
    )
    ping = AcquisitionPing(
        ping_index=0,
        timing=timing,
        tx_pose=pose,
        rx_start_pose=pose,
        rx_end_pose=pose,
    )
    beam = BeamRay(
        definition=BeamDefinition(index=0, across_track_angle=0.0, role="rx", array_name="rx"),
        direction_array_frame=Vector3(x=0.0, y=0.0, z=1.0),
        direction_sensor_frame=Vector3(x=0.0, y=0.0, z=1.0),
    )
    detection = BottomDetection(
        parent_beam_index=0,
        detection_method="amplitude_peak",
        arrival_offset_seconds=0.04,
        tx_delay_seconds=0.0,
        twtt_seconds=0.04,
        detected_across_track_angle_rad=0.0,
        normalized_amplitude=1.0,
    )
    truth = SoundingState(
        point=Vector3(x=0.0, y=0.0, z=30.0),
        sensor_origin=pose.position,
        beam_direction=Vector3(x=0.0, y=0.0, z=1.0),
        slant_range=30.0,
    )
    observed = SoundingState(
        point=Vector3(x=0.0, y=0.0, z=30.0),
        sensor_origin=pose.position,
        beam_direction=Vector3(x=0.0, y=0.0, z=1.0),
        slant_range=30.0,
    )
    comparison = SoundingComparison(
        beam_index=0,
        true=truth,
        configured=observed,
        error_vector=Vector3(x=0.0, y=0.0, z=0.0),
        horizontal_error=0.0,
        vertical_error=0.0,
        error_magnitude=0.0,
    )
    return SoundingFormationSnapshot(
        ping=ping,
        beam=beam,
        detection=detection,
        associated_pose=pose,
        sounding=comparison,
    )


def test_sounding_formation_stage_order_covers_canonical_chain():
    assert STAGE_ORDER == (
        SoundingFormationStage.TRANSMIT,
        SoundingFormationStage.PROPAGATION,
        SoundingFormationStage.SEABED_INTERACTION,
        SoundingFormationStage.RECEIVE,
        SoundingFormationStage.DETECTION,
        SoundingFormationStage.TWTT_RANGE,
        SoundingFormationStage.BEAM_ANGLE,
        SoundingFormationStage.POSE_ASSOCIATION,
        SoundingFormationStage.RECONSTRUCTION,
        SoundingFormationStage.TRUTH_OBSERVED,
    )


def test_sounding_formation_reuses_existing_scientific_outputs_without_recomputation():
    snapshot = _snapshot()

    assert snapshot.twtt_seconds == 0.04
    assert snapshot.detected_angle_rad == 0.0
    assert snapshot.truth_sounding is snapshot.sounding.true
    assert snapshot.observed_sounding is snapshot.sounding.configured


def test_sounding_formation_stage_navigation_preserves_scientific_state():
    snapshot = _snapshot()
    next_snapshot = snapshot.next_stage()

    assert next_snapshot.active_stage == SoundingFormationStage.PROPAGATION
    assert next_snapshot.ping == snapshot.ping
    assert next_snapshot.detection == snapshot.detection
    assert next_snapshot.sounding == snapshot.sounding
    assert next_snapshot.previous_stage().active_stage == SoundingFormationStage.TRANSMIT


def test_sounding_formation_stage_navigation_saturates_and_resets():
    snapshot = _snapshot().at_stage(SoundingFormationStage.TRUTH_OBSERVED)

    assert snapshot.next_stage().active_stage == SoundingFormationStage.TRUTH_OBSERVED
    assert snapshot.reset().active_stage == SoundingFormationStage.TRANSMIT


def test_sounding_formation_rejects_detection_from_another_beam():
    snapshot = _snapshot()
    other_detection = snapshot.detection.model_copy(update={"parent_beam_index": 1})

    with pytest.raises(ValueError, match="detection parent_beam_index"):
        SoundingFormationSnapshot(
            ping=snapshot.ping,
            beam=snapshot.beam,
            detection=other_detection,
            associated_pose=snapshot.associated_pose,
            sounding=snapshot.sounding,
        )


def test_sounding_formation_rejects_sounding_from_another_beam():
    snapshot = _snapshot()
    other_sounding = snapshot.sounding.model_copy(update={"beam_index": 1})

    with pytest.raises(ValueError, match="sounding beam_index"):
        SoundingFormationSnapshot(
            ping=snapshot.ping,
            beam=snapshot.beam,
            detection=snapshot.detection,
            associated_pose=snapshot.associated_pose,
            sounding=other_sounding,
        )

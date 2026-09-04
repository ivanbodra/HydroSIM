"""Application adapter for the PED-D15 sounding-formation learner experience.

The adapter serializes the existing :mod:`hydrosim.app.sounding_formation`
contract. It does not introduce a parallel sounding pipeline or relabel the
canonical Truth / Observed / Configured / Derived states.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

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


class D15SoundingFormationRequest(BaseModel):
    """First-slice control: select which canonical chain stage is active."""

    model_config = ConfigDict(extra="forbid")

    active_stage: SoundingFormationStage = SoundingFormationStage.TRANSMIT


class D15VectorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    x: float
    y: float
    z: float
    unit: str = "m"


class D15SoundingFormationResponse(BaseModel):
    """Render-ready serialization of one canonical sounding-formation snapshot."""

    model_config = ConfigDict(frozen=True)

    scenario_id: str
    stages: tuple[str, ...]
    active_stage: str
    stage_index: int
    ping_index: int
    beam_index: int
    detection_index: int
    detection_method: str
    twtt_seconds: float
    detected_across_track_angle_rad: float | None
    associated_pose_position: D15VectorResponse
    truth_sounding: D15VectorResponse
    reconstructed_sounding: D15VectorResponse
    truth_minus_reconstructed: D15VectorResponse
    reconstruction_basis: str
    semantics: dict[str, str]


def _vector(value: Vector3) -> D15VectorResponse:
    return D15VectorResponse(x=float(value.x), y=float(value.y), z=float(value.z))


def reference_sounding_formation_snapshot() -> SoundingFormationSnapshot:
    """Return the deterministic first-slice scenario as canonical model objects.

    These are fixture inputs for the pedagogical chain. All identities, state
    validation, stage ordering, and semantic boundaries are owned by the
    canonical HydroSIM models assembled below; no alternate equations are used.
    """

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
        ping_index=12,
        timing=timing,
        tx_pose=pose,
        rx_start_pose=pose,
        rx_end_pose=pose,
    )
    beam = BeamRay(
        definition=BeamDefinition(index=7, across_track_angle=0.0, role="rx", array_name="rx"),
        direction_array_frame=Vector3(x=0.0, y=0.30, z=0.954),
        direction_sensor_frame=Vector3(x=0.0, y=0.30, z=0.954),
    )
    detection = BottomDetection(
        parent_beam_index=7,
        detection_index=2,
        detection_method="amplitude_peak",
        arrival_offset_seconds=0.04,
        tx_delay_seconds=0.0,
        twtt_seconds=0.04,
        detected_across_track_angle_rad=0.3047,
        normalized_amplitude=1.0,
    )
    truth = SoundingState(
        point=Vector3(x=0.0, y=9.40, z=29.85),
        sensor_origin=pose.position,
        beam_direction=beam.direction_sensor_frame,
        slant_range=31.30,
    )
    reconstructed = SoundingState(
        point=Vector3(x=0.0, y=9.30, z=29.90),
        sensor_origin=pose.position,
        beam_direction=beam.direction_sensor_frame,
        slant_range=31.30,
    )
    comparison = SoundingComparison(
        beam_index=7,
        true=truth,
        configured=reconstructed,
        error_vector=Vector3(x=0.0, y=0.10, z=-0.05),
        horizontal_error=0.10,
        vertical_error=-0.05,
        error_magnitude=0.1118,
    )
    return SoundingFormationSnapshot(
        ping=ping,
        beam=beam,
        detection=detection,
        associated_pose=pose,
        sounding=comparison,
    )


def prepare_d15_sounding_formation_response(
    request: D15SoundingFormationRequest,
) -> D15SoundingFormationResponse:
    snapshot = reference_sounding_formation_snapshot().at_stage(request.active_stage)
    state = snapshot.observation_state
    association = state.association

    return D15SoundingFormationResponse(
        scenario_id="reference-chain-v1",
        stages=tuple(stage.value for stage in STAGE_ORDER),
        active_stage=snapshot.active_stage.value,
        stage_index=snapshot.stage_index,
        ping_index=association.ping_index,
        beam_index=association.beam_index,
        detection_index=association.detection_index,
        detection_method=state.observation.detection_method,
        twtt_seconds=snapshot.twtt_seconds,
        detected_across_track_angle_rad=snapshot.detected_angle_rad,
        associated_pose_position=_vector(state.configured_state.processing_pose.position),
        truth_sounding=_vector(state.truth_sounding.point),
        reconstructed_sounding=_vector(state.reconstructed_sounding.point),
        truth_minus_reconstructed=_vector(snapshot.sounding.error_vector),
        reconstruction_basis=state.reconstruction_basis,
        semantics={
            "truth": "SoundingState",
            "observed": "BottomDetection",
            "configured": "Pose + BeamRay",
            "derived": "configured-geometry reference reconstruction",
            "frame": "canonical geometry frame; vector components preserved from source models",
        },
    )

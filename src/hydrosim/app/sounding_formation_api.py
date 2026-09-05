"""Application adapter for the PED-D15 sounding-formation learner experience.

The adapter serializes the existing :mod:`hydrosim.app.sounding_formation`
contract. It does not introduce a parallel sounding pipeline or relabel the
canonical Truth / Observed / Configured / Derived states.
"""

from __future__ import annotations

from math import hypot, sqrt

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition.bottom_detection import BottomDetection
from hydrosim.acquisition.models import AcquisitionPing
from hydrosim.acquisition.sounding_observation import acoustic_observation_from_detection
from hydrosim.acquisition.sounding_reconstruction import reconstruct_constant_sound_speed_sounding
from hydrosim.app.sounding_formation import (
    STAGE_ORDER,
    SoundingFormationSnapshot,
    SoundingFormationStage,
)
from hydrosim.geometry.beams import BeamDefinition, BeamRay
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.geometry.soundings import SoundingComparison, SoundingState
from hydrosim.geometry.transforms import sensor_pose_from_vessel
from hydrosim.timing import PingTiming, SimulationTime


class D15SoundingFormationRequest(BaseModel):
    """Learner controls backed by existing canonical HydroSIM models.

    Optional controls preserve the deterministic reference fixture when omitted.
    Position is the vessel VRP in frame ``N``; the lever arm is VRP-to-sensor in
    body frame ``B``. Sound speed selects the canonical stationary reciprocal
    constant-sound-speed reconstruction. A layered SVP is deliberately not
    represented by this narrow request contract.
    """

    model_config = ConfigDict(extra="forbid")

    active_stage: SoundingFormationStage = SoundingFormationStage.TRANSMIT
    twtt_seconds: float | None = Field(default=None, gt=0.0)
    detected_across_track_angle_rad: float | None = None
    position_x_m: float | None = None
    position_y_m: float | None = None
    position_z_m: float | None = None
    roll_deg: float | None = None
    pitch_deg: float | None = None
    yaw_deg: float | None = None
    lever_arm_x_m: float | None = None
    lever_arm_y_m: float | None = None
    lever_arm_z_m: float | None = None
    sound_speed_mps: float | None = Field(default=None, gt=0.0)
    ping_index: int | None = Field(default=None, ge=0)
    trigger_time_seconds: float | None = None
    tx_time_seconds: float | None = None
    rx_start_time_seconds: float | None = None
    rx_end_time_seconds: float | None = None


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
    reconstructed_range_m: float
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


def _has_learner_configuration(request: D15SoundingFormationRequest) -> bool:
    return any(
        value is not None
        for name, value in request.model_dump().items()
        if name != "active_stage"
    )


def _configured_snapshot(request: D15SoundingFormationRequest) -> SoundingFormationSnapshot:
    """Recompute the configurable D15 slice through existing Core helpers."""

    reference = reference_sounding_formation_snapshot()
    if not _has_learner_configuration(request):
        return reference

    vessel_pose = Pose(
        position=Vector3(
            x=0.0 if request.position_x_m is None else request.position_x_m,
            y=0.0 if request.position_y_m is None else request.position_y_m,
            z=0.0 if request.position_z_m is None else request.position_z_m,
        ),
        attitude=Attitude.from_degrees(
            roll=0.0 if request.roll_deg is None else request.roll_deg,
            pitch=0.0 if request.pitch_deg is None else request.pitch_deg,
            yaw=0.0 if request.yaw_deg is None else request.yaw_deg,
        ),
        frame="N",
    )
    lever_arm = Vector3(
        x=0.0 if request.lever_arm_x_m is None else request.lever_arm_x_m,
        y=0.0 if request.lever_arm_y_m is None else request.lever_arm_y_m,
        z=0.0 if request.lever_arm_z_m is None else request.lever_arm_z_m,
    )
    sensor_pose = sensor_pose_from_vessel(
        vessel_pose,
        lever_arm,
        Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
        sensor_frame="T",
    )

    detection = reference.detection.model_copy(
        update={
            "twtt_seconds": (
                reference.detection.twtt_seconds
                if request.twtt_seconds is None
                else request.twtt_seconds
            ),
            "arrival_offset_seconds": (
                reference.detection.arrival_offset_seconds
                if request.twtt_seconds is None
                else request.twtt_seconds
            ),
            "detected_across_track_angle_rad": (
                reference.detection.detected_across_track_angle_rad
                if request.detected_across_track_angle_rad is None
                else request.detected_across_track_angle_rad
            ),
        }
    )
    observation = acoustic_observation_from_detection(detection)
    reconstructed = reconstruct_constant_sound_speed_sounding(
        observation,
        sensor_pose=sensor_pose,
        along_track_angle_rad=0.0,
        sound_speed_mps=1565.0 if request.sound_speed_mps is None else request.sound_speed_mps,
    )

    configured_state = SoundingState(
        point=reconstructed.point,
        sensor_origin=sensor_pose.position,
        beam_direction=reconstructed.direction_destination_frame,
        slant_range=float(reconstructed.range_interpretation.reciprocal_one_way_range_m),
    )
    truth = reference.sounding.true
    configured_minus_truth = Vector3(
        x=float(configured_state.point.x) - float(truth.point.x),
        y=float(configured_state.point.y) - float(truth.point.y),
        z=float(configured_state.point.z) - float(truth.point.z),
    )
    comparison = SoundingComparison(
        beam_index=reference.beam.definition.index,
        true=truth,
        configured=configured_state,
        error_vector=configured_minus_truth,
        horizontal_error=hypot(configured_minus_truth.x, configured_minus_truth.y),
        vertical_error=configured_minus_truth.z,
        error_magnitude=sqrt(
            configured_minus_truth.x * configured_minus_truth.x
            + configured_minus_truth.y * configured_minus_truth.y
            + configured_minus_truth.z * configured_minus_truth.z
        ),
    )

    timing = PingTiming(
        trigger_time=SimulationTime(
            seconds=0.0 if request.trigger_time_seconds is None else request.trigger_time_seconds
        ),
        tx_time=SimulationTime(seconds=0.0 if request.tx_time_seconds is None else request.tx_time_seconds),
        rx_start_time=SimulationTime(
            seconds=0.01 if request.rx_start_time_seconds is None else request.rx_start_time_seconds
        ),
        rx_end_time=SimulationTime(
            seconds=0.10 if request.rx_end_time_seconds is None else request.rx_end_time_seconds
        ),
    )
    ping = AcquisitionPing(
        ping_index=reference.ping.ping_index if request.ping_index is None else request.ping_index,
        timing=timing,
        tx_pose=sensor_pose,
        rx_start_pose=sensor_pose,
        rx_end_pose=sensor_pose,
    )
    beam = reference.beam.model_copy(
        update={
            "direction_array_frame": reconstructed.direction_sensor_frame,
            "direction_sensor_frame": reconstructed.direction_sensor_frame,
        }
    )
    return SoundingFormationSnapshot(
        ping=ping,
        beam=beam,
        detection=detection,
        associated_pose=sensor_pose,
        sounding=comparison,
    )


def prepare_d15_sounding_formation_response(
    request: D15SoundingFormationRequest,
) -> D15SoundingFormationResponse:
    snapshot = _configured_snapshot(request).at_stage(request.active_stage)
    state = snapshot.observation_state
    association = state.association
    truth = state.truth_sounding.point
    reconstructed = state.reconstructed_sounding.point

    return D15SoundingFormationResponse(
        scenario_id=("learner-constant-c-v1" if _has_learner_configuration(request) else "reference-chain-v1"),
        stages=tuple(stage.value for stage in STAGE_ORDER),
        active_stage=snapshot.active_stage.value,
        stage_index=snapshot.stage_index,
        ping_index=association.ping_index,
        beam_index=association.beam_index,
        detection_index=association.detection_index,
        detection_method=state.observation.detection_method,
        twtt_seconds=snapshot.twtt_seconds,
        reconstructed_range_m=float(state.reconstructed_sounding.slant_range),
        detected_across_track_angle_rad=snapshot.detected_angle_rad,
        associated_pose_position=_vector(state.configured_state.processing_pose.position),
        truth_sounding=_vector(truth),
        reconstructed_sounding=_vector(reconstructed),
        truth_minus_reconstructed=D15VectorResponse(
            x=float(truth.x) - float(reconstructed.x),
            y=float(truth.y) - float(reconstructed.y),
            z=float(truth.z) - float(reconstructed.z),
        ),
        reconstruction_basis=(
            "observation_constant_sound_speed"
            if _has_learner_configuration(request)
            else state.reconstruction_basis
        ),
        semantics={
            "truth": "SoundingState",
            "observed": "BottomDetection",
            "configured": "Pose + BeamRay",
            "derived": (
                "TWTT + detected angle + configured sensor pose + constant sound speed"
                if _has_learner_configuration(request)
                else "configured-geometry reference reconstruction"
            ),
            "frame": "canonical geometry frame; vector components preserved from source models",
        },
    )

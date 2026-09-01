"""Minimum deterministic Motion lesson adapter for the Didactic Explorer.

The adapter deliberately reuses HydroSIM's existing deterministic motion and
rigid-body geometry core. It introduces no new motion physics: UI-controlled
roll, pitch, yaw deviation, and heave are represented as constant offsets in
``HarmonicSignal`` instances and evaluated through ``VesselMotionModel``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import Vector3
from hydrosim.geometry.transforms import apply_lever_arm, transform_vector
from hydrosim.geometry.rotations import rotation_matrix_from_rpy
from hydrosim.motion.models import HarmonicSignal, StraightLineTrajectory, VesselMotionModel
from hydrosim.timing import SimulationTime


class MotionLessonControls(BaseModel):
    """Configured instantaneous motion state for the first Motion lesson slice.

    Angular values are radians internally. ``heave_m`` follows HydroSIM's
    hydrographic convention: positive heave is Up.
    """

    model_config = ConfigDict(frozen=True)

    roll_rad: FiniteFloat = 0.0
    pitch_rad: FiniteFloat = 0.0
    yaw_deviation_rad: FiniteFloat = 0.0
    heave_m: FiniteFloat = 0.0


class MotionLessonConfiguration(BaseModel):
    """Static geometry reused while varying the instantaneous motion controls."""

    model_config = ConfigDict(frozen=True)

    vrp_position_n_m: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)
    heading_rad: FiniteFloat = 0.0
    lever_arm_vrp_to_transducer_b_m: Vector3 = Vector3(x=0.0, y=0.0, z=1.0)
    beam_direction_b: Vector3 = Vector3(x=0.0, y=0.0, z=1.0)


class MotionLessonSnapshot(BaseModel):
    """Derived instantaneous geometry suitable for a Motion didactic renderer."""

    model_config = ConfigDict(frozen=True)

    controls: MotionLessonControls
    vrp_position_n_m: Vector3
    transducer_position_n_m: Vector3
    body_forward_axis_n: Vector3
    body_starboard_axis_n: Vector3
    body_down_axis_n: Vector3
    beam_direction_n: Vector3


def _constant_signal(value: float) -> HarmonicSignal:
    """Represent an instantaneous lesson control through the existing motion core."""

    return HarmonicSignal(amplitude=0.0, offset=value)


def prepare_motion_lesson_snapshot(
    controls: MotionLessonControls,
    configuration: MotionLessonConfiguration = MotionLessonConfiguration(),
) -> MotionLessonSnapshot:
    """Derive vessel, transducer, and orientation consequences of motion controls.

    The mean trajectory is stationary. Roll, pitch, yaw deviation, and heave are
    passed through ``VesselMotionModel`` as constant deterministic signals, so
    sign/frame semantics stay owned by the existing motion core. Rigid-body
    lever-arm and vector rotations are then derived with the existing geometry
    transforms.
    """

    trajectory = StraightLineTrajectory(
        start_position=configuration.vrp_position_n_m,
        speed_mps=0.0,
        heading_rad=configuration.heading_rad,
        frame="N",
    )
    motion = VesselMotionModel(
        trajectory=trajectory,
        roll=_constant_signal(float(controls.roll_rad)),
        pitch=_constant_signal(float(controls.pitch_rad)),
        yaw_deviation=_constant_signal(float(controls.yaw_deviation_rad)),
        heave=_constant_signal(float(controls.heave_m)),
    )
    pose = motion.pose_at(SimulationTime(seconds=0.0))
    rotation = rotation_matrix_from_rpy(pose.attitude)

    return MotionLessonSnapshot(
        controls=controls,
        vrp_position_n_m=pose.position,
        transducer_position_n_m=apply_lever_arm(
            pose,
            configuration.lever_arm_vrp_to_transducer_b_m,
        ),
        body_forward_axis_n=transform_vector(Vector3(x=1.0, y=0.0, z=0.0), rotation),
        body_starboard_axis_n=transform_vector(Vector3(x=0.0, y=1.0, z=0.0), rotation),
        body_down_axis_n=transform_vector(Vector3(x=0.0, y=0.0, z=1.0), rotation),
        beam_direction_n=transform_vector(configuration.beam_direction_b, rotation),
    )

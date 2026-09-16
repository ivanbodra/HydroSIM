"""HTTP-facing adapter for the instantaneous PED-D11 motion scene.

Learner-facing angles are accepted in degrees, while all rigid-body geometry stays
owned by ``prepare_motion_lesson_snapshot`` and the canonical motion/geometry Core.
"""

from __future__ import annotations

from math import radians

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.app.motion_lesson import (
    MotionLessonConfiguration,
    MotionLessonControls,
    prepare_motion_lesson_snapshot,
)
from hydrosim.geometry import Vector3


class D11MotionSnapshotRequest(BaseModel):
    """Learner-facing instantaneous motion controls plus fixed installation geometry."""

    model_config = ConfigDict(extra="forbid")

    roll_deg: FiniteFloat = 0.0
    pitch_deg: FiniteFloat = 0.0
    yaw_deviation_deg: FiniteFloat = 0.0
    heave_m: FiniteFloat = 0.0
    vrp_position_n_m: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)
    heading_deg: FiniteFloat = 0.0
    lever_arm_vrp_to_transducer_b_m: Vector3 = Vector3(x=0.0, y=0.0, z=1.0)
    beam_direction_b: Vector3 = Vector3(x=0.0, y=0.0, z=1.0)


class D11MotionSnapshotResponse(BaseModel):
    """Render-ready authoritative instantaneous rigid-body scene."""

    model_config = ConfigDict(frozen=True)

    roll_deg: float
    pitch_deg: float
    yaw_deviation_deg: float
    heave_m: float
    vrp_position_n_m: Vector3
    transducer_position_n_m: Vector3
    body_forward_axis_n: Vector3
    body_starboard_axis_n: Vector3
    body_down_axis_n: Vector3
    beam_direction_n: Vector3
    metadata: dict[str, str]


def prepare_d11_motion_snapshot_response(
    request: D11MotionSnapshotRequest,
) -> D11MotionSnapshotResponse:
    """Convert learner units, then delegate all geometry to the existing snapshot authority."""

    snapshot = prepare_motion_lesson_snapshot(
        MotionLessonControls(
            roll_rad=radians(float(request.roll_deg)),
            pitch_rad=radians(float(request.pitch_deg)),
            yaw_deviation_rad=radians(float(request.yaw_deviation_deg)),
            heave_m=request.heave_m,
        ),
        MotionLessonConfiguration(
            vrp_position_n_m=request.vrp_position_n_m,
            heading_rad=radians(float(request.heading_deg)),
            lever_arm_vrp_to_transducer_b_m=request.lever_arm_vrp_to_transducer_b_m,
            beam_direction_b=request.beam_direction_b,
        ),
    )
    return D11MotionSnapshotResponse(
        roll_deg=float(request.roll_deg),
        pitch_deg=float(request.pitch_deg),
        yaw_deviation_deg=float(request.yaw_deviation_deg),
        heave_m=float(request.heave_m),
        vrp_position_n_m=snapshot.vrp_position_n_m,
        transducer_position_n_m=snapshot.transducer_position_n_m,
        body_forward_axis_n=snapshot.body_forward_axis_n,
        body_starboard_axis_n=snapshot.body_starboard_axis_n,
        body_down_axis_n=snapshot.body_down_axis_n,
        beam_direction_n=snapshot.beam_direction_n,
        metadata={
            "navigation_frame": "N (North-East-Down)",
            "body_frame": "B (+X Forward, +Y Starboard, +Z Down)",
            "heading_convention": "degrees clockwise from North",
            "heave_convention": "positive Up",
            "state_semantics": "Configured instantaneous motion; Derived rigid-body geometry",
            "geometry_authority": "MotionLessonSnapshot / canonical motion and geometry Core",
        },
    )

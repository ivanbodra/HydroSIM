"""Narrow PED-D11 application bridge for vessel vertical references."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.app.vessel_vertical_reference import (
    VesselVerticalReferenceConfiguration,
    prepare_vessel_vertical_reference_snapshot,
)
from hydrosim.geometry.models import Attitude, Pose, Vector3


class D11VesselRequest(BaseModel):
    """Configured static geometry owned by the PED-D11 learner controls."""

    model_config = ConfigDict(extra="forbid")

    transducer_lever_arm_m: Vector3
    waterline_z_from_vrp_m: float
    static_draft_m: float
    water_level_m_relative_to_datum: float
    gnss_lever_arm_m: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)
    imu_lever_arm_m: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)
    vessel_length_m: float | None = Field(default=None, gt=0.0)
    vessel_beam_m: float | None = Field(default=None, gt=0.0)
    vessel_height_m: float | None = Field(default=None, gt=0.0)
    vrp_position_from_envelope_center_m: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)


class D11VesselResponse(BaseModel):
    """Render-ready canonical static vessel snapshot."""

    model_config = ConfigDict(frozen=True)

    vessel_length_m: float | None
    vessel_beam_m: float | None
    vessel_height_m: float | None
    vrp_position_m: Vector3
    gnss_position_m: Vector3
    imu_position_m: Vector3
    transducer_position_m: Vector3
    gnss_lever_arm_from_selected_vrp_m: Vector3
    imu_lever_arm_from_selected_vrp_m: Vector3
    transducer_lever_arm_from_selected_vrp_m: Vector3
    waterline_z_from_vrp_m: float
    static_draft_m: float
    keel_z_from_vrp_m: float
    transducer_z_from_vrp_m: float
    transducer_depth_below_waterline_m: float
    water_level_m_relative_to_datum: float
    metadata: dict[str, str]


def _subtract(left: Vector3, right: Vector3) -> Vector3:
    return Vector3(x=left.x - right.x, y=left.y - right.y, z=left.z - right.z)


def prepare_d11_vessel_response(request: D11VesselRequest) -> D11VesselResponse:
    """Serialize the canonical static vertical-reference snapshot.

    Existing lever-arm inputs describe the rigid installation relative to the
    envelope-centre default VRP. Moving the selected VRP is therefore a pure
    reference change: transformed VRP->sensor lever arms subtract the VRP
    translation so physical sensor positions in the common vessel frame remain
    invariant.
    """

    vrp_position = request.vrp_position_from_envelope_center_m
    gnss_lever_arm = _subtract(request.gnss_lever_arm_m, vrp_position)
    imu_lever_arm = _subtract(request.imu_lever_arm_m, vrp_position)
    transducer_lever_arm = _subtract(request.transducer_lever_arm_m, vrp_position)
    waterline_z_from_selected_vrp_m = request.waterline_z_from_vrp_m - vrp_position.z

    configuration = VesselVerticalReferenceConfiguration(
        lever_arm_vrp_to_gnss=gnss_lever_arm,
        lever_arm_vrp_to_imu=imu_lever_arm,
        lever_arm_vrp_to_transducer=transducer_lever_arm,
        waterline_z_from_vrp_m=waterline_z_from_selected_vrp_m,
        static_draft_m=request.static_draft_m,
        water_level_m_relative_to_datum=request.water_level_m_relative_to_datum,
    )
    vrp_pose = Pose(
        position=vrp_position,
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="B",
    )
    snapshot = prepare_vessel_vertical_reference_snapshot(vrp_pose, configuration)
    return D11VesselResponse(
        vessel_length_m=request.vessel_length_m,
        vessel_beam_m=request.vessel_beam_m,
        vessel_height_m=request.vessel_height_m,
        vrp_position_m=snapshot.vessel_vrp_pose.position,
        gnss_position_m=snapshot.gnss_position,
        imu_position_m=snapshot.imu_position,
        transducer_position_m=snapshot.transducer_position,
        gnss_lever_arm_from_selected_vrp_m=gnss_lever_arm,
        imu_lever_arm_from_selected_vrp_m=imu_lever_arm,
        transducer_lever_arm_from_selected_vrp_m=transducer_lever_arm,
        waterline_z_from_vrp_m=float(snapshot.waterline_z_from_vrp_m),
        static_draft_m=float(snapshot.static_draft_m),
        keel_z_from_vrp_m=float(snapshot.keel_z_from_vrp_m),
        transducer_z_from_vrp_m=float(snapshot.transducer_z_from_vrp_m),
        transducer_depth_below_waterline_m=float(snapshot.transducer_depth_below_waterline_m),
        water_level_m_relative_to_datum=float(snapshot.water_level_m_relative_to_datum),
        metadata={
            "frame": "B: +X Forward, +Y Starboard, +Z Down",
            "vessel_dimensions_semantics": "Configured geometric envelope only; not hydrostatic particulars",
            "vrp_semantics": "Configured VRP position relative to vessel geometric-envelope centre",
            "reference_change_semantics": "VRP translation preserves rigid sensor positions and pairwise separations",
            "state_semantics": "Configured vessel geometry; Derived sensor/reference positions",
            "water_level_semantics": "hydrographic quantity kept separate from vessel-frame Z",
        },
    )

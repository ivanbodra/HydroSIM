"""Narrow PED-D11 application bridge for vessel vertical references."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

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


class D11VesselResponse(BaseModel):
    """Render-ready canonical static vessel snapshot."""

    model_config = ConfigDict(frozen=True)

    vrp_position_m: Vector3
    gnss_position_m: Vector3
    imu_position_m: Vector3
    transducer_position_m: Vector3
    waterline_z_from_vrp_m: float
    static_draft_m: float
    keel_z_from_vrp_m: float
    transducer_z_from_vrp_m: float
    transducer_depth_below_waterline_m: float
    water_level_m_relative_to_datum: float
    metadata: dict[str, str]


def prepare_d11_vessel_response(request: D11VesselRequest) -> D11VesselResponse:
    """Serialize the existing canonical static vertical-reference snapshot."""

    configuration = VesselVerticalReferenceConfiguration(
        lever_arm_vrp_to_gnss=request.gnss_lever_arm_m,
        lever_arm_vrp_to_imu=request.imu_lever_arm_m,
        lever_arm_vrp_to_transducer=request.transducer_lever_arm_m,
        waterline_z_from_vrp_m=request.waterline_z_from_vrp_m,
        static_draft_m=request.static_draft_m,
        water_level_m_relative_to_datum=request.water_level_m_relative_to_datum,
    )
    vrp_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="B",
    )
    snapshot = prepare_vessel_vertical_reference_snapshot(vrp_pose, configuration)
    return D11VesselResponse(
        vrp_position_m=snapshot.vessel_vrp_pose.position,
        gnss_position_m=snapshot.gnss_position,
        imu_position_m=snapshot.imu_position,
        transducer_position_m=snapshot.transducer_position,
        waterline_z_from_vrp_m=float(snapshot.waterline_z_from_vrp_m),
        static_draft_m=float(snapshot.static_draft_m),
        keel_z_from_vrp_m=float(snapshot.keel_z_from_vrp_m),
        transducer_z_from_vrp_m=float(snapshot.transducer_z_from_vrp_m),
        transducer_depth_below_waterline_m=float(snapshot.transducer_depth_below_waterline_m),
        water_level_m_relative_to_datum=float(snapshot.water_level_m_relative_to_datum),
        metadata={
            "frame": "B: +X Forward, +Y Starboard, +Z Down",
            "state_semantics": "Configured vessel geometry; Derived sensor/reference positions",
            "water_level_semantics": "hydrographic quantity kept separate from vessel-frame Z",
        },
    )

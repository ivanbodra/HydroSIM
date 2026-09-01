"""Survey Simulator vessel-configuration application state.

This module composes existing HydroSIM vessel geometry and vertical-reference
structures into a reusable Survey Simulator configuration object. It deliberately
contains no rendering, persistence format, motion, squat, or new vertical science.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, NonNegativeFloat

from hydrosim.app.vessel_vertical_reference import (
    VesselVerticalReferenceConfiguration,
    VesselVerticalReferenceSnapshot,
    prepare_vessel_vertical_reference_snapshot,
)
from hydrosim.geometry.models import Attitude, Pose, Vector3


class SurveyVesselConfiguration(BaseModel):
    """Configured vessel/sensor installation shared by Survey Simulator workflows."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="Survey vessel", min_length=1)
    vrp_pose: Pose
    lever_arm_vrp_to_gnss: Vector3
    lever_arm_vrp_to_imu: Vector3
    lever_arm_vrp_to_sonar: Vector3
    waterline_z_from_vrp_m: FiniteFloat
    static_draft_m: NonNegativeFloat
    water_level_m_relative_to_datum: FiniteFloat = 0.0


class SurveyVesselConfigurationSnapshot(BaseModel):
    """Derived installation geometry ready for downstream survey modules."""

    model_config = ConfigDict(frozen=True)

    configuration: SurveyVesselConfiguration
    vertical_reference: VesselVerticalReferenceSnapshot


def default_survey_vessel_configuration() -> SurveyVesselConfiguration:
    """Return a neutral deterministic configuration suitable for reset/new scenarios."""

    return SurveyVesselConfiguration(
        vrp_pose=Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
            frame="N",
        ),
        lever_arm_vrp_to_gnss=Vector3(x=-1.8, y=0.0, z=-2.4),
        lever_arm_vrp_to_imu=Vector3(x=0.6, y=0.0, z=-0.4),
        lever_arm_vrp_to_sonar=Vector3(x=1.2, y=0.0, z=2.1),
        waterline_z_from_vrp_m=0.7,
        static_draft_m=2.2,
        water_level_m_relative_to_datum=0.0,
    )


def prepare_survey_vessel_configuration_snapshot(
    configuration: SurveyVesselConfiguration,
) -> SurveyVesselConfigurationSnapshot:
    """Derive sensor positions/vertical geometry through the existing vessel adapter."""

    vessel_configuration = VesselVerticalReferenceConfiguration(
        lever_arm_vrp_to_gnss=configuration.lever_arm_vrp_to_gnss,
        lever_arm_vrp_to_imu=configuration.lever_arm_vrp_to_imu,
        lever_arm_vrp_to_transducer=configuration.lever_arm_vrp_to_sonar,
        waterline_z_from_vrp_m=configuration.waterline_z_from_vrp_m,
        static_draft_m=configuration.static_draft_m,
        water_level_m_relative_to_datum=configuration.water_level_m_relative_to_datum,
    )
    snapshot = prepare_vessel_vertical_reference_snapshot(
        configuration.vrp_pose,
        vessel_configuration,
    )
    return SurveyVesselConfigurationSnapshot(
        configuration=configuration,
        vertical_reference=snapshot,
    )

"""Static Vessel / Sensors / Vertical References adapter for Didactic Explorer.

This module does not introduce a new vertical-reference model. It composes the
existing HydroSIM geometry core with the conventions in ``docs/conventions.md``
so a didactic view can display configured vessel geometry and derived vertical
relationships without mixing them with motion or hydrographic datum semantics.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry.models import Pose, Vector3
from hydrosim.geometry.transforms import apply_lever_arm


class VesselVerticalReferenceConfiguration(BaseModel):
    """Configured static vessel geometry for the first Vessel lesson slice.

    Lever arms are directed VRP-to-sensor vectors expressed in vessel/body frame
    ``B``. ``waterline_z_from_vrp_m`` is a body-frame vertical offset and therefore
    follows HydroSIM positive-down Z. ``water_level_m_relative_to_datum`` remains
    a separate hydrographic quantity and is deliberately not converted into a
    vessel-frame coordinate here.
    """

    model_config = ConfigDict(frozen=True)

    lever_arm_vrp_to_gnss: Vector3
    lever_arm_vrp_to_imu: Vector3
    lever_arm_vrp_to_transducer: Vector3
    waterline_z_from_vrp_m: FiniteFloat
    water_level_m_relative_to_datum: FiniteFloat


class VesselVerticalReferenceSnapshot(BaseModel):
    """Derived static snapshot suitable for a Vessel didactic renderer."""

    model_config = ConfigDict(frozen=True)

    vessel_vrp_pose: Pose
    gnss_position: Vector3
    imu_position: Vector3
    transducer_position: Vector3
    waterline_z_from_vrp_m: FiniteFloat
    transducer_z_from_vrp_m: FiniteFloat
    transducer_depth_below_waterline_m: FiniteFloat
    water_level_m_relative_to_datum: FiniteFloat


def prepare_vessel_vertical_reference_snapshot(
    vessel_vrp_pose: Pose,
    configuration: VesselVerticalReferenceConfiguration,
) -> VesselVerticalReferenceSnapshot:
    """Compose configured vessel geometry into a static didactic snapshot.

    Sensor positions are derived with the existing rigid-body lever-arm transform.
    The transducer-to-waterline relationship is derived in body-frame positive-down
    Z as ``z_transducer - z_waterline``. Hydrographic water level is passed through
    unchanged because no datum-to-VRP relationship is defined by this slice.
    """

    gnss_position = apply_lever_arm(vessel_vrp_pose, configuration.lever_arm_vrp_to_gnss)
    imu_position = apply_lever_arm(vessel_vrp_pose, configuration.lever_arm_vrp_to_imu)
    transducer_position = apply_lever_arm(
        vessel_vrp_pose,
        configuration.lever_arm_vrp_to_transducer,
    )

    transducer_z_from_vrp_m = float(configuration.lever_arm_vrp_to_transducer.z)
    transducer_depth_below_waterline_m = (
        transducer_z_from_vrp_m - float(configuration.waterline_z_from_vrp_m)
    )

    return VesselVerticalReferenceSnapshot(
        vessel_vrp_pose=vessel_vrp_pose,
        gnss_position=gnss_position,
        imu_position=imu_position,
        transducer_position=transducer_position,
        waterline_z_from_vrp_m=configuration.waterline_z_from_vrp_m,
        transducer_z_from_vrp_m=transducer_z_from_vrp_m,
        transducer_depth_below_waterline_m=transducer_depth_below_waterline_m,
        water_level_m_relative_to_datum=configuration.water_level_m_relative_to_datum,
    )

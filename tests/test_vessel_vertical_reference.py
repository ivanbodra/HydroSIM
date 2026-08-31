from hydrosim.app.vessel_vertical_reference import (
    VesselVerticalReferenceConfiguration,
    prepare_vessel_vertical_reference_snapshot,
)
from hydrosim.geometry.models import Attitude, Pose, Vector3


def _zero_attitude() -> Attitude:
    return Attitude(roll=0.0, pitch=0.0, yaw=0.0)


def test_vessel_vertical_reference_snapshot_preserves_positive_down_signs():
    vessel_pose = Pose(
        position=Vector3(x=100.0, y=200.0, z=5.0),
        attitude=_zero_attitude(),
        frame="N",
    )
    configuration = VesselVerticalReferenceConfiguration(
        lever_arm_vrp_to_gnss=Vector3(x=2.0, y=-0.5, z=-3.0),
        lever_arm_vrp_to_imu=Vector3(x=0.5, y=0.2, z=-0.4),
        lever_arm_vrp_to_transducer=Vector3(x=-1.0, y=0.0, z=2.5),
        waterline_z_from_vrp_m=1.0,
        water_level_m_relative_to_datum=2.2,
    )

    snapshot = prepare_vessel_vertical_reference_snapshot(vessel_pose, configuration)

    assert snapshot.gnss_position == Vector3(x=102.0, y=199.5, z=2.0)
    assert snapshot.imu_position == Vector3(x=100.5, y=200.2, z=4.6)
    assert snapshot.transducer_position == Vector3(x=99.0, y=200.0, z=7.5)
    assert snapshot.transducer_z_from_vrp_m == 2.5
    assert snapshot.transducer_depth_below_waterline_m == 1.5


def test_water_level_remains_separate_from_vessel_geometry():
    vessel_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=_zero_attitude(),
        frame="N",
    )
    common = dict(
        lever_arm_vrp_to_gnss=Vector3(x=0.0, y=0.0, z=-2.0),
        lever_arm_vrp_to_imu=Vector3(x=0.0, y=0.0, z=0.0),
        lever_arm_vrp_to_transducer=Vector3(x=0.0, y=0.0, z=3.0),
        waterline_z_from_vrp_m=1.2,
    )

    low = prepare_vessel_vertical_reference_snapshot(
        vessel_pose,
        VesselVerticalReferenceConfiguration(
            **common,
            water_level_m_relative_to_datum=0.5,
        ),
    )
    high = prepare_vessel_vertical_reference_snapshot(
        vessel_pose,
        VesselVerticalReferenceConfiguration(
            **common,
            water_level_m_relative_to_datum=2.0,
        ),
    )

    assert low.transducer_position == high.transducer_position
    assert low.transducer_depth_below_waterline_m == high.transducer_depth_below_waterline_m
    assert low.water_level_m_relative_to_datum == 0.5
    assert high.water_level_m_relative_to_datum == 2.0


def test_snapshot_reuses_existing_rigid_body_rotation_for_sensor_positions():
    vessel_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=90.0),
        frame="N",
    )
    configuration = VesselVerticalReferenceConfiguration(
        lever_arm_vrp_to_gnss=Vector3(x=2.0, y=0.0, z=0.0),
        lever_arm_vrp_to_imu=Vector3(x=0.0, y=1.0, z=0.0),
        lever_arm_vrp_to_transducer=Vector3(x=0.0, y=0.0, z=2.0),
        waterline_z_from_vrp_m=0.5,
        water_level_m_relative_to_datum=1.0,
    )

    snapshot = prepare_vessel_vertical_reference_snapshot(vessel_pose, configuration)

    assert snapshot.gnss_position.is_close(Vector3(x=0.0, y=2.0, z=0.0), atol=1e-12)
    assert snapshot.imu_position.is_close(Vector3(x=-1.0, y=0.0, z=0.0), atol=1e-12)
    assert snapshot.transducer_position.is_close(Vector3(x=0.0, y=0.0, z=2.0), atol=1e-12)

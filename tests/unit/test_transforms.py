from math import pi

import numpy as np
import pytest

from hydrosim.geometry import Attitude, Pose, Vector3
from hydrosim.geometry.rotations import rotation_matrix_from_rpy
from hydrosim.geometry.transforms import (
    apply_lever_arm,
    attitude_from_rotation_matrix,
    sensor_pose_from_vessel,
    transform_point,
    transform_vector,
)


def test_zero_offset_identity_case() -> None:
    vessel = Pose(
        position=Vector3(x=10.0, y=20.0, z=5.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )

    sensor = sensor_pose_from_vessel(
        vessel,
        Vector3(x=0.0, y=0.0, z=0.0),
        Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        sensor_frame="T",
    )

    assert sensor.position == vessel.position
    assert sensor.attitude == vessel.attitude
    assert sensor.frame == "N"


def test_pure_lever_arm_translation() -> None:
    vessel = Pose(
        position=Vector3(x=100.0, y=200.0, z=10.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )
    lever = Vector3(x=2.0, y=3.0, z=4.0)

    result = apply_lever_arm(vessel, lever)

    assert result == Vector3(x=102.0, y=203.0, z=14.0)


def test_yaw_rotates_forward_lever_arm_to_east() -> None:
    vessel = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=pi / 2),
        frame="N",
    )

    result = apply_lever_arm(vessel, Vector3(x=2.0, y=0.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=2.0, z=0.0), atol=1e-12)


def test_roll_rotates_starboard_lever_arm_down() -> None:
    vessel = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=pi / 2, pitch=0.0, yaw=0.0),
        frame="N",
    )

    result = apply_lever_arm(vessel, Vector3(x=0.0, y=1.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=0.0, z=1.0), atol=1e-12)


def test_pitch_rotates_forward_lever_arm_up() -> None:
    vessel = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=pi / 2, yaw=0.0),
        frame="N",
    )

    result = apply_lever_arm(vessel, Vector3(x=1.0, y=0.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=0.0, z=-1.0), atol=1e-12)


def test_transform_vector_does_not_translate() -> None:
    rotation = rotation_matrix_from_rpy(Attitude(roll=0.0, pitch=0.0, yaw=pi / 2))
    vector = transform_vector(Vector3(x=1.0, y=0.0, z=0.0), rotation)
    point = transform_point(
        Vector3(x=1.0, y=0.0, z=0.0),
        rotation,
        Vector3(x=10.0, y=20.0, z=30.0),
    )

    assert vector.is_close(Vector3(x=0.0, y=1.0, z=0.0), atol=1e-12)
    assert point.is_close(Vector3(x=10.0, y=21.0, z=30.0), atol=1e-12)


def test_sensor_alignment_is_composed_separately_from_vessel_attitude() -> None:
    vessel = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=90.0),
        frame="N",
    )
    alignment = Attitude.from_degrees(roll=10.0, pitch=0.0, yaw=0.0)

    sensor = sensor_pose_from_vessel(
        vessel,
        Vector3(x=0.0, y=0.0, z=0.0),
        alignment,
        sensor_frame="T",
    )

    expected = rotation_matrix_from_rpy(vessel.attitude) @ rotation_matrix_from_rpy(alignment)
    actual = rotation_matrix_from_rpy(sensor.attitude)

    assert np.allclose(actual, expected, atol=1e-12)
    assert sensor.attitude != vessel.attitude
    assert sensor.attitude != alignment


def test_combined_attitude_and_lever_arm_case() -> None:
    vessel = Pose(
        position=Vector3(x=100.0, y=200.0, z=10.0),
        attitude=Attitude.from_degrees(roll=5.0, pitch=-3.0, yaw=35.0),
        frame="N",
    )
    lever = Vector3(x=2.0, y=-1.0, z=1.5)

    result = apply_lever_arm(vessel, lever)
    rotation = rotation_matrix_from_rpy(vessel.attitude)
    expected_array = np.array([100.0, 200.0, 10.0]) + rotation @ np.array([2.0, -1.0, 1.5])

    assert result.is_close(
        Vector3(x=expected_array[0], y=expected_array[1], z=expected_array[2]),
        atol=1e-12,
    )


def test_attitude_matrix_round_trip() -> None:
    original = Attitude.from_degrees(roll=12.0, pitch=-7.0, yaw=123.0)
    recovered = attitude_from_rotation_matrix(rotation_matrix_from_rpy(original))

    assert recovered.is_close(original, atol=1e-12)


def test_sensor_frame_must_not_be_blank() -> None:
    vessel = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )

    with pytest.raises(ValueError):
        sensor_pose_from_vessel(
            vessel,
            Vector3(x=0.0, y=0.0, z=0.0),
            Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            sensor_frame="  ",
        )

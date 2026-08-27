from math import pi

import pytest
from pydantic import ValidationError

from hydrosim.geometry import Attitude, Pose, Vector3


def test_vector3_basic_construction() -> None:
    vector = Vector3(x=1.0, y=-2.5, z=3.25)

    assert vector.x == 1.0
    assert vector.y == -2.5
    assert vector.z == 3.25


def test_vector3_rejects_non_finite_values() -> None:
    with pytest.raises(ValidationError):
        Vector3(x=float("nan"), y=0.0, z=0.0)

    with pytest.raises(ValidationError):
        Vector3(x=0.0, y=float("inf"), z=0.0)


def test_vector3_tolerance_comparison() -> None:
    reference = Vector3(x=1.0, y=2.0, z=3.0)
    close = Vector3(x=1.0 + 1e-10, y=2.0, z=3.0)

    assert reference != close
    assert reference.is_close(close, atol=1e-9)
    assert not reference.is_close(close, atol=1e-12)


def test_attitude_from_degrees_stores_radians() -> None:
    attitude = Attitude.from_degrees(roll=90.0, pitch=-45.0, yaw=180.0)

    assert attitude.roll == pytest.approx(pi / 2)
    assert attitude.pitch == pytest.approx(-pi / 4)
    assert attitude.yaw == pytest.approx(pi)
    assert attitude.as_degrees() == pytest.approx((90.0, -45.0, 180.0))


def test_attitude_rejects_non_finite_values() -> None:
    with pytest.raises(ValidationError):
        Attitude(roll=0.0, pitch=float("nan"), yaw=0.0)


def test_attitude_tolerance_comparison() -> None:
    reference = Attitude(roll=0.1, pitch=0.2, yaw=0.3)
    close = Attitude(roll=0.1 + 1e-13, pitch=0.2, yaw=0.3)

    assert reference != close
    assert reference.is_close(close, atol=1e-12)
    assert not reference.is_close(close, atol=1e-14)


def test_pose_requires_explicit_frame() -> None:
    position = Vector3(x=1.0, y=2.0, z=3.0)
    attitude = Attitude(roll=0.0, pitch=0.0, yaw=0.0)

    with pytest.raises(ValidationError):
        Pose(position=position, attitude=attitude, frame="   ")


def test_pose_construction_and_frame_semantics() -> None:
    pose = Pose(
        position=Vector3(x=10.0, y=20.0, z=5.0),
        attitude=Attitude.from_degrees(roll=1.0, pitch=2.0, yaw=90.0),
        frame=" N ",
    )

    assert pose.frame == "N"
    assert pose.position.z == 5.0
    assert pose.attitude.yaw == pytest.approx(pi / 2)


def test_pose_tolerance_requires_same_frame() -> None:
    pose_n = Pose(
        position=Vector3(x=1.0, y=2.0, z=3.0),
        attitude=Attitude(roll=0.1, pitch=0.2, yaw=0.3),
        frame="N",
    )
    close_n = Pose(
        position=Vector3(x=1.0 + 1e-10, y=2.0, z=3.0),
        attitude=Attitude(roll=0.1, pitch=0.2, yaw=0.3),
        frame="N",
    )
    same_numbers_body = Pose(
        position=Vector3(x=1.0, y=2.0, z=3.0),
        attitude=Attitude(roll=0.1, pitch=0.2, yaw=0.3),
        frame="B",
    )

    assert pose_n.is_close(close_n)
    assert not pose_n.is_close(same_numbers_body)


def test_models_are_immutable() -> None:
    vector = Vector3(x=1.0, y=2.0, z=3.0)

    with pytest.raises(ValidationError):
        vector.x = 4.0

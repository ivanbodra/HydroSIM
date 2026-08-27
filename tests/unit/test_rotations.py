from math import pi

import numpy as np
import pytest

from hydrosim.geometry import Attitude, Vector3
from hydrosim.geometry.rotations import (
    rotate_vector,
    rotation_matrix_from_rpy,
    rotation_x,
    rotation_y,
    rotation_z,
)


def assert_rotation_matrix(matrix: np.ndarray) -> None:
    identity = np.eye(3)
    assert matrix.T @ matrix == pytest.approx(identity)
    assert np.linalg.det(matrix) == pytest.approx(1.0)
    assert np.linalg.inv(matrix) == pytest.approx(matrix.T)


def test_elementary_rotations_are_proper_orthogonal() -> None:
    for matrix in (rotation_x(0.37), rotation_y(-0.42), rotation_z(1.13)):
        assert_rotation_matrix(matrix)


def test_heading_zero_maps_forward_to_north() -> None:
    attitude = Attitude(roll=0.0, pitch=0.0, yaw=0.0)
    matrix = rotation_matrix_from_rpy(attitude)
    result = rotate_vector(matrix, Vector3(x=1.0, y=0.0, z=0.0))

    assert result.is_close(Vector3(x=1.0, y=0.0, z=0.0), atol=1e-12)


def test_positive_yaw_90_maps_forward_to_east() -> None:
    result = rotate_vector(rotation_z(pi / 2), Vector3(x=1.0, y=0.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=1.0, z=0.0), atol=1e-12)


def test_positive_roll_90_maps_starboard_to_down() -> None:
    result = rotate_vector(rotation_x(pi / 2), Vector3(x=0.0, y=1.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=0.0, z=1.0), atol=1e-12)


def test_positive_pitch_90_maps_forward_to_up() -> None:
    result = rotate_vector(rotation_y(pi / 2), Vector3(x=1.0, y=0.0, z=0.0))

    assert result.is_close(Vector3(x=0.0, y=0.0, z=-1.0), atol=1e-12)


def test_rpy_composition_matches_explicit_product() -> None:
    attitude = Attitude(roll=0.2, pitch=-0.3, yaw=0.4)

    expected = rotation_z(0.4) @ rotation_y(-0.3) @ rotation_x(0.2)
    actual = rotation_matrix_from_rpy(attitude)

    assert actual == pytest.approx(expected)
    assert_rotation_matrix(actual)


def test_rpy_application_order_is_roll_then_pitch_then_yaw() -> None:
    vector = np.array([0.3, -0.4, 0.5])
    roll = 0.25
    pitch = -0.35
    yaw = 0.6

    sequential = rotation_z(yaw) @ (rotation_y(pitch) @ (rotation_x(roll) @ vector))
    combined = rotation_matrix_from_rpy(
        Attitude(roll=roll, pitch=pitch, yaw=yaw)
    ) @ vector

    assert combined == pytest.approx(sequential)


def test_rotate_vector_rejects_invalid_matrix_shape() -> None:
    with pytest.raises(ValueError):
        rotate_vector(np.eye(2), Vector3(x=1.0, y=0.0, z=0.0))


def test_rotate_vector_rejects_non_finite_matrix() -> None:
    matrix = np.eye(3)
    matrix[0, 0] = np.nan

    with pytest.raises(ValueError):
        rotate_vector(matrix, Vector3(x=1.0, y=0.0, z=0.0))

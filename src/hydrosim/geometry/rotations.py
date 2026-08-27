"""Explicit HydroSIM rotation matrices.

HydroSIM uses column vectors and active right-hand rotations. For vessel attitude,
roll is applied first, then pitch, then yaw, so the body-to-navigation matrix is

    R_NB = R_z(yaw) @ R_y(pitch) @ R_x(roll)

No function in this module relies on a library-default Euler-angle convention.
"""

from __future__ import annotations

from math import cos, sin

import numpy as np

from .models import Attitude, Vector3


def rotation_x(angle: float) -> np.ndarray:
    """Return the active right-hand rotation matrix about +X."""

    c = cos(angle)
    s = sin(angle)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ],
        dtype=float,
    )


def rotation_y(angle: float) -> np.ndarray:
    """Return the active right-hand rotation matrix about +Y."""

    c = cos(angle)
    s = sin(angle)
    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ],
        dtype=float,
    )


def rotation_z(angle: float) -> np.ndarray:
    """Return the active right-hand rotation matrix about +Z."""

    c = cos(angle)
    s = sin(angle)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotation_matrix_from_rpy(attitude: Attitude) -> np.ndarray:
    """Return HydroSIM body-to-navigation DCM for roll, pitch, yaw.

    With column vectors, the rightmost matrix acts first. Therefore
    ``R_z @ R_y @ R_x`` corresponds to the conceptual sequence roll -> pitch -> yaw.
    """

    return rotation_z(attitude.yaw) @ rotation_y(attitude.pitch) @ rotation_x(attitude.roll)


def rotate_vector(matrix: np.ndarray, vector: Vector3) -> Vector3:
    """Apply a 3x3 active rotation matrix to a Cartesian ``Vector3``."""

    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError("rotation matrix must have shape (3, 3)")
    if not np.isfinite(matrix).all():
        raise ValueError("rotation matrix must contain only finite values")

    result = matrix @ np.array([vector.x, vector.y, vector.z], dtype=float)
    return Vector3(x=float(result[0]), y=float(result[1]), z=float(result[2]))

"""Coordinate-frame transforms and lever-arm application for HydroSIM.

The functions in this module follow the conventions frozen in
``docs/conventions.md``:

- column vectors;
- active right-hand rotations;
- body-to-navigation attitude matrix ``R_NB``;
- lever arms expressed from source to target in the source frame unless stated
  otherwise;
- sensor installation alignment kept separate from dynamic vessel attitude.

For a vessel pose expressed in navigation frame ``N`` and a lever arm from VRP to
sensor expressed in body frame ``B``::

    p_sensor^N = p_VRP^N + R_NB @ l_VRP_to_sensor^B

A sensor alignment ``R_BS`` maps sensor-frame components into the vessel/body
frame. Therefore the sensor-to-navigation orientation is::

    R_NS = R_NB @ R_BS
"""

from __future__ import annotations

from math import asin, atan2, cos

import numpy as np

from .models import Attitude, Pose, Vector3
from .rotations import rotate_vector, rotation_matrix_from_rpy


def transform_vector(vector: Vector3, rotation: np.ndarray) -> Vector3:
    """Rotate a vector between Cartesian frames without applying translation."""

    return rotate_vector(rotation, vector)


def transform_point(point: Vector3, rotation: np.ndarray, translation: Vector3) -> Vector3:
    """Rotate a point and then apply a translation in the destination frame.

    The operation is ``p_dest = translation + R_dest_source @ p_source``.
    """

    rotated = rotate_vector(rotation, point)
    return Vector3(
        x=translation.x + rotated.x,
        y=translation.y + rotated.y,
        z=translation.z + rotated.z,
    )


def apply_lever_arm(vessel_pose: Pose, lever_arm_vrp_to_sensor: Vector3) -> Vector3:
    """Return sensor-origin position in the vessel pose destination frame.

    ``lever_arm_vrp_to_sensor`` is expressed in vessel/body frame ``B``. The
    vessel pose attitude maps body-frame components into ``vessel_pose.frame``.
    """

    rotation = rotation_matrix_from_rpy(vessel_pose.attitude)
    return transform_point(lever_arm_vrp_to_sensor, rotation, vessel_pose.position)


def attitude_from_rotation_matrix(matrix: np.ndarray) -> Attitude:
    """Recover HydroSIM roll/pitch/yaw from ``R = Rz(yaw) Ry(pitch) Rx(roll)``.

    This inverse is intended for deterministic frame-composition output. The
    general Euler-angle non-uniqueness remains; near gimbal lock, yaw is set to
    zero and roll absorbs the remaining observable rotation.
    """

    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (3, 3):
        raise ValueError("rotation matrix must have shape (3, 3)")
    if not np.isfinite(matrix).all():
        raise ValueError("rotation matrix must contain only finite values")

    # For R = Rz(yaw) Ry(pitch) Rx(roll), R[2, 0] = -sin(pitch).
    sin_pitch = float(np.clip(-matrix[2, 0], -1.0, 1.0))
    pitch = asin(sin_pitch)

    if abs(cos(pitch)) > 1e-12:
        roll = atan2(matrix[2, 1], matrix[2, 2])
        yaw = atan2(matrix[1, 0], matrix[0, 0])
    else:
        # Deterministic convention at gimbal lock: yaw = 0.
        yaw = 0.0
        if sin_pitch > 0.0:  # pitch = +90 deg
            roll = atan2(matrix[0, 1], matrix[0, 2])
        else:  # pitch = -90 deg
            roll = atan2(-matrix[0, 1], -matrix[0, 2])

    return Attitude(roll=roll, pitch=pitch, yaw=yaw)


def sensor_pose_from_vessel(
    vessel_pose: Pose,
    lever_arm_vrp_to_sensor: Vector3,
    sensor_alignment: Attitude,
    *,
    sensor_frame: str,
) -> Pose:
    """Derive a fixed-mounted sensor pose from vessel pose and installation data.

    ``vessel_pose`` gives the VRP position and vessel/body attitude in its stated
    destination frame, normally ``N``. ``lever_arm_vrp_to_sensor`` is expressed
    in ``B``. ``sensor_alignment`` defines the fixed sensor-to-body orientation
    ``R_BS`` using the same explicit HydroSIM RPY convention as other rotations.

    The returned pose is expressed in the same destination frame as
    ``vessel_pose``. ``sensor_frame`` names the mounted sensor frame for semantic
    traceability, but the returned Pose ``frame`` remains the coordinate frame in
    which its position and attitude are expressed.
    """

    if not sensor_frame.strip():
        raise ValueError("sensor_frame must not be blank")

    sensor_position = apply_lever_arm(vessel_pose, lever_arm_vrp_to_sensor)

    r_parent_body = rotation_matrix_from_rpy(vessel_pose.attitude)
    r_body_sensor = rotation_matrix_from_rpy(sensor_alignment)
    r_parent_sensor = r_parent_body @ r_body_sensor
    sensor_attitude = attitude_from_rotation_matrix(r_parent_sensor)

    return Pose(
        position=sensor_position,
        attitude=sensor_attitude,
        frame=vessel_pose.frame,
    )

"""Geometry primitives for HydroSIM."""

from .arrays import ArrayElement, TransducerArray
from .models import Attitude, Pose, Vector3
from .rotations import (
    rotate_vector,
    rotation_matrix_from_rpy,
    rotation_x,
    rotation_y,
    rotation_z,
)
from .terrain import FlatTerrain, PlaneTerrain, RayIntersection
from .transforms import (
    apply_lever_arm,
    attitude_from_rotation_matrix,
    sensor_pose_from_vessel,
    transform_point,
    transform_vector,
)

__all__ = [
    "ArrayElement",
    "Attitude",
    "FlatTerrain",
    "PlaneTerrain",
    "Pose",
    "RayIntersection",
    "TransducerArray",
    "Vector3",
    "apply_lever_arm",
    "attitude_from_rotation_matrix",
    "rotate_vector",
    "rotation_matrix_from_rpy",
    "rotation_x",
    "rotation_y",
    "rotation_z",
    "sensor_pose_from_vessel",
    "transform_point",
    "transform_vector",
]

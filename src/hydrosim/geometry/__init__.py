"""Geometry primitives for HydroSIM."""

from .arrays import ArrayElement, TransducerArray
from .beams import BeamDefinition, BeamRay, IdealFan, generate_ideal_fan, generate_ideal_fan_degrees
from .models import Attitude, Pose, Vector3
from .rotations import (
    rotate_vector,
    rotation_matrix_from_rpy,
    rotation_x,
    rotation_y,
    rotation_z,
)
from .soundings import (
    SoundingComparison,
    SoundingState,
    compare_true_and_configured_sounding,
    compare_true_and_configured_state_sounding,
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
    "BeamDefinition",
    "BeamRay",
    "FlatTerrain",
    "IdealFan",
    "PlaneTerrain",
    "Pose",
    "RayIntersection",
    "SoundingComparison",
    "SoundingState",
    "TransducerArray",
    "Vector3",
    "apply_lever_arm",
    "attitude_from_rotation_matrix",
    "compare_true_and_configured_sounding",
    "compare_true_and_configured_state_sounding",
    "generate_ideal_fan",
    "generate_ideal_fan_degrees",
    "rotate_vector",
    "rotation_matrix_from_rpy",
    "rotation_x",
    "rotation_y",
    "rotation_z",
    "sensor_pose_from_vessel",
    "transform_point",
    "transform_vector",
]

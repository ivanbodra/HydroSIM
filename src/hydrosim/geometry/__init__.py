"""Geometry primitives for HydroSIM."""

from .arrays import ArrayElement, TransducerArray
from .beams import BeamDefinition, BeamRay, IdealFan, generate_ideal_fan, generate_ideal_fan_degrees
from .mills_cross import MillsCrossConfiguration, make_reference_mills_cross, principal_axis_sensor_frame
from .models import Attitude, Pose, Vector3
from .rotations import (
    rotate_vector,
    rotation_matrix_from_rpy,
    rotation_x,
    rotation_y,
    rotation_z,
)
from .sonar_systems import (
    DualHeadGeometry,
    SBESGeometry,
    SonarHeadGeometry,
    TxSectorGeometry,
    TxSectorSetGeometry,
    make_sbes_geometry,
    make_sonar_head_geometry,
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

__all__ = [name for name in globals() if not name.startswith("_")]

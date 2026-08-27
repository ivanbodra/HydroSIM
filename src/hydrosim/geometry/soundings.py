"""End-to-end geometric sounding pipeline for HydroSIM.

This module separates Truth from Configured state. The physical echo range is
obtained from the Truth ray/terrain intersection. The configured/calculated
sounding is then reconstructed from that same measured slant range using the
configured sensor alignment.

This distinction is important: processing does not normally know the true terrain
and re-intersect an erroneous configured ray with it. Re-using the measured range
allows alignment errors to produce the expected deterministic horizontal and
vertical sounding residuals, including over a flat bottom.
"""

from __future__ import annotations

from math import hypot, sqrt

from pydantic import BaseModel, ConfigDict, FiniteFloat

from .beams import BeamRay
from .models import Attitude, Pose, Vector3
from .rotations import rotate_vector, rotation_matrix_from_rpy
from .terrain import PlaneTerrain, RayIntersection
from .transforms import sensor_pose_from_vessel


class SoundingState(BaseModel):
    """One sounding solution in a Cartesian destination frame."""

    model_config = ConfigDict(frozen=True)

    point: Vector3
    sensor_origin: Vector3
    beam_direction: Vector3
    slant_range: FiniteFloat


class SoundingComparison(BaseModel):
    """Truth/configured sounding pair and deterministic residual metrics."""

    model_config = ConfigDict(frozen=True)

    beam_index: int
    true: SoundingState
    configured: SoundingState
    error_vector: Vector3
    horizontal_error: FiniteFloat
    vertical_error: FiniteFloat
    error_magnitude: FiniteFloat


def _point_along_ray(origin: Vector3, direction: Vector3, distance: float) -> Vector3:
    """Return ``origin + distance * unit(direction)``."""

    norm = sqrt(direction.x * direction.x + direction.y * direction.y + direction.z * direction.z)
    if norm <= 1e-12:
        raise ValueError("beam direction must be non-zero")
    scale = float(distance) / norm
    return Vector3(
        x=origin.x + scale * direction.x,
        y=origin.y + scale * direction.y,
        z=origin.z + scale * direction.z,
    )


def _beam_direction_in_destination(sensor_pose: Pose, beam: BeamRay) -> Vector3:
    """Rotate a sensor-frame beam direction into the pose destination frame."""

    r_destination_sensor = rotation_matrix_from_rpy(sensor_pose.attitude)
    return rotate_vector(r_destination_sensor, beam.direction_sensor_frame)


def compare_true_and_configured_sounding(
    *,
    vessel_truth_pose: Pose,
    lever_arm_vrp_to_sensor: Vector3,
    true_sensor_alignment: Attitude,
    configured_sensor_alignment: Attitude,
    beam: BeamRay,
    terrain: PlaneTerrain,
    sensor_frame: str = "T",
) -> SoundingComparison:
    """Generate one true sounding and its configured/calculated counterpart.

    Assumptions for this v0.1 geometric pipeline:

    - vessel pose and lever arm are known perfectly;
    - the only configuration discrepancy represented here is sensor alignment;
    - straight rays are used;
    - the true terrain intersection supplies the ideal measured slant range;
    - the configured solution uses that same range with the configured direction.

    Later modules can replace the ideal range with TWTT-derived range, sound-speed
    models, latency, lever-arm errors, and other Observed/Configured quantities.
    """

    true_sensor_pose = sensor_pose_from_vessel(
        vessel_truth_pose,
        lever_arm_vrp_to_sensor,
        true_sensor_alignment,
        sensor_frame=sensor_frame,
    )
    configured_sensor_pose = sensor_pose_from_vessel(
        vessel_truth_pose,
        lever_arm_vrp_to_sensor,
        configured_sensor_alignment,
        sensor_frame=sensor_frame,
    )

    true_direction = _beam_direction_in_destination(true_sensor_pose, beam)
    true_intersection: RayIntersection = terrain.intersect_ray(
        true_sensor_pose.position,
        true_direction,
    )
    if not true_intersection.valid or true_intersection.point is None or true_intersection.slant_range is None:
        raise ValueError("true beam does not intersect terrain in the forward direction")

    true_range = float(true_intersection.slant_range)
    configured_direction = _beam_direction_in_destination(configured_sensor_pose, beam)
    configured_point = _point_along_ray(
        configured_sensor_pose.position,
        configured_direction,
        true_range,
    )

    error = Vector3(
        x=configured_point.x - true_intersection.point.x,
        y=configured_point.y - true_intersection.point.y,
        z=configured_point.z - true_intersection.point.z,
    )

    return SoundingComparison(
        beam_index=beam.definition.index,
        true=SoundingState(
            point=true_intersection.point,
            sensor_origin=true_sensor_pose.position,
            beam_direction=true_direction,
            slant_range=true_range,
        ),
        configured=SoundingState(
            point=configured_point,
            sensor_origin=configured_sensor_pose.position,
            beam_direction=configured_direction,
            slant_range=true_range,
        ),
        error_vector=error,
        horizontal_error=hypot(error.x, error.y),
        vertical_error=error.z,
        error_magnitude=sqrt(error.x * error.x + error.y * error.y + error.z * error.z),
    )

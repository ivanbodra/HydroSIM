"""Truth pencil-ray-to-terrain propagation and beam-specific return epochs.

The current reference model uses an ideal geometric ``BeamRay`` as a pencil-ray
proxy. It does not yet represent the finite transmit footprint or the intersection
of separate transmit and receive beam patterns found in a Mills-Cross MBES.
"""

from __future__ import annotations

from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Attitude, BeamRay, PlaneTerrain, Pose, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy
from hydrosim.geometry.transforms import sensor_pose_from_vessel
from hydrosim.timing import PoseTimeSeries, SimulationTime


class ConstantSoundSpeedPropagation(BaseModel):
    """Straight-ray constant-sound-speed reference propagation model."""

    model_config = ConfigDict(frozen=True)

    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    convergence_tolerance_seconds: FiniteFloat = Field(default=1e-10, gt=0.0)
    max_iterations: int = Field(default=50, ge=1)


class BeamTruthReturn(BaseModel):
    """One Truth pencil-ray interaction and its array-centre receive epoch."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    tx_time: SimulationTime
    bottom_point: Vector3
    tx_sensor_origin: Vector3
    return_sensor_origin: Vector3
    outbound_range_m: FiniteFloat = Field(ge=0.0)
    inbound_range_m: FiniteFloat = Field(ge=0.0)
    twtt_seconds: FiniteFloat = Field(ge=0.0)
    return_time: SimulationTime
    return_vessel_pose: Pose
    iterations: int = Field(ge=1)
    fixed_point_residual_seconds: FiniteFloat = Field(default=0.0, ge=0.0)


def _distance(a: Vector3, b: Vector3) -> float:
    dx = float(a.x - b.x)
    dy = float(a.y - b.y)
    dz = float(a.z - b.z)
    return sqrt(dx * dx + dy * dy + dz * dz)


def _beam_direction_in_navigation(sensor_pose: Pose, beam: BeamRay) -> Vector3:
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    return rotate_vector(rotation, beam.direction_sensor_frame)


def simulate_truth_beam_return(
    *,
    tx_time: SimulationTime,
    poses: PoseTimeSeries,
    beam: BeamRay,
    terrain: PlaneTerrain,
    lever_arm_vrp_to_sensor: Vector3,
    sensor_alignment: Attitude,
    propagation: ConstantSoundSpeedPropagation,
    sensor_frame: str = "T",
) -> BeamTruthReturn:
    """Intersect one Truth pencil ray with terrain and solve its return epoch.

    The supplied ``BeamRay`` is currently interpreted only as an ideal geometric
    pencil ray. Its ``role`` metadata is not used to claim a physical TX or RX
    beam-pattern model. This is deliberate until HydroSIM represents finite TX/RX
    beam patterns and their intersection explicitly.

    Outbound propagation follows the pencil-ray direction at ``tx_time``. The first
    forward terrain intersection defines one fixed physical bottom interaction point.
    The present return model treats that point as a point scatterer that can return
    energy toward the displaced receive sensor; it is *not* a specular-mirror model
    and it does not assume that the received energy retraces the outbound path.

    In a homogeneous medium the receive epoch satisfies

        t_return = t_tx + (R_out + R_in(t_return)) / c

    and is solved by fixed-point iteration. The returned pose and sensor origin are
    evaluated at exactly ``return_time``. ``fixed_point_residual_seconds`` records
    the remaining absolute timing residual of the implicit equation.

    Refraction, finite footprint, scattering strength, receive acceptance, waveform
    physics, and bottom detection remain separate capabilities.
    """

    tx_vessel_pose = poses.pose_at(tx_time)
    tx_sensor_pose = sensor_pose_from_vessel(
        tx_vessel_pose,
        lever_arm_vrp_to_sensor,
        sensor_alignment,
        sensor_frame=sensor_frame,
    )
    tx_direction = _beam_direction_in_navigation(tx_sensor_pose, beam)
    intersection = terrain.intersect_ray(tx_sensor_pose.position, tx_direction)
    if not intersection.valid or intersection.point is None or intersection.slant_range is None:
        raise ValueError("truth pencil ray does not intersect terrain in the forward direction")

    bottom_point = intersection.point
    outbound_range = float(intersection.slant_range)
    c = float(propagation.sound_speed_mps)
    tx_seconds = float(tx_time.seconds)

    estimate = tx_seconds + 2.0 * outbound_range / c

    for iteration in range(1, propagation.max_iterations + 1):
        estimate_time = SimulationTime(seconds=estimate)
        return_pose = poses.pose_at(estimate_time)
        return_sensor_pose = sensor_pose_from_vessel(
            return_pose,
            lever_arm_vrp_to_sensor,
            sensor_alignment,
            sensor_frame=sensor_frame,
        )
        return_sensor_origin = return_sensor_pose.position
        inbound_range = _distance(bottom_point, return_sensor_origin)
        updated = tx_seconds + (outbound_range + inbound_range) / c
        residual = abs(updated - estimate)

        if residual <= float(propagation.convergence_tolerance_seconds):
            return BeamTruthReturn(
                beam_index=beam.definition.index,
                tx_time=tx_time,
                bottom_point=bottom_point,
                tx_sensor_origin=tx_sensor_pose.position,
                return_sensor_origin=return_sensor_origin,
                outbound_range_m=outbound_range,
                inbound_range_m=inbound_range,
                twtt_seconds=estimate - tx_seconds,
                return_time=estimate_time,
                return_vessel_pose=return_pose,
                iterations=iteration,
                fixed_point_residual_seconds=residual,
            )
        estimate = updated

    raise RuntimeError("beam return epoch did not converge within max_iterations")

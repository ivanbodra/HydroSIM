"""Truth beam-to-terrain propagation and beam-specific return epochs."""

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
    """One Truth beam interaction and its beam-specific receive epoch."""

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
    """Intersect one transmitted beam with terrain and solve its return epoch.

    Outbound propagation follows the beam direction at ``tx_time``. The bottom
    interaction point is therefore fixed by the transmitted Truth beam. Inbound
    propagation is modeled as the Euclidean straight-ray distance from that point
    to the moving receive sensor. The receive epoch satisfies

        t_return = t_tx + (R_out + R_in(t_return)) / c

    and is solved by fixed-point iteration. This is a geometric constant-sound-
    speed reference model; receive beam acceptance, refraction, waveform physics,
    scattering, and detection are intentionally separate future capabilities.
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
        raise ValueError("truth beam does not intersect terrain in the forward direction")

    bottom_point = intersection.point
    outbound_range = float(intersection.slant_range)
    c = float(propagation.sound_speed_mps)

    estimate = float(tx_time.seconds) + 2.0 * outbound_range / c
    return_pose: Pose | None = None
    return_sensor_origin: Vector3 | None = None
    inbound_range = outbound_range

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
        updated = float(tx_time.seconds) + (outbound_range + inbound_range) / c
        if abs(updated - estimate) <= float(propagation.convergence_tolerance_seconds):
            return BeamTruthReturn(
                beam_index=beam.definition.index,
                tx_time=tx_time,
                bottom_point=bottom_point,
                tx_sensor_origin=tx_sensor_pose.position,
                return_sensor_origin=return_sensor_origin,
                outbound_range_m=outbound_range,
                inbound_range_m=inbound_range,
                twtt_seconds=updated - float(tx_time.seconds),
                return_time=SimulationTime(seconds=updated),
                return_vessel_pose=return_pose,
                iterations=iteration,
            )
        estimate = updated

    raise RuntimeError("beam return epoch did not converge within max_iterations")

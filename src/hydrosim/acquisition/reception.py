"""Truth receive-array geometry for beam-specific acoustic returns.

This module resolves the fact that a vessel translates and rotates while sound is
in flight. A bottom return therefore reaches the receive-array centre at one pose
and reaches individual physical elements at slightly different epochs and positions.
"""

from __future__ import annotations

from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import Attitude, TransducerArray, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy
from hydrosim.geometry.transforms import sensor_pose_from_vessel
from hydrosim.timing import PoseTimeSeries, SimulationTime

from .returns import BeamTruthReturn, ConstantSoundSpeedPropagation


class ArrayElementTruthArrival(BaseModel):
    """Truth arrival of one bottom echo at one physical receive-array element."""

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    element_position_array_frame: Vector3
    arrival_position_navigation: Vector3
    inbound_range_m: FiniteFloat = Field(ge=0.0)
    arrival_time: SimulationTime
    relative_to_array_center_seconds: FiniteFloat
    iterations: int = Field(ge=1)


class ArrayTruthReception(BaseModel):
    """Truth reception geometry for one beam at a physical receive array."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    array_name: str = Field(min_length=1)
    center_return_time: SimulationTime
    direction_to_bottom_navigation: Vector3
    direction_to_bottom_array_frame: Vector3
    element_arrivals: tuple[ArrayElementTruthArrival, ...]


def _distance(a: Vector3, b: Vector3) -> float:
    dx = float(a.x - b.x)
    dy = float(a.y - b.y)
    dz = float(a.z - b.z)
    return sqrt(dx * dx + dy * dy + dz * dz)


def _unit(vector: Vector3) -> Vector3:
    length = sqrt(float(vector.x * vector.x + vector.y * vector.y + vector.z * vector.z))
    if length <= 1e-15:
        raise ValueError("direction vector must be non-zero")
    return Vector3(x=vector.x / length, y=vector.y / length, z=vector.z / length)


def _add(a: Vector3, b: Vector3) -> Vector3:
    return Vector3(x=a.x + b.x, y=a.y + b.y, z=a.z + b.z)


def _element_position_navigation(
    *,
    time: SimulationTime,
    poses: PoseTimeSeries,
    element_position_sensor_frame: Vector3,
    lever_arm_vrp_to_sensor: Vector3,
    sensor_alignment: Attitude,
    sensor_frame: str,
) -> Vector3:
    vessel_pose = poses.pose_at(time)
    sensor_pose = sensor_pose_from_vessel(
        vessel_pose,
        lever_arm_vrp_to_sensor,
        sensor_alignment,
        sensor_frame=sensor_frame,
    )
    sensor_to_navigation = rotation_matrix_from_rpy(sensor_pose.attitude)
    element_offset_navigation = rotate_vector(sensor_to_navigation, element_position_sensor_frame)
    return _add(sensor_pose.position, element_offset_navigation)


def simulate_truth_array_reception(
    *,
    beam_return: BeamTruthReturn,
    poses: PoseTimeSeries,
    receive_array: TransducerArray,
    lever_arm_vrp_to_sensor: Vector3,
    sensor_alignment: Attitude,
    propagation: ConstantSoundSpeedPropagation,
    sensor_frame: str = "T",
) -> ArrayTruthReception:
    """Resolve one beam return at the moving receive-array centre and elements.

    The physical bottom interaction point and outbound path are inherited from the
    already-computed :class:`BeamTruthReturn`. For each array element, HydroSIM
    solves the implicit moving-receiver equation

        t_i = t_tx + (R_out + |x_bottom - x_i(t_i)|) / c

    independently. The resulting inter-element arrival-time differences are the
    geometric precursor to receive beamforming delays/phases; no beamforming weights
    or phase processing are applied here.

    ``direction_to_bottom_array_frame`` points from the receive-array centre toward
    the acoustic source point on the bottom. It is deliberately named this way to
    avoid confusing source direction with the opposite wave-propagation direction.
    """

    if receive_array.role not in {"rx", "txrx"}:
        raise ValueError("receive_array must have role 'rx' or 'txrx'")

    center_pose = poses.pose_at(beam_return.return_time)
    center_sensor_pose = sensor_pose_from_vessel(
        center_pose,
        lever_arm_vrp_to_sensor,
        sensor_alignment,
        sensor_frame=sensor_frame,
    )
    direction_navigation = _unit(
        Vector3(
            x=beam_return.bottom_point.x - center_sensor_pose.position.x,
            y=beam_return.bottom_point.y - center_sensor_pose.position.y,
            z=beam_return.bottom_point.z - center_sensor_pose.position.z,
        )
    )
    navigation_to_sensor = rotation_matrix_from_rpy(center_sensor_pose.attitude).T
    direction_sensor = rotate_vector(navigation_to_sensor, direction_navigation)
    sensor_to_array = rotation_matrix_from_rpy(receive_array.orientation).T
    direction_array = rotate_vector(sensor_to_array, direction_sensor)

    c = float(propagation.sound_speed_mps)
    outbound = float(beam_return.outbound_range_m)
    tx_seconds = float(beam_return.tx_time.seconds)
    center_seconds = float(beam_return.return_time.seconds)
    element_sensor_positions = receive_array.element_positions_sensor_frame()

    arrivals: list[ArrayElementTruthArrival] = []
    for element, element_sensor_position in zip(
        receive_array.elements(), element_sensor_positions, strict=True
    ):
        estimate = center_seconds
        for iteration in range(1, propagation.max_iterations + 1):
            estimate_time = SimulationTime(seconds=estimate)
            element_position_navigation = _element_position_navigation(
                time=estimate_time,
                poses=poses,
                element_position_sensor_frame=element_sensor_position,
                lever_arm_vrp_to_sensor=lever_arm_vrp_to_sensor,
                sensor_alignment=sensor_alignment,
                sensor_frame=sensor_frame,
            )
            inbound = _distance(beam_return.bottom_point, element_position_navigation)
            updated = tx_seconds + (outbound + inbound) / c
            if abs(updated - estimate) <= float(propagation.convergence_tolerance_seconds):
                arrivals.append(
                    ArrayElementTruthArrival(
                        index_x=element.index_x,
                        index_y=element.index_y,
                        element_position_array_frame=element.position,
                        arrival_position_navigation=element_position_navigation,
                        inbound_range_m=inbound,
                        arrival_time=SimulationTime(seconds=updated),
                        relative_to_array_center_seconds=updated - center_seconds,
                        iterations=iteration,
                    )
                )
                break
            estimate = updated
        else:
            raise RuntimeError(
                "array-element return epoch did not converge within max_iterations"
            )

    return ArrayTruthReception(
        beam_index=beam_return.beam_index,
        array_name=receive_array.name,
        center_return_time=beam_return.return_time,
        direction_to_bottom_navigation=direction_navigation,
        direction_to_bottom_array_frame=direction_array,
        element_arrivals=tuple(arrivals),
    )

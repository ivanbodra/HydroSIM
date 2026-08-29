from math import isclose, radians

from hydrosim.acquisition import (
    ConstantSoundSpeedPropagation,
    simulate_truth_array_reception,
    simulate_truth_beam_return,
)
from hydrosim.geometry import (
    Attitude,
    BeamDefinition,
    BeamRay,
    FlatTerrain,
    TransducerArray,
    Vector3,
)
from hydrosim.motion import (
    HarmonicSignal,
    MotionSamplingConfig,
    StraightLineTrajectory,
    VesselMotionModel,
    generate_pose_time_series,
)
from hydrosim.timing import SimulationTime, TimeInterval


def _beam(angle_deg: float) -> BeamRay:
    from math import cos, sin

    angle = radians(angle_deg)
    direction = Vector3(x=0.0, y=-sin(angle), z=cos(angle))
    return BeamRay(
        definition=BeamDefinition(
            index=0,
            across_track_angle=angle,
            role="tx",
            array_name="tx",
        ),
        direction_array_frame=direction,
        direction_sensor_frame=direction,
    )


def _receive_array() -> TransducerArray:
    return TransducerArray(
        name="rx",
        role="rx",
        n_x=1,
        n_y=3,
        d_x=0.0,
        d_y=0.5,
        element_longitudinal_size=0.1,
        element_transverse_size=0.1,
    )


def _poses(*, speed_mps: float = 0.0, roll: HarmonicSignal | None = None):
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=0.0),
            speed_mps=speed_mps,
            heading_rad=0.0,
        ),
        roll=roll or HarmonicSignal(),
    )
    return generate_pose_time_series(
        motion,
        MotionSamplingConfig(
            interval=TimeInterval(
                start=SimulationTime(seconds=0.0),
                end=SimulationTime(seconds=1.0),
            ),
            sample_period_seconds=0.0005,
        ),
    )


def _return(poses, beam):
    propagation = ConstantSoundSpeedPropagation(sound_speed_mps=1500.0)
    result = simulate_truth_beam_return(
        tx_time=SimulationTime(seconds=0.1),
        poses=poses,
        beam=beam,
        terrain=FlatTerrain(depth=75.0),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=propagation,
    )
    return result, propagation


def test_center_element_matches_array_center_return_for_stationary_nadir():
    poses = _poses()
    beam_return, propagation = _return(poses, _beam(0.0))
    reception = simulate_truth_array_reception(
        beam_return=beam_return,
        poses=poses,
        receive_array=_receive_array(),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=propagation,
    )

    center = reception.element_arrivals[1]
    assert isclose(center.element_position_array_frame.y, 0.0, abs_tol=1e-15)
    assert isclose(center.arrival_time.seconds, beam_return.return_time.seconds, abs_tol=1e-12)
    assert isclose(center.relative_to_array_center_seconds, 0.0, abs_tol=1e-12)
    assert isclose(reception.direction_to_bottom_array_frame.x, 0.0, abs_tol=1e-12)
    assert isclose(reception.direction_to_bottom_array_frame.y, 0.0, abs_tol=1e-12)
    assert isclose(reception.direction_to_bottom_array_frame.z, 1.0, abs_tol=1e-12)


def test_off_nadir_echo_reaches_port_element_before_starboard_element():
    poses = _poses()
    beam_return, propagation = _return(poses, _beam(30.0))
    reception = simulate_truth_array_reception(
        beam_return=beam_return,
        poses=poses,
        receive_array=_receive_array(),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=propagation,
    )

    port, center, starboard = reception.element_arrivals
    assert port.element_position_array_frame.y < center.element_position_array_frame.y
    assert center.element_position_array_frame.y < starboard.element_position_array_frame.y
    assert port.arrival_time.seconds < center.arrival_time.seconds < starboard.arrival_time.seconds
    assert reception.direction_to_bottom_array_frame.y < 0.0


def test_receive_attitude_changes_apparent_arrival_direction():
    roll = HarmonicSignal(amplitude=0.2, period_seconds=0.4)
    poses = _poses(roll=roll)
    transmitted = _beam(0.0)
    beam_return, propagation = _return(poses, transmitted)
    reception = simulate_truth_array_reception(
        beam_return=beam_return,
        poses=poses,
        receive_array=_receive_array(),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=propagation,
    )

    # The nadir beam left at the Tx attitude, but the array has rotated by reception.
    assert not isclose(reception.direction_to_bottom_array_frame.y, 0.0, abs_tol=1e-6)
    assert reception.element_arrivals[0].arrival_time.seconds != reception.element_arrivals[-1].arrival_time.seconds

from math import isclose, radians

from hydrosim.acquisition import ConstantSoundSpeedPropagation, simulate_truth_beam_return
from hydrosim.geometry import Attitude, BeamDefinition, BeamRay, FlatTerrain, Vector3
from hydrosim.motion import MotionSamplingConfig, StraightLineTrajectory, VesselMotionModel, generate_pose_time_series
from hydrosim.timing import SimulationTime, TimeInterval


def _beam(index: int, angle_deg: float) -> BeamRay:
    from math import cos, sin

    angle = radians(angle_deg)
    return BeamRay(
        definition=BeamDefinition(
            index=index,
            across_track_angle=angle,
            role="rx",
            array_name="test_array",
        ),
        direction_array_frame=Vector3(x=0.0, y=-sin(angle), z=cos(angle)),
        direction_sensor_frame=Vector3(x=0.0, y=-sin(angle), z=cos(angle)),
    )


def _poses(speed_mps: float = 0.0):
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=0.0),
            speed_mps=speed_mps,
            heading_rad=0.0,
        )
    )
    return generate_pose_time_series(
        motion,
        MotionSamplingConfig(
            interval=TimeInterval(
                start=SimulationTime(seconds=0.0),
                end=SimulationTime(seconds=2.0),
            ),
            sample_period_seconds=0.001,
        ),
    )


def test_stationary_nadir_twtt_is_two_way_range_over_sound_speed():
    result = simulate_truth_beam_return(
        tx_time=SimulationTime(seconds=0.1),
        poses=_poses(),
        beam=_beam(0, 0.0),
        terrain=FlatTerrain(depth=75.0),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=ConstantSoundSpeedPropagation(sound_speed_mps=1500.0),
    )

    assert isclose(result.outbound_range_m, 75.0, abs_tol=1e-12)
    assert isclose(result.inbound_range_m, 75.0, abs_tol=1e-12)
    assert isclose(result.twtt_seconds, 0.1, abs_tol=1e-12)
    assert isclose(result.return_time.seconds, 0.2, abs_tol=1e-12)


def test_off_nadir_beam_has_later_return_epoch_than_nadir():
    kwargs = dict(
        tx_time=SimulationTime(seconds=0.1),
        poses=_poses(),
        terrain=FlatTerrain(depth=75.0),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=ConstantSoundSpeedPropagation(sound_speed_mps=1500.0),
    )
    nadir = simulate_truth_beam_return(beam=_beam(0, 0.0), **kwargs)
    outer = simulate_truth_beam_return(beam=_beam(1, 60.0), **kwargs)

    assert outer.outbound_range_m > nadir.outbound_range_m
    assert outer.twtt_seconds > nadir.twtt_seconds
    assert outer.return_time.seconds > nadir.return_time.seconds


def test_moving_receiver_changes_inbound_range_and_return_pose():
    result = simulate_truth_beam_return(
        tx_time=SimulationTime(seconds=0.1),
        poses=_poses(speed_mps=10.0),
        beam=_beam(0, 0.0),
        terrain=FlatTerrain(depth=75.0),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        propagation=ConstantSoundSpeedPropagation(sound_speed_mps=1500.0),
    )

    assert result.return_vessel_pose.position.x > result.tx_sensor_origin.x
    assert result.inbound_range_m > result.outbound_range_m
    assert result.twtt_seconds > 0.1
    assert result.iterations >= 1

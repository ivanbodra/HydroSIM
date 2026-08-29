from math import isclose, radians

from hydrosim.acquisition import (
    ConstantSoundSpeedPropagation,
    SoundSpeedSensorAtTransducer,
    evaluate_receive_steering,
    ideal_receive_steering,
    ideal_receive_steering_from_sound_speed_measurement,
    measure_sound_speed_at_transducer,
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
    MotionSamplingConfig,
    StraightLineTrajectory,
    VesselMotionModel,
    generate_pose_time_series,
)
from hydrosim.timing import SimulationTime, TimeInterval


def _beam(index: int, angle_deg: float) -> BeamRay:
    from math import cos, sin

    angle = radians(angle_deg)
    return BeamRay(
        definition=BeamDefinition(
            index=index,
            across_track_angle=angle,
            role="rx",
            array_name="rx_array",
        ),
        direction_array_frame=Vector3(x=0.0, y=-sin(angle), z=cos(angle)),
        direction_sensor_frame=Vector3(x=0.0, y=-sin(angle), z=cos(angle)),
    )


def _poses():
    motion = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_position=Vector3(x=0.0, y=0.0, z=0.0),
            speed_mps=0.0,
            heading_rad=0.0,
        )
    )
    return generate_pose_time_series(
        motion,
        MotionSamplingConfig(
            interval=TimeInterval(
                start=SimulationTime(seconds=0.0),
                end=SimulationTime(seconds=1.0),
            ),
            sample_period_seconds=0.001,
        ),
    )


def _array() -> TransducerArray:
    return TransducerArray(
        name="rx_array",
        role="rx",
        n_x=1,
        n_y=5,
        d_x=0.0,
        d_y=0.1,
        element_longitudinal_size=0.05,
        element_transverse_size=0.05,
    )


def test_positive_port_steering_predicts_port_elements_arrive_earlier():
    hypothesis = ideal_receive_steering(
        receive_array=_array(),
        across_track_angle_rad=radians(30.0),
        sound_speed_mps=1500.0,
    )

    offsets = [float(item.predicted_arrival_offset_seconds) for item in hypothesis.element_delays]
    assert offsets[0] < 0.0
    assert isclose(offsets[2], 0.0, abs_tol=1e-15)
    assert offsets[-1] > 0.0
    assert isclose(offsets[0], -offsets[-1], abs_tol=1e-15)


def test_sensor_measurement_feeds_receive_steering_without_truth_access():
    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=1497.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=3.0),
    )
    hypothesis = ideal_receive_steering_from_sound_speed_measurement(
        receive_array=_array(),
        across_track_angle_rad=radians(30.0),
        sound_speed_measurement=measurement,
    )
    assert hypothesis.sound_speed_mps == 1500.0
    assert not hasattr(measurement, "true_local_sound_speed_mps")


def test_true_receive_pattern_matches_correct_steering_better_than_nadir():
    poses = _poses()
    propagation = ConstantSoundSpeedPropagation(sound_speed_mps=1500.0)
    alignment = Attitude(roll=0.0, pitch=0.0, yaw=0.0)
    lever = Vector3(x=0.0, y=0.0, z=0.0)

    beam_return = simulate_truth_beam_return(
        tx_time=SimulationTime(seconds=0.1),
        poses=poses,
        beam=_beam(0, 30.0),
        terrain=FlatTerrain(depth=100.0),
        lever_arm_vrp_to_sensor=lever,
        sensor_alignment=alignment,
        propagation=propagation,
    )
    reception = simulate_truth_array_reception(
        beam_return=beam_return,
        poses=poses,
        receive_array=_array(),
        lever_arm_vrp_to_sensor=lever,
        sensor_alignment=alignment,
        propagation=propagation,
    )

    correct = evaluate_receive_steering(
        reception=reception,
        hypothesis=ideal_receive_steering(
            receive_array=_array(),
            across_track_angle_rad=radians(30.0),
            sound_speed_mps=1500.0,
        ),
    )
    nadir = evaluate_receive_steering(
        reception=reception,
        hypothesis=ideal_receive_steering(
            receive_array=_array(),
            across_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
        ),
    )

    assert correct.rms_residual_seconds < nadir.rms_residual_seconds
    assert correct.max_abs_residual_seconds < nadir.max_abs_residual_seconds


def test_compensation_delay_is_opposite_of_predicted_arrival_offset():
    hypothesis = ideal_receive_steering(
        receive_array=_array(),
        across_track_angle_rad=radians(-20.0),
        sound_speed_mps=1480.0,
    )

    for item in hypothesis.element_delays:
        assert isclose(
            item.compensation_delay_seconds,
            -item.predicted_arrival_offset_seconds,
            abs_tol=1e-15,
        )

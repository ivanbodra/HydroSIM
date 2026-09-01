from math import pi

import pytest

from hydrosim.app.motion_lesson import (
    MotionLessonConfiguration,
    MotionLessonControls,
    prepare_motion_lesson_snapshot,
)
from hydrosim.geometry import Vector3


def test_zero_motion_preserves_stationary_geometry():
    configuration = MotionLessonConfiguration(
        vrp_position_n_m=Vector3(x=10.0, y=20.0, z=5.0),
        lever_arm_vrp_to_transducer_b_m=Vector3(x=1.0, y=2.0, z=3.0),
    )

    snapshot = prepare_motion_lesson_snapshot(MotionLessonControls(), configuration)

    assert snapshot.vrp_position_n_m.is_close(Vector3(x=10.0, y=20.0, z=5.0))
    assert snapshot.transducer_position_n_m.is_close(Vector3(x=11.0, y=22.0, z=8.0))
    assert snapshot.body_forward_axis_n.is_close(Vector3(x=1.0, y=0.0, z=0.0))
    assert snapshot.body_starboard_axis_n.is_close(Vector3(x=0.0, y=1.0, z=0.0))
    assert snapshot.body_down_axis_n.is_close(Vector3(x=0.0, y=0.0, z=1.0))
    assert snapshot.beam_direction_n.is_close(Vector3(x=0.0, y=0.0, z=1.0))


def test_positive_heave_moves_vrp_and_transducer_up_in_down_positive_navigation_frame():
    configuration = MotionLessonConfiguration(
        vrp_position_n_m=Vector3(x=0.0, y=0.0, z=10.0),
        lever_arm_vrp_to_transducer_b_m=Vector3(x=0.0, y=0.0, z=2.0),
    )

    snapshot = prepare_motion_lesson_snapshot(MotionLessonControls(heave_m=1.5), configuration)

    assert snapshot.vrp_position_n_m.z == pytest.approx(8.5)
    assert snapshot.transducer_position_n_m.z == pytest.approx(10.5)


def test_positive_roll_rotates_starboard_axis_toward_down():
    snapshot = prepare_motion_lesson_snapshot(MotionLessonControls(roll_rad=pi / 2.0))

    assert snapshot.body_forward_axis_n.is_close(Vector3(x=1.0, y=0.0, z=0.0), atol=1e-12)
    assert snapshot.body_starboard_axis_n.is_close(Vector3(x=0.0, y=0.0, z=1.0), atol=1e-12)
    assert snapshot.body_down_axis_n.is_close(Vector3(x=0.0, y=-1.0, z=0.0), atol=1e-12)


def test_positive_pitch_rotates_forward_axis_toward_up():
    snapshot = prepare_motion_lesson_snapshot(MotionLessonControls(pitch_rad=pi / 2.0))

    assert snapshot.body_forward_axis_n.is_close(Vector3(x=0.0, y=0.0, z=-1.0), atol=1e-12)
    assert snapshot.body_starboard_axis_n.is_close(Vector3(x=0.0, y=1.0, z=0.0), atol=1e-12)


def test_positive_yaw_deviation_rotates_forward_axis_clockwise_from_north():
    snapshot = prepare_motion_lesson_snapshot(MotionLessonControls(yaw_deviation_rad=pi / 2.0))

    assert snapshot.body_forward_axis_n.is_close(Vector3(x=0.0, y=1.0, z=0.0), atol=1e-12)
    assert snapshot.body_starboard_axis_n.is_close(Vector3(x=-1.0, y=0.0, z=0.0), atol=1e-12)
    assert snapshot.body_down_axis_n.is_close(Vector3(x=0.0, y=0.0, z=1.0), atol=1e-12)


def test_each_angular_axis_has_an_independent_geometric_effect():
    zero = prepare_motion_lesson_snapshot(MotionLessonControls())
    roll = prepare_motion_lesson_snapshot(MotionLessonControls(roll_rad=0.1))
    pitch = prepare_motion_lesson_snapshot(MotionLessonControls(pitch_rad=0.1))
    yaw = prepare_motion_lesson_snapshot(MotionLessonControls(yaw_deviation_rad=0.1))

    assert roll.body_forward_axis_n.is_close(zero.body_forward_axis_n)
    assert not roll.body_down_axis_n.is_close(zero.body_down_axis_n)

    assert pitch.body_starboard_axis_n.is_close(zero.body_starboard_axis_n)
    assert not pitch.body_forward_axis_n.is_close(zero.body_forward_axis_n)

    assert yaw.body_down_axis_n.is_close(zero.body_down_axis_n)
    assert not yaw.body_forward_axis_n.is_close(zero.body_forward_axis_n)

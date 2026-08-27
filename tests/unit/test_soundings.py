from math import radians

import pytest

from hydrosim.geometry import (
    Attitude,
    FlatTerrain,
    Pose,
    TransducerArray,
    Vector3,
)
from hydrosim.geometry.beams import generate_ideal_fan_degrees
from hydrosim.geometry.soundings import compare_true_and_configured_sounding


def make_array() -> TransducerArray:
    return TransducerArray(
        name="rx",
        role="rx",
        n_x=8,
        n_y=1,
        d_x=0.02,
        d_y=0.0,
        element_longitudinal_size=0.015,
        element_transverse_size=0.03,
    )


def make_vessel_pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def test_zero_configuration_error_coincides() -> None:
    array = make_array()
    fan = generate_ideal_fan_degrees(array, beam_count=5, total_swath_angle_degrees=120.0)
    alignment = Attitude(roll=0.0, pitch=0.0, yaw=0.0)

    for beam in fan.beams:
        result = compare_true_and_configured_sounding(
            vessel_truth_pose=make_vessel_pose(),
            lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
            true_sensor_alignment=alignment,
            configured_sensor_alignment=alignment,
            beam=beam,
            terrain=FlatTerrain(depth=21.0),
        )
        assert result.true.point.is_close(result.configured.point, atol=1e-12)
        assert result.error_vector.is_close(Vector3(x=0.0, y=0.0, z=0.0), atol=1e-12)
        assert result.horizontal_error == pytest.approx(0.0, abs=1e-12)
        assert result.vertical_error == pytest.approx(0.0, abs=1e-12)


def test_true_nadir_geometry_and_range() -> None:
    beam = generate_ideal_fan_degrees(make_array(), beam_count=1, total_swath_angle_degrees=0.0).beams[0]
    result = compare_true_and_configured_sounding(
        vessel_truth_pose=make_vessel_pose(),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
        true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        configured_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        beam=beam,
        terrain=FlatTerrain(depth=21.0),
    )

    assert result.true.point.is_close(Vector3(x=0.0, y=0.0, z=21.0))
    assert result.true.slant_range == pytest.approx(20.0)
    assert result.configured.slant_range == pytest.approx(20.0)


def test_roll_alignment_error_moves_nadir_sounding() -> None:
    beam = generate_ideal_fan_degrees(make_array(), beam_count=1, total_swath_angle_degrees=0.0).beams[0]
    result = compare_true_and_configured_sounding(
        vessel_truth_pose=make_vessel_pose(),
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
        true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        configured_sensor_alignment=Attitude(roll=radians(1.0), pitch=0.0, yaw=0.0),
        beam=beam,
        terrain=FlatTerrain(depth=21.0),
    )

    # Positive roll rotates +Z toward -Y in the configured sensor solution.
    assert result.error_vector.y < 0.0
    assert result.error_vector.z < 0.0
    assert result.horizontal_error > 0.0
    assert result.error_magnitude > 0.0


def test_roll_error_is_beam_dependent() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=3, total_swath_angle_degrees=90.0)
    results = [
        compare_true_and_configured_sounding(
            vessel_truth_pose=make_vessel_pose(),
            lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
            true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            configured_sensor_alignment=Attitude(roll=radians(1.0), pitch=0.0, yaw=0.0),
            beam=beam,
            terrain=FlatTerrain(depth=21.0),
        )
        for beam in fan.beams
    ]

    vertical_errors = [result.vertical_error for result in results]
    assert vertical_errors[0] != pytest.approx(vertical_errors[1])
    assert vertical_errors[2] != pytest.approx(vertical_errors[1])


def test_vessel_attitude_is_applied_to_true_geometry() -> None:
    vessel = Pose(
        position=Vector3(x=10.0, y=20.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=radians(90.0)),
        frame="N",
    )
    fan = generate_ideal_fan_degrees(make_array(), beam_count=3, total_swath_angle_degrees=60.0)
    port_beam = fan.beams[0]

    result = compare_true_and_configured_sounding(
        vessel_truth_pose=vessel,
        lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
        true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        configured_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        beam=port_beam,
        terrain=FlatTerrain(depth=21.0),
    )

    # With yaw +90 deg, array-local -Y (port) rotates toward +X/North.
    assert result.true.point.x > 10.0
    assert result.true.point.y == pytest.approx(20.0, abs=1e-12)


def test_non_intersecting_true_ray_is_rejected() -> None:
    array = TransducerArray(
        name="upward",
        role="rx",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.02,
        element_transverse_size=0.02,
        orientation=Attitude(roll=radians(180.0), pitch=0.0, yaw=0.0),
    )
    beam = generate_ideal_fan_degrees(array, beam_count=1, total_swath_angle_degrees=0.0).beams[0]

    with pytest.raises(ValueError, match="does not intersect terrain"):
        compare_true_and_configured_sounding(
            vessel_truth_pose=make_vessel_pose(),
            lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=1.0),
            true_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            configured_sensor_alignment=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            beam=beam,
            terrain=FlatTerrain(depth=21.0),
        )

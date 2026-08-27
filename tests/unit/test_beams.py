from math import pi

import pytest

from hydrosim.geometry import Attitude, TransducerArray, Vector3
from hydrosim.geometry.beams import generate_ideal_fan, generate_ideal_fan_degrees


def make_array(*, name: str = "rx", orientation: Attitude | None = None) -> TransducerArray:
    return TransducerArray(
        name=name,
        role="rx",
        n_x=8,
        n_y=1,
        d_x=0.02,
        d_y=0.0,
        element_longitudinal_size=0.015,
        element_transverse_size=0.03,
        orientation=orientation or Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def test_first_and_last_beams_match_swath_limits() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=5, total_swath_angle_degrees=120.0)
    angles = [beam.definition.across_track_angle for beam in fan.beams]

    assert angles[0] == pytest.approx(pi / 3)
    assert angles[-1] == pytest.approx(-pi / 3)


def test_beam_count_is_exact() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=7, total_swath_angle_degrees=140.0)

    assert fan.beam_count == 7
    assert len(fan.beams) == 7


def test_equal_angle_fan_is_symmetric_about_nadir() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=6, total_swath_angle_degrees=100.0)
    angles = [beam.definition.across_track_angle for beam in fan.beams]

    for left, right in zip(angles, reversed(angles), strict=True):
        assert left == pytest.approx(-right)


def test_odd_beam_count_contains_nadir() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=5, total_swath_angle_degrees=120.0)

    assert fan.has_nadir_beam
    assert fan.beams[2].definition.across_track_angle == pytest.approx(0.0)


def test_even_beam_count_does_not_contain_nadir() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=4, total_swath_angle_degrees=120.0)

    assert not fan.has_nadir_beam


def test_positive_angle_is_port_and_negative_is_starboard() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=3, total_swath_angle_degrees=90.0)
    port, nadir, starboard = fan.beams

    assert port.direction_array_frame.y < 0.0
    assert port.direction_array_frame.z > 0.0
    assert nadir.direction_array_frame.is_close(Vector3(x=0.0, y=0.0, z=1.0))
    assert starboard.direction_array_frame.y > 0.0
    assert starboard.direction_array_frame.z > 0.0


def test_one_beam_is_nadir() -> None:
    fan = generate_ideal_fan_degrees(make_array(), beam_count=1, total_swath_angle_degrees=120.0)

    assert fan.has_nadir_beam
    assert fan.beams[0].definition.across_track_angle == pytest.approx(0.0)


def test_array_dimensions_do_not_change_v01_equal_angle_geometry() -> None:
    small = make_array(name="small")
    large = TransducerArray(
        name="large",
        role="rx",
        n_x=32,
        n_y=4,
        d_x=0.05,
        d_y=0.04,
        element_longitudinal_size=0.04,
        element_transverse_size=0.03,
    )

    fan_small = generate_ideal_fan_degrees(small, beam_count=5, total_swath_angle_degrees=120.0)
    fan_large = generate_ideal_fan_degrees(large, beam_count=5, total_swath_angle_degrees=120.0)

    assert [b.definition.across_track_angle for b in fan_small.beams] == pytest.approx(
        [b.definition.across_track_angle for b in fan_large.beams]
    )


def test_array_orientation_rotates_ray_into_sensor_frame() -> None:
    array = make_array(orientation=Attitude.from_degrees(roll=90.0, pitch=0.0, yaw=0.0))
    fan = generate_ideal_fan(array, beam_count=1, total_swath_angle=0.0)

    ray = fan.beams[0]
    assert ray.direction_array_frame.is_close(Vector3(x=0.0, y=0.0, z=1.0))
    assert ray.direction_sensor_frame.is_close(Vector3(x=0.0, y=-1.0, z=0.0), atol=1e-12)


def test_role_and_array_reference_are_preserved() -> None:
    array = make_array(name="rx_array")
    fan = generate_ideal_fan_degrees(
        array,
        beam_count=3,
        total_swath_angle_degrees=60.0,
        role="rx",
    )

    assert fan.array_name == "rx_array"
    assert all(beam.definition.array_name == "rx_array" for beam in fan.beams)
    assert all(beam.definition.role == "rx" for beam in fan.beams)

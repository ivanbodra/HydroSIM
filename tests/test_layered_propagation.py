from math import asin, cos, pi, sin, tan

import pytest

from hydrosim.acquisition.layered_propagation import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    assess_layered_ray_time_depth_closure,
    trace_layered_ray_for_travel_time,
    trace_layered_ray_to_depth,
)
from hydrosim.acquisition.sound_speed_profile_boundary import SoundSpeedProfileBoundary


def test_constant_speed_layer_reduces_to_straight_ray_geometry() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=100.0, sound_speed_mps=1500.0),)
    )
    angle = pi / 6.0
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=angle,
        target_depth_m=60.0,
    )

    assert path.horizontal_distance_m == pytest.approx(60.0 * tan(angle))
    assert path.path_length_m == pytest.approx(60.0 / cos(angle))
    assert path.travel_time_seconds == pytest.approx(path.path_length_m / 1500.0)
    assert len(path.segments) == 1


def test_two_layer_snell_solution_matches_closed_form_independent_values() -> None:
    c1 = 1500.0
    c2 = 1540.0
    dz1 = 40.0
    dz2 = 60.0
    theta1 = pi / 6.0
    expected_ray_parameter = sin(theta1) / c1
    expected_theta2 = asin(expected_ray_parameter * c2)

    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=dz1, sound_speed_mps=c1),
            SoundSpeedLayer(top_depth_m=dz1, bottom_depth_m=dz1 + dz2, sound_speed_mps=c2),
        )
    )
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=theta1,
        target_depth_m=dz1 + dz2,
    )

    expected_horizontal = dz1 * tan(theta1) + dz2 * tan(expected_theta2)
    expected_path_length = dz1 / cos(theta1) + dz2 / cos(expected_theta2)
    expected_travel_time = dz1 / (c1 * cos(theta1)) + dz2 / (c2 * cos(expected_theta2))

    assert path.ray_parameter_seconds_per_m == pytest.approx(expected_ray_parameter)
    assert path.segments[0].angle_from_vertical_rad == pytest.approx(theta1)
    assert path.segments[1].angle_from_vertical_rad == pytest.approx(expected_theta2)
    assert sin(path.segments[0].angle_from_vertical_rad) / c1 == pytest.approx(
        sin(path.segments[1].angle_from_vertical_rad) / c2
    )
    assert path.horizontal_distance_m == pytest.approx(expected_horizontal)
    assert path.path_length_m == pytest.approx(expected_path_length)
    assert path.travel_time_seconds == pytest.approx(expected_travel_time)


def test_zero_thickness_boundary_sets_snell_parameter_without_replacing_first_layer() -> None:
    boundary_c = 1480.0
    layer_c = 1520.0
    launch_angle = 0.30
    dz = 80.0
    expected_ray_parameter = sin(launch_angle) / boundary_c
    expected_layer_angle = asin(expected_ray_parameter * layer_c)

    profile = LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=dz, sound_speed_mps=layer_c),)
    )
    boundary = SoundSpeedProfileBoundary(
        depth_m=0.0,
        sound_speed_mps=boundary_c,
        source="sound_speed_at_transducer",
    )
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=launch_angle,
        target_depth_m=dz,
        start_boundary=boundary,
    )

    expected_horizontal = dz * tan(expected_layer_angle)
    expected_path_length = dz / cos(expected_layer_angle)
    expected_travel_time = expected_path_length / layer_c

    assert path.ray_parameter_seconds_per_m == pytest.approx(expected_ray_parameter)
    assert path.segments[0].sound_speed_mps == pytest.approx(layer_c)
    assert path.segments[0].angle_from_vertical_rad == pytest.approx(expected_layer_angle)
    assert path.horizontal_distance_m == pytest.approx(expected_horizontal)
    assert path.path_length_m == pytest.approx(expected_path_length)
    assert path.travel_time_seconds == pytest.approx(expected_travel_time)


def test_increasing_sound_speed_refracts_ray_away_from_vertical() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=50.0, sound_speed_mps=1480.0),
            SoundSpeedLayer(top_depth_m=50.0, bottom_depth_m=100.0, sound_speed_mps=1520.0),
        )
    )
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=0.4,
        target_depth_m=100.0,
    )

    assert len(path.segments) == 2
    upper, lower = path.segments
    assert lower.angle_from_vertical_rad > upper.angle_from_vertical_rad
    assert lower.horizontal_distance_m > upper.horizontal_distance_m


def test_profile_requires_contiguous_layers() -> None:
    with pytest.raises(ValueError, match="contiguous"):
        LayeredSoundSpeedProfile(
            layers=(
                SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
                SoundSpeedLayer(top_depth_m=50.0, bottom_depth_m=100.0, sound_speed_mps=1510.0),
            )
        )


def test_critical_condition_is_rejected_explicitly() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=10.0, sound_speed_mps=1000.0),
            SoundSpeedLayer(top_depth_m=10.0, bottom_depth_m=20.0, sound_speed_mps=2000.0),
        )
    )
    with pytest.raises(ValueError, match="critical"):
        trace_layered_ray_to_depth(
            profile=profile,
            launch_angle_from_vertical_rad=pi / 4.0,
            target_depth_m=20.0,
        )


def test_travel_time_stopping_reaches_partial_second_layer_without_average_speed() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=50.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=50.0, bottom_depth_m=100.0, sound_speed_mps=1600.0),
        )
    )
    travel_time = 50.0 / 1500.0 + 25.0 / 1600.0
    path = trace_layered_ray_for_travel_time(
        profile=profile,
        launch_angle_from_vertical_rad=0.0,
        travel_time_seconds=travel_time,
    )

    assert path.target_depth_m == pytest.approx(75.0)
    assert path.path_length_m == pytest.approx(75.0)
    assert path.travel_time_seconds == pytest.approx(travel_time)
    assert len(path.segments) == 2
    assert path.segments[1].end_depth_m == pytest.approx(75.0)


def test_travel_time_stopping_rejects_time_beyond_profile() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=10.0, sound_speed_mps=1500.0),)
    )
    with pytest.raises(ValueError, match="extends beyond"):
        trace_layered_ray_for_travel_time(
            profile=profile,
            launch_angle_from_vertical_rad=0.0,
            travel_time_seconds=1.0,
        )


def test_depth_and_travel_time_solvers_close_on_same_refracted_ray() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=30.0, sound_speed_mps=1475.0),
            SoundSpeedLayer(top_depth_m=30.0, bottom_depth_m=80.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=80.0, bottom_depth_m=150.0, sound_speed_mps=1530.0),
        )
    )

    diagnostic = assess_layered_ray_time_depth_closure(
        profile=profile,
        launch_angle_from_vertical_rad=0.55,
        target_depth_m=112.5,
        depth_tolerance_m=1e-9,
        horizontal_tolerance_m=1e-9,
        path_length_tolerance_m=1e-9,
    )

    assert diagnostic.depth_driven_path.travel_time_seconds == pytest.approx(
        diagnostic.time_driven_path.travel_time_seconds
    )
    assert diagnostic.absolute_depth_closure_m <= 1e-9
    assert diagnostic.absolute_horizontal_closure_m <= 1e-9
    assert diagnostic.absolute_path_length_closure_m <= 1e-9
    assert diagnostic.converged is True


def test_closure_diagnostic_rejects_negative_tolerance() -> None:
    profile = LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=100.0, sound_speed_mps=1500.0),)
    )
    with pytest.raises(ValueError, match="closure tolerances must be non-negative"):
        assess_layered_ray_time_depth_closure(
            profile=profile,
            launch_angle_from_vertical_rad=0.2,
            target_depth_m=50.0,
            depth_tolerance_m=-1.0,
        )

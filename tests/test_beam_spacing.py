from math import radians

import pytest

from hydrosim.acquisition import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    make_equiangular_beam_plan,
    make_equidistant_beam_plan,
    trace_layered_ray_to_depth,
)


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=100.0, sound_speed_mps=1540.0),
        )
    )


def test_equiangular_has_constant_angle_increment() -> None:
    plan = make_equiangular_beam_plan(minimum_angle_rad=radians(-60), maximum_angle_rad=radians(60), beam_count=7)
    increments = [plan.across_track_angles_rad[i + 1] - plan.across_track_angles_rad[i] for i in range(6)]
    assert all(value == pytest.approx(increments[0]) for value in increments)
    assert plan.target_across_track_positions_m is None


def test_equidistant_solves_constant_bottom_spacing_through_profile() -> None:
    profile = _profile()
    plan = make_equidistant_beam_plan(
        profile=profile,
        minimum_angle_rad=radians(-55),
        maximum_angle_rad=radians(55),
        beam_count=7,
        target_depth_m=80.0,
    )
    endpoints = []
    for angle in plan.across_track_angles_rad:
        path = trace_layered_ray_to_depth(
            profile=profile,
            launch_angle_from_vertical_rad=abs(float(angle)),
            target_depth_m=80.0,
        )
        endpoints.append((-1.0 if angle < 0 else 1.0) * float(path.horizontal_distance_m) if angle != 0 else 0.0)
    increments = [endpoints[i + 1] - endpoints[i] for i in range(6)]
    assert all(value == pytest.approx(increments[0], rel=1e-8) for value in increments)
    assert plan.target_across_track_positions_m is not None

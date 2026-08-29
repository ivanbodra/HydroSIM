from math import radians, sin

import pytest

from hydrosim.acquisition.layered_propagation import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_for_travel_time,
    trace_layered_ray_to_depth,
)
from hydrosim.acquisition.sound_speed_profile_boundary import SoundSpeedProfileBoundary


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(layers=(
        SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=20.0, sound_speed_mps=1490.0),
        SoundSpeedLayer(top_depth_m=20.0, bottom_depth_m=100.0, sound_speed_mps=1510.0),
    ))


def test_explicit_boundary_sets_ray_parameter_without_overwriting_first_layer() -> None:
    profile = _profile()
    angle = radians(30.0)
    boundary = SoundSpeedProfileBoundary(depth_m=0.0, sound_speed_mps=1502.0, source="sound_speed_at_transducer")
    path = trace_layered_ray_to_depth(profile=profile, launch_angle_from_vertical_rad=angle, target_depth_m=60.0, start_boundary=boundary)
    assert path.ray_parameter_seconds_per_m == pytest.approx(sin(angle) / 1502.0)
    assert path.segments[0].sound_speed_mps == pytest.approx(1490.0)
    assert path.segments[1].sound_speed_mps == pytest.approx(1510.0)


def test_boundary_changes_geometry_relative_to_profile_initialized_ray() -> None:
    profile = _profile()
    baseline = trace_layered_ray_to_depth(profile=profile, launch_angle_from_vertical_rad=radians(40.0), target_depth_m=80.0)
    boundary = SoundSpeedProfileBoundary(depth_m=0.0, sound_speed_mps=1520.0, source="sound_speed_at_transducer")
    bounded = trace_layered_ray_to_depth(profile=profile, launch_angle_from_vertical_rad=radians(40.0), target_depth_m=80.0, start_boundary=boundary)
    assert bounded.horizontal_distance_m != pytest.approx(baseline.horizontal_distance_m)


def test_depth_and_time_solvers_close_with_same_explicit_boundary() -> None:
    profile = _profile()
    boundary = SoundSpeedProfileBoundary(depth_m=0.0, sound_speed_mps=1505.0, source="sound_speed_at_transducer")
    depth_path = trace_layered_ray_to_depth(profile=profile, launch_angle_from_vertical_rad=radians(35.0), target_depth_m=75.0, start_boundary=boundary)
    time_path = trace_layered_ray_for_travel_time(profile=profile, launch_angle_from_vertical_rad=radians(35.0), travel_time_seconds=depth_path.travel_time_seconds, start_boundary=boundary)
    assert time_path.target_depth_m == pytest.approx(75.0, abs=1e-9)
    assert time_path.horizontal_distance_m == pytest.approx(depth_path.horizontal_distance_m, abs=1e-9)


def test_boundary_depth_must_match_trace_start() -> None:
    with pytest.raises(ValueError, match="boundary depth"):
        trace_layered_ray_to_depth(profile=_profile(), launch_angle_from_vertical_rad=radians(20.0), target_depth_m=50.0, start_depth_m=0.0, start_boundary=SoundSpeedProfileBoundary(depth_m=2.0, sound_speed_mps=1500.0, source="sound_speed_at_transducer"))

from math import cos, pi, tan

import pytest

from hydrosim.acquisition.layered_propagation import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_to_depth,
)


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

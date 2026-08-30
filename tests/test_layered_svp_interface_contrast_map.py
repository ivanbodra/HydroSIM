from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_contrast_map import (
    run_layered_svp_interface_contrast_map,
    set_layered_profile_interface_contrast,
)
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=120.0, sound_speed_mps=1540.0),
            SoundSpeedLayer(top_depth_m=120.0, bottom_depth_m=250.0, sound_speed_mps=1510.0),
        )
    )


def _angles() -> tuple[float, ...]:
    return tuple(radians(value) for value in (-60, -30, 0, 30, 60))


def test_set_contrast_changes_only_lower_adjacent_speed() -> None:
    profile = _profile()
    changed = set_layered_profile_interface_contrast(
        profile=profile,
        interface_index=0,
        sound_speed_contrast_mps=25.0,
    )

    assert tuple(float(layer.sound_speed_mps) for layer in changed.layers) == (
        1500.0,
        1525.0,
        1510.0,
    )
    assert tuple(float(layer.top_depth_m) for layer in changed.layers) == (0.0, 40.0, 120.0)
    assert tuple(float(layer.bottom_depth_m) for layer in changed.layers) == (40.0, 120.0, 250.0)


def test_truth_depth_and_truth_contrast_close_full_swath() -> None:
    result = run_layered_svp_interface_contrast_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=(35.0, 40.0, 45.0),
        processing_sound_speed_contrasts_mps=(20.0, 40.0, 60.0),
        profile_start_depth_m=0.0,
    )

    reference = next(
        point
        for point in result.points
        if float(point.interface_depth_m) == 40.0
        and float(point.sound_speed_contrast_mps) == 40.0
    )
    assert reference.interface_depth_error_m == pytest.approx(0.0)
    assert reference.sound_speed_contrast_error_mps == pytest.approx(0.0)
    assert reference.mean_edge_minus_nadir_vertical_error_m == pytest.approx(0.0, abs=1e-9)
    for point in reference.swath_curvature.points:
        assert point.vertical_error_m == pytest.approx(0.0, abs=1e-9)
        assert point.across_track_error_m == pytest.approx(0.0, abs=1e-9)


def test_depth_and_contrast_are_independent_experiment_coordinates() -> None:
    result = run_layered_svp_interface_contrast_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=(35.0, 45.0),
        processing_sound_speed_contrasts_mps=(20.0, 60.0),
        profile_start_depth_m=0.0,
    )

    curvatures = {
        (float(point.interface_depth_m), float(point.sound_speed_contrast_mps)): float(
            point.mean_edge_minus_nadir_vertical_error_m
        )
        for point in result.points
    }
    assert len(set(round(value, 10) for value in curvatures.values())) > 1


def test_map_order_is_depth_outer_contrast_inner() -> None:
    depths = (50.0, 30.0)
    contrasts = (60.0, 10.0, 40.0)
    result = run_layered_svp_interface_contrast_map(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-45, 0, 45)),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=depths,
        processing_sound_speed_contrasts_mps=contrasts,
        profile_start_depth_m=0.0,
    )

    observed = tuple(
        (float(point.interface_depth_m), float(point.sound_speed_contrast_mps))
        for point in result.points
    )
    expected = tuple((depth, contrast) for depth in depths for contrast in contrasts)
    assert observed == expected


def test_rejects_empty_axes_and_non_positive_lower_speed() -> None:
    profile = _profile()
    with pytest.raises(ValueError, match="non-positive lower-layer speed"):
        set_layered_profile_interface_contrast(
            profile=profile,
            interface_index=0,
            sound_speed_contrast_mps=-1500.0,
        )
    with pytest.raises(ValueError, match="processing_interface_depths_m must not be empty"):
        run_layered_svp_interface_contrast_map(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=_angles(),
            true_profile=profile,
            interface_index=0,
            processing_interface_depths_m=(),
            processing_sound_speed_contrasts_mps=(40.0,),
            profile_start_depth_m=0.0,
        )
    with pytest.raises(ValueError, match="processing_sound_speed_contrasts_mps must not be empty"):
        run_layered_svp_interface_contrast_map(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=_angles(),
            true_profile=profile,
            interface_index=0,
            processing_interface_depths_m=(40.0,),
            processing_sound_speed_contrasts_mps=(),
            profile_start_depth_m=0.0,
        )

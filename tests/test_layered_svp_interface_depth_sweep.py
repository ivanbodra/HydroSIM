from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_depth_sweep import (
    move_layered_profile_interface,
    run_layered_svp_interface_depth_sweep,
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


def test_move_interface_changes_only_adjacent_geometry() -> None:
    profile = _profile()
    moved = move_layered_profile_interface(
        profile=profile,
        interface_index=0,
        interface_depth_m=55.0,
    )

    assert tuple(float(layer.sound_speed_mps) for layer in moved.layers) == (1500.0, 1540.0, 1510.0)
    assert tuple(float(layer.top_depth_m) for layer in moved.layers) == (0.0, 55.0, 120.0)
    assert tuple(float(layer.bottom_depth_m) for layer in moved.layers) == (55.0, 120.0, 250.0)


def test_truth_interface_depth_closes_curvature() -> None:
    result = run_layered_svp_interface_depth_sweep(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, -30, 0, 30, 60)),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=(25.0, 40.0, 55.0),
        profile_start_depth_m=0.0,
    )

    reference = result.points[1]
    assert reference.interface_depth_error_m == pytest.approx(0.0)
    assert reference.mean_edge_minus_nadir_vertical_error_m == pytest.approx(0.0, abs=1e-9)
    for point in reference.swath_curvature.points:
        assert point.vertical_error_m == pytest.approx(0.0, abs=1e-9)
        assert point.across_track_error_m == pytest.approx(0.0, abs=1e-9)


def test_opposite_interface_displacements_produce_opposite_local_curvature_signs() -> None:
    result = run_layered_svp_interface_depth_sweep(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, -30, 0, 30, 60)),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=(35.0, 45.0),
        profile_start_depth_m=0.0,
    )

    shallow, deep = result.points
    assert float(shallow.mean_edge_minus_nadir_vertical_error_m) != pytest.approx(0.0)
    assert float(deep.mean_edge_minus_nadir_vertical_error_m) != pytest.approx(0.0)
    assert (
        float(shallow.mean_edge_minus_nadir_vertical_error_m)
        * float(deep.mean_edge_minus_nadir_vertical_error_m)
        < 0.0
    )


def test_sweep_preserves_requested_depth_order() -> None:
    depths = (60.0, 20.0, 40.0)
    result = run_layered_svp_interface_depth_sweep(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-45, 0, 45)),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=depths,
        profile_start_depth_m=0.0,
    )

    assert tuple(float(value) for value in result.interface_depths_m) == depths
    assert tuple(float(point.interface_depth_m) for point in result.points) == depths


def test_rejects_invalid_interface_or_empty_sweep() -> None:
    profile = _profile()
    with pytest.raises(ValueError, match="interior layer boundary"):
        move_layered_profile_interface(profile=profile, interface_index=2, interface_depth_m=150.0)
    with pytest.raises(ValueError, match="adjacent-layer extent"):
        move_layered_profile_interface(profile=profile, interface_index=0, interface_depth_m=0.0)
    with pytest.raises(ValueError, match="must not be empty"):
        run_layered_svp_interface_depth_sweep(
            sensor_pose=_pose(), terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=tuple(radians(v) for v in (-45, 0, 45)),
            true_profile=profile, interface_index=0, processing_interface_depths_m=(),
            profile_start_depth_m=0.0,
        )

from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_swath_curvature import run_layered_svp_swath_curvature
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _profile(c1: float, c2: float) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=c1),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=200.0, sound_speed_mps=c2),
        )
    )


def test_identical_profiles_reconstruct_flat_bottom() -> None:
    profile = _profile(1500.0, 1540.0)
    result = run_layered_svp_swath_curvature(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, -30, 0, 30, 60)),
        true_profile=profile,
        processing_profile=profile,
        profile_start_depth_m=0.0,
    )

    for point in result.points:
        assert point.across_track_error_m == pytest.approx(0.0, abs=1e-9)
        assert point.vertical_error_m == pytest.approx(0.0, abs=1e-9)
    assert result.mean_edge_minus_nadir_vertical_error_m == pytest.approx(0.0, abs=1e-9)


def test_profile_mismatch_produces_symmetric_nonzero_swath_curvature() -> None:
    true_profile = _profile(1500.0, 1540.0)
    processing_profile = _profile(1500.0, 1490.0)
    result = run_layered_svp_swath_curvature(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, -30, 0, 30, 60)),
        true_profile=true_profile,
        processing_profile=processing_profile,
        profile_start_depth_m=0.0,
    )

    by_angle = {round(float(point.configured_across_track_angle_rad), 12): point for point in result.points}
    for degrees in (30, 60):
        port = by_angle[round(radians(-degrees), 12)]
        starboard = by_angle[round(radians(degrees), 12)]
        assert port.vertical_error_m == pytest.approx(starboard.vertical_error_m, abs=1e-10)
        assert port.across_track_error_m == pytest.approx(-float(starboard.across_track_error_m), abs=1e-10)

    assert abs(float(result.mean_edge_minus_nadir_vertical_error_m)) > 0.01


def test_reversing_profile_perturbation_changes_curvature_response() -> None:
    truth = _profile(1500.0, 1520.0)
    low = run_layered_svp_swath_curvature(
        sensor_pose=_pose(), terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, 0, 60)),
        true_profile=truth, processing_profile=_profile(1500.0, 1480.0), profile_start_depth_m=0.0,
    )
    high = run_layered_svp_swath_curvature(
        sensor_pose=_pose(), terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, 0, 60)),
        true_profile=truth, processing_profile=_profile(1500.0, 1560.0), profile_start_depth_m=0.0,
    )

    assert float(low.mean_edge_minus_nadir_vertical_error_m) * float(high.mean_edge_minus_nadir_vertical_error_m) < 0.0


def test_requires_nadir_and_both_swath_sides() -> None:
    common = dict(
        sensor_pose=_pose(), terrain=FlatTerrain(depth=120.0), true_profile=_profile(1500.0, 1520.0),
        processing_profile=_profile(1500.0, 1500.0), profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="include nadir"):
        run_layered_svp_swath_curvature(configured_across_track_angles_rad=(radians(-30), radians(30)), **common)
    with pytest.raises(ValueError, match="span port and starboard"):
        run_layered_svp_swath_curvature(configured_across_track_angles_rad=(0.0, radians(30)), **common)

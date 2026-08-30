from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3
from hydrosim.visualization.layered_svp_explorer import prepare_layered_svp_explorer_snapshot


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


def test_identical_profiles_close_truth_and_reconstruction() -> None:
    profile = _profile(1500.0, 1540.0)
    snapshot = prepare_layered_svp_explorer_snapshot(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, 0, 60)),
        true_profile=profile,
        processing_profile=profile,
        profile_start_depth_m=0.0,
    )

    assert len(snapshot.beams) == 3
    for beam in snapshot.beams:
        assert beam.reconstructed_bottom_point.x == pytest.approx(beam.truth_bottom_point.x, abs=1e-9)
        assert beam.reconstructed_bottom_point.y == pytest.approx(beam.truth_bottom_point.y, abs=1e-9)
        assert beam.reconstructed_bottom_point.z == pytest.approx(beam.truth_bottom_point.z, abs=1e-9)
        assert beam.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)


def test_profile_mismatch_is_visible_without_changing_truth_bottom() -> None:
    snapshot = prepare_layered_svp_explorer_snapshot(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=(radians(-60), 0.0, radians(60)),
        true_profile=_profile(1500.0, 1540.0),
        processing_profile=_profile(1500.0, 1490.0),
        profile_start_depth_m=0.0,
    )

    for beam in snapshot.beams:
        assert beam.truth_bottom_point.z == pytest.approx(120.0)
        assert beam.true_twtt_seconds > 0.0
        assert beam.truth_ray_path.segments

    assert snapshot.beams[0].sounding_error_norm_m > 0.01
    assert snapshot.beams[2].sounding_error_norm_m > 0.01


def test_beam_order_is_preserved_and_single_beam_is_allowed() -> None:
    angles = (radians(35), radians(-10), 0.0)
    snapshot = prepare_layered_svp_explorer_snapshot(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=80.0),
        configured_across_track_angles_rad=angles,
        true_profile=_profile(1500.0, 1520.0),
        processing_profile=_profile(1500.0, 1510.0),
        profile_start_depth_m=0.0,
    )
    assert tuple(float(beam.configured_across_track_angle_rad) for beam in snapshot.beams) == angles

    single = prepare_layered_svp_explorer_snapshot(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=80.0),
        configured_across_track_angles_rad=(radians(20),),
        true_profile=_profile(1500.0, 1520.0),
        processing_profile=_profile(1500.0, 1510.0),
        profile_start_depth_m=0.0,
    )
    assert len(single.beams) == 1


def test_empty_beam_axis_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        prepare_layered_svp_explorer_snapshot(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=80.0),
            configured_across_track_angles_rad=(),
            true_profile=_profile(1500.0, 1520.0),
            processing_profile=_profile(1500.0, 1510.0),
            profile_start_depth_m=0.0,
        )

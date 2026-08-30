from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_contrast_compensation_curve import (
    run_layered_svp_interface_contrast_compensation_curve,
)
from hydrosim.acquisition.layered_svp_interface_contrast_map import (
    run_layered_svp_interface_contrast_map,
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


def _run(depths: tuple[float, ...]):
    return run_layered_svp_interface_contrast_compensation_curve(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=depths,
        contrast_bracket_mps=(-200.0, 300.0),
        profile_start_depth_m=0.0,
        local_interface_depth_step_m=2.0,
        local_sound_speed_contrast_step_mps=4.0,
        curvature_tolerance_m=1e-10,
        contrast_tolerance_mps=1e-10,
    )


def test_truth_coordinate_is_on_compensation_curve() -> None:
    result = _run((40.0,))
    point = result.points[0]

    assert point.interface_depth_error_m == pytest.approx(0.0)
    assert point.compensated_sound_speed_contrast_mps == pytest.approx(40.0, abs=1e-7)
    assert point.sound_speed_contrast_error_mps == pytest.approx(0.0, abs=1e-7)
    assert point.residual_curvature_m == pytest.approx(0.0, abs=1e-10)


def test_reported_roots_close_edge_curvature_when_re_evaluated() -> None:
    result = _run((38.0, 40.0, 42.0))

    for point in result.points:
        direct = run_layered_svp_interface_contrast_map(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=_angles(),
            true_profile=_profile(),
            interface_index=0,
            processing_interface_depths_m=(float(point.interface_depth_m),),
            processing_sound_speed_contrasts_mps=(
                float(point.compensated_sound_speed_contrast_mps),
            ),
            profile_start_depth_m=0.0,
        )
        assert direct.points[0].mean_edge_minus_nadir_vertical_error_m == pytest.approx(
            0.0, abs=2e-9
        )


def test_local_tangent_is_exact_at_truth_and_used_as_comparison_not_constraint() -> None:
    result = _run((39.0, 40.0, 41.0))
    reference = result.points[1]

    assert reference.local_tangent_predicted_contrast_error_mps == pytest.approx(0.0)
    assert reference.tangent_prediction_residual_mps == pytest.approx(0.0, abs=1e-7)
    assert result.local_sensitivity.contrast_compensation_slope_mps_per_m is not None

    off_truth = (result.points[0], result.points[2])
    assert any(abs(float(point.sound_speed_contrast_error_mps)) > 1e-8 for point in off_truth)


def test_curve_preserves_requested_depth_order() -> None:
    depths = (42.0, 38.0, 40.0)
    result = _run(depths)
    assert tuple(float(point.interface_depth_m) for point in result.points) == depths


def test_rejects_non_bracketing_contrast_interval() -> None:
    with pytest.raises(ValueError, match="does not bracket zero curvature"):
        run_layered_svp_interface_contrast_compensation_curve(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=_angles(),
            true_profile=_profile(),
            interface_index=0,
            processing_interface_depths_m=(40.0,),
            contrast_bracket_mps=(0.0, 10.0),
            profile_start_depth_m=0.0,
            local_interface_depth_step_m=2.0,
            local_sound_speed_contrast_step_mps=4.0,
        )

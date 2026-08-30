from math import radians, sqrt

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_contrast_compensated_swath_response import (
    run_layered_svp_compensated_swath_response,
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
    return run_layered_svp_compensated_swath_response(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        processing_interface_depths_m=depths,
        contrast_bracket_mps=(-20.0, 100.0),
        profile_start_depth_m=0.0,
        local_interface_depth_step_m=2.0,
        local_sound_speed_contrast_step_mps=4.0,
        curvature_tolerance_m=1e-10,
        contrast_tolerance_mps=1e-10,
    )


def test_truth_compensation_point_closes_complete_swath() -> None:
    result = _run((40.0,))
    point = result.points[0]

    assert point.compensation_point.sound_speed_contrast_error_mps == pytest.approx(0.0, abs=1e-7)
    assert point.max_abs_vertical_error_m == pytest.approx(0.0, abs=1e-8)
    assert point.max_abs_across_track_error_m == pytest.approx(0.0, abs=1e-8)
    assert point.max_sounding_error_norm_m == pytest.approx(0.0, abs=1e-8)


def test_zero_edge_curvature_can_hide_nonzero_full_swath_error() -> None:
    result = _run((38.0, 42.0))

    for point in result.points:
        assert point.swath_curvature.mean_edge_minus_nadir_vertical_error_m == pytest.approx(
            0.0, abs=2e-9
        )
        assert abs(float(point.compensation_point.interface_depth_error_m)) > 0.0
        assert point.max_sounding_error_norm_m > 1e-6
        assert any(
            abs(float(sample.vertical_error_m)) > 1e-6
            or abs(float(sample.across_track_error_m)) > 1e-6
            for sample in point.swath_curvature.points
        )


def test_aggregate_metrics_are_independent_summaries_of_beamwise_errors() -> None:
    point = _run((38.0,)).points[0]
    swath = point.swath_curvature.points
    n = len(swath)
    across = [float(sample.across_track_error_m) for sample in swath]
    vertical = [float(sample.vertical_error_m) for sample in swath]
    norms = [float(sample.sounding_error_norm_m) for sample in swath]

    assert point.max_abs_across_track_error_m == pytest.approx(max(abs(value) for value in across))
    assert point.rms_across_track_error_m == pytest.approx(
        sqrt(sum(value * value for value in across) / n)
    )
    assert point.max_abs_vertical_error_m == pytest.approx(max(abs(value) for value in vertical))
    assert point.rms_vertical_error_m == pytest.approx(
        sqrt(sum(value * value for value in vertical) / n)
    )
    assert point.max_sounding_error_norm_m == pytest.approx(max(norms))
    assert point.rms_sounding_error_norm_m == pytest.approx(
        sqrt(sum(value * value for value in norms) / n)
    )


def test_response_preserves_requested_depth_and_beam_order() -> None:
    depths = (42.0, 38.0, 40.0)
    result = _run(depths)

    assert tuple(
        float(point.compensation_point.interface_depth_m) for point in result.points
    ) == depths
    for point in result.points:
        assert tuple(
            float(sample.configured_across_track_angle_rad)
            for sample in point.swath_curvature.points
        ) == _angles()

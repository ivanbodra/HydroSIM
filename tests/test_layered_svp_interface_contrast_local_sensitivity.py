from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_contrast_local_sensitivity import (
    run_layered_svp_interface_contrast_local_sensitivity,
)
from hydrosim.acquisition.layered_svp_swath_curvature import run_layered_svp_swath_curvature
from hydrosim.acquisition.layered_svp_interface_depth_sweep import move_layered_profile_interface
from hydrosim.acquisition.layered_svp_interface_contrast_map import (
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


def _curvature(depth: float, contrast: float) -> float:
    profile = _profile()
    moved = move_layered_profile_interface(
        profile=profile,
        interface_index=0,
        interface_depth_m=depth,
    )
    processing = set_layered_profile_interface_contrast(
        profile=moved,
        interface_index=0,
        sound_speed_contrast_mps=contrast,
    )
    result = run_layered_svp_swath_curvature(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=profile,
        processing_profile=processing,
        profile_start_depth_m=0.0,
    )
    return float(result.mean_edge_minus_nadir_vertical_error_m)


def test_reference_closes_and_derivatives_match_independent_centered_formulas() -> None:
    h = 5.0
    k = 10.0
    result = run_layered_svp_interface_contrast_local_sensitivity(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        interface_depth_step_m=h,
        sound_speed_contrast_step_mps=k,
        profile_start_depth_m=0.0,
    )

    assert result.reference_curvature_m == pytest.approx(0.0, abs=1e-9)

    c_zm = _curvature(40.0 - h, 40.0)
    c_zp = _curvature(40.0 + h, 40.0)
    c_cm = _curvature(40.0, 40.0 - k)
    c_cp = _curvature(40.0, 40.0 + k)
    c_pp = _curvature(40.0 + h, 40.0 + k)
    c_pm = _curvature(40.0 + h, 40.0 - k)
    c_mp = _curvature(40.0 - h, 40.0 + k)
    c_mm = _curvature(40.0 - h, 40.0 - k)

    expected_depth = (c_zp - c_zm) / (2.0 * h)
    expected_contrast = (c_cp - c_cm) / (2.0 * k)
    expected_mixed = (c_pp - c_pm - c_mp + c_mm) / (4.0 * h * k)

    assert result.depth_sensitivity_m_per_m == pytest.approx(expected_depth, rel=1e-12, abs=1e-12)
    assert result.contrast_sensitivity_m_per_mps == pytest.approx(
        expected_contrast, rel=1e-12, abs=1e-12
    )
    assert result.mixed_derivative_m_per_m_per_mps == pytest.approx(
        expected_mixed, rel=1e-12, abs=1e-12
    )


def test_local_compensation_slope_reduces_small_depth_only_curvature() -> None:
    result = run_layered_svp_interface_contrast_local_sensitivity(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        interface_depth_step_m=2.0,
        sound_speed_contrast_step_mps=4.0,
        profile_start_depth_m=0.0,
    )

    slope = result.contrast_compensation_slope_mps_per_m
    assert slope is not None

    dz = 0.25
    pure_depth = abs(_curvature(40.0 + dz, 40.0))
    compensated = abs(_curvature(40.0 + dz, 40.0 + float(slope) * dz))
    assert compensated < pure_depth


def test_interaction_residual_is_non_negative_and_stencil_is_complete() -> None:
    result = run_layered_svp_interface_contrast_local_sensitivity(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        interface_depth_step_m=5.0,
        sound_speed_contrast_step_mps=10.0,
        profile_start_depth_m=0.0,
    )

    assert result.max_abs_corner_interaction_residual_m >= 0.0
    assert len(result.stencil.points) == 9
    assert tuple(float(v) for v in result.stencil.interface_depths_m) == (35.0, 40.0, 45.0)
    assert tuple(float(v) for v in result.stencil.sound_speed_contrasts_mps) == (30.0, 40.0, 50.0)


def test_rejects_invalid_steps_and_stencil_outside_interface_domain() -> None:
    common = dict(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="interface_depth_step_m must be positive"):
        run_layered_svp_interface_contrast_local_sensitivity(
            **common, interface_depth_step_m=0.0, sound_speed_contrast_step_mps=5.0
        )
    with pytest.raises(ValueError, match="sound_speed_contrast_step_mps must be positive"):
        run_layered_svp_interface_contrast_local_sensitivity(
            **common, interface_depth_step_m=5.0, sound_speed_contrast_step_mps=0.0
        )
    with pytest.raises(ValueError, match="adjacent-layer extent"):
        run_layered_svp_interface_contrast_local_sensitivity(
            **common, interface_depth_step_m=50.0, sound_speed_contrast_step_mps=5.0
        )

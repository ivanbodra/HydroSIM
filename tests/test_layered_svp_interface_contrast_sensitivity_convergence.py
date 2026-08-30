from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_interface_contrast_local_sensitivity import (
    run_layered_svp_interface_contrast_local_sensitivity,
)
from hydrosim.acquisition.layered_svp_interface_contrast_sensitivity_convergence import (
    run_layered_svp_local_sensitivity_convergence_study,
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


def test_each_level_matches_direct_local_sensitivity_evaluation() -> None:
    steps = ((8.0, 16.0), (4.0, 8.0), (2.0, 4.0))
    study = run_layered_svp_local_sensitivity_convergence_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        refinement_steps=steps,
        profile_start_depth_m=0.0,
    )

    for point, (h, k) in zip(study.points, steps):
        direct = run_layered_svp_interface_contrast_local_sensitivity(
            sensor_pose=_pose(),
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angles_rad=_angles(),
            true_profile=_profile(),
            interface_index=0,
            interface_depth_step_m=h,
            sound_speed_contrast_step_mps=k,
            profile_start_depth_m=0.0,
        )
        assert point.sensitivity.depth_sensitivity_m_per_m == pytest.approx(
            direct.depth_sensitivity_m_per_m
        )
        assert point.sensitivity.contrast_sensitivity_m_per_mps == pytest.approx(
            direct.contrast_sensitivity_m_per_mps
        )
        assert point.sensitivity.mixed_derivative_m_per_m_per_mps == pytest.approx(
            direct.mixed_derivative_m_per_m_per_mps
        )
        assert point.sensitivity.contrast_compensation_slope_mps_per_m == pytest.approx(
            direct.contrast_compensation_slope_mps_per_m
        )


def test_changes_are_current_minus_previous_and_first_level_has_none() -> None:
    study = run_layered_svp_local_sensitivity_convergence_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        refinement_steps=((8.0, 16.0), (4.0, 8.0), (2.0, 4.0)),
        profile_start_depth_m=0.0,
    )

    first, second, third = study.points
    assert first.depth_sensitivity_change_m_per_m is None
    assert first.contrast_sensitivity_change_m_per_mps is None
    assert first.mixed_derivative_change_m_per_m_per_mps is None
    assert first.compensation_slope_change_mps_per_m is None

    assert second.depth_sensitivity_change_m_per_m == pytest.approx(
        float(second.sensitivity.depth_sensitivity_m_per_m)
        - float(first.sensitivity.depth_sensitivity_m_per_m)
    )
    assert third.contrast_sensitivity_change_m_per_mps == pytest.approx(
        float(third.sensitivity.contrast_sensitivity_m_per_mps)
        - float(second.sensitivity.contrast_sensitivity_m_per_mps)
    )
    assert third.mixed_derivative_change_m_per_m_per_mps == pytest.approx(
        float(third.sensitivity.mixed_derivative_m_per_m_per_mps)
        - float(second.sensitivity.mixed_derivative_m_per_m_per_mps)
    )


def test_refinement_order_is_preserved_exactly() -> None:
    steps = ((10.0, 20.0), (5.0, 10.0), (2.5, 5.0))
    study = run_layered_svp_local_sensitivity_convergence_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        refinement_steps=steps,
        profile_start_depth_m=0.0,
    )

    observed = tuple(
        (float(point.interface_depth_step_m), float(point.sound_speed_contrast_step_mps))
        for point in study.points
    )
    assert observed == steps
    assert tuple((float(h), float(k)) for h, k in study.refinement_steps) == steps


def test_reference_curvature_remains_closed_at_every_level() -> None:
    study = run_layered_svp_local_sensitivity_convergence_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        refinement_steps=((8.0, 16.0), (4.0, 8.0), (2.0, 4.0)),
        profile_start_depth_m=0.0,
    )

    for point in study.points:
        assert point.sensitivity.reference_curvature_m == pytest.approx(0.0, abs=1e-9)


def test_rejects_insufficient_nonpositive_or_nonrefining_sequences() -> None:
    kwargs = dict(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=_profile(),
        interface_index=0,
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="at least two"):
        run_layered_svp_local_sensitivity_convergence_study(
            **kwargs, refinement_steps=((4.0, 8.0),)
        )
    with pytest.raises(ValueError, match="strictly positive"):
        run_layered_svp_local_sensitivity_convergence_study(
            **kwargs, refinement_steps=((4.0, 8.0), (0.0, 4.0))
        )
    with pytest.raises(ValueError, match="strictly decrease"):
        run_layered_svp_local_sensitivity_convergence_study(
            **kwargs, refinement_steps=((4.0, 8.0), (4.0, 4.0))
        )

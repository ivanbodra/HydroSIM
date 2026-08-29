from math import asin, radians, sin

import pytest

from hydrosim.acquisition import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    SoundSpeedSensorAtTransducer,
    run_layered_sound_speed_error_isolation_matrix,
    run_layered_sound_speed_error_isolation_study,
    run_layered_sound_speed_reference_experiment,
)
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _true_profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=140.0, sound_speed_mps=1550.0),
        )
    )


def _perturbed_profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=140.0, sound_speed_mps=1450.0),
        )
    )


def test_identical_profiles_and_ideal_sensor_close_to_truth() -> None:
    profile = _true_profile()
    result = run_layered_sound_speed_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=radians(30.0),
        true_profile=profile,
        processing_profile=profile,
        profile_start_depth_m=0.0,
    )
    assert result.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)
    assert result.calculated_sounding.sounding.point.is_close(result.truth_bottom_point, atol=1e-9)
    assert len(result.true_ray_path.segments) == 2


def test_transducer_boundary_sensor_perturbation_closes_in_narrow_aligned_reference() -> None:
    profile = _true_profile()
    result = run_layered_sound_speed_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=radians(35.0),
        true_profile=profile,
        processing_profile=profile,
        profile_start_depth_m=0.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=20.0),
    )
    assert result.sound_speed_error_scope == "array_and_zero_thickness_boundary_sensor_perturbation"
    assert "aligned_platform" in result.experiment_assumption
    assert result.principal_plane_array_tilt_rad == pytest.approx(0.0)
    assert result.sensor_measurement.measured_sound_speed_mps == pytest.approx(1520.0)
    assert result.transmit_truth.physical_angle_rad != pytest.approx(radians(35.0))
    assert result.receive_angle_estimate.estimated_angle_rad == pytest.approx(radians(35.0))
    assert result.calculated_sounding.sounding.profile_boundary is not None
    assert result.calculated_sounding.sounding.profile_boundary.sound_speed_mps == pytest.approx(1520.0)
    assert result.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)


def test_principal_plane_array_tilt_breaks_transducer_bias_cancellation_analytically() -> None:
    configured = radians(35.0)
    tilt = radians(8.0)
    c_true = 1500.0
    c_used = 1520.0

    result = run_layered_sound_speed_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=configured,
        true_profile=_true_profile(),
        processing_profile=_true_profile(),
        profile_start_depth_m=0.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=c_used - c_true),
        principal_plane_array_tilt_rad=tilt,
    )

    # Independent principal-plane anchor. Steering/receive mapping occurs in array
    # coordinates; Snell propagation uses the horizontal profile frame.
    expected_physical_array_angle = asin((c_true / c_used) * sin(configured))
    expected_physical_profile_angle = tilt + expected_physical_array_angle
    expected_estimated_profile_angle = tilt + configured
    truth_ray_parameter = sin(expected_physical_profile_angle) / c_true
    processing_boundary_parameter = sin(expected_estimated_profile_angle) / c_used

    assert result.transmit_truth.physical_angle_rad == pytest.approx(expected_physical_array_angle)
    assert result.physical_launch_angle_profile_frame_rad == pytest.approx(
        expected_physical_profile_angle
    )
    assert result.receive_angle_estimate.estimated_angle_rad == pytest.approx(configured)
    assert result.estimated_receive_angle_profile_frame_rad == pytest.approx(
        expected_estimated_profile_angle
    )
    assert processing_boundary_parameter != pytest.approx(truth_ray_parameter, abs=1e-9)
    assert result.sounding_error_norm_m > 0.01


def test_processing_profile_error_produces_sounding_error() -> None:
    result = run_layered_sound_speed_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=radians(30.0),
        true_profile=_true_profile(),
        processing_profile=_perturbed_profile(),
        profile_start_depth_m=0.0,
    )
    assert result.sounding_error_norm_m > 0.1
    assert abs(float(result.sounding_error.y)) > 0.01 or abs(float(result.sounding_error.z)) > 0.01


def test_error_isolation_matrix_separates_transducer_and_profile_perturbations() -> None:
    matrix = run_layered_sound_speed_error_isolation_matrix(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angle_rad=radians(35.0),
        true_profile=_true_profile(),
        perturbed_processing_profile=_perturbed_profile(),
        profile_start_depth_m=0.0,
        transducer_sensor_bias_mps=20.0,
    )

    assert matrix.reference.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)
    # This is a measured result of the deliberately narrow aligned reciprocal case,
    # not a universal assertion about transducer sound-speed errors.
    assert matrix.transducer_only.sounding_error_norm_m == pytest.approx(0.0, abs=1e-9)
    assert matrix.profile_only.sounding_error_norm_m > 0.1
    assert matrix.combined.sounding_error_norm_m > 0.1
    assert matrix.transducer_only.processing_profile == matrix.reference.processing_profile
    assert matrix.profile_only.sound_speed_used_by_sonar.sound_speed_mps == pytest.approx(1500.0)
    assert matrix.combined.sound_speed_used_by_sonar.sound_speed_mps == pytest.approx(1520.0)
    assert matrix.combined.processing_profile == _perturbed_profile()


def test_error_isolation_study_reuses_matrix_over_explicit_angle_bias_grid() -> None:
    angles = (radians(20.0), radians(35.0))
    biases = (-10.0, 20.0)
    study = run_layered_sound_speed_error_isolation_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        true_profile=_true_profile(),
        perturbed_processing_profile=_perturbed_profile(),
        profile_start_depth_m=0.0,
    )

    assert study.configured_across_track_angles_rad == pytest.approx(angles)
    assert study.transducer_sensor_biases_mps == pytest.approx(biases)
    assert study.principal_plane_array_tilts_rad == pytest.approx((0.0,))
    assert len(study.cases) == 4
    assert [case.configured_across_track_angle_rad for case in study.cases] == pytest.approx(
        (angles[0], angles[0], angles[1], angles[1])
    )
    assert [case.transducer_sensor_bias_mps for case in study.cases] == pytest.approx(
        (biases[0], biases[1], biases[0], biases[1])
    )
    assert all(case.principal_plane_array_tilt_rad == pytest.approx(0.0) for case in study.cases)
    assert all(case.matrix.reference.sounding_error_norm_m < 1e-9 for case in study.cases)
    assert all(case.matrix.transducer_only.sounding_error_norm_m < 1e-9 for case in study.cases)
    assert all(case.matrix.profile_only.sounding_error_norm_m > 0.1 for case in study.cases)


def test_error_isolation_study_maps_tilt_as_explicit_symmetry_break_coordinate() -> None:
    tilts = (0.0, radians(8.0))
    study = run_layered_sound_speed_error_isolation_study(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        configured_across_track_angles_rad=(radians(35.0),),
        transducer_sensor_biases_mps=(20.0,),
        principal_plane_array_tilts_rad=tilts,
        true_profile=_true_profile(),
        perturbed_processing_profile=_perturbed_profile(),
        profile_start_depth_m=0.0,
    )

    assert len(study.cases) == 2
    assert [case.principal_plane_array_tilt_rad for case in study.cases] == pytest.approx(tilts)
    aligned, tilted = study.cases
    assert aligned.matrix.reference.sounding_error_norm_m < 1e-9
    assert aligned.matrix.transducer_only.sounding_error_norm_m < 1e-9
    assert tilted.matrix.reference.sounding_error_norm_m < 1e-9
    assert tilted.matrix.transducer_only.sounding_error_norm_m > 0.01


def test_error_isolation_study_rejects_empty_parameter_axes() -> None:
    common = dict(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=100.0),
        true_profile=_true_profile(),
        perturbed_processing_profile=_perturbed_profile(),
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="angles.*must not be empty"):
        run_layered_sound_speed_error_isolation_study(
            configured_across_track_angles_rad=(),
            transducer_sensor_biases_mps=(20.0,),
            **common,
        )
    with pytest.raises(ValueError, match="biases.*must not be empty"):
        run_layered_sound_speed_error_isolation_study(
            configured_across_track_angles_rad=(radians(30.0),),
            transducer_sensor_biases_mps=(),
            **common,
        )
    with pytest.raises(ValueError, match="tilts.*must not be empty"):
        run_layered_sound_speed_error_isolation_study(
            configured_across_track_angles_rad=(radians(30.0),),
            transducer_sensor_biases_mps=(20.0,),
            principal_plane_array_tilts_rad=(),
            **common,
        )


def test_processing_side_states_do_not_expose_truth_profile() -> None:
    profile = _true_profile()
    result = run_layered_sound_speed_reference_experiment(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=80.0),
        configured_across_track_angle_rad=radians(20.0),
        true_profile=profile,
        processing_profile=profile,
        profile_start_depth_m=0.0,
    )
    assert not hasattr(result.sound_speed_used_by_sonar, "true_local_sound_speed_mps")
    assert not hasattr(result.calculated_sounding, "true_profile")
    assert not hasattr(result.calculated_sounding.initial_direction_resolution, "true_local_sound_speed_mps")


def test_reference_experiment_rejects_attitude_to_avoid_mixed_error_sources() -> None:
    pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=radians(1.0), pitch=0.0, yaw=0.0),
        frame="N",
    )
    with pytest.raises(ValueError, match="requires sensor attitude aligned"):
        run_layered_sound_speed_reference_experiment(
            sensor_pose=pose,
            terrain=FlatTerrain(depth=100.0),
            configured_across_track_angle_rad=radians(30.0),
            true_profile=_true_profile(),
            processing_profile=_true_profile(),
            profile_start_depth_m=0.0,
        )

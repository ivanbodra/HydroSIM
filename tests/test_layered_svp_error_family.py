from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.layered_svp_error_family import (
    ControlledProcessingSvpCase,
    run_layered_svp_error_family,
)
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3


def _pose() -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )


def _profile(c_top: float, c_mid: float, c_deep: float, interface_1: float = 40.0, interface_2: float = 100.0) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=interface_1, sound_speed_mps=c_top),
            SoundSpeedLayer(top_depth_m=interface_1, bottom_depth_m=interface_2, sound_speed_mps=c_mid),
            SoundSpeedLayer(top_depth_m=interface_2, bottom_depth_m=200.0, sound_speed_mps=c_deep),
        )
    )


def _angles() -> tuple[float, ...]:
    return tuple(radians(value) for value in (-60, -30, 0, 30, 60))


def test_reference_case_closes_and_perturbed_cases_differ() -> None:
    truth = _profile(1500.0, 1480.0, 1520.0)
    cases = (
        ControlledProcessingSvpCase(
            case_id="reference",
            description="Processing profile equals Truth.",
            classification="reference",
            processing_profile=truth,
        ),
        ControlledProcessingSvpCase(
            case_id="uniform_plus_20",
            description="All finite-thickness layers are 20 m/s faster than Truth.",
            classification="uniform_offset",
            processing_profile=_profile(1520.0, 1500.0, 1540.0),
        ),
        ControlledProcessingSvpCase(
            case_id="middle_layer_fast",
            description="Only the middle layer is faster than Truth.",
            classification="layer_speed_perturbation",
            processing_profile=_profile(1500.0, 1510.0, 1520.0),
        ),
        ControlledProcessingSvpCase(
            case_id="interfaces_deeper",
            description="Both internal interfaces are displaced deeper.",
            classification="interface_displacement",
            processing_profile=_profile(1500.0, 1480.0, 1520.0, 55.0, 120.0),
        ),
    )

    result = run_layered_svp_error_family(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=150.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=truth,
        processing_profile_cases=cases,
        profile_start_depth_m=0.0,
    )

    assert result.case_ids == tuple(case.case_id for case in cases)
    reference = result.cases[0].swath_curvature
    assert reference.mean_edge_minus_nadir_vertical_error_m == pytest.approx(0.0, abs=1e-9)

    perturbed = [
        float(case.swath_curvature.mean_edge_minus_nadir_vertical_error_m)
        for case in result.cases[1:]
    ]
    assert all(abs(value) > 1e-3 for value in perturbed)
    assert len({round(value, 8) for value in perturbed}) > 1


def test_duplicate_profiles_under_different_ids_produce_identical_response() -> None:
    truth = _profile(1500.0, 1480.0, 1520.0)
    processing = _profile(1500.0, 1500.0, 1520.0)
    result = run_layered_svp_error_family(
        sensor_pose=_pose(),
        terrain=FlatTerrain(depth=150.0),
        configured_across_track_angles_rad=_angles(),
        true_profile=truth,
        processing_profile_cases=(
            ControlledProcessingSvpCase(
                case_id="a",
                description="Duplicate profile A.",
                classification="synthetic_profile",
                processing_profile=processing,
            ),
            ControlledProcessingSvpCase(
                case_id="b",
                description="Duplicate profile B.",
                classification="synthetic_profile",
                processing_profile=processing,
            ),
        ),
        profile_start_depth_m=0.0,
    )

    assert result.cases[0].swath_curvature == result.cases[1].swath_curvature


def test_case_order_is_preserved() -> None:
    truth = _profile(1500.0, 1480.0, 1520.0)
    ids = ("third", "first", "second")
    cases = tuple(
        ControlledProcessingSvpCase(
            case_id=case_id,
            description=f"Case {case_id}.",
            classification="reference",
            processing_profile=truth,
        )
        for case_id in ids
    )
    result = run_layered_svp_error_family(
        sensor_pose=_pose(), terrain=FlatTerrain(depth=150.0),
        configured_across_track_angles_rad=_angles(), true_profile=truth,
        processing_profile_cases=cases, profile_start_depth_m=0.0,
    )
    assert result.case_ids == ids


def test_rejects_empty_family_and_duplicate_ids() -> None:
    truth = _profile(1500.0, 1480.0, 1520.0)
    common = dict(
        sensor_pose=_pose(), terrain=FlatTerrain(depth=150.0),
        configured_across_track_angles_rad=_angles(), true_profile=truth,
        profile_start_depth_m=0.0,
    )
    with pytest.raises(ValueError, match="must not be empty"):
        run_layered_svp_error_family(processing_profile_cases=(), **common)

    duplicate = ControlledProcessingSvpCase(
        case_id="duplicate", description="Duplicate ID.", classification="reference",
        processing_profile=truth,
    )
    with pytest.raises(ValueError, match="unique case_id"):
        run_layered_svp_error_family(processing_profile_cases=(duplicate, duplicate), **common)

"""Golden-value regression tests for the HydroSIM v0.1 geometry core.

The expected numbers live in the scientific registry and are analytically
independent of the implementation under test.
"""

from pathlib import Path

import pytest
import yaml

from hydrosim.geometry import (
    Attitude,
    BeamDefinition,
    BeamRay,
    FlatTerrain,
    PlaneTerrain,
    Pose,
    Vector3,
    apply_lever_arm,
    compare_true_and_configured_sounding,
)


GOLDEN_PATH = (
    Path(__file__).resolve().parents[2]
    / "scientific_registry"
    / "validation"
    / "golden_values"
    / "geometry_v0_1.yaml"
)


def _load_cases():
    with GOLDEN_PATH.open("r", encoding="utf-8") as stream:
        document = yaml.safe_load(stream)
    return document["registry"], {case["id"]: case for case in document["cases"]}


def _assert_vector(actual: Vector3, expected, tolerance: float):
    assert actual.x == pytest.approx(expected[0], abs=tolerance)
    assert actual.y == pytest.approx(expected[1], abs=tolerance)
    assert actual.z == pytest.approx(expected[2], abs=tolerance)


def test_nadir_flat_bottom_golden_value():
    registry, cases = _load_cases()
    case = cases["flat_bottom_nadir_30m"]
    tol = registry["default_tolerance"]
    result = FlatTerrain(case["input"]["terrain_depth"]).intersect_ray(
        Vector3(x=0, y=0, z=0), Vector3(x=0, y=0, z=1)
    )
    assert result.valid
    _assert_vector(result.point, case["expected"]["point"], tol)
    assert result.slant_range == pytest.approx(case["expected"]["slant_range"], abs=tol)


def test_port_45_flat_bottom_golden_value():
    registry, cases = _load_cases()
    case = cases["flat_bottom_port_45deg_30m"]
    tol = registry["default_tolerance"]
    beam = BeamRay(
        definition=BeamDefinition(index=0, angle=0.7853981633974483, role="rx"),
        origin_sensor_frame=Vector3(x=0, y=0, z=0),
        direction_array_frame=Vector3(x=0, y=-0.7071067811865476, z=0.7071067811865476),
        direction_sensor_frame=Vector3(x=0, y=-0.7071067811865476, z=0.7071067811865476),
    )
    _assert_vector(beam.direction_sensor_frame, case["expected"]["direction"], tol)
    result = FlatTerrain(case["input"]["terrain_depth"]).intersect_ray(
        beam.origin_sensor_frame, beam.direction_sensor_frame
    )
    _assert_vector(result.point, case["expected"]["point"], tol)
    assert result.slant_range == pytest.approx(case["expected"]["slant_range"], abs=tol)


def test_known_plane_intersection_golden_value():
    registry, cases = _load_cases()
    case = cases["plane_intersection_known"]
    tol = registry["default_tolerance"]
    inp = case["input"]
    terrain = PlaneTerrain(
        point=Vector3(x=inp["plane_point"][0], y=inp["plane_point"][1], z=inp["plane_point"][2]),
        normal=Vector3(x=inp["plane_normal"][0], y=inp["plane_normal"][1], z=inp["plane_normal"][2]),
    )
    result = terrain.intersect_ray(
        Vector3(x=inp["origin"][0], y=inp["origin"][1], z=inp["origin"][2]),
        Vector3(x=inp["direction"][0], y=inp["direction"][1], z=inp["direction"][2]),
    )
    _assert_vector(result.point, case["expected"]["point"], tol)
    assert result.slant_range == pytest.approx(case["expected"]["slant_range"], abs=tol)


def test_lever_arm_yaw_90_golden_value():
    registry, cases = _load_cases()
    case = cases["lever_arm_yaw_90"]
    tol = registry["default_tolerance"]
    inp = case["input"]
    pose = Pose(
        position=Vector3(x=inp["vessel_position"][0], y=inp["vessel_position"][1], z=inp["vessel_position"][2]),
        attitude=Attitude.from_degrees(roll=0, pitch=0, yaw=90),
        frame="N",
    )
    result = apply_lever_arm(pose, Vector3(x=2, y=0, z=0))
    _assert_vector(result, case["expected"]["sensor_position"], tol)


def test_roll_offset_sounding_golden_value():
    registry, cases = _load_cases()
    case = cases["roll_offset_nadir_30m_half_degree"]
    tol = registry["default_tolerance"]
    beam = BeamRay(
        definition=BeamDefinition(index=0, angle=0.0, role="rx"),
        origin_sensor_frame=Vector3(x=0, y=0, z=0),
        direction_array_frame=Vector3(x=0, y=0, z=1),
        direction_sensor_frame=Vector3(x=0, y=0, z=1),
    )
    comparison = compare_true_and_configured_sounding(
        vessel_truth_pose=Pose(
            position=Vector3(x=0, y=0, z=0),
            attitude=Attitude.from_degrees(roll=0, pitch=0, yaw=0),
            frame="N",
        ),
        lever_arm_vrp_to_sensor=Vector3(x=0, y=0, z=0),
        true_sensor_alignment=Attitude.from_degrees(roll=0.5, pitch=0, yaw=0),
        configured_sensor_alignment=Attitude.from_degrees(roll=0, pitch=0, yaw=0),
        beam=beam,
        terrain=FlatTerrain(case["input"]["terrain_depth"]),
    )
    expected = case["expected"]
    _assert_vector(comparison.true.point, expected["true_point"], tol)
    assert comparison.true.slant_range == pytest.approx(expected["measured_slant_range"], abs=tol)
    _assert_vector(comparison.configured.point, expected["configured_point"], tol)
    _assert_vector(comparison.error_vector, expected["error_vector"], tol)
    assert comparison.horizontal_error == pytest.approx(expected["horizontal_error"], abs=tol)
    assert comparison.vertical_error == pytest.approx(expected["vertical_error"], abs=tol)
    assert comparison.error_magnitude == pytest.approx(expected["error_magnitude"], abs=tol)

"""Second-tier RISC validation against HydroSIM physical sounding geometry.

Tier 1 tests reproduce the published Maingot (2019) equations directly. These
Tier 2 tests verify that selected published RISC parameter semantics map into the
HydroSIM Truth/Configured sounding pipeline with the expected physical effect.

The tests intentionally begin with the least ambiguous parameters:

- Delta Lx;
- Delta Ly;
- Delta t.

They do not validate the RISC optimizer or field performance.
"""

from __future__ import annotations

from math import cos, isclose, sin, sqrt, tan

import pytest

from hydrosim.geometry import (
    Attitude,
    BeamDefinition,
    BeamRay,
    FlatTerrain,
    Pose,
    Vector3,
    compare_true_and_configured_state_sounding,
)
from hydrosim.integration.risc_maingot import (
    apply_maingot_motion_errors,
    configured_lever_arm_from_maingot_error,
    hydrosim_lever_arm_error_from_maingot,
)


ABS_TOL = 1e-10


def _nadir_beam() -> BeamRay:
    return BeamRay(
        definition=BeamDefinition(
            index=0,
            across_track_angle=0.0,
            role="rx",
            array_name="risc_crosswalk",
        ),
        origin_array_frame=Vector3(x=0.0, y=0.0, z=0.0),
        direction_array_frame=Vector3(x=0.0, y=0.0, z=1.0),
        direction_sensor_frame=Vector3(x=0.0, y=0.0, z=1.0),
    )


def _zero_alignment() -> Attitude:
    return Attitude(roll=0.0, pitch=0.0, yaw=0.0)


def _static_pose(*, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> Pose:
    return Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude(roll=roll, pitch=pitch, yaw=yaw),
        frame="N",
    )


def test_maingot_delta_lx_maps_to_hydrosim_origin_error() -> None:
    """Positive Maingot Delta Lx means a negative HydroSIM configured-minus-truth error."""

    true_lever = Vector3(x=2.0, y=-1.0, z=0.0)
    delta_lx_maingot = 0.25
    configured_x = configured_lever_arm_from_maingot_error(
        true_lever.x, delta_lx_maingot
    )
    configured_lever = Vector3(x=configured_x, y=true_lever.y, z=true_lever.z)

    comparison = compare_true_and_configured_state_sounding(
        vessel_truth_pose=_static_pose(),
        vessel_configured_pose=_static_pose(),
        true_lever_arm_vrp_to_sensor=true_lever,
        configured_lever_arm_vrp_to_sensor=configured_lever,
        true_sensor_alignment=_zero_alignment(),
        configured_sensor_alignment=_zero_alignment(),
        beam=_nadir_beam(),
        terrain=FlatTerrain(depth=30.0),
    )

    expected_hydrosim_error = hydrosim_lever_arm_error_from_maingot(
        delta_lx_maingot
    )
    assert expected_hydrosim_error == pytest.approx(-0.25, abs=ABS_TOL)
    assert comparison.error_vector.x == pytest.approx(
        expected_hydrosim_error, abs=ABS_TOL
    )
    assert comparison.error_vector.y == pytest.approx(0.0, abs=ABS_TOL)
    assert comparison.error_vector.z == pytest.approx(0.0, abs=ABS_TOL)
    assert comparison.true.slant_range == pytest.approx(
        comparison.configured.slant_range, abs=ABS_TOL
    )


def test_maingot_delta_ly_maps_to_hydrosim_origin_error() -> None:
    """The Maingot/HydroSIM lever-arm sign crosswalk applies componentwise to Y."""

    true_lever = Vector3(x=2.0, y=-1.4, z=0.0)
    delta_ly_maingot = -0.20
    configured_y = configured_lever_arm_from_maingot_error(
        true_lever.y, delta_ly_maingot
    )
    configured_lever = Vector3(x=true_lever.x, y=configured_y, z=true_lever.z)

    comparison = compare_true_and_configured_state_sounding(
        vessel_truth_pose=_static_pose(),
        vessel_configured_pose=_static_pose(),
        true_lever_arm_vrp_to_sensor=true_lever,
        configured_lever_arm_vrp_to_sensor=configured_lever,
        true_sensor_alignment=_zero_alignment(),
        configured_sensor_alignment=_zero_alignment(),
        beam=_nadir_beam(),
        terrain=FlatTerrain(depth=30.0),
    )

    expected_hydrosim_error = hydrosim_lever_arm_error_from_maingot(
        delta_ly_maingot
    )
    assert expected_hydrosim_error == pytest.approx(0.20, abs=ABS_TOL)
    assert comparison.error_vector.x == pytest.approx(0.0, abs=ABS_TOL)
    assert comparison.error_vector.y == pytest.approx(
        expected_hydrosim_error, abs=ABS_TOL
    )
    assert comparison.error_vector.z == pytest.approx(0.0, abs=ABS_TOL)


def test_maingot_positive_latency_maps_to_older_roll_in_physical_sounding() -> None:
    """Positive Delta t must use an older roll state and the same measured range.

    The signal is deliberately affine so Maingot's first-order latency equation is
    exact. A flat bottom and nadir sensor-frame beam provide an analytical physical
    check independent of terrain re-intersection.
    """

    true_roll = 0.10
    roll_rate = 0.50
    latency_s = 0.04
    depth = 30.0

    adjusted = apply_maingot_motion_errors(
        roll_rad=true_roll,
        pitch_rad=0.0,
        heading_rad=0.0,
        heave_m=0.0,
        roll_rate_rad_s=roll_rate,
        pitch_rate_rad_s=0.0,
        heading_rate_rad_s=0.0,
        heave_rate_m_s=0.0,
        latency_s=latency_s,
        scale_factor=1.0,
        z_axis_misalignment_rad=0.0,
    )

    expected_older_roll = true_roll - roll_rate * latency_s
    assert isclose(adjusted.roll_rad, expected_older_roll, abs_tol=ABS_TOL)
    assert adjusted.roll_rad == pytest.approx(0.08, abs=ABS_TOL)

    comparison = compare_true_and_configured_state_sounding(
        vessel_truth_pose=_static_pose(roll=true_roll),
        vessel_configured_pose=_static_pose(roll=adjusted.roll_rad),
        true_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        configured_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        true_sensor_alignment=_zero_alignment(),
        configured_sensor_alignment=_zero_alignment(),
        beam=_nadir_beam(),
        terrain=FlatTerrain(depth=depth),
    )

    measured_range = depth / cos(true_roll)
    expected_true_y = -depth * tan(true_roll)
    expected_configured_y = -measured_range * sin(expected_older_roll)
    expected_configured_z = measured_range * cos(expected_older_roll)

    assert comparison.true.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.configured.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.true.point.y == pytest.approx(expected_true_y, abs=ABS_TOL)
    assert comparison.true.point.z == pytest.approx(depth, abs=ABS_TOL)
    assert comparison.configured.point.y == pytest.approx(
        expected_configured_y, abs=ABS_TOL
    )
    assert comparison.configured.point.z == pytest.approx(
        expected_configured_z, abs=ABS_TOL
    )
    assert comparison.error_vector.y == pytest.approx(
        expected_configured_y - expected_true_y, abs=ABS_TOL
    )
    assert comparison.error_vector.z == pytest.approx(
        expected_configured_z - depth, abs=ABS_TOL
    )
    assert comparison.error_magnitude == pytest.approx(
        sqrt(
            (expected_configured_y - expected_true_y) ** 2
            + (expected_configured_z - depth) ** 2
        ),
        abs=ABS_TOL,
    )

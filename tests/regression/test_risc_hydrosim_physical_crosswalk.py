"""Second-tier RISC validation against HydroSIM physical sounding geometry.

Tier 1 tests reproduce the published Maingot (2019) equations directly. These
Tier 2 tests verify that selected published RISC parameter semantics map into the
HydroSIM Truth/Configured sounding pipeline with the expected physical effect.

The current physical cross-validation covers all six published RISC parameters:

- Delta Lx;
- Delta Ly;
- Delta t;
- Delta rho;
- Delta kappa;
- Delta SSS.

The Delta SSS case is deliberately limited to the published simple steering
relation followed by straight-ray propagation in a homogeneous medium. It is not
a substitute for the later coupled Tx/Rx motion-compensation and water-column
ray-tracing model.

These tests do not validate the RISC optimizer or field performance.
"""

from __future__ import annotations

from math import asin, cos, isclose, radians, sin, sqrt, tan

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
    hydrosim_sss_error_from_maingot,
    maingot_surface_sound_speed,
    maingot_surface_sound_speed_steering_angle,
)


ABS_TOL = 1e-10


def _beam_at_across_track_angle(angle_rad: float, *, index: int = 0) -> BeamRay:
    """Create an ideal RX beam using HydroSIM's +Port across-track convention."""

    direction = Vector3(
        x=0.0,
        y=-sin(angle_rad),
        z=cos(angle_rad),
    )
    return BeamRay(
        definition=BeamDefinition(
            index=index,
            across_track_angle=angle_rad,
            role="rx",
            array_name="risc_crosswalk",
        ),
        origin_array_frame=Vector3(x=0.0, y=0.0, z=0.0),
        direction_array_frame=direction,
        direction_sensor_frame=direction,
    )


def _nadir_beam() -> BeamRay:
    return _beam_at_across_track_angle(0.0)


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


def test_maingot_motion_scale_maps_to_scaled_roll_physical_sounding() -> None:
    """Delta rho is the total multiplicative motion scale, with 1.0 as identity."""

    true_roll = 0.10
    scale_factor = 1.02
    depth = 30.0

    adjusted = apply_maingot_motion_errors(
        roll_rad=true_roll,
        pitch_rad=0.0,
        heading_rad=0.0,
        heave_m=0.0,
        roll_rate_rad_s=0.0,
        pitch_rate_rad_s=0.0,
        heading_rate_rad_s=0.0,
        heave_rate_m_s=0.0,
        latency_s=0.0,
        scale_factor=scale_factor,
        z_axis_misalignment_rad=0.0,
    )

    expected_configured_roll = scale_factor * true_roll
    assert adjusted.roll_rad == pytest.approx(expected_configured_roll, abs=ABS_TOL)

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
    expected_configured_y = -measured_range * sin(expected_configured_roll)
    expected_configured_z = measured_range * cos(expected_configured_roll)

    assert comparison.true.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.configured.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.true.point.y == pytest.approx(expected_true_y, abs=ABS_TOL)
    assert comparison.configured.point.y == pytest.approx(expected_configured_y, abs=ABS_TOL)
    assert comparison.configured.point.z == pytest.approx(expected_configured_z, abs=ABS_TOL)
    assert comparison.error_vector.y < 0.0
    assert comparison.error_vector.z < 0.0


def test_maingot_positive_delta_kappa_cross_talk_has_expected_physical_direction() -> None:
    """For pure +pitch, positive Maingot Delta kappa induces +roll cross-talk.

    This test fixes the observable sign consequence of the published equation in
    HydroSIM coordinates. It intentionally does not yet relabel Delta kappa as a
    generic sonar yaw installation error: it is the INS-to-MB motion-axis Z-axis
    misalignment term of the RISC model.
    """

    true_pitch = 0.12
    delta_kappa = 0.01
    depth = 30.0

    adjusted = apply_maingot_motion_errors(
        roll_rad=0.0,
        pitch_rad=true_pitch,
        heading_rad=0.0,
        heave_m=0.0,
        roll_rate_rad_s=0.0,
        pitch_rate_rad_s=0.0,
        heading_rate_rad_s=0.0,
        heave_rate_m_s=0.0,
        latency_s=0.0,
        scale_factor=1.0,
        z_axis_misalignment_rad=delta_kappa,
    )

    expected_roll = asin(sin(delta_kappa) * sin(true_pitch))
    expected_pitch = asin(cos(delta_kappa) * sin(true_pitch))

    assert adjusted.roll_rad == pytest.approx(expected_roll, abs=ABS_TOL)
    assert adjusted.pitch_rad == pytest.approx(expected_pitch, abs=ABS_TOL)
    assert adjusted.roll_rad > 0.0
    assert adjusted.pitch_rad < true_pitch

    comparison = compare_true_and_configured_state_sounding(
        vessel_truth_pose=_static_pose(pitch=true_pitch),
        vessel_configured_pose=_static_pose(
            roll=adjusted.roll_rad,
            pitch=adjusted.pitch_rad,
        ),
        true_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        configured_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        true_sensor_alignment=_zero_alignment(),
        configured_sensor_alignment=_zero_alignment(),
        beam=_nadir_beam(),
        terrain=FlatTerrain(depth=depth),
    )

    measured_range = depth / cos(true_pitch)
    expected_configured_x = (
        measured_range * sin(expected_pitch) * cos(expected_roll)
    )
    expected_configured_y = -measured_range * sin(expected_roll)
    expected_configured_z = (
        measured_range * cos(expected_pitch) * cos(expected_roll)
    )

    assert comparison.true.point.x == pytest.approx(depth * tan(true_pitch), abs=ABS_TOL)
    assert comparison.true.point.y == pytest.approx(0.0, abs=ABS_TOL)
    assert comparison.true.point.z == pytest.approx(depth, abs=ABS_TOL)
    assert comparison.configured.point.x == pytest.approx(expected_configured_x, abs=ABS_TOL)
    assert comparison.configured.point.y == pytest.approx(expected_configured_y, abs=ABS_TOL)
    assert comparison.configured.point.z == pytest.approx(expected_configured_z, abs=ABS_TOL)

    # HydroSIM +roll is starboard-down; a +roll rotation of a +Z beam points it
    # toward Port (-Y). This makes the cross-talk sign observable in geometry.
    assert comparison.configured.point.y < 0.0
    assert comparison.error_vector.y < 0.0


def test_maingot_delta_sss_maps_through_steering_then_straight_propagation() -> None:
    """Delta SSS changes steering before propagation; it is not a generic pose error.

    The test uses a homogeneous medium and straight propagation so only the
    published simple SSS steering relation is under examination. The Truth echo
    fixes the measured slant range; the Configured branch reuses that range with
    the SSS-adjusted steering direction.
    """

    true_sss = 1500.0
    delta_sss_maingot = 2.0
    true_angle = radians(30.0)
    depth = 30.0

    configured_sss = maingot_surface_sound_speed(true_sss, delta_sss_maingot)
    hydrosim_sss_error = hydrosim_sss_error_from_maingot(delta_sss_maingot)
    configured_angle = maingot_surface_sound_speed_steering_angle(
        true_angle,
        true_sss,
        delta_sss_maingot,
    )

    assert configured_sss == pytest.approx(1498.0, abs=ABS_TOL)
    assert hydrosim_sss_error == pytest.approx(-2.0, abs=ABS_TOL)
    assert configured_angle < true_angle

    true_beam = _beam_at_across_track_angle(true_angle)
    configured_beam = _beam_at_across_track_angle(configured_angle)

    comparison = compare_true_and_configured_state_sounding(
        vessel_truth_pose=_static_pose(),
        vessel_configured_pose=_static_pose(),
        true_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        configured_lever_arm_vrp_to_sensor=Vector3(x=0.0, y=0.0, z=0.0),
        true_sensor_alignment=_zero_alignment(),
        configured_sensor_alignment=_zero_alignment(),
        beam=true_beam,
        configured_beam=configured_beam,
        terrain=FlatTerrain(depth=depth),
    )

    measured_range = depth / cos(true_angle)
    expected_true_y = -depth * tan(true_angle)
    expected_configured_y = -measured_range * sin(configured_angle)
    expected_configured_z = measured_range * cos(configured_angle)

    assert comparison.true.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.configured.slant_range == pytest.approx(measured_range, abs=ABS_TOL)
    assert comparison.true.point.y == pytest.approx(expected_true_y, abs=ABS_TOL)
    assert comparison.true.point.z == pytest.approx(depth, abs=ABS_TOL)
    assert comparison.configured.point.y == pytest.approx(expected_configured_y, abs=ABS_TOL)
    assert comparison.configured.point.z == pytest.approx(expected_configured_z, abs=ABS_TOL)

    # Positive Maingot Delta SSS means configured SSS is too low. In the simple
    # steering relation this reduces a positive Port steering angle. The
    # reconstructed point therefore moves toward nadir and becomes deeper when
    # the original measured slant range is preserved.
    assert comparison.configured.point.y > comparison.true.point.y
    assert comparison.error_vector.y > 0.0
    assert comparison.error_vector.z > 0.0

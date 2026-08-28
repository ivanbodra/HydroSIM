"""Literature-derived analytical tests for Maingot (2019) RISC parameterization.

These tests are an executable scientific specification. They verify the published
Section 3.1 equations and HydroSIM sign/parameter crosswalks against the reference
implementation in ``hydrosim.integration.risc_maingot``.

Passing these tests does *not* validate field performance of RISC.
"""

from __future__ import annotations

from math import asin, cos, isclose, sin

from hydrosim.integration.risc_maingot import (
    apply_maingot_motion_errors,
    configured_lever_arm_from_maingot_error,
    hydrosim_lever_arm_error_from_maingot,
    hydrosim_sss_error_from_maingot,
    maingot_latency_adjusted,
    maingot_surface_sound_speed,
    maingot_surface_sound_speed_steering_angle,
)


ABS_TOL = 1e-12


def test_zero_error_identity() -> None:
    state = apply_maingot_motion_errors(
        roll_rad=0.10,
        pitch_rad=-0.05,
        heading_rad=0.30,
        heave_m=0.40,
        roll_rate_rad_s=0.02,
        pitch_rate_rad_s=-0.01,
        heading_rate_rad_s=0.03,
        heave_rate_m_s=0.10,
        latency_s=0.0,
        scale_factor=1.0,
        z_axis_misalignment_rad=0.0,
    )

    assert isclose(state.roll_rad, 0.10, abs_tol=ABS_TOL)
    assert isclose(state.pitch_rad, -0.05, abs_tol=ABS_TOL)
    assert isclose(state.heading_rad, 0.30, abs_tol=ABS_TOL)
    assert isclose(state.heave_m, 0.40, abs_tol=ABS_TOL)


def test_positive_latency_uses_older_affine_state() -> None:
    state_at_t = 0.20
    state_rate = 0.50
    latency_s = 0.04

    maingot = maingot_latency_adjusted(state_at_t, state_rate, latency_s)
    exact_affine_state_at_t_minus_dt = state_at_t - state_rate * latency_s

    assert isclose(maingot, 0.18, abs_tol=ABS_TOL)
    assert isclose(maingot, exact_affine_state_at_t_minus_dt, abs_tol=ABS_TOL)


def test_motion_scale_factor_102_percent() -> None:
    state = apply_maingot_motion_errors(
        roll_rad=0.10,
        pitch_rad=0.0,
        heading_rad=0.0,
        heave_m=0.0,
        roll_rate_rad_s=0.0,
        pitch_rate_rad_s=0.0,
        heading_rate_rad_s=0.0,
        heave_rate_m_s=0.0,
        scale_factor=1.02,
    )

    assert isclose(state.roll_rad, 0.102, abs_tol=ABS_TOL)
    assert isclose(1.02 - 1.0, 0.02, abs_tol=ABS_TOL)


def test_z_axis_misalignment_cross_talk_matches_published_equation() -> None:
    roll = 0.10
    pitch = 0.20
    dk = 0.01

    state = apply_maingot_motion_errors(
        roll_rad=roll,
        pitch_rad=pitch,
        heading_rad=0.0,
        heave_m=0.0,
        roll_rate_rad_s=0.0,
        pitch_rate_rad_s=0.0,
        heading_rate_rad_s=0.0,
        heave_rate_m_s=0.0,
        z_axis_misalignment_rad=dk,
    )

    expected_roll = asin(cos(dk) * sin(roll) + sin(dk) * sin(pitch))
    expected_pitch = asin(cos(dk) * sin(pitch) - sin(dk) * sin(roll))

    assert isclose(state.roll_rad, expected_roll, abs_tol=ABS_TOL)
    assert isclose(state.pitch_rad, expected_pitch, abs_tol=ABS_TOL)
    assert state.roll_rad > roll
    assert state.pitch_rad < pitch


def test_x_lever_arm_sign_crosswalk() -> None:
    true_lever_arm_m = 2.0
    delta_l_maingot_m = 0.25

    configured = configured_lever_arm_from_maingot_error(
        true_lever_arm_m, delta_l_maingot_m
    )
    hydrosim_error = hydrosim_lever_arm_error_from_maingot(delta_l_maingot_m)

    assert isclose(configured, 1.75, abs_tol=ABS_TOL)
    assert isclose(hydrosim_error, -0.25, abs_tol=ABS_TOL)
    assert isclose(configured - true_lever_arm_m, hydrosim_error, abs_tol=ABS_TOL)


def test_y_lever_arm_uses_same_componentwise_sign_crosswalk() -> None:
    true_y_m = -1.4
    delta_y_maingot_m = -0.2

    configured_y = configured_lever_arm_from_maingot_error(
        true_y_m, delta_y_maingot_m
    )
    hydrosim_error_y = hydrosim_lever_arm_error_from_maingot(delta_y_maingot_m)

    assert isclose(configured_y, -1.2, abs_tol=ABS_TOL)
    assert isclose(hydrosim_error_y, 0.2, abs_tol=ABS_TOL)
    assert isclose(configured_y - true_y_m, hydrosim_error_y, abs_tol=ABS_TOL)


def test_surface_sound_speed_sign_crosswalk_and_steering() -> None:
    true_sss_m_s = 1500.0
    delta_sss_maingot_m_s = 2.0
    steering_angle_rad = 0.5235987755982988  # 30 degrees

    configured_sss = maingot_surface_sound_speed(
        true_sss_m_s, delta_sss_maingot_m_s
    )
    hydrosim_error = hydrosim_sss_error_from_maingot(delta_sss_maingot_m_s)
    adjusted_angle = maingot_surface_sound_speed_steering_angle(
        steering_angle_rad,
        true_sss_m_s,
        delta_sss_maingot_m_s,
    )

    expected_angle = asin((1498.0 / 1500.0) * sin(steering_angle_rad))

    assert isclose(configured_sss, 1498.0, abs_tol=ABS_TOL)
    assert isclose(hydrosim_error, -2.0, abs_tol=ABS_TOL)
    assert isclose(configured_sss - true_sss_m_s, hydrosim_error, abs_tol=ABS_TOL)
    assert isclose(adjusted_angle, expected_angle, abs_tol=ABS_TOL)
    assert adjusted_angle < steering_angle_rad


def test_scale_latency_and_z_axis_error_are_coupled_in_published_form() -> None:
    """Guard against incorrectly treating the attitude terms as additive residuals."""

    state = apply_maingot_motion_errors(
        roll_rad=0.15,
        pitch_rad=-0.08,
        heading_rad=0.30,
        heave_m=0.50,
        roll_rate_rad_s=0.04,
        pitch_rate_rad_s=-0.03,
        heading_rate_rad_s=0.02,
        heave_rate_m_s=0.10,
        latency_s=0.02,
        scale_factor=1.01,
        z_axis_misalignment_rad=0.005,
    )

    # Independently evaluate the literal published nesting.
    roll_lagged_scaled = 1.01 * (0.15 - 0.04 * 0.02)
    pitch_lagged_scaled = 1.01 * (-0.08 - (-0.03) * 0.02)
    expected_roll = asin(
        cos(0.005) * sin(roll_lagged_scaled)
        + sin(0.005) * sin(pitch_lagged_scaled)
    )
    expected_pitch = asin(
        cos(0.005) * sin(pitch_lagged_scaled)
        - sin(0.005) * sin(roll_lagged_scaled)
    )
    expected_heading = 0.30 - 0.02 * 0.02
    expected_heave = 1.01 * (0.50 - 0.10 * 0.02)

    assert isclose(state.roll_rad, expected_roll, abs_tol=ABS_TOL)
    assert isclose(state.pitch_rad, expected_pitch, abs_tol=ABS_TOL)
    assert isclose(state.heading_rad, expected_heading, abs_tol=ABS_TOL)
    assert isclose(state.heave_m, expected_heave, abs_tol=ABS_TOL)

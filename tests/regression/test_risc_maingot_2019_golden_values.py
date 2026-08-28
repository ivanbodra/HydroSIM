"""Literature-derived analytical tests for Maingot (2019) RISC parameterization.

These tests are an executable scientific specification. They verify the published
Section 3.1 equations and HydroSIM sign/parameter crosswalks before production RISC
code exists. Passing these tests does *not* validate field performance of RISC.
"""

from __future__ import annotations

from math import asin, cos, isclose, sin


ABS_TOL = 1e-12


def _maingot_latency_adjusted(value: float, rate: float, latency_s: float) -> float:
    """Maingot first-order latency form: x* = x - x_dot * Delta_t."""
    return value - rate * latency_s


def _maingot_adjusted_roll_pitch(
    roll_rad: float,
    pitch_rad: float,
    roll_rate_rad_s: float,
    pitch_rate_rad_s: float,
    latency_s: float,
    scale_factor: float,
    z_axis_misalignment_rad: float,
) -> tuple[float, float]:
    """Published Maingot Section 3.1 roll/pitch adjustment."""
    roll_lagged = roll_rad - roll_rate_rad_s * latency_s
    pitch_lagged = pitch_rad - pitch_rate_rad_s * latency_s
    scaled_roll = scale_factor * roll_lagged
    scaled_pitch = scale_factor * pitch_lagged
    dk = z_axis_misalignment_rad

    adjusted_roll = asin(cos(dk) * sin(scaled_roll) + sin(dk) * sin(scaled_pitch))
    adjusted_pitch = asin(cos(dk) * sin(scaled_pitch) - sin(dk) * sin(scaled_roll))
    return adjusted_roll, adjusted_pitch


def _maingot_adjusted_heading(
    heading_rad: float, heading_rate_rad_s: float, latency_s: float
) -> float:
    """Published Maingot Section 3.1 heading latency adjustment."""
    return heading_rad - heading_rate_rad_s * latency_s


def _maingot_adjusted_heave(
    heave_m: float, heave_rate_m_s: float, latency_s: float, scale_factor: float
) -> float:
    """Published Maingot Section 3.1 heave adjustment, without asserting heave sign."""
    return scale_factor * (heave_m - heave_rate_m_s * latency_s)


def _maingot_configured_lever_arm(true_lever_arm: float, delta_l_maingot: float) -> float:
    """Maingot Section 3.1 uses L_configured = L_true - Delta_L_M."""
    return true_lever_arm - delta_l_maingot


def _hydrosim_lever_arm_error_from_maingot(delta_l_maingot: float) -> float:
    """HydroSIM delta_L = L_configured - L_true."""
    return -delta_l_maingot


def _maingot_adjusted_steering_angle(
    steering_angle_rad: float, true_sss_m_s: float, delta_sss_maingot_m_s: float
) -> float:
    """Published simple SSS steering relation from Maingot Section 3.1."""
    ratio = (true_sss_m_s - delta_sss_maingot_m_s) / true_sss_m_s
    return asin(ratio * sin(steering_angle_rad))


def _hydrosim_sss_error_from_maingot(delta_sss_maingot_m_s: float) -> float:
    """HydroSIM delta_c = c_configured - c_true."""
    return -delta_sss_maingot_m_s


def test_zero_error_identity() -> None:
    roll = 0.10
    pitch = -0.05
    heading = 0.30
    heave = 0.40

    adjusted_roll, adjusted_pitch = _maingot_adjusted_roll_pitch(
        roll_rad=roll,
        pitch_rad=pitch,
        roll_rate_rad_s=0.02,
        pitch_rate_rad_s=-0.01,
        latency_s=0.0,
        scale_factor=1.0,
        z_axis_misalignment_rad=0.0,
    )
    adjusted_heading = _maingot_adjusted_heading(heading, 0.03, 0.0)
    adjusted_heave = _maingot_adjusted_heave(heave, 0.10, 0.0, 1.0)

    assert isclose(adjusted_roll, roll, abs_tol=ABS_TOL)
    assert isclose(adjusted_pitch, pitch, abs_tol=ABS_TOL)
    assert isclose(adjusted_heading, heading, abs_tol=ABS_TOL)
    assert isclose(adjusted_heave, heave, abs_tol=ABS_TOL)


def test_positive_latency_uses_older_affine_state() -> None:
    state_at_t = 0.20
    state_rate = 0.50
    latency_s = 0.04

    maingot = _maingot_latency_adjusted(state_at_t, state_rate, latency_s)
    exact_affine_state_at_t_minus_dt = state_at_t - state_rate * latency_s

    assert isclose(maingot, 0.18, abs_tol=ABS_TOL)
    assert isclose(maingot, exact_affine_state_at_t_minus_dt, abs_tol=ABS_TOL)


def test_motion_scale_factor_102_percent() -> None:
    state = 0.10
    scale_factor = 1.02

    scaled = scale_factor * state

    assert isclose(scaled, 0.102, abs_tol=ABS_TOL)
    assert isclose(scale_factor - 1.0, 0.02, abs_tol=ABS_TOL)


def test_z_axis_misalignment_cross_talk_matches_published_equation() -> None:
    roll = 0.10
    pitch = 0.20
    dk = 0.01

    adjusted_roll, adjusted_pitch = _maingot_adjusted_roll_pitch(
        roll_rad=roll,
        pitch_rad=pitch,
        roll_rate_rad_s=0.0,
        pitch_rate_rad_s=0.0,
        latency_s=0.0,
        scale_factor=1.0,
        z_axis_misalignment_rad=dk,
    )

    expected_roll = asin(cos(dk) * sin(roll) + sin(dk) * sin(pitch))
    expected_pitch = asin(cos(dk) * sin(pitch) - sin(dk) * sin(roll))

    assert isclose(adjusted_roll, expected_roll, abs_tol=ABS_TOL)
    assert isclose(adjusted_pitch, expected_pitch, abs_tol=ABS_TOL)
    assert adjusted_roll > roll
    assert adjusted_pitch < pitch


def test_lever_arm_sign_crosswalk() -> None:
    true_lever_arm_m = 2.0
    delta_l_maingot_m = 0.25

    configured = _maingot_configured_lever_arm(true_lever_arm_m, delta_l_maingot_m)
    hydrosim_error = _hydrosim_lever_arm_error_from_maingot(delta_l_maingot_m)

    assert isclose(configured, 1.75, abs_tol=ABS_TOL)
    assert isclose(hydrosim_error, -0.25, abs_tol=ABS_TOL)
    assert isclose(configured - true_lever_arm_m, hydrosim_error, abs_tol=ABS_TOL)


def test_surface_sound_speed_sign_crosswalk_and_steering() -> None:
    true_sss_m_s = 1500.0
    delta_sss_maingot_m_s = 2.0
    steering_angle_rad = 0.5235987755982988  # 30 degrees

    configured_sss = true_sss_m_s - delta_sss_maingot_m_s
    hydrosim_error = _hydrosim_sss_error_from_maingot(delta_sss_maingot_m_s)
    adjusted_angle = _maingot_adjusted_steering_angle(
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
    """Guard against incorrectly treating the three attitude terms as additive residuals."""
    adjusted_roll, adjusted_pitch = _maingot_adjusted_roll_pitch(
        roll_rad=0.15,
        pitch_rad=-0.08,
        roll_rate_rad_s=0.04,
        pitch_rate_rad_s=-0.03,
        latency_s=0.02,
        scale_factor=1.01,
        z_axis_misalignment_rad=0.005,
    )

    # Re-evaluate independently from the literal published nesting.
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

    assert isclose(adjusted_roll, expected_roll, abs_tol=ABS_TOL)
    assert isclose(adjusted_pitch, expected_pitch, abs_tol=ABS_TOL)

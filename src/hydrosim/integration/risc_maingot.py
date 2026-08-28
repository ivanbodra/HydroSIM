"""Reference implementation of the six Maingot (2019) RISC integration errors.

This module reproduces the analytical parameterization presented in Section 3.1
of Brandon Maingot's 2019 M.S. thesis. It is intentionally *not* an implementation
of the RISC estimator itself. The goal is to provide small, transparent, testable
functions against which future HydroSIM production models can be validated.

Scientific scope
----------------
The six RISC parameters are:

- GNSS-MBES X lever-arm error, Delta Lx;
- GNSS-MBES Y lever-arm error, Delta Ly;
- INS-MBES latency, Delta t;
- INS scale factor, Delta rho;
- INS-MB Z-axis misalignment, Delta kappa;
- effective surface sound-speed error, Delta SSS.

The published equations define Maingot's error signs. HydroSIM may use different
canonical error semantics. Explicit crosswalk functions are therefore provided
rather than silently changing signs inside the published equations.

Limitations
-----------
- The latency term is Maingot's first-order local approximation x - x_dot*Delta t.
- Delta rho is the multiplicative scale factor itself; 1.0 means no scale error.
- The thesis identifies Delta SSS as an effective error that may arise from bias
  and/or latency. This module does not split those physical causes.
- The thesis does not directly state the sign convention of heave. The function
  preserves the published algebra without converting to HydroSIM's +Up heave.
- The simplified SSS steering equation is implemented here. The later coupled
  Tx/Rx motion-compensation expression should be implemented separately with the
  beam/sector and ray-tracing models.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, isfinite, sin


@dataclass(frozen=True, slots=True)
class AdjustedMotionState:
    """Motion state after applying Maingot's latency, scale, and Z-axis errors.

    All angular quantities are radians; angular rates are radians per second.
    ``heave`` retains Maingot's source convention and is deliberately not mapped
    to HydroSIM's canonical +Up heave in this reference object.
    """

    roll_rad: float
    pitch_rad: float
    heading_rad: float
    heave_m: float


def _require_finite(**values: float) -> None:
    for name, value in values.items():
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")


def _safe_asin_argument(value: float, *, label: str) -> float:
    """Validate a mathematically expected asin argument without hiding errors."""

    if value < -1.0 or value > 1.0:
        raise ValueError(f"{label} must be within [-1, 1], got {value!r}")
    return value


def maingot_latency_adjusted(value: float, rate: float, latency_s: float) -> float:
    """Apply Maingot's first-order positive-latency convention.

    Published form::

        x* = x - x_dot * Delta_t

    Thus positive ``latency_s`` uses an older state for a locally affine signal.
    """

    _require_finite(value=value, rate=rate, latency_s=latency_s)
    return value - rate * latency_s


def apply_maingot_motion_errors(
    *,
    roll_rad: float,
    pitch_rad: float,
    heading_rad: float,
    heave_m: float,
    roll_rate_rad_s: float,
    pitch_rate_rad_s: float,
    heading_rate_rad_s: float,
    heave_rate_m_s: float,
    latency_s: float = 0.0,
    scale_factor: float = 1.0,
    z_axis_misalignment_rad: float = 0.0,
) -> AdjustedMotionState:
    """Apply the published coupled INS error equations from Maingot (2019).

    Latency is applied first through the local first-order approximation. The
    lagged roll, pitch, and heave are then multiplied by ``scale_factor``. The
    Z-axis misalignment couples the scaled roll and pitch channels. Heading is
    affected by latency but not by the scale or Z-axis cross-talk terms in the
    published Section 3.1 expression.

    ``scale_factor=1`` and ``z_axis_misalignment_rad=0`` represent no respective
    error. No heave-sign conversion is made here.
    """

    _require_finite(
        roll_rad=roll_rad,
        pitch_rad=pitch_rad,
        heading_rad=heading_rad,
        heave_m=heave_m,
        roll_rate_rad_s=roll_rate_rad_s,
        pitch_rate_rad_s=pitch_rate_rad_s,
        heading_rate_rad_s=heading_rate_rad_s,
        heave_rate_m_s=heave_rate_m_s,
        latency_s=latency_s,
        scale_factor=scale_factor,
        z_axis_misalignment_rad=z_axis_misalignment_rad,
    )

    roll_lagged = maingot_latency_adjusted(roll_rad, roll_rate_rad_s, latency_s)
    pitch_lagged = maingot_latency_adjusted(pitch_rad, pitch_rate_rad_s, latency_s)
    heading_adjusted = maingot_latency_adjusted(
        heading_rad, heading_rate_rad_s, latency_s
    )
    heave_lagged = maingot_latency_adjusted(heave_m, heave_rate_m_s, latency_s)

    scaled_roll = scale_factor * roll_lagged
    scaled_pitch = scale_factor * pitch_lagged
    adjusted_heave = scale_factor * heave_lagged

    dk = z_axis_misalignment_rad
    roll_argument = cos(dk) * sin(scaled_roll) + sin(dk) * sin(scaled_pitch)
    pitch_argument = cos(dk) * sin(scaled_pitch) - sin(dk) * sin(scaled_roll)

    adjusted_roll = asin(
        _safe_asin_argument(roll_argument, label="adjusted roll asin argument")
    )
    adjusted_pitch = asin(
        _safe_asin_argument(pitch_argument, label="adjusted pitch asin argument")
    )

    return AdjustedMotionState(
        roll_rad=adjusted_roll,
        pitch_rad=adjusted_pitch,
        heading_rad=heading_adjusted,
        heave_m=adjusted_heave,
    )


def configured_lever_arm_from_maingot_error(
    true_lever_arm_m: float, delta_l_maingot_m: float
) -> float:
    """Return the lever arm used by Maingot's erroneous integration.

    Published sign convention::

        L_configured = L_true - Delta_L_M

    Apply independently to the X and Y components.
    """

    _require_finite(
        true_lever_arm_m=true_lever_arm_m,
        delta_l_maingot_m=delta_l_maingot_m,
    )
    return true_lever_arm_m - delta_l_maingot_m


def hydrosim_lever_arm_error_from_maingot(delta_l_maingot_m: float) -> float:
    """Convert Maingot Delta L to HydroSIM configured-minus-truth semantics."""

    _require_finite(delta_l_maingot_m=delta_l_maingot_m)
    return -delta_l_maingot_m


def maingot_surface_sound_speed(
    true_sss_m_s: float, delta_sss_maingot_m_s: float
) -> float:
    """Return the SSS used by Maingot's erroneous steering model.

    Published sign convention::

        SSS_configured = SSS_true - Delta_SSS_M
    """

    _require_finite(
        true_sss_m_s=true_sss_m_s,
        delta_sss_maingot_m_s=delta_sss_maingot_m_s,
    )
    configured = true_sss_m_s - delta_sss_maingot_m_s
    if true_sss_m_s <= 0.0:
        raise ValueError("true_sss_m_s must be positive")
    if configured <= 0.0:
        raise ValueError("configured surface sound speed must be positive")
    return configured


def hydrosim_sss_error_from_maingot(delta_sss_maingot_m_s: float) -> float:
    """Convert Maingot Delta SSS to HydroSIM configured-minus-truth semantics."""

    _require_finite(delta_sss_maingot_m_s=delta_sss_maingot_m_s)
    return -delta_sss_maingot_m_s


def maingot_surface_sound_speed_steering_angle(
    steering_angle_rad: float,
    true_sss_m_s: float,
    delta_sss_maingot_m_s: float,
) -> float:
    """Apply Maingot's simplified SSS-dependent array steering equation.

    Published form::

        theta* = asin(((SSS - Delta_SSS) / SSS) * sin(theta))

    This is the simple steering relation from Section 3.1, not the subsequent
    motion-coupled Tx/Rx expression and not a water-column ray-tracing model.
    """

    _require_finite(
        steering_angle_rad=steering_angle_rad,
        true_sss_m_s=true_sss_m_s,
        delta_sss_maingot_m_s=delta_sss_maingot_m_s,
    )
    configured_sss = maingot_surface_sound_speed(
        true_sss_m_s, delta_sss_maingot_m_s
    )
    argument = (configured_sss / true_sss_m_s) * sin(steering_angle_rad)
    return asin(_safe_asin_argument(argument, label="SSS steering asin argument"))

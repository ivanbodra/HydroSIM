"""Local finite-difference sensitivity of SVP-induced swath curvature.

This diagnostic evaluates a centered 3 x 3 stencil around the Truth interface depth
and Truth adjacent-layer sound-speed contrast. It derives local first derivatives,
second derivatives, a mixed interaction derivative, and the first-order compensation
slope for the existing edge-minus-nadir curvature metric.

The quantities are numerical diagnostics of the controlled piecewise-constant model.
They are not analytical oceanographic laws, operational uncertainty estimates, or
claims that the response is globally linear or separable.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_svp_interface_contrast_map import (
    LayeredSvpInterfaceContrastMap,
    run_layered_svp_interface_contrast_map,
)


class LayeredSvpInterfaceContrastLocalSensitivity(BaseModel):
    """Centered local response around the Truth interface/contrast coordinate."""

    model_config = ConfigDict(frozen=True)

    interface_index: int = Field(ge=0)
    truth_interface_depth_m: FiniteFloat = Field(gt=0.0)
    truth_sound_speed_contrast_mps: FiniteFloat
    interface_depth_step_m: FiniteFloat = Field(gt=0.0)
    sound_speed_contrast_step_mps: FiniteFloat = Field(gt=0.0)
    reference_curvature_m: FiniteFloat
    depth_sensitivity_m_per_m: FiniteFloat
    contrast_sensitivity_m_per_mps: FiniteFloat
    depth_second_derivative_m_per_m2: FiniteFloat
    contrast_second_derivative_m_per_mps2: FiniteFloat
    mixed_derivative_m_per_m_per_mps: FiniteFloat
    contrast_compensation_slope_mps_per_m: FiniteFloat | None
    max_abs_corner_interaction_residual_m: FiniteFloat = Field(ge=0.0)
    stencil: LayeredSvpInterfaceContrastMap


def run_layered_svp_interface_contrast_local_sensitivity(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    interface_depth_step_m: float,
    sound_speed_contrast_step_mps: float,
    profile_start_depth_m: float,
    compensation_denominator_tolerance: float = 1e-15,
) -> LayeredSvpInterfaceContrastLocalSensitivity:
    """Evaluate local curvature derivatives on a centered Truth-referenced stencil.

    Let C(z, dc) denote the edge-minus-nadir vertical curvature, where z is the
    processing interface depth and dc is lower-minus-upper sound-speed contrast.
    The stencil is centered at the Truth coordinate and uses positive steps h and k.

    The first-order local zero-curvature tangent is

        d(dc) / dz = -(dC/dz) / (dC/d(dc))

    when the contrast derivative is numerically resolvable. The mixed derivative
    measures local non-separability; it is not assumed to vanish.
    """

    h = float(interface_depth_step_m)
    k = float(sound_speed_contrast_step_mps)
    if h <= 0.0:
        raise ValueError("interface_depth_step_m must be positive")
    if k <= 0.0:
        raise ValueError("sound_speed_contrast_step_mps must be positive")
    tolerance = float(compensation_denominator_tolerance)
    if tolerance < 0.0:
        raise ValueError("compensation_denominator_tolerance must be non-negative")

    index = int(interface_index)
    if index < 0 or index >= len(true_profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    upper = true_profile.layers[index]
    lower = true_profile.layers[index + 1]
    z0 = float(upper.bottom_depth_m)
    dc0 = float(lower.sound_speed_mps) - float(upper.sound_speed_mps)

    stencil = run_layered_svp_interface_contrast_map(
        sensor_pose=sensor_pose,
        terrain=terrain,
        configured_across_track_angles_rad=configured_across_track_angles_rad,
        true_profile=true_profile,
        interface_index=index,
        processing_interface_depths_m=(z0 - h, z0, z0 + h),
        processing_sound_speed_contrasts_mps=(dc0 - k, dc0, dc0 + k),
        profile_start_depth_m=profile_start_depth_m,
    )

    curvature = {
        (
            round(float(point.interface_depth_m), 12),
            round(float(point.sound_speed_contrast_mps), 12),
        ): float(point.mean_edge_minus_nadir_vertical_error_m)
        for point in stencil.points
    }

    def c(depth: float, contrast: float) -> float:
        return curvature[(round(depth, 12), round(contrast, 12))]

    c00 = c(z0, dc0)
    cz_minus = c(z0 - h, dc0)
    cz_plus = c(z0 + h, dc0)
    cc_minus = c(z0, dc0 - k)
    cc_plus = c(z0, dc0 + k)

    depth_sensitivity = (cz_plus - cz_minus) / (2.0 * h)
    contrast_sensitivity = (cc_plus - cc_minus) / (2.0 * k)
    depth_second = (cz_plus - 2.0 * c00 + cz_minus) / (h * h)
    contrast_second = (cc_plus - 2.0 * c00 + cc_minus) / (k * k)

    cpp = c(z0 + h, dc0 + k)
    cpm = c(z0 + h, dc0 - k)
    cmp = c(z0 - h, dc0 + k)
    cmm = c(z0 - h, dc0 - k)
    mixed = (cpp - cpm - cmp + cmm) / (4.0 * h * k)

    interaction_residuals = (
        cpp - cz_plus - cc_plus + c00,
        cpm - cz_plus - cc_minus + c00,
        cmp - cz_minus - cc_plus + c00,
        cmm - cz_minus - cc_minus + c00,
    )
    max_interaction = max(abs(value) for value in interaction_residuals)

    compensation_slope = None
    if abs(contrast_sensitivity) > tolerance:
        compensation_slope = -depth_sensitivity / contrast_sensitivity

    return LayeredSvpInterfaceContrastLocalSensitivity(
        interface_index=index,
        truth_interface_depth_m=z0,
        truth_sound_speed_contrast_mps=dc0,
        interface_depth_step_m=h,
        sound_speed_contrast_step_mps=k,
        reference_curvature_m=c00,
        depth_sensitivity_m_per_m=depth_sensitivity,
        contrast_sensitivity_m_per_mps=contrast_sensitivity,
        depth_second_derivative_m_per_m2=depth_second,
        contrast_second_derivative_m_per_mps2=contrast_second,
        mixed_derivative_m_per_m_per_mps=mixed,
        contrast_compensation_slope_mps_per_m=compensation_slope,
        max_abs_corner_interaction_residual_m=max_interaction,
        stencil=stencil,
    )

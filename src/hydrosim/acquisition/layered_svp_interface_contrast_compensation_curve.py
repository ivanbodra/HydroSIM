"""Numerical zero-curvature compensation curve for processing-SVP interface errors.

For each requested processing interface depth, this diagnostic searches a supplied
sound-speed-contrast bracket for a root of the existing edge-minus-nadir curvature
metric. The resulting family of depth/contrast pairs approximates the controlled
C_edge = 0 contour.

The root is numerical and metric-specific. A compensated edge-curvature value does
not imply that the complete reconstructed swath equals Truth.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_svp_interface_contrast_local_sensitivity import (
    LayeredSvpInterfaceContrastLocalSensitivity,
    run_layered_svp_interface_contrast_local_sensitivity,
)
from .layered_svp_interface_contrast_map import run_layered_svp_interface_contrast_map


class LayeredSvpInterfaceContrastCompensationPoint(BaseModel):
    """One numerically located point on the controlled zero-curvature contour."""

    model_config = ConfigDict(frozen=True)

    interface_depth_m: FiniteFloat = Field(gt=0.0)
    interface_depth_error_m: FiniteFloat
    compensated_sound_speed_contrast_mps: FiniteFloat
    sound_speed_contrast_error_mps: FiniteFloat
    residual_curvature_m: FiniteFloat
    iterations: int = Field(ge=0)
    bracket_lower_contrast_mps: FiniteFloat
    bracket_upper_contrast_mps: FiniteFloat
    local_tangent_predicted_contrast_error_mps: FiniteFloat | None
    tangent_prediction_residual_mps: FiniteFloat | None


class LayeredSvpInterfaceContrastCompensationCurve(BaseModel):
    """Deterministic zero-curvature contour over processing interface depth."""

    model_config = ConfigDict(frozen=True)

    interface_index: int = Field(ge=0)
    truth_interface_depth_m: FiniteFloat = Field(gt=0.0)
    truth_sound_speed_contrast_mps: FiniteFloat
    local_sensitivity: LayeredSvpInterfaceContrastLocalSensitivity
    points: tuple[LayeredSvpInterfaceContrastCompensationPoint, ...]


def run_layered_svp_interface_contrast_compensation_curve(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    processing_interface_depths_m: Iterable[float],
    contrast_bracket_mps: tuple[float, float],
    profile_start_depth_m: float,
    local_interface_depth_step_m: float,
    local_sound_speed_contrast_step_mps: float,
    curvature_tolerance_m: float = 1e-9,
    contrast_tolerance_mps: float = 1e-9,
    max_iterations: int = 80,
) -> LayeredSvpInterfaceContrastCompensationCurve:
    """Locate the controlled C_edge = 0 contour by bisection in contrast.

    A single contrast bracket is applied independently at every requested interface
    depth. The endpoint curvatures must bracket a sign change or already satisfy the
    curvature tolerance. No extrapolated root is invented outside the supplied bracket.
    """

    index = int(interface_index)
    if index < 0 or index >= len(true_profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    depths = tuple(float(value) for value in processing_interface_depths_m)
    if not depths:
        raise ValueError("processing_interface_depths_m must not be empty")

    lower_bracket = float(contrast_bracket_mps[0])
    upper_bracket = float(contrast_bracket_mps[1])
    if not lower_bracket < upper_bracket:
        raise ValueError("contrast_bracket_mps must be strictly increasing")
    if curvature_tolerance_m < 0.0:
        raise ValueError("curvature_tolerance_m must be non-negative")
    if contrast_tolerance_mps <= 0.0:
        raise ValueError("contrast_tolerance_mps must be positive")
    if max_iterations < 1:
        raise ValueError("max_iterations must be at least one")

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    upper = true_profile.layers[index]
    lower = true_profile.layers[index + 1]
    z0 = float(upper.bottom_depth_m)
    dc0 = float(lower.sound_speed_mps) - float(upper.sound_speed_mps)

    local = run_layered_svp_interface_contrast_local_sensitivity(
        sensor_pose=sensor_pose,
        terrain=terrain,
        configured_across_track_angles_rad=angles,
        true_profile=true_profile,
        interface_index=index,
        interface_depth_step_m=local_interface_depth_step_m,
        sound_speed_contrast_step_mps=local_sound_speed_contrast_step_mps,
        profile_start_depth_m=profile_start_depth_m,
    )

    def curvature(depth: float, contrast: float) -> float:
        response = run_layered_svp_interface_contrast_map(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angles_rad=angles,
            true_profile=true_profile,
            interface_index=index,
            processing_interface_depths_m=(depth,),
            processing_sound_speed_contrasts_mps=(contrast,),
            profile_start_depth_m=profile_start_depth_m,
        )
        return float(response.points[0].mean_edge_minus_nadir_vertical_error_m)

    points = []
    for depth in depths:
        a = lower_bracket
        b = upper_bracket
        fa = curvature(depth, a)
        fb = curvature(depth, b)

        if abs(fa) <= curvature_tolerance_m:
            root, residual, iterations = a, fa, 0
        elif abs(fb) <= curvature_tolerance_m:
            root, residual, iterations = b, fb, 0
        else:
            if fa * fb > 0.0:
                raise ValueError(
                    "contrast_bracket_mps does not bracket zero curvature "
                    f"at interface depth {depth} m"
                )
            root = 0.5 * (a + b)
            residual = curvature(depth, root)
            iterations = 0
            for iteration in range(1, max_iterations + 1):
                root = 0.5 * (a + b)
                residual = curvature(depth, root)
                iterations = iteration
                if (
                    abs(residual) <= curvature_tolerance_m
                    or 0.5 * (b - a) <= contrast_tolerance_mps
                ):
                    break
                if fa * residual <= 0.0:
                    b = root
                    fb = residual
                else:
                    a = root
                    fa = residual
            else:
                raise RuntimeError("compensation root did not converge within max_iterations")

        depth_error = depth - z0
        contrast_error = root - dc0
        tangent_prediction = None
        tangent_residual = None
        slope = local.contrast_compensation_slope_mps_per_m
        if slope is not None:
            tangent_prediction = float(slope) * depth_error
            tangent_residual = contrast_error - tangent_prediction

        points.append(
            LayeredSvpInterfaceContrastCompensationPoint(
                interface_depth_m=depth,
                interface_depth_error_m=depth_error,
                compensated_sound_speed_contrast_mps=root,
                sound_speed_contrast_error_mps=contrast_error,
                residual_curvature_m=residual,
                iterations=iterations,
                bracket_lower_contrast_mps=lower_bracket,
                bracket_upper_contrast_mps=upper_bracket,
                local_tangent_predicted_contrast_error_mps=tangent_prediction,
                tangent_prediction_residual_mps=tangent_residual,
            )
        )

    return LayeredSvpInterfaceContrastCompensationCurve(
        interface_index=index,
        truth_interface_depth_m=z0,
        truth_sound_speed_contrast_mps=dc0,
        local_sensitivity=local,
        points=tuple(points),
    )

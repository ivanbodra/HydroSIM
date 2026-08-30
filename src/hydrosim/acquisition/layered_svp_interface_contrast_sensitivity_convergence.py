"""Convergence study for local SVP interface/contrast sensitivity diagnostics.

The study evaluates the existing centered finite-difference local sensitivity at an
explicit sequence of progressively refined step pairs. It records step-to-step
changes in the principal derivatives and compensation slope without imposing an
arbitrary pass/fail threshold or claiming a formal asymptotic order.
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


class LayeredSvpLocalSensitivityConvergencePoint(BaseModel):
    """One finite-difference resolution and its change from the previous level."""

    model_config = ConfigDict(frozen=True)

    level: int = Field(ge=0)
    interface_depth_step_m: FiniteFloat = Field(gt=0.0)
    sound_speed_contrast_step_mps: FiniteFloat = Field(gt=0.0)
    sensitivity: LayeredSvpInterfaceContrastLocalSensitivity
    depth_sensitivity_change_m_per_m: FiniteFloat | None
    contrast_sensitivity_change_m_per_mps: FiniteFloat | None
    mixed_derivative_change_m_per_m_per_mps: FiniteFloat | None
    compensation_slope_change_mps_per_m: FiniteFloat | None


class LayeredSvpLocalSensitivityConvergenceStudy(BaseModel):
    """Ordered finite-difference refinement history around the Truth coordinate."""

    model_config = ConfigDict(frozen=True)

    interface_index: int = Field(ge=0)
    refinement_steps: tuple[tuple[FiniteFloat, FiniteFloat], ...]
    points: tuple[LayeredSvpLocalSensitivityConvergencePoint, ...]


def run_layered_svp_local_sensitivity_convergence_study(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    refinement_steps: Iterable[tuple[float, float]],
    profile_start_depth_m: float,
    compensation_denominator_tolerance: float = 1e-15,
) -> LayeredSvpLocalSensitivityConvergenceStudy:
    """Evaluate local sensitivities for progressively smaller centered stencil steps.

    Each refinement coordinate is ``(h, k)``, where ``h`` is interface-depth step in
    metres and ``k`` is sound-speed-contrast step in m/s. Both coordinates must be
    strictly positive and strictly decrease from one level to the next. This keeps
    the sequence unambiguously ordered from coarse to fine.

    The returned changes are signed ``current - previous`` values. No convergence
    threshold is applied: callers retain the numerical evidence needed to choose a
    tolerance appropriate to a later scientific or didactic use.
    """

    steps = tuple((float(h), float(k)) for h, k in refinement_steps)
    if len(steps) < 2:
        raise ValueError("refinement_steps must contain at least two step pairs")
    for h, k in steps:
        if h <= 0.0 or k <= 0.0:
            raise ValueError("all refinement steps must be strictly positive")
    for previous, current in zip(steps, steps[1:]):
        if not (current[0] < previous[0] and current[1] < previous[1]):
            raise ValueError("refinement_steps must strictly decrease in both coordinates")

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    points = []
    previous_sensitivity: LayeredSvpInterfaceContrastLocalSensitivity | None = None

    for level, (h, k) in enumerate(steps):
        sensitivity = run_layered_svp_interface_contrast_local_sensitivity(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angles_rad=angles,
            true_profile=true_profile,
            interface_index=interface_index,
            interface_depth_step_m=h,
            sound_speed_contrast_step_mps=k,
            profile_start_depth_m=profile_start_depth_m,
            compensation_denominator_tolerance=compensation_denominator_tolerance,
        )

        depth_change = None
        contrast_change = None
        mixed_change = None
        slope_change = None
        if previous_sensitivity is not None:
            depth_change = (
                float(sensitivity.depth_sensitivity_m_per_m)
                - float(previous_sensitivity.depth_sensitivity_m_per_m)
            )
            contrast_change = (
                float(sensitivity.contrast_sensitivity_m_per_mps)
                - float(previous_sensitivity.contrast_sensitivity_m_per_mps)
            )
            mixed_change = (
                float(sensitivity.mixed_derivative_m_per_m_per_mps)
                - float(previous_sensitivity.mixed_derivative_m_per_m_per_mps)
            )
            current_slope = sensitivity.contrast_compensation_slope_mps_per_m
            previous_slope = previous_sensitivity.contrast_compensation_slope_mps_per_m
            if current_slope is not None and previous_slope is not None:
                slope_change = float(current_slope) - float(previous_slope)

        points.append(
            LayeredSvpLocalSensitivityConvergencePoint(
                level=level,
                interface_depth_step_m=h,
                sound_speed_contrast_step_mps=k,
                sensitivity=sensitivity,
                depth_sensitivity_change_m_per_m=depth_change,
                contrast_sensitivity_change_m_per_mps=contrast_change,
                mixed_derivative_change_m_per_m_per_mps=mixed_change,
                compensation_slope_change_mps_per_m=slope_change,
            )
        )
        previous_sensitivity = sensitivity

    return LayeredSvpLocalSensitivityConvergenceStudy(
        interface_index=int(interface_index),
        refinement_steps=steps,
        points=tuple(points),
    )

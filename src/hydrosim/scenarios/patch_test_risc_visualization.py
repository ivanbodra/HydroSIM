"""Deterministic P6 forward-model experience for advanced integration residuals.

This module deliberately exposes Maingot-style parameter influence, not an
estimator.  The reference surface is a neutral comparison construct and is
never labelled or used as hidden terrain Truth.
"""

from __future__ import annotations

from math import degrees, pi, sin, tan
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.integration.risc_maingot import (
    apply_maingot_motion_errors,
    configured_lever_arm_from_maingot_error,
    maingot_surface_sound_speed_steering_angle,
)

RiscParameter = Literal["delta_lx", "delta_ly", "delta_t", "delta_rho", "delta_kappa", "delta_sss"]


class RiscVisualizationConfig(BaseModel):
    """One-at-a-time P6 control expressed in canonical Maingot units."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    parameter: RiscParameter = "delta_lx"
    value: float | None = None


class RiscPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    along_m: float
    across_m: float
    depth_m: float
    residual_m: float


class RiscParameterMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    symbol: str
    unit: str
    zero_value: float
    default_demo_value: float
    sign_semantics: str


class RiscVisualizationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    mode: Literal["visualize_only"] = "visualize_only"
    scenario_id: Literal["p6-risc-forward-v1"] = "p6-risc-forward-v1"
    parameter: RiscParameter
    configured_value: float
    parameter_metadata: RiscParameterMetadata
    reference_role: Literal["neutral_estimator_construct"] = "neutral_estimator_construct"
    baseline: tuple[RiscPoint, ...]
    changed: tuple[RiscPoint, ...]
    display_scale_m: float
    motion_context: dict[str, float | str]
    sensor_context: dict[str, float | str]
    provenance: dict[str, str]
    limitations: tuple[str, ...]


_METADATA: dict[RiscParameter, RiscParameterMetadata] = {
    "delta_lx": RiscParameterMetadata(symbol="ΔLx", unit="m", zero_value=0.0, default_demo_value=0.35, sign_semantics="Maingot: L_configured = L_true - ΔLx."),
    "delta_ly": RiscParameterMetadata(symbol="ΔLy", unit="m", zero_value=0.0, default_demo_value=0.35, sign_semantics="Maingot: L_configured = L_true - ΔLy."),
    "delta_t": RiscParameterMetadata(symbol="Δt", unit="s", zero_value=0.0, default_demo_value=0.08, sign_semantics="Positive latency uses the older local state x - x_dot·Δt."),
    "delta_rho": RiscParameterMetadata(symbol="Δρ", unit="1", zero_value=1.0, default_demo_value=1.04, sign_semantics="Published total multiplicative INS scale; 1.0 means no scale error."),
    "delta_kappa": RiscParameterMetadata(symbol="Δκ", unit="rad", zero_value=0.0, default_demo_value=0.035, sign_semantics="Positive Z-axis misalignment follows the published roll/pitch cross-talk equations."),
    "delta_sss": RiscParameterMetadata(symbol="ΔSSS", unit="m/s", zero_value=0.0, default_demo_value=8.0, sign_semantics="Maingot: SSS_configured = SSS_true - ΔSSS."),
}


def run_risc_visualization(config: RiscVisualizationConfig) -> RiscVisualizationResult:
    """Return fixed-scale reference and changed forward-model traces."""

    metadata = _METADATA[config.parameter]
    value = metadata.default_demo_value if config.value is None else config.value
    if config.parameter == "delta_rho" and value <= 0.0:
        raise ValueError("delta_rho must be positive because it is a total scale factor")

    depth = 25.0
    speed = 4.0
    true_sss = 1500.0
    baseline: list[RiscPoint] = []
    changed: list[RiscPoint] = []
    for index in range(41):
        t = index * 0.25
        phase = 2.0 * pi * index / 40.0
        roll = 0.035 * sin(phase)
        pitch = 0.025 * sin(phase + pi / 3.0)
        roll_rate = 0.035 * (2.0 * pi / 10.0) * sin(phase + pi / 2.0)
        pitch_rate = 0.025 * (2.0 * pi / 10.0) * sin(phase + 5.0 * pi / 6.0)
        steering = 0.55 * sin(phase)
        along0 = speed * t + depth * tan(pitch)
        across0 = depth * tan(steering + roll)
        along, across, changed_depth = along0, across0, depth

        if config.parameter == "delta_lx":
            along += configured_lever_arm_from_maingot_error(0.0, value)
        elif config.parameter == "delta_ly":
            across += configured_lever_arm_from_maingot_error(0.0, value)
        elif config.parameter in {"delta_t", "delta_rho", "delta_kappa"}:
            adjusted = apply_maingot_motion_errors(
                roll_rad=roll,
                pitch_rad=pitch,
                heading_rad=0.0,
                heave_m=0.0,
                roll_rate_rad_s=roll_rate,
                pitch_rate_rad_s=pitch_rate,
                heading_rate_rad_s=0.015,
                heave_rate_m_s=0.0,
                latency_s=value if config.parameter == "delta_t" else 0.0,
                scale_factor=value if config.parameter == "delta_rho" else 1.0,
                z_axis_misalignment_rad=value if config.parameter == "delta_kappa" else 0.0,
            )
            if config.parameter == "delta_t":
                along -= speed * value
            along += depth * (tan(adjusted.pitch_rad) - tan(pitch))
            across += depth * (tan(steering + adjusted.roll_rad) - tan(steering + roll))
        else:
            adjusted_steering = maingot_surface_sound_speed_steering_angle(steering, true_sss, value)
            across += depth * (tan(adjusted_steering + roll) - tan(steering + roll))

        residual = ((along - along0) ** 2 + (across - across0) ** 2 + (changed_depth - depth) ** 2) ** 0.5
        baseline.append(RiscPoint(along_m=along0, across_m=across0, depth_m=depth, residual_m=0.0))
        changed.append(RiscPoint(along_m=along, across_m=across, depth_m=changed_depth, residual_m=residual))

    return RiscVisualizationResult(
        parameter=config.parameter,
        configured_value=value,
        parameter_metadata=metadata,
        baseline=tuple(baseline),
        changed=tuple(changed),
        display_scale_m=2.5,
        motion_context={"speed_m_s": speed, "roll_amplitude_deg": degrees(0.035), "pitch_amplitude_deg": degrees(0.025), "period_s": 10.0},
        sensor_context={"depth_m": depth, "surface_sound_speed_m_s": true_sss, "steering_amplitude_deg": degrees(0.55), "frame": "Forward-Starboard-Down"},
        provenance={"forward_model": "hydrosim.integration.risc_maingot", "parameterization": "Maingot 2019 Section 3.1", "reference_surface": "deterministic neutral comparison surface", "baseline": "post-P1-P5 zero-residual configuration"},
        limitations=(
            "Model-based parameter influence; not an estimate or automatic diagnosis.",
            "Different physical causes can produce confounded residual structures.",
            "The reference surface is an estimator construct, not hidden Truth.",
            "The simplified ΔSSS relation does not include coupled Tx/Rx steering or ray tracing.",
        ),
    )


__all__ = ["RiscVisualizationConfig", "RiscVisualizationResult", "run_risc_visualization"]

"""Deterministic Patch Test P2 planning adequacy evaluation."""

from __future__ import annotations

from math import radians, tan
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

PatchPlanningFamily = Literal["roll", "pitch", "yaw", "latency"]
PatchPlanningAdequacy = Literal["Adequate", "Suboptimal", "Inadequate"]
TerrainKind = Literal["flat", "slope", "feature"]


class PatchPlanningConfig(BaseModel):
    """Learner plan plus explicit scenario-specific pedagogical criteria."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_family: PatchPlanningFamily = "roll"
    heading_a_deg: FiniteFloat = 0.0
    heading_b_deg: FiniteFloat = 180.0
    speed_a_mps: FiniteFloat = Field(default=4.0, gt=0.0, le=20.0)
    speed_b_mps: FiniteFloat = Field(default=4.0, gt=0.0, le=20.0)
    line_offset_m: FiniteFloat = Field(default=0.0, ge=0.0, le=1000.0)
    water_depth_m: FiniteFloat = Field(default=50.0, gt=0.0, le=2000.0)
    swath_angle_deg: FiniteFloat = Field(default=100.0, gt=0.0, lt=170.0)
    terrain_cross_extent_m: FiniteFloat = Field(default=300.0, gt=0.0)
    terrain_along_extent_m: FiniteFloat = Field(default=500.0, gt=0.0)
    terrain_kind: TerrainKind = "flat"
    heading_tolerance_deg: FiniteFloat = Field(default=5.0, gt=0.0, le=45.0)
    same_line_tolerance_m: FiniteFloat = Field(default=2.0, ge=0.0)
    preferred_common_support_m: FiniteFloat = Field(default=25.0, gt=0.0)
    preferred_speed_contrast_mps: FiniteFloat = Field(default=2.0, gt=0.0)


class PatchPlanningMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    swath_half_width_m: FiniteFloat
    common_support_m: FiniteFloat = Field(ge=0.0)
    common_support_fraction: FiniteFloat = Field(ge=0.0, le=1.0)
    heading_difference_deg: FiniteFloat = Field(ge=0.0, le=180.0)
    speed_contrast_mps: FiniteFloat = Field(ge=0.0)
    line_offset_m: FiniteFloat = Field(ge=0.0)
    common_support_interval_m: tuple[FiniteFloat, FiniteFloat] | None


class PatchPlanningResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    target_family: PatchPlanningFamily
    adequacy: PatchPlanningAdequacy
    reasons: tuple[str, ...]
    metrics: PatchPlanningMetrics
    comparison_region: Literal["outer_swath", "near_nadir", "common_outer_swath"]
    criteria_basis: str = "scenario_configured_pedagogical_defaults"
    state_semantics: str = (
        "Configured acquisition plan; Derived geometry/adequacy; "
        "no hidden Truth and no Estimated correction"
    )


def _angular_difference_deg(first: float, second: float) -> float:
    return abs((second - first + 180.0) % 360.0 - 180.0)


def _overlap_interval(config: PatchPlanningConfig, half_width: float) -> tuple[float, float] | None:
    terrain_min = -float(config.terrain_cross_extent_m) / 2.0
    terrain_max = float(config.terrain_cross_extent_m) / 2.0
    first_min, first_max = max(-half_width, terrain_min), min(half_width, terrain_max)
    center_b = float(config.line_offset_m)
    second_min = max(center_b - half_width, terrain_min)
    second_max = min(center_b + half_width, terrain_max)
    lower, upper = max(first_min, second_min), min(first_max, second_max)
    return None if upper <= lower else (lower, upper)


def evaluate_patch_test_plan(config: PatchPlanningConfig) -> PatchPlanningResult:
    """Evaluate P2 observability geometry without estimating any calibration bias."""

    half_width = float(config.water_depth_m) * tan(radians(float(config.swath_angle_deg)) / 2.0)
    interval = _overlap_interval(config, half_width)
    support = 0.0 if interval is None else interval[1] - interval[0]
    available_width = min(2.0 * half_width, float(config.terrain_cross_extent_m))
    support_fraction = support / available_width if available_width > 0.0 else 0.0
    heading_difference = _angular_difference_deg(
        float(config.heading_a_deg), float(config.heading_b_deg)
    )
    speed_contrast = abs(float(config.speed_b_mps) - float(config.speed_a_mps))
    same_direction = heading_difference <= float(config.heading_tolerance_deg)
    reciprocal = abs(heading_difference - 180.0) <= float(config.heading_tolerance_deg)
    coincident = float(config.line_offset_m) <= float(config.same_line_tolerance_m)

    inadequate: list[str] = []
    weak: list[str] = []
    if support <= 0.0:
        inadequate.append("no common physical seabed support")
    elif support < float(config.preferred_common_support_m):
        weak.append("common support is weaker than the configured scenario preference")

    family = config.target_family
    if family == "roll":
        if not reciprocal:
            inadequate.append("roll requires reciprocal line directions")
        if not coincident:
            inadequate.append("roll requires the same nominal line")
        if config.terrain_kind != "flat":
            weak.append("non-flat terrain weakens roll isolation")
        region = "outer_swath"
    elif family == "pitch":
        if not reciprocal:
            inadequate.append("pitch requires reciprocal line directions")
        if not coincident:
            inadequate.append("pitch requires the same nominal line")
        if config.terrain_kind == "flat":
            inadequate.append("pitch requires a distinct along-track slope or feature")
        region = "near_nadir"
    elif family == "yaw":
        if not same_direction:
            inadequate.append("yaw requires parallel same-direction lines")
        if coincident:
            inadequate.append("yaw requires laterally offset lines")
        if config.terrain_kind == "flat":
            inadequate.append("yaw requires a distinct feature or slope in common support")
        region = "common_outer_swath"
    else:
        if not same_direction:
            inadequate.append("latency requires same-direction lines")
        if not coincident:
            inadequate.append("latency requires the same nominal line")
        if config.terrain_kind == "flat":
            inadequate.append("latency requires a distinct along-track slope or feature")
        if speed_contrast <= 1e-12:
            inadequate.append("latency requires nonzero speed contrast")
        elif speed_contrast < float(config.preferred_speed_contrast_mps):
            weak.append("speed contrast is weaker than the configured scenario preference")
        region = "near_nadir"

    if inadequate:
        adequacy: PatchPlanningAdequacy = "Inadequate"
        reasons = tuple(inadequate + weak)
    elif weak:
        adequacy = "Suboptimal"
        reasons = tuple(weak)
    else:
        adequacy = "Adequate"
        reasons = ("required geometry and common support are present",)

    return PatchPlanningResult(
        target_family=family,
        adequacy=adequacy,
        reasons=reasons,
        metrics=PatchPlanningMetrics(
            swath_half_width_m=half_width,
            common_support_m=support,
            common_support_fraction=support_fraction,
            heading_difference_deg=heading_difference,
            speed_contrast_mps=speed_contrast,
            line_offset_m=float(config.line_offset_m),
            common_support_interval_m=interval,
        ),
        comparison_region=region,
    )


__all__ = [
    "PatchPlanningConfig",
    "PatchPlanningMetrics",
    "PatchPlanningResult",
    "evaluate_patch_test_plan",
]

from __future__ import annotations

import pytest

from hydrosim.scenarios.patch_test_planning import (
    PatchPlanningConfig,
    evaluate_patch_test_plan,
)


@pytest.mark.parametrize(
    ("config", "region"),
    [
        (PatchPlanningConfig(target_family="roll"), "outer_swath"),
        (
            PatchPlanningConfig(target_family="pitch", terrain_kind="slope"),
            "near_nadir",
        ),
        (
            PatchPlanningConfig(
                target_family="yaw",
                heading_b_deg=0.0,
                line_offset_m=50.0,
                terrain_kind="feature",
            ),
            "common_outer_swath",
        ),
        (
            PatchPlanningConfig(
                target_family="latency",
                heading_b_deg=0.0,
                speed_b_mps=7.0,
                terrain_kind="slope",
            ),
            "near_nadir",
        ),
    ],
)
def test_reference_plans_are_adequate(
    config: PatchPlanningConfig, region: str
) -> None:
    result = evaluate_patch_test_plan(config)

    assert result.adequacy == "Adequate"
    assert result.comparison_region == region
    assert result.metrics.common_support_m > 0.0
    assert "no hidden Truth" in result.state_semantics


def test_pitch_flat_terrain_is_inadequate() -> None:
    result = evaluate_patch_test_plan(PatchPlanningConfig(target_family="pitch"))

    assert result.adequacy == "Inadequate"
    assert any("slope or feature" in reason for reason in result.reasons)


def test_latency_equal_speeds_is_inadequate() -> None:
    result = evaluate_patch_test_plan(
        PatchPlanningConfig(
            target_family="latency",
            heading_b_deg=0.0,
            terrain_kind="feature",
        )
    )

    assert result.adequacy == "Inadequate"
    assert any("speed contrast" in reason for reason in result.reasons)


def test_yaw_without_common_support_is_inadequate() -> None:
    result = evaluate_patch_test_plan(
        PatchPlanningConfig(
            target_family="yaw",
            heading_b_deg=0.0,
            line_offset_m=280.0,
            water_depth_m=20.0,
            terrain_kind="feature",
        )
    )

    assert result.adequacy == "Inadequate"
    assert result.metrics.common_support_m == 0.0
    assert any("common physical seabed" in reason for reason in result.reasons)


def test_roll_on_slope_is_suboptimal_not_redefined_by_hidden_threshold() -> None:
    result = evaluate_patch_test_plan(
        PatchPlanningConfig(target_family="roll", terrain_kind="slope")
    )

    assert result.adequacy == "Suboptimal"
    assert any("isolation" in reason for reason in result.reasons)


def test_configured_preferences_control_suboptimal_boundary() -> None:
    result = evaluate_patch_test_plan(
        PatchPlanningConfig(
            target_family="latency",
            heading_b_deg=0.0,
            speed_b_mps=4.5,
            terrain_kind="slope",
            preferred_speed_contrast_mps=1.0,
        )
    )

    assert result.adequacy == "Suboptimal"
    assert result.metrics.speed_contrast_mps == pytest.approx(0.5)

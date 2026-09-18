from __future__ import annotations

import pytest

from hydrosim.scenarios import PatchSignatureConfig, run_patch_signature_scenario


@pytest.mark.parametrize("family", ["roll", "pitch", "yaw", "latency"])
def test_isolated_p1_families_return_two_comparable_runs(family: str) -> None:
    result = run_patch_signature_scenario(PatchSignatureConfig(error_family=family))

    assert result.likely_classification == family
    assert result.evidence_sufficient
    assert len(result.runs) == 2
    assert all(run.points for run in result.runs)
    assert max(point.horizontal_residual_m for run in result.runs for point in run.points) > 0.0


def test_zero_roll_residual_closes_truth_and_configured_geometry() -> None:
    result = run_patch_signature_scenario(
        PatchSignatureConfig(error_family="roll", angular_residual_deg=0.0)
    )

    assert all(
        point.horizontal_residual_m == pytest.approx(0.0, abs=1e-12)
        and point.vertical_residual_m == pytest.approx(0.0, abs=1e-12)
        for run in result.runs
        for point in run.points
    )


def test_latency_spatial_effect_scales_with_speed() -> None:
    result = run_patch_signature_scenario(
        PatchSignatureConfig(
            error_family="latency",
            latency_residual_ms=100.0,
            slow_speed_mps=2.0,
            fast_speed_mps=6.0,
        )
    )
    slow, fast = result.runs

    assert slow.points[0].horizontal_residual_m == pytest.approx(0.2)
    assert fast.points[0].horizontal_residual_m == pytest.approx(0.6)


def test_latency_with_equal_speeds_is_not_sufficient_evidence() -> None:
    result = run_patch_signature_scenario(
        PatchSignatureConfig(error_family="latency", slow_speed_mps=4.0, fast_speed_mps=4.0)
    )

    assert not result.evidence_sufficient


def test_flat_pitch_profile_is_reported_non_identifying() -> None:
    result = run_patch_signature_scenario(
        PatchSignatureConfig(error_family="pitch", terrain_slope_deg=0.0)
    )

    assert not result.evidence_sufficient


def test_combined_case_does_not_force_a_classic_label() -> None:
    result = run_patch_signature_scenario(PatchSignatureConfig(error_family="confounded"))

    assert result.likely_classification == "confounded"
    assert not result.evidence_sufficient

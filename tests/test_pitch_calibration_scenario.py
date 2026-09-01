from __future__ import annotations

import pytest

from hydrosim.scenarios import PitchCalibrationScenarioConfig, run_pitch_calibration_scenario


def test_pitch_calibration_zero_residual_closes_near_zero() -> None:
    result = run_pitch_calibration_scenario(
        PitchCalibrationScenarioConfig(
            true_pitch_alignment_deg=0.0,
            configured_pitch_alignment_deg=0.0,
        )
    )
    assert result.estimated_pitch_correction_deg == pytest.approx(0.0, abs=0.01)
    assert result.corrected_rms_mismatch_m <= result.uncorrected_rms_mismatch_m + 1e-12


def test_pitch_calibration_positive_residual_returns_positive_correction() -> None:
    result = run_pitch_calibration_scenario(
        PitchCalibrationScenarioConfig(
            true_pitch_alignment_deg=1.0,
            configured_pitch_alignment_deg=0.0,
        )
    )
    assert result.estimated_pitch_correction_deg > 0.0
    assert result.estimated_pitch_alignment_deg == pytest.approx(1.0, abs=0.02)
    assert result.corrected_rms_mismatch_m < result.uncorrected_rms_mismatch_m
    assert abs(result.validation_alignment_error_deg) <= 0.02


def test_pitch_calibration_negative_residual_returns_negative_correction() -> None:
    result = run_pitch_calibration_scenario(
        PitchCalibrationScenarioConfig(
            true_pitch_alignment_deg=-1.25,
            configured_pitch_alignment_deg=0.25,
        )
    )
    assert result.estimated_pitch_correction_deg < 0.0
    assert result.estimated_pitch_alignment_deg == pytest.approx(-1.25, abs=0.02)
    assert result.corrected_rms_mismatch_m < result.uncorrected_rms_mismatch_m


def test_pitch_calibration_profiles_share_canonical_reciprocal_headings() -> None:
    result = run_pitch_calibration_scenario(PitchCalibrationScenarioConfig())
    assert result.pass_a_uncorrected.heading_deg == 0.0
    assert result.pass_b_uncorrected.heading_deg == 180.0
    assert result.pass_a_corrected.heading_deg == 0.0
    assert result.pass_b_corrected.heading_deg == 180.0


def test_pitch_calibration_requires_positive_slope_for_identifiable_reference() -> None:
    with pytest.raises(ValueError):
        PitchCalibrationScenarioConfig(terrain_slope_deg=0.0)

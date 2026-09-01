"""Deterministic P2 Pitch Patch Test scenario adapter.

The implementation follows ``docs/science/pitch_patch_test_v0_1_contract.md``.
It reuses the existing HydroSIM sounding geometry to generate two reciprocal
near-nadir profiles over a planar along-track slope. The learner-facing estimate
minimizes reciprocal-profile RMS mismatch; hidden Truth is used only to generate
the synthetic observations and to report validation diagnostics.
"""

from __future__ import annotations

from math import radians, sqrt, tan

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, PositiveInt

from hydrosim.geometry import (
    Attitude,
    PlaneTerrain,
    Pose,
    TransducerArray,
    Vector3,
    compare_true_and_configured_sounding,
    generate_ideal_fan_degrees,
)


class PitchCalibrationScenarioConfig(BaseModel):
    """Validated deterministic configuration for the minimum P2 scenario."""

    model_config = ConfigDict(frozen=True)

    true_pitch_alignment_deg: FiniteFloat = 1.0
    configured_pitch_alignment_deg: FiniteFloat = 0.0
    terrain_slope_deg: FiniteFloat = Field(default=15.0, gt=0.0, lt=45.0)
    reference_depth_m: FiniteFloat = Field(default=50.0, gt=0.0)
    line_half_length_m: FiniteFloat = Field(default=30.0, gt=0.0)
    profile_sample_count: PositiveInt = Field(default=61, ge=9)
    search_min_correction_deg: FiniteFloat = -5.0
    search_max_correction_deg: FiniteFloat = 5.0
    coarse_step_deg: FiniteFloat = Field(default=0.05, gt=0.0)
    fine_step_deg: FiniteFloat = Field(default=0.001, gt=0.0)

    def model_post_init(self, __context: object) -> None:
        if float(self.search_max_correction_deg) <= float(self.search_min_correction_deg):
            raise ValueError("search_max_correction_deg must exceed search_min_correction_deg")
        if float(self.fine_step_deg) >= float(self.coarse_step_deg):
            raise ValueError("fine_step_deg must be smaller than coarse_step_deg")


class PitchProfile(BaseModel):
    """One reconstructed reciprocal profile in the common navigation frame."""

    model_config = ConfigDict(frozen=True)

    heading_deg: FiniteFloat
    x_m: tuple[FiniteFloat, ...]
    z_m: tuple[FiniteFloat, ...]


class PitchCalibrationResult(BaseModel):
    """Deterministic P2 estimate and profile-mismatch diagnostics."""

    model_config = ConfigDict(frozen=True)

    true_pitch_alignment_deg: FiniteFloat
    configured_pitch_alignment_deg: FiniteFloat
    estimated_pitch_correction_deg: FiniteFloat
    estimated_pitch_alignment_deg: FiniteFloat
    uncorrected_rms_mismatch_m: FiniteFloat = Field(ge=0.0)
    corrected_rms_mismatch_m: FiniteFloat = Field(ge=0.0)
    validation_alignment_error_deg: FiniteFloat
    pass_a_uncorrected: PitchProfile
    pass_b_uncorrected: PitchProfile
    pass_a_corrected: PitchProfile
    pass_b_corrected: PitchProfile


def _terrain(config: PitchCalibrationScenarioConfig) -> PlaneTerrain:
    slope = tan(radians(float(config.terrain_slope_deg)))
    return PlaneTerrain(
        point=Vector3(x=0.0, y=0.0, z=float(config.reference_depth_m)),
        normal=Vector3(x=-slope, y=0.0, z=1.0),
    )


def _nadir_beam():
    array = TransducerArray(
        name="pitch_demo_rx",
        role="rx",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.01,
        element_transverse_size=0.01,
    )
    return generate_ideal_fan_degrees(
        array,
        beam_count=1,
        total_swath_angle_degrees=0.0,
        role="rx",
    ).beams[0]


def _profile(
    config: PitchCalibrationScenarioConfig,
    *,
    heading_deg: float,
    candidate_correction_deg: float,
) -> PitchProfile:
    terrain = _terrain(config)
    beam = _nadir_beam()
    true_alignment = Attitude.from_degrees(
        roll=0.0,
        pitch=float(config.true_pitch_alignment_deg),
        yaw=0.0,
    )
    configured_alignment = Attitude.from_degrees(
        roll=0.0,
        pitch=float(config.configured_pitch_alignment_deg) + float(candidate_correction_deg),
        yaw=0.0,
    )
    lever_arm = Vector3(x=0.0, y=0.0, z=0.0)
    vessel_positions = np.linspace(
        -float(config.line_half_length_m),
        float(config.line_half_length_m),
        int(config.profile_sample_count),
    )

    points: list[tuple[float, float]] = []
    for x in vessel_positions:
        vessel_pose = Pose(
            position=Vector3(x=float(x), y=0.0, z=0.0),
            attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=heading_deg),
            frame="N",
        )
        comparison = compare_true_and_configured_sounding(
            vessel_truth_pose=vessel_pose,
            lever_arm_vrp_to_sensor=lever_arm,
            true_sensor_alignment=true_alignment,
            configured_sensor_alignment=configured_alignment,
            beam=beam,
            terrain=terrain,
            sensor_frame="T",
        )
        points.append((float(comparison.configured.point.x), float(comparison.configured.point.z)))

    points.sort(key=lambda item: item[0])
    return PitchProfile(
        heading_deg=heading_deg,
        x_m=tuple(item[0] for item in points),
        z_m=tuple(item[1] for item in points),
    )


def _profile_rms(first: PitchProfile, second: PitchProfile) -> float:
    x_first = np.asarray(first.x_m, dtype=float)
    z_first = np.asarray(first.z_m, dtype=float)
    x_second = np.asarray(second.x_m, dtype=float)
    z_second = np.asarray(second.z_m, dtype=float)
    overlap_min = max(float(x_first[0]), float(x_second[0]))
    overlap_max = min(float(x_first[-1]), float(x_second[-1]))
    if overlap_max <= overlap_min:
        raise ValueError("reciprocal profiles have no common along-track coverage")

    count = min(x_first.size, x_second.size)
    common_x = np.linspace(overlap_min, overlap_max, count)
    first_interp = np.interp(common_x, x_first, z_first)
    second_interp = np.interp(common_x, x_second, z_second)
    residual = first_interp - second_interp
    return float(sqrt(float(np.mean(residual * residual))))


def pitch_profile_mismatch_rms(
    config: PitchCalibrationScenarioConfig,
    *,
    candidate_correction_deg: float,
) -> float:
    """Return reciprocal-profile RMS mismatch for one candidate correction."""

    first = _profile(config, heading_deg=0.0, candidate_correction_deg=candidate_correction_deg)
    second = _profile(config, heading_deg=180.0, candidate_correction_deg=candidate_correction_deg)
    return _profile_rms(first, second)


def _candidate_grid(start: float, stop: float, step: float) -> np.ndarray:
    count = int(round((stop - start) / step)) + 1
    return np.linspace(start, stop, max(2, count))


def estimate_pitch_correction(config: PitchCalibrationScenarioConfig) -> float:
    """Estimate the configured-alignment correction by deterministic grid refinement."""

    lower = float(config.search_min_correction_deg)
    upper = float(config.search_max_correction_deg)
    coarse_step = float(config.coarse_step_deg)
    coarse = _candidate_grid(lower, upper, coarse_step)
    coarse_objective = np.asarray(
        [pitch_profile_mismatch_rms(config, candidate_correction_deg=float(value)) for value in coarse]
    )
    best_coarse = float(coarse[int(np.argmin(coarse_objective))])

    fine_half_width = coarse_step
    fine_lower = max(lower, best_coarse - fine_half_width)
    fine_upper = min(upper, best_coarse + fine_half_width)
    fine = _candidate_grid(fine_lower, fine_upper, float(config.fine_step_deg))
    fine_objective = np.asarray(
        [pitch_profile_mismatch_rms(config, candidate_correction_deg=float(value)) for value in fine]
    )
    return float(fine[int(np.argmin(fine_objective))])


def run_pitch_calibration_scenario(config: PitchCalibrationScenarioConfig) -> PitchCalibrationResult:
    """Run the deterministic P2 reference scenario and return estimate diagnostics."""

    uncorrected_a = _profile(config, heading_deg=0.0, candidate_correction_deg=0.0)
    uncorrected_b = _profile(config, heading_deg=180.0, candidate_correction_deg=0.0)
    uncorrected_rms = _profile_rms(uncorrected_a, uncorrected_b)

    correction = estimate_pitch_correction(config)
    corrected_a = _profile(config, heading_deg=0.0, candidate_correction_deg=correction)
    corrected_b = _profile(config, heading_deg=180.0, candidate_correction_deg=correction)
    corrected_rms = _profile_rms(corrected_a, corrected_b)
    estimated_alignment = float(config.configured_pitch_alignment_deg) + correction

    return PitchCalibrationResult(
        true_pitch_alignment_deg=config.true_pitch_alignment_deg,
        configured_pitch_alignment_deg=config.configured_pitch_alignment_deg,
        estimated_pitch_correction_deg=correction,
        estimated_pitch_alignment_deg=estimated_alignment,
        uncorrected_rms_mismatch_m=uncorrected_rms,
        corrected_rms_mismatch_m=corrected_rms,
        validation_alignment_error_deg=estimated_alignment - float(config.true_pitch_alignment_deg),
        pass_a_uncorrected=uncorrected_a,
        pass_b_uncorrected=uncorrected_b,
        pass_a_corrected=corrected_a,
        pass_b_corrected=corrected_b,
    )

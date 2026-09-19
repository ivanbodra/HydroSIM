"""P5 assessment of a P4 candidate against calibration and holdout evidence."""

from __future__ import annotations

from math import sqrt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.scenarios.patch_test_acquisition import AcquisitionRun, PatchAcquisitionConfig, run_patch_acquisition
from hydrosim.scenarios.patch_test_manual_calibration import PatchManualCalibrationConfig, run_manual_calibration
from hydrosim.scenarios.patch_test_signatures import PatchDatasetResidualPoint


class PatchAssessmentConfig(PatchManualCalibrationConfig):
    model_config = ConfigDict(frozen=True, extra="forbid")

    submitted: bool = False
    minimum_improvement_fraction: FiniteFloat = Field(default=0.5, ge=0.0, le=1.0)
    maximum_structured_fraction: FiniteFloat = Field(default=0.25, ge=0.0, le=1.0)


class ValidationEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    evidence_id: Literal["calibration_pair", "holdout_pair"]
    runs: tuple[AcquisitionRun, AcquisitionRun]
    before_residual: tuple[PatchDatasetResidualPoint, ...]
    after_residual: tuple[PatchDatasetResidualPoint, ...]
    before_rms_m: FiniteFloat = Field(ge=0.0)
    after_rms_m: FiniteFloat = Field(ge=0.0)
    improvement_fraction: FiniteFloat
    structured_fraction: FiniteFloat = Field(ge=0.0)
    opposite_sense: bool


class PatchAssessmentResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    error_family: Literal["roll", "pitch", "yaw", "latency"]
    correction_unit: Literal["degrees", "milliseconds"]
    candidate_correction: FiniteFloat
    assessment: Literal["Adequate", "Suboptimal", "Inadequate"]
    reasons: tuple[str, ...]
    calibration: ValidationEvidence
    holdout: ValidationEvidence
    inherited_warnings: tuple[str, ...]
    submitted: bool
    estimation_error: FiniteFloat | None = None
    estimation_error_semantics: str | None = None
    state_semantics: str = (
        "P3 observations remain Observed/locked; candidate is Configured; residuals and RMS are "
        "Derived; holdout is independent of fitting; Truth comparison appears only after submission"
    )


def _rms(points: tuple[PatchDatasetResidualPoint, ...]) -> float:
    if not points:
        return 0.0
    return sqrt(sum(float(p.vertical_difference_m) ** 2 for p in points) / len(points))


def _evidence(evidence_id: Literal["calibration_pair", "holdout_pair"], before, after) -> ValidationEvidence:
    before_rms = _rms(before.spatial_residual)
    after_rms = _rms(after.spatial_residual)
    improvement = (before_rms - after_rms) / before_rms if before_rms > 1e-12 else 0.0
    signed_after = sum(float(p.vertical_difference_m) for p in after.spatial_residual)
    direction_dot = sum(
        float(a.vertical_difference_m) * float(b.vertical_difference_m)
        for a, b in zip(before.spatial_residual, after.spatial_residual, strict=True)
    )
    opposite = direction_dot < -1e-12 and after_rms > 1e-9
    mean_after = abs(signed_after / len(after.spatial_residual)) if after.spatial_residual else 0.0
    structured = mean_after / after_rms if after_rms > 1e-12 else 0.0
    return ValidationEvidence(
        evidence_id=evidence_id,
        runs=before.runs,
        before_residual=before.spatial_residual,
        after_residual=after.spatial_residual,
        before_rms_m=before_rms,
        after_rms_m=after_rms,
        improvement_fraction=improvement,
        structured_fraction=structured,
        opposite_sense=opposite,
    )


def _without_p5(config: PatchAssessmentConfig, **updates) -> PatchManualCalibrationConfig:
    values = config.model_dump(exclude={
        "submitted", "minimum_improvement_fraction", "maximum_structured_fraction"
    })
    values.update(updates)
    return PatchManualCalibrationConfig(**values)


def run_patch_assessment(config: PatchAssessmentConfig) -> PatchAssessmentResult:
    if config.error_family == "confounded":
        raise ValueError("P5 assessment accepts one classic parameter family at a time")

    before = run_manual_calibration(_without_p5(config, candidate_correction=0.0, search_steps=11))
    after = run_manual_calibration(_without_p5(config))
    calibration = _evidence("calibration_pair", before, after)

    # This repeated pair is generated independently and is never consulted by the P4 search.
    holdout_count = min(201, int(config.sample_count) + 2)
    holdout_before = run_manual_calibration(_without_p5(
        config, candidate_correction=0.0, sample_count=holdout_count, search_steps=11,
        deterministic_seed=int(config.deterministic_seed) + 1,
    ))
    holdout_after = run_manual_calibration(_without_p5(
        config, sample_count=holdout_count, deterministic_seed=int(config.deterministic_seed) + 1,
    ))
    holdout = _evidence("holdout_pair", holdout_before, holdout_after)

    acquisition = run_patch_acquisition(PatchAcquisitionConfig(**config.model_dump(exclude={
        "candidate_correction", "search_min", "search_max", "search_steps", "submitted",
        "minimum_improvement_fraction", "maximum_structured_fraction",
    })))
    warnings = tuple(acquisition.fitness_reasons) + tuple(after.estimate_reasons)
    reasons: list[str] = []
    criterion = float(config.minimum_improvement_fraction)
    structure_limit = float(config.maximum_structured_fraction)

    if acquisition.fitness == "reacquire" or after.estimate_status == "weak_or_flat":
        assessment = "Inadequate"
        reasons.append("acquisition evidence does not identify and validate the target parameter")
    elif calibration.improvement_fraction <= 0.0 or holdout.improvement_fraction <= 0.0:
        assessment = "Inadequate"
        reasons.append("candidate does not improve both calibration and independent holdout evidence")
    elif calibration.opposite_sense or holdout.opposite_sense:
        assessment = "Inadequate"
        reasons.append("candidate introduces an opposite-sense residual consistent with overcorrection")
    elif (
        calibration.improvement_fraction < criterion
        or holdout.improvement_fraction < criterion
        or calibration.structured_fraction > structure_limit
        or holdout.structured_fraction > structure_limit
        or after.estimate_status == "boundary_minimum"
        or acquisition.fitness == "marginal"
    ):
        assessment = "Suboptimal"
        reasons.append("improvement, residual structure, or conditioning does not meet the configured criterion")
    else:
        assessment = "Adequate"
        reasons.append("candidate improves calibration and independent holdout evidence without overcorrection")

    truth_correction = (
        float(config.latency_residual_ms)
        if config.error_family == "latency"
        else float(config.angular_residual_deg)
    )
    estimation_error = float(config.candidate_correction) - truth_correction if config.submitted else None
    return PatchAssessmentResult(
        error_family=config.error_family,
        correction_unit=after.correction_unit,
        candidate_correction=float(config.candidate_correction),
        assessment=assessment,
        reasons=tuple(reasons),
        calibration=calibration,
        holdout=holdout,
        inherited_warnings=warnings,
        submitted=config.submitted,
        estimation_error=estimation_error,
        estimation_error_semantics=(
            "Estimated - Truth; separate from inter-dataset residual RMS and not TPU"
            if config.submitted else None
        ),
    )


__all__ = ["PatchAssessmentConfig", "PatchAssessmentResult", "run_patch_assessment"]

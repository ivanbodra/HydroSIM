"""P4 manual calibration over immutable P3 acquisition evidence.

The candidate is applied to the configured reconstruction only.  The P3
acquisition returned with the result is retained verbatim so its Observed
samples, epochs and provenance cannot change while the learner explores the
objective.
"""

from __future__ import annotations

from math import sqrt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from hydrosim.scenarios.patch_test_acquisition import (
    AcquisitionRun,
    PatchAcquisitionConfig,
    run_patch_acquisition,
)
from hydrosim.scenarios.patch_test_signatures import (
    PatchDatasetResidualPoint,
    PatchSignatureConfig,
    run_patch_signature_scenario,
)


class PatchManualCalibrationConfig(PatchAcquisitionConfig):
    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_correction: FiniteFloat = 0.0
    search_min: FiniteFloat = -4.0
    search_max: FiniteFloat = 4.0
    search_steps: int = Field(default=101, ge=11, le=1001)

    @model_validator(mode="after")
    def validate_search(self):
        if float(self.search_max) <= float(self.search_min):
            raise ValueError("search_max must be greater than search_min")
        if not float(self.search_min) <= float(self.candidate_correction) <= float(self.search_max):
            raise ValueError("candidate_correction must lie inside the search interval")
        return self


class ObjectiveSample(BaseModel):
    model_config = ConfigDict(frozen=True)
    correction: FiniteFloat
    rms_m: FiniteFloat = Field(ge=0.0)


class PatchManualCalibrationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    acquisition_id: str
    error_family: Literal["roll", "pitch", "yaw", "latency"]
    correction_unit: Literal["degrees", "milliseconds"]
    configured_value: FiniteFloat = 0.0
    candidate_correction: FiniteFloat
    candidate_value: FiniteFloat
    runs: tuple[AcquisitionRun, AcquisitionRun]
    residual_axis: Literal["x", "y"]
    spatial_residual: tuple[PatchDatasetResidualPoint, ...]
    objective_rms_m: FiniteFloat = Field(ge=0.0)
    objective_curve: tuple[ObjectiveSample, ...]
    estimated_correction: FiniteFloat | None
    estimate_status: Literal["determined", "weak_or_flat", "boundary_minimum"]
    estimate_reasons: tuple[str, ...]
    state_semantics: str = (
        "Truth hidden; P3 Observed evidence immutable; candidate changes Configured "
        "reconstruction; residual and RMS Derived; bounded minimum Estimated"
    )


def _signature_config(config: PatchManualCalibrationConfig, correction: float) -> PatchSignatureConfig:
    values = config.model_dump(exclude={
        "ping_period_seconds", "sonar_id", "deterministic_seed",
        "executed_overlap_fraction", "steering_error_m", "candidate_correction",
        "search_min", "search_max", "search_steps",
    })
    if config.error_family == "latency":
        values["latency_residual_ms"] = float(config.latency_residual_ms) - correction
    else:
        values["angular_residual_deg"] = float(config.angular_residual_deg) - correction
    return PatchSignatureConfig(**values)


def _evaluate(config: PatchManualCalibrationConfig, correction: float):
    result = run_patch_signature_scenario(_signature_config(config, correction))
    residual = result.dataset_residuals
    rms = sqrt(sum(float(point.vertical_difference_m) ** 2 for point in residual) / len(residual)) if residual else 0.0
    return result, rms


def run_manual_calibration(config: PatchManualCalibrationConfig) -> PatchManualCalibrationResult:
    if config.error_family == "confounded":
        raise ValueError("P4 manual calibration accepts one classic parameter family at a time")

    acquisition = run_patch_acquisition(PatchAcquisitionConfig(**config.model_dump(exclude={
        "candidate_correction", "search_min", "search_max", "search_steps",
    })))
    candidate, candidate_rms = _evaluate(config, float(config.candidate_correction))

    low, high = float(config.search_min), float(config.search_max)
    corrections = [low + (high - low) * i / (config.search_steps - 1) for i in range(config.search_steps)]
    curve = tuple(ObjectiveSample(correction=value, rms_m=_evaluate(config, value)[1]) for value in corrections)
    minimum_index = min(range(len(curve)), key=lambda i: float(curve[i].rms_m))
    minimum = curve[minimum_index]
    reasons: list[str] = []
    if not candidate.evidence_sufficient or acquisition.fitness == "reacquire":
        status = "weak_or_flat"
        estimate = None
        reasons.append("acquisition geometry does not identify this parameter")
    elif minimum_index in {0, len(curve) - 1}:
        status = "boundary_minimum"
        estimate = None
        reasons.append("objective minimum lies on the declared search boundary")
    else:
        spread = max(float(item.rms_m) for item in curve) - min(float(item.rms_m) for item in curve)
        if spread <= 1e-9:
            status = "weak_or_flat"
            estimate = None
            reasons.append("objective is flat over the declared search interval")
        else:
            status = "determined"
            estimate = float(minimum.correction)

    return PatchManualCalibrationResult(
        acquisition_id=acquisition.acquisition_id,
        error_family=config.error_family,
        correction_unit="milliseconds" if config.error_family == "latency" else "degrees",
        candidate_correction=float(config.candidate_correction),
        candidate_value=float(config.candidate_correction),
        runs=acquisition.runs,
        residual_axis=candidate.dataset_residual_axis,
        spatial_residual=candidate.dataset_residuals,
        objective_rms_m=candidate_rms,
        objective_curve=curve,
        estimated_correction=estimate,
        estimate_status=status,
        estimate_reasons=tuple(reasons),
    )


__all__ = ["PatchManualCalibrationConfig", "PatchManualCalibrationResult", "run_manual_calibration"]

"""Immutable synthetic acquisition evidence for Patch Test P3.

The forward geometry is delegated to the canonical P1 scenario.  This module
adds acquisition identity, time ordering and provenance without estimating a
patch correction or mutating the generated observations.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.scenarios.patch_test_signatures import (
    PatchErrorFamily,
    PatchSignatureConfig,
    run_patch_signature_scenario,
)


class PatchAcquisitionConfig(PatchSignatureConfig):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ping_period_seconds: FiniteFloat = Field(default=0.25, gt=0.0, le=10.0)
    sonar_id: str = Field(default="hydrosim-mbes-01", min_length=1, max_length=80)
    deterministic_seed: int = Field(default=0, ge=0)
    executed_overlap_fraction: FiniteFloat = Field(default=1.0, ge=0.0, le=1.0)
    steering_error_m: FiniteFloat = Field(default=0.0, ge=0.0, le=1000.0)


class ObservedSample(BaseModel):
    """Locked measurement and its acquisition epoch; no hidden Truth fields."""

    model_config = ConfigDict(frozen=True)

    sample_index: int = Field(ge=0)
    ping_time_seconds: FiniteFloat = Field(ge=0.0)
    measured_x_m: FiniteFloat
    measured_y_m: FiniteFloat
    measured_z_m: FiniteFloat


class DerivedSounding(BaseModel):
    model_config = ConfigDict(frozen=True)

    sample_index: int = Field(ge=0)
    x_m: FiniteFloat
    y_m: FiniteFloat
    z_m: FiniteFloat


class AcquisitionRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    line_id: str
    heading_deg: FiniteFloat
    speed_mps: FiniteFloat
    observation_state: Literal["Observed/locked"] = "Observed/locked"
    observed: tuple[ObservedSample, ...]
    derived_soundings: tuple[DerivedSounding, ...]
    configuration_snapshot: dict[str, float | int | str]


class PatchAcquisitionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    acquisition_id: str
    error_family: PatchErrorFamily
    runs: tuple[AcquisitionRun, AcquisitionRun]
    fitness: Literal["usable", "marginal", "reacquire"]
    fitness_reasons: tuple[str, ...]
    common_support_fraction: FiniteFloat = Field(ge=0.0, le=1.0)
    residual_axis: Literal["x", "y"]
    residual_preview: tuple[dict[str, float], ...]
    truth_reference: str = Field(exclude=True)
    state_semantics: str = (
        "Truth reference hidden; measurements Observed/locked; configuration "
        "snapshot Configured; navigation-frame soundings and preview Derived; no estimate"
    )


def run_patch_acquisition(config: PatchAcquisitionConfig) -> PatchAcquisitionResult:
    """Acquire a deterministic pair and freeze observations plus provenance."""

    signature = run_patch_signature_scenario(PatchSignatureConfig(**config.model_dump(exclude={
        "ping_period_seconds", "sonar_id", "deterministic_seed",
        "executed_overlap_fraction", "steering_error_m",
    })))
    config_hash = sha256(config.model_dump_json().encode()).hexdigest()[:12]
    runs = []
    for run_number, source in enumerate(signature.runs, start=1):
        observed = tuple(
            ObservedSample(
                sample_index=index,
                ping_time_seconds=index * float(config.ping_period_seconds),
                measured_x_m=point.true_x_m,
                measured_y_m=point.true_y_m,
                measured_z_m=point.true_z_m,
            )
            for index, point in enumerate(source.points)
        )
        derived = tuple(
            DerivedSounding(
                sample_index=index,
                x_m=point.configured_x_m,
                y_m=point.configured_y_m,
                z_m=point.configured_z_m,
            )
            for index, point in enumerate(source.points)
        )
        runs.append(AcquisitionRun(
            run_id=f"{config_hash}-{run_number}",
            line_id=source.id,
            heading_deg=source.heading_deg,
            speed_mps=source.speed_mps,
            observed=observed,
            derived_soundings=derived,
            configuration_snapshot={
                "sonar_id": config.sonar_id,
                "ping_period_seconds": float(config.ping_period_seconds),
                "deterministic_seed": config.deterministic_seed,
                "configured_alignment_deg": 0.0,
                "configured_latency_ms": 0.0,
            },
        ))

    support = float(config.executed_overlap_fraction)
    reasons: list[str] = []
    if not signature.evidence_sufficient:
        reasons.append("target signature is not identifiable in the executed geometry")
    if support <= 0.0:
        reasons.append("paired runs have no executed common support")
    elif support < 0.5:
        reasons.append("executed common support is weak")
    if float(config.steering_error_m) > float(config.line_offset_m):
        reasons.append("line steering error exceeds the planned offset scale")

    if not signature.evidence_sufficient or support <= 0.0:
        fitness = "reacquire"
    elif support < 0.5 or reasons:
        fitness = "marginal"
    else:
        fitness = "usable"

    return PatchAcquisitionResult(
        acquisition_id=f"p3-{config_hash}",
        error_family=config.error_family,
        runs=(runs[0], runs[1]),
        fitness=fitness,
        fitness_reasons=tuple(reasons),
        common_support_fraction=support,
        residual_axis=signature.dataset_residual_axis,
        residual_preview=tuple({
            "coordinate_m": point.coordinate_m,
            "vertical_difference_m": point.vertical_difference_m,
        } for point in signature.dataset_residuals),
        truth_reference=f"hidden:{config_hash}",
    )


__all__ = ["PatchAcquisitionConfig", "PatchAcquisitionResult", "run_patch_acquisition"]

"""Application state for the Roll Calibration Patch Test submodule.

This module adds no new hydrographic physics. It wraps the existing deterministic
``hydrosim.scenarios.roll_offset`` scenario so a learner can adjust a configured
roll value, run the same scientific pipeline, inspect the residual swath, and
optionally check the estimate against the hidden Truth value.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.scenarios.roll_offset import (
    AlignmentConfig,
    AlignmentStateConfig,
    RollOffsetResult,
    RollOffsetScenarioConfig,
    RollOffsetSummary,
    run_roll_offset_scenario,
)


class RollPatchLessonControls(BaseModel):
    """Learner-controlled estimate for the roll calibration exercise."""

    model_config = ConfigDict(frozen=True)

    estimated_roll_deg: FiniteFloat = 0.0


class RollPatchLessonSnapshot(BaseModel):
    """Observable Patch Test state derived from the existing roll-offset scenario."""

    model_config = ConfigDict(frozen=True)

    estimated_roll_deg: FiniteFloat
    result: RollOffsetResult
    summary: RollOffsetSummary
    truth_roll_deg: FiniteFloat | None = None
    estimation_error_deg: FiniteFloat | None = None


def _scenario_with_estimate(
    scenario: RollOffsetScenarioConfig,
    estimated_roll_deg: float,
) -> RollOffsetScenarioConfig:
    """Return the same scenario with only Configured roll replaced by the learner estimate."""

    configured_alignment = scenario.configured.transducer_alignment
    replacement = AlignmentConfig(
        roll_deg=estimated_roll_deg,
        pitch_deg=configured_alignment.pitch_deg,
        yaw_deg=configured_alignment.yaw_deg,
    )
    configured = AlignmentStateConfig(transducer_alignment=replacement)
    return scenario.model_copy(update={"configured": configured})


def prepare_roll_patch_lesson_snapshot(
    scenario: RollOffsetScenarioConfig,
    controls: RollPatchLessonControls = RollPatchLessonControls(),
    *,
    reveal_truth: bool = False,
) -> RollPatchLessonSnapshot:
    """Run the existing roll-offset pipeline for a learner-supplied roll estimate.

    ``Truth`` remains hidden until ``reveal_truth`` is explicitly requested. The
    learner's estimate is represented as the scenario's Configured alignment, so
    all sounding and residual consequences are still produced by the canonical
    geometry/scenario implementation.
    """

    estimated = float(controls.estimated_roll_deg)
    evaluated_scenario = _scenario_with_estimate(scenario, estimated)
    result = run_roll_offset_scenario(evaluated_scenario)

    truth_roll_deg: float | None = None
    estimation_error_deg: float | None = None
    if reveal_truth:
        truth_roll_deg = float(scenario.truth.transducer_alignment.roll_deg)
        estimation_error_deg = estimated - truth_roll_deg

    return RollPatchLessonSnapshot(
        estimated_roll_deg=estimated,
        result=result,
        summary=result.summary,
        truth_roll_deg=truth_roll_deg,
        estimation_error_deg=estimation_error_deg,
    )

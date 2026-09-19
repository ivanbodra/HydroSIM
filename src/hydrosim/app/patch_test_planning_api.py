"""Application adapter for Patch Test P2 planning."""

from hydrosim.scenarios.patch_test_planning import (
    PatchPlanningConfig,
    PatchPlanningResult,
    evaluate_patch_test_plan,
)

PatchPlanningRequest = PatchPlanningConfig
PatchPlanningResponse = PatchPlanningResult


def prepare_patch_planning_response(request: PatchPlanningRequest) -> PatchPlanningResponse:
    """Return render-ready planning evidence from the scientific scenario."""

    return evaluate_patch_test_plan(request)


__all__ = [
    "PatchPlanningRequest",
    "PatchPlanningResponse",
    "prepare_patch_planning_response",
]

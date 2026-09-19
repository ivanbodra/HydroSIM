"""Application adapter for Patch Test P5 assessment and validation."""

from hydrosim.scenarios.patch_test_assessment import (
    PatchAssessmentConfig,
    PatchAssessmentResult,
    run_patch_assessment,
)

PatchAssessmentRequest = PatchAssessmentConfig
PatchAssessmentResponse = PatchAssessmentResult


def prepare_patch_assessment_response(request: PatchAssessmentRequest) -> PatchAssessmentResponse:
    return run_patch_assessment(request)


__all__ = ["PatchAssessmentRequest", "PatchAssessmentResponse", "prepare_patch_assessment_response"]

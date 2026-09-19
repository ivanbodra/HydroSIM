"""Application adapter for Patch Test P3 synthetic acquisition."""

from hydrosim.scenarios.patch_test_acquisition import (
    PatchAcquisitionConfig,
    PatchAcquisitionResult,
    run_patch_acquisition,
)

PatchAcquisitionRequest = PatchAcquisitionConfig
PatchAcquisitionResponse = PatchAcquisitionResult


def prepare_patch_acquisition_response(request: PatchAcquisitionRequest) -> PatchAcquisitionResponse:
    return run_patch_acquisition(request)


__all__ = ["PatchAcquisitionRequest", "PatchAcquisitionResponse", "prepare_patch_acquisition_response"]

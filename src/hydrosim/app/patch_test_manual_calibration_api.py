"""Application adapter for Patch Test P4 manual calibration."""

from hydrosim.scenarios.patch_test_manual_calibration import (
    PatchManualCalibrationConfig,
    PatchManualCalibrationResult,
    run_manual_calibration,
)

PatchManualCalibrationRequest = PatchManualCalibrationConfig
PatchManualCalibrationResponse = PatchManualCalibrationResult


def prepare_patch_manual_calibration_response(request: PatchManualCalibrationRequest) -> PatchManualCalibrationResponse:
    return run_manual_calibration(request)


__all__ = ["PatchManualCalibrationRequest", "PatchManualCalibrationResponse", "prepare_patch_manual_calibration_response"]

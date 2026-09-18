"""Application adapter for the Patch Test P1 signature explorer."""

from hydrosim.scenarios.patch_test_signatures import (
    PatchSignatureConfig,
    PatchSignatureResult,
    run_patch_signature_scenario,
)


PatchSignatureRequest = PatchSignatureConfig
PatchSignatureResponse = PatchSignatureResult


def prepare_patch_signature_response(request: PatchSignatureRequest) -> PatchSignatureResponse:
    """Return render-ready P1 geometry without duplicating scientific equations."""

    return run_patch_signature_scenario(request)


__all__ = [
    "PatchSignatureRequest",
    "PatchSignatureResponse",
    "prepare_patch_signature_response",
]

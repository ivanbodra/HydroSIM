"""Application adapter for the bounded P6 RISC visualization."""

from hydrosim.scenarios.patch_test_risc_visualization import (
    RiscVisualizationConfig,
    RiscVisualizationResult,
    run_risc_visualization,
)

RiscVisualizationRequest = RiscVisualizationConfig
RiscVisualizationResponse = RiscVisualizationResult


def prepare_risc_visualization_response(request: RiscVisualizationRequest) -> RiscVisualizationResponse:
    return run_risc_visualization(request)


__all__ = ["RiscVisualizationRequest", "RiscVisualizationResponse", "prepare_risc_visualization_response"]

from __future__ import annotations

from inspect import signature

from hydrosim.app.motion_lesson_page import build_motion_lesson
from hydrosim.app.propagation_lesson_page import build_propagation_lesson
from hydrosim.app.vessel_lesson import build_vessel_lesson
from hydrosim.visualization import PropagationExplorerControls, prepare_propagation_explorer_snapshot


def test_mature_page_builders_support_zero_argument_shell_contract():
    for builder in (build_propagation_lesson, build_vessel_lesson, build_motion_lesson):
        parameters = signature(builder).parameters
        assert tuple(parameters) == ("FigureCanvas",)
        assert parameters["FigureCanvas"].default is None


def test_propagation_builder_reuses_canonical_propagation_adapter():
    baseline = prepare_propagation_explorer_snapshot(PropagationExplorerControls())
    biased = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(processing_lower_layer_bias_mps=10.0)
    )

    assert len(baseline.beams) == len(biased.beams)
    assert tuple(beam.truth_sounding for beam in baseline.beams) == tuple(
        beam.truth_sounding for beam in biased.beams
    )
    assert max(beam.sounding_error_norm_m for beam in baseline.beams) == 0.0
    assert max(beam.sounding_error_norm_m for beam in biased.beams) > 0.0

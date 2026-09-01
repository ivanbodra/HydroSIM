from pathlib import Path

import pytest

from hydrosim.app.patch_roll_lesson import (
    RollPatchLessonControls,
    prepare_roll_patch_lesson_snapshot,
)
from hydrosim.scenarios.roll_offset import load_roll_offset_scenario, run_roll_offset_scenario


_SCENARIO = Path("scenarios/roll_offset_demo.yaml")


def test_default_roll_patch_state_reuses_existing_scenario_result():
    scenario = load_roll_offset_scenario(_SCENARIO)
    expected = run_roll_offset_scenario(scenario)

    snapshot = prepare_roll_patch_lesson_snapshot(scenario)

    assert snapshot.result == expected
    assert snapshot.summary == expected.summary
    assert snapshot.truth_roll_deg is None
    assert snapshot.estimation_error_deg is None


def test_truth_remains_hidden_until_solution_check():
    scenario = load_roll_offset_scenario(_SCENARIO)
    controls = RollPatchLessonControls(estimated_roll_deg=0.25)

    hidden = prepare_roll_patch_lesson_snapshot(scenario, controls)
    checked = prepare_roll_patch_lesson_snapshot(scenario, controls, reveal_truth=True)

    assert hidden.truth_roll_deg is None
    assert checked.truth_roll_deg == pytest.approx(0.5)
    assert checked.estimation_error_deg == pytest.approx(-0.25)


def test_matching_truth_roll_removes_roll_offset_residuals():
    scenario = load_roll_offset_scenario(_SCENARIO)
    truth_roll = float(scenario.truth.transducer_alignment.roll_deg)

    snapshot = prepare_roll_patch_lesson_snapshot(
        scenario,
        RollPatchLessonControls(estimated_roll_deg=truth_roll),
        reveal_truth=True,
    )

    assert snapshot.estimation_error_deg == pytest.approx(0.0)
    assert snapshot.summary.max_error_magnitude == pytest.approx(0.0, abs=1e-10)
    assert snapshot.summary.rms_horizontal_error == pytest.approx(0.0, abs=1e-10)
    assert snapshot.summary.rms_vertical_error == pytest.approx(0.0, abs=1e-10)


def test_estimate_changes_only_configured_roll_semantics():
    scenario = load_roll_offset_scenario(_SCENARIO)
    controls = RollPatchLessonControls(estimated_roll_deg=-0.75)

    snapshot = prepare_roll_patch_lesson_snapshot(scenario, controls, reveal_truth=True)

    assert snapshot.estimated_roll_deg == pytest.approx(-0.75)
    assert snapshot.truth_roll_deg == pytest.approx(
        float(scenario.truth.transducer_alignment.roll_deg)
    )
    assert snapshot.result.scenario_id == scenario.scenario.id
    assert snapshot.result.random_seed == scenario.random_seed

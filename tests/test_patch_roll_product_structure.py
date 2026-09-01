from pathlib import Path

from hydrosim.product.structure import find_submodule


def test_roll_calibration_canonical_submodule_has_complete_object_inventory():
    submodule = find_submodule("roll-calibration")

    assert submodule.name == "Roll Calibration"
    assert tuple(item.id for item in submodule.items) == (
        "scenario",
        "hidden-bias",
        "swath-output",
        "adjustment",
        "estimated",
        "truth-estimated",
        "run-reset-check",
    )


def test_roll_patch_adapter_consumes_existing_scientific_scenario():
    source = Path("src/hydrosim/app/patch_roll_lesson.py").read_text(encoding="utf-8")

    assert "run_roll_offset_scenario" in source
    assert "RollOffsetScenarioConfig" in source
    assert "RollPatchLessonControls" in source
    assert "RollPatchLessonSnapshot" in source
    assert "estimated_roll_deg" in source
    assert "reveal_truth" in source
    assert "Truth" in source

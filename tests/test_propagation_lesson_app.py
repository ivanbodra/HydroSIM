from pathlib import Path


def test_propagation_lesson_reuses_existing_explorer_and_single_control() -> None:
    source = Path("src/hydrosim/app/propagation_lesson.py").read_text(encoding="utf-8")

    assert "prepare_propagation_explorer_snapshot" in source
    assert "draw_layered_svp_explorer_snapshot" in source
    controls_block = source.split("controls = {", 1)[1].split("return page", 1)[0]
    assert '"processing_bias"' in controls_block
    assert '"processing_bias_slider"' in controls_block
    for excluded in ("frequency", "roll", "pitch", "yaw", "heave"):
        assert f'"{excluded}"' not in controls_block


def test_propagation_language_switch_does_not_change_processing_bias() -> None:
    source = Path("src/hydrosim/app/propagation_lesson.py").read_text(encoding="utf-8")

    language_function = source.split("def apply_language(locale: str)", 1)[1].split(
        'apply_language("en")', 1
    )[0]
    assert "setValue(" not in language_function
    assert "page.setProperty" in language_function


def test_propagation_readout_keeps_truth_and_processing_quantities_explicit() -> None:
    source = Path("src/hydrosim/app/propagation_lesson.py").read_text(encoding="utf-8")

    assert "propagation.truth_lower_layer" in source
    assert "propagation.processing_lower_layer" in source
    assert "propagation.max_error" in source

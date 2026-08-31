from pathlib import Path


def _signal_source() -> str:
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")
    return source.split("# Signal lesson", 1)[1].split("# Beam lesson", 1)[0]


def test_signal_page_wires_existing_pedagogical_comparison_model():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    assert "SignalLessonSnapshot" in source
    assert "SignalLessonComparison" in source
    assert "signal_set_baseline" in source
    assert "signal_clear_baseline" in source
    assert "signal_comparison_readout" in source


def test_signal_baseline_captures_only_visible_duration_and_bandwidth_controls():
    signal = _signal_source()
    snapshot_function = signal.split("def current_signal_snapshot()", 1)[1].split(
        "def update_signal_comparison_display()", 1
    )[0]

    assert "duration.value()" in snapshot_function
    assert "bandwidth.value()" in snapshot_function
    assert "center_frequency" not in snapshot_function


def test_signal_reset_does_not_redefine_or_clear_baseline():
    signal = _signal_source()
    reset_function = signal.split("def reset_signal()", 1)[1].split(
        "signal_set_baseline.clicked.connect", 1
    )[0]

    assert "signal_baseline" not in reset_function


def test_language_switch_updates_presentation_without_mutating_baseline():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")
    language_function = source.split("def apply_language(locale: str)", 1)[1].split(
        "def on_language_changed", 1
    )[0]

    assert "update_signal_comparison_display()" in language_function
    assert "signal_baseline =" not in language_function


def test_current_control_redraw_refreshes_comparison_without_replacing_baseline():
    signal = _signal_source()
    redraw_function = signal.split("def redraw_signal()", 1)[1].split(
        "duration.valueChanged.connect", 1
    )[0]

    assert "update_signal_comparison_display()" in redraw_function
    assert "signal_baseline =" not in redraw_function

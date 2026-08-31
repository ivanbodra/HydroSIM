from pathlib import Path


def _signal_source() -> str:
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")
    return source.split("# Signal lesson", 1)[1].split("# Beam lesson", 1)[0]


def test_signal_page_keeps_visualization_first_compact_shell() -> None:
    signal = _signal_source()

    assert "navigation.setMaximumWidth(165)" in Path(
        "src/hydrosim/app/didactic_explorer.py"
    ).read_text(encoding="utf-8")
    assert "controls_frame.setMaximumWidth(255)" in signal
    assert "baseline_hint.setVisible(False)" in signal
    assert "question_layout = QHBoxLayout(question_frame)" in signal
    assert "signal_readout.setText(" in signal
    assert "T={state.duration_seconds * 1e3:.1f} ms · " in signal


def test_signal_footer_stays_compact_without_losing_boundary_or_comparison() -> None:
    signal = _signal_source()

    assert "quantitative_layout.setContentsMargins(8, 6, 8, 6)" in signal
    assert "boundary_layout.setContentsMargins(8, 6, 8, 6)" in signal
    assert "signal_comparison_readout.setStyleSheet(\"font-size: 10px;\")" in signal
    assert "signal.baseline_note" in signal
    assert "signal.scientific_boundary" in signal

from pathlib import Path


def _renderer_source() -> str:
    return Path("src/hydrosim/visualization/signal_explorer_plot.py").read_text(encoding="utf-8")


def test_signal_renderer_prioritizes_waveform_over_supporting_views():
    source = _renderer_source()

    assert "figure.add_gridspec(2, 2" in source
    assert "figure.add_subplot(grid[0, :])" in source
    assert "figure.add_subplot(grid[1, 0])" in source
    assert "figure.add_subplot(grid[1, 1])" in source


def test_signal_renderer_avoids_redundant_embedded_figure_title():
    source = _renderer_source()

    assert ".suptitle(" not in source
    assert 'set_title("Transmitted waveform")' in source
    assert 'set_title("Phase evolution")' in source
    assert 'set_title("Pulse-compression response")' in source


def test_signal_renderer_keeps_readable_scientific_axes():
    source = _renderer_source()

    assert 'set_ylabel("In-phase baseband")' in source
    assert 'set_ylabel("Phase (rad)")' in source
    assert 'set_ylabel("Normalized amplitude")' in source
    assert "waveform_axis.grid(alpha=0.18)" in source
    assert "phase_axis.grid(alpha=0.18)" in source
    assert "matched_axis.grid(alpha=0.18)" in source

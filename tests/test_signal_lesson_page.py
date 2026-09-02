from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_signal_lesson_uses_canonical_passband_and_signed_lfm_direction():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from hydrosim.app.signal_lesson_page import build_signal_lesson

    app = QApplication.instance() or QApplication([])
    page, controls, apply_language = build_signal_lesson()

    assert page is not None
    assert controls["bandwidth"].isEnabled() is False
    assert controls["direction"].isEnabled() is False

    controls["pulse_type"].setCurrentIndex(1)
    controls["direction"].setCurrentIndex(1)
    controls["envelope"].setCurrentIndex(1)
    app.processEvents()

    assert controls["bandwidth"].isEnabled() is True
    assert controls["direction"].isEnabled() is True

    axes = controls["figure"].axes
    assert len(axes) == 4
    assert "passband" in axes[0].get_title().lower()
    assert "passband" in axes[1].get_title().lower()
    assert "processing" in axes[3].get_title().lower()

    instantaneous_frequency_lines = axes[2].lines
    assert len(instantaneous_frequency_lines) == 2
    cw_frequency = instantaneous_frequency_lines[0].get_ydata()
    lfm_frequency = instantaneous_frequency_lines[1].get_ydata()
    assert cw_frequency[0] == pytest.approx(cw_frequency[-1])
    assert lfm_frequency[0] > lfm_frequency[-1]

    apply_language("pt-BR")
    app.processEvents()
    assert "frequência instantânea" in axes[2].get_title().lower()

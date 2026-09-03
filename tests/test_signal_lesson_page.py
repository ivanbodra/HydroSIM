from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_signal_lesson_matches_current_three_stage_concept_lab():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from hydrosim.app.signal_lesson_page import build_signal_lesson

    app = QApplication.instance() or QApplication([])
    page, controls, apply_language = build_signal_lesson()

    assert page is not None
    assert controls["bandwidth"].isEnabled() is True
    assert controls["direction"].isEnabled() is True

    axes = controls["figure"].axes
    assert len(axes) == 3
    assert "waveform" in axes[0].get_title().lower()
    assert "echo" in axes[1].get_title().lower()
    assert "matched-filter" in axes[2].get_title().lower()

    controls["cw"].click()
    app.processEvents()
    assert controls["bandwidth"].isEnabled() is False
    assert controls["direction"].isEnabled() is False

    controls["chirp"].click()
    controls["direction"].setCurrentIndex(1)
    controls["envelope"].setCurrentIndex(1)
    app.processEvents()
    assert controls["bandwidth"].isEnabled() is True
    assert controls["direction"].isEnabled() is True

    apply_language("pt-BR")
    app.processEvents()
    assert "forma de onda" in axes[0].get_title().lower()
    assert "eco" in axes[1].get_title().lower()
    assert "filtro casado" in axes[2].get_title().lower()

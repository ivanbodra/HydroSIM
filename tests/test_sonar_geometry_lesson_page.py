from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_sonar_geometry_lesson_preserves_d7_semantic_separations():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from hydrosim.app.sonar_geometry_lesson_page import build_sonar_geometry_lesson

    app = QApplication.instance() or QApplication([])
    page, controls, apply_language = build_sonar_geometry_lesson()
    assert page is not None

    axes = controls["figure"].axes
    assert len(axes) == 4
    assert "SBES" in axes[0].get_title()
    assert "RX fan" in axes[1].get_title()
    assert "TX sectors" in axes[2].get_title()
    assert "derived" in axes[3].get_title()

    controls["swath"].setValue(130.0)
    controls["cant"].setValue(25.0)
    app.processEvents()
    assert "union=" in axes[3].get_title()
    assert len(axes[3].texts) == 2

    apply_language("pt-BR")
    app.processEvents()
    assert "Setores TX" in axes[2].get_title()
    assert "cobertura combinada" in axes[3].get_title()

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_sounding_formation_lesson_uses_canonical_stage_state_and_semantics():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from hydrosim.app.sounding_formation import SoundingFormationStage
    from hydrosim.app.sounding_formation_lesson_page import build_sounding_formation_lesson

    app = QApplication.instance() or QApplication([])
    page, controls, apply_language = build_sounding_formation_lesson()
    assert page is not None

    snapshot = controls["snapshot"]()
    assert snapshot.active_stage == SoundingFormationStage.TRANSMIT
    assert len(controls["stage_labels"]) == 10
    assert "BottomDetection" in controls["semantics"].text()
    assert "Derived/reference" in controls["semantics"].text()
    assert "Observed sounding" not in controls["semantics"].text()

    controls["next"].click()
    app.processEvents()
    assert controls["snapshot"]().active_stage == SoundingFormationStage.PROPAGATION

    for _ in range(8):
        controls["next"].click()
    app.processEvents()
    final_snapshot = controls["snapshot"]()
    assert final_snapshot.active_stage == SoundingFormationStage.TRUTH_OBSERVED
    assert "BottomDetection" in controls["readout"].text()
    assert "Derived/reference" in controls["readout"].text()
    assert "Truth sounding" in controls["readout"].text()

    controls["reset"].click()
    app.processEvents()
    assert controls["snapshot"]().active_stage == SoundingFormationStage.TRANSMIT

    apply_language("pt-BR")
    app.processEvents()
    assert "Formação da Sondagem" in controls["stage_labels"][0].window().windowTitle() or controls["stage_labels"][0].text() == "Transmissão"
    assert controls["stage_labels"][0].text() == "Transmissão"
    assert "Medição observada" in controls["semantics"].text()
    assert "Reconstrução derivada" in controls["semantics"].text()


def test_sounding_formation_run_saturates_at_final_stage_without_mutating_science():
    pytest.importorskip("PySide6")
    from PySide6.QtWidgets import QApplication

    from hydrosim.app.sounding_formation import SoundingFormationStage
    from hydrosim.app.sounding_formation_lesson_page import build_sounding_formation_lesson

    app = QApplication.instance() or QApplication([])
    _page, controls, _apply_language = build_sounding_formation_lesson()
    initial = controls["snapshot"]()

    for _ in range(12):
        controls["next"].click()
    app.processEvents()
    final = controls["snapshot"]()

    assert final.active_stage == SoundingFormationStage.TRUTH_OBSERVED
    assert final.ping == initial.ping
    assert final.detection == initial.detection
    assert final.sounding == initial.sounding

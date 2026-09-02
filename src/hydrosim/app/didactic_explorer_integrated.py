"""Integrated HydroSIM Didactic Explorer launcher.

The mature base shell remains the owner of navigation and established lessons.
This wrapper replaces D1 with the canonical Signal experience and inserts later
lesson pages without duplicating scientific logic in presentation code.
"""

from __future__ import annotations

from hydrosim.app.didactic_explorer import launch_didactic_explorer as _launch_base
from hydrosim.app.signal_lesson_page import build_signal_lesson
from hydrosim.app.sonar_equation_lesson_page import build_sonar_equation_lesson
from hydrosim.app.sonar_geometry_lesson_page import build_sonar_geometry_lesson
from hydrosim.app.sounding_formation_lesson_page import build_sounding_formation_lesson

_NAV = {
    "en": (
        "Signal", "Beam", "Sonar Equation", "Propagation", "Vessel", "Motion",
        "Sonar Systems", "Sounding Formation",
    ),
    "pt-BR": (
        "Sinal", "Feixe", "Equação Sonar", "Propagação", "Embarcação", "Movimento",
        "Sistemas Sonar", "Formação da Sondagem",
    ),
}
_READY = {"en": "ready", "pt-BR": "disponível"}


def launch_didactic_explorer() -> None:
    """Launch the real shell with corrected D1 plus integrated D3, D7, and D8."""

    try:
        from PySide6.QtCore import QTimer, Qt
        from PySide6.QtWidgets import QApplication, QListWidgetItem
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PySide6 is required for the HydroSIM desktop shell; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    app = QApplication.instance() or QApplication([])

    def integrate_lessons() -> None:
        window = getattr(app, "hydrosim_didactic_explorer_window", None)
        if window is None:
            raise RuntimeError("Base Didactic Explorer window was not created")
        if hasattr(window, "hydrosim_sounding_formation_controls"):
            return

        signal_page, signal_controls, apply_signal_language = build_signal_lesson()
        old_signal_page = window.hydrosim_pages.widget(0)
        window.hydrosim_pages.removeWidget(old_signal_page)
        old_signal_page.deleteLater()
        window.hydrosim_pages.insertWidget(0, signal_page)

        page, sonar_controls, apply_sonar_language = build_sonar_equation_lesson()
        window.hydrosim_pages.insertWidget(2, page)
        nav_item = QListWidgetItem()
        nav_item.setData(Qt.ItemDataRole.UserRole, "Sonar Equation")
        window.hydrosim_navigation.insertItem(2, nav_item)

        geometry_page, geometry_controls, apply_geometry_language = build_sonar_geometry_lesson()
        window.hydrosim_pages.addWidget(geometry_page)
        geometry_item = QListWidgetItem()
        geometry_item.setData(Qt.ItemDataRole.UserRole, "Sonar Systems")
        window.hydrosim_navigation.addItem(geometry_item)

        sounding_page, sounding_controls, apply_sounding_language = build_sounding_formation_lesson()
        window.hydrosim_pages.addWidget(sounding_page)
        sounding_item = QListWidgetItem()
        sounding_item.setData(Qt.ItemDataRole.UserRole, "Sounding Formation")
        window.hydrosim_navigation.addItem(sounding_item)

        def apply_integrated_language(locale: str) -> None:
            locale = locale if locale in _NAV else "en"
            ready = _READY[locale]
            for index, label in enumerate(_NAV[locale]):
                window.hydrosim_navigation.item(index).setText(f"{label}  • {ready}")
            apply_signal_language(locale)
            apply_sonar_language(locale)
            apply_geometry_language(locale)
            apply_sounding_language(locale)

        selector = window.hydrosim_language_selector
        selector.currentIndexChanged.connect(
            lambda _index: apply_integrated_language(str(selector.currentData() or "en"))
        )
        apply_integrated_language(str(selector.currentData() or "en"))

        window.hydrosim_signal_lesson_controls = signal_controls
        window.hydrosim_apply_signal_lesson_language = apply_signal_language
        window.hydrosim_sonar_equation_controls = sonar_controls
        window.hydrosim_apply_sonar_equation_language = apply_sonar_language
        window.hydrosim_sonar_geometry_controls = geometry_controls
        window.hydrosim_apply_sonar_geometry_language = apply_geometry_language
        window.hydrosim_sounding_formation_controls = sounding_controls
        window.hydrosim_apply_sounding_formation_language = apply_sounding_language

    QTimer.singleShot(0, integrate_lessons)
    _launch_base()

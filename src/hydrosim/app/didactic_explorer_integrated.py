"""Integrated HydroSIM Didactic Explorer launcher.

The mature base shell remains the owner of navigation and established lessons.
This wrapper replaces D1 with the canonical Signal experience and inserts D3,
without duplicating scientific logic in presentation code.
"""

from __future__ import annotations

from hydrosim.app.didactic_explorer import launch_didactic_explorer as _launch_base
from hydrosim.app.signal_lesson_page import build_signal_lesson
from hydrosim.app.sonar_equation_lesson_page import build_sonar_equation_lesson

_NAV = {
    "en": ("Signal", "Beam", "Sonar Equation", "Propagation", "Vessel", "Motion"),
    "pt-BR": ("Sinal", "Feixe", "Equação Sonar", "Propagação", "Embarcação", "Movimento"),
}
_READY = {"en": "ready", "pt-BR": "disponível"}


def launch_didactic_explorer() -> None:
    """Launch the real shell with corrected D1 and integrated D3."""

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
        if hasattr(window, "hydrosim_signal_lesson_controls"):
            return

        signal_page, signal_controls, apply_signal_language = build_signal_lesson()
        old_signal_page = window.hydrosim_pages.widget(0)
        window.hydrosim_pages.removeWidget(old_signal_page)
        old_signal_page.deleteLater()
        window.hydrosim_pages.insertWidget(0, signal_page)

        sonar_page, sonar_controls, apply_sonar_language = build_sonar_equation_lesson()
        window.hydrosim_pages.insertWidget(2, sonar_page)
        nav_item = QListWidgetItem()
        nav_item.setData(Qt.ItemDataRole.UserRole, "Sonar Equation")
        window.hydrosim_navigation.insertItem(2, nav_item)

        def apply_integrated_language(locale: str) -> None:
            locale = locale if locale in _NAV else "en"
            ready = _READY[locale]
            for index, label in enumerate(_NAV[locale]):
                window.hydrosim_navigation.item(index).setText(f"{label}  • {ready}")
            apply_signal_language(locale)
            apply_sonar_language(locale)

        selector = window.hydrosim_language_selector
        selector.currentIndexChanged.connect(
            lambda _index: apply_integrated_language(str(selector.currentData() or "en"))
        )
        apply_integrated_language(str(selector.currentData() or "en"))

        window.hydrosim_signal_lesson_controls = signal_controls
        window.hydrosim_apply_signal_lesson_language = apply_signal_language
        window.hydrosim_sonar_equation_controls = sonar_controls
        window.hydrosim_apply_sonar_equation_language = apply_sonar_language

    QTimer.singleShot(0, integrate_lessons)
    _launch_base()

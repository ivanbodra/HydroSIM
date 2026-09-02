"""Integrated Didactic Explorer launcher including the D3 Sonar Equation lesson.

The existing shell remains the owner of the five established lessons. This wrapper
adds D3 through the same Qt application instance without duplicating scientific
logic or rewriting the mature shell while the lesson inventory is still growing.
"""

from __future__ import annotations

from hydrosim.app.didactic_explorer import launch_didactic_explorer as _launch_base
from hydrosim.app.sonar_equation_lesson_page import build_sonar_equation_lesson

_NAV = {
    "en": ("Signal", "Beam", "Sonar Equation", "Propagation", "Vessel", "Motion"),
    "pt-BR": ("Sinal", "Feixe", "Equação Sonar", "Propagação", "Embarcação", "Movimento"),
}
_READY = {"en": "ready", "pt-BR": "disponível"}


def launch_didactic_explorer() -> None:
    """Launch the real shell with D3 inserted after Beam."""

    try:
        from PySide6.QtCore import QTimer, Qt
        from PySide6.QtWidgets import QApplication, QListWidgetItem
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PySide6 is required for the HydroSIM desktop shell; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    app = QApplication.instance() or QApplication([])

    def integrate_d3() -> None:
        window = getattr(app, "hydrosim_didactic_explorer_window", None)
        if window is None:
            raise RuntimeError("Base Didactic Explorer window was not created")
        if hasattr(window, "hydrosim_sonar_equation_controls"):
            return

        page, controls, apply_page_language = build_sonar_equation_lesson()
        window.hydrosim_pages.insertWidget(2, page)
        nav_item = QListWidgetItem()
        nav_item.setData(Qt.ItemDataRole.UserRole, "Sonar Equation")
        window.hydrosim_navigation.insertItem(2, nav_item)

        def apply_integrated_language(locale: str) -> None:
            locale = locale if locale in _NAV else "en"
            ready = _READY[locale]
            for index, label in enumerate(_NAV[locale]):
                window.hydrosim_navigation.item(index).setText(f"{label}  • {ready}")
            apply_page_language(locale)

        selector = window.hydrosim_language_selector
        selector.currentIndexChanged.connect(
            lambda _index: apply_integrated_language(str(selector.currentData() or "en"))
        )
        apply_integrated_language(str(selector.currentData() or "en"))

        window.hydrosim_sonar_equation_controls = controls
        window.hydrosim_apply_sonar_equation_language = apply_page_language

    QTimer.singleShot(0, integrate_d3)
    _launch_base()

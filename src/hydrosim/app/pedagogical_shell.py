"""Bilingual production shell for the pedagogical HydroSIM generation."""

from __future__ import annotations

from importlib import import_module
from inspect import signature

from hydrosim.app.pedagogical_catalog import PEDAGOGICAL_EXPERIENCES, experiences_for

_TEXT = {
    "en": {
        "title": "HydroSIM — Virtual Hydrographic Laboratory",
        "tagline": "Choose a learning experience from the system map.",
        "home": "System Map",
        "didactic": "Didactic Module",
        "patch-test": "Patch Test",
        "acquisition": "Acquisition Simulator",
        "available": "Available",
        "coming-soon": "Coming soon",
        "unavailable_body": "This experience is visible in the product map but is not yet released.",
        "language": "Language",
    },
    "pt-BR": {
        "title": "HydroSIM — Laboratório Hidrográfico Virtual",
        "tagline": "Escolha uma experiência de aprendizagem no mapa do sistema.",
        "home": "Mapa do Sistema",
        "didactic": "Módulo Didático",
        "patch-test": "Patch Test",
        "acquisition": "Simulador de Aquisição",
        "available": "Disponível",
        "coming-soon": "Em breve",
        "unavailable_body": "Esta experiência já faz parte do mapa do produto, mas ainda não foi liberada.",
        "language": "Idioma",
    },
}

_TERM_HELP_PT = {
    "Roll": "rotação da embarcação em torno do eixo longitudinal",
    "Pitch": "rotação da embarcação em torno do eixo transversal",
    "Heave": "movimento vertical da embarcação",
    "Yaw": "rotação em torno do eixo vertical; relacionada à orientação horizontal",
    "Heading": "direção para a qual a proa está orientada",
}


def _resolve_builder(path: str):
    module_name, function_name = path.rsplit(".", 1)
    return getattr(import_module(module_name), function_name)


def _invoke_builder(builder, FigureCanvas):
    """Invoke a reusable lesson builder with its declared presentation dependency.

    Most current builders own their canvas import and take no arguments. The
    Motion builder predates that convention and explicitly requires the Qt
    FigureCanvas type. Keep the shell compatible with both contracts without
    catching unrelated TypeError exceptions raised inside a builder.
    """

    parameters = signature(builder).parameters
    if "FigureCanvas" in parameters:
        return builder(FigureCanvas)
    return builder()


def launch_pedagogical_shell() -> None:
    """Launch the 31-experience HydroSIM system map and available lessons."""

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QScrollArea,
            QStackedWidget,
            QVBoxLayout,
            QWidget,
        )
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PySide6 and Matplotlib are required for the HydroSIM desktop shell; "
            "install the visualization extra"
        ) from exc

    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    window.resize(1480, 900)
    window.setStyleSheet(
        "QMainWindow { background: #07121d; }"
        "QLabel { color: #eaf2f7; }"
        "QPushButton { background: #102535; color: #eaf2f7; border: 1px solid #29485c; "
        "border-radius: 9px; padding: 9px 12px; text-align: left; }"
        "QPushButton:hover { background: #173247; }"
        "QPushButton:disabled { color: #718796; background: #0b1924; border-color: #183040; }"
        "QComboBox { background: #102535; color: #eaf2f7; padding: 5px; }"
    )

    central = QWidget()
    root = QVBoxLayout(central)
    root.setContentsMargins(18, 14, 18, 16)
    root.setSpacing(12)

    header = QHBoxLayout()
    header_text = QVBoxLayout()
    title = QLabel()
    title.setStyleSheet("font-size: 24px; font-weight: 700;")
    tagline = QLabel()
    tagline.setStyleSheet("color: #8fa9ba; font-size: 12px;")
    header_text.addWidget(title)
    header_text.addWidget(tagline)
    header.addLayout(header_text)
    header.addStretch(1)
    language_label = QLabel()
    language_selector = QComboBox()
    language_selector.addItem("EN", "en")
    language_selector.addItem("PT-BR", "pt-BR")
    header.addWidget(language_label)
    header.addWidget(language_selector)
    root.addLayout(header)

    pages = QStackedWidget()
    root.addWidget(pages, 1)

    home = QWidget()
    home_root = QVBoxLayout(home)
    home_root.setContentsMargins(0, 4, 0, 0)
    intro = QLabel()
    intro.setWordWrap(True)
    intro.setStyleSheet("font-size: 15px; color: #b7c9d5;")
    home_root.addWidget(intro)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    map_widget = QWidget()
    map_grid = QGridLayout(map_widget)
    map_grid.setHorizontalSpacing(12)
    map_grid.setVerticalSpacing(8)
    scroll.setWidget(map_widget)
    home_root.addWidget(scroll, 1)
    pages.addWidget(home)

    module_labels = {}
    buttons = {}
    lesson_pages = {}
    lesson_localizers = {}

    for column, module_id in enumerate(("didactic", "patch-test", "acquisition")):
        heading = QLabel()
        heading.setStyleSheet("font-size: 17px; font-weight: 700; padding: 8px 2px;")
        map_grid.addWidget(heading, 0, column)
        module_labels[module_id] = heading
        for row, experience in enumerate(experiences_for(module_id), start=1):
            button = QPushButton()
            button.setMinimumHeight(50)
            button.setEnabled(experience.availability == "available")
            buttons[experience.id] = button
            map_grid.addWidget(button, row, column)

            if experience.availability == "available" and experience.page_builder:
                builder = _resolve_builder(experience.page_builder)
                page, _controls, apply_language = _invoke_builder(builder, FigureCanvas)
                pages.addWidget(page)
                lesson_pages[experience.id] = page
                lesson_localizers[experience.id] = apply_language
                button.clicked.connect(lambda _checked=False, p=page: pages.setCurrentWidget(p))
            else:
                # Disabled cards remain visible and truthfully unavailable.
                button.clicked.connect(lambda _checked=False: None)

    def apply_language(locale: str) -> None:
        locale = locale if locale in _TEXT else "en"
        text = _TEXT[locale]
        title.setText(text["title"])
        tagline.setText(text["tagline"])
        language_label.setText(text["language"])
        intro.setText(
            "INPUT → IMMEDIATE VISUAL RESPONSE → PHYSICAL INTUITION"
            if locale == "en"
            else "ENTRADA → RESPOSTA VISUAL IMEDIATA → INTUIÇÃO FÍSICA"
        )
        for module_id, label in module_labels.items():
            label.setText(text[module_id])
        for experience in PEDAGOGICAL_EXPERIENCES:
            status = text[experience.availability]
            buttons[experience.id].setText(f"{experience.id}  ·  {experience.name(locale)}\n{status}")
        if locale == "pt-BR":
            buttons["PED-D12"].setToolTip(
                "Roll — " + _TERM_HELP_PT["Roll"] + "\n"
                "Pitch — " + _TERM_HELP_PT["Pitch"] + "\n"
                "Heave — " + _TERM_HELP_PT["Heave"] + "\n"
                "Yaw — " + _TERM_HELP_PT["Yaw"]
            )
        else:
            buttons["PED-D12"].setToolTip("")
        for localize in lesson_localizers.values():
            localize(locale)

    language_selector.currentIndexChanged.connect(
        lambda _index: apply_language(str(language_selector.currentData() or "en"))
    )
    apply_language("en")

    window.setCentralWidget(central)
    window.hydrosim_pedagogical_pages = pages
    window.hydrosim_pedagogical_buttons = buttons
    window.hydrosim_language_selector = language_selector
    window.hydrosim_apply_language = apply_language
    window.hydrosim_pedagogical_experiences = PEDAGOGICAL_EXPERIENCES
    app.hydrosim_pedagogical_shell_window = window
    window.show()
    app.exec()

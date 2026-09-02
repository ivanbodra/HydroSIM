"""Reusable PySide6 page for the D4 Sound Speed & Refraction lesson."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hydrosim.app.localization import Localizer
from hydrosim.visualization import (
    PropagationExplorerControls,
    draw_layered_svp_explorer_snapshot,
    prepare_propagation_explorer_snapshot,
)
from hydrosim.visualization.layered_svp_explorer_plot import plot_layered_svp_explorer_snapshot

_DEFAULTS = PropagationExplorerControls()

_TEXT = {
    "en": {
        "scientific_view": (
            "Stationary monostatic principal-plane geometry, flat bottom, two piecewise-constant "
            "layers, ideal transducer sound speed, and zero array tilt."
        ),
        "instruction": (
            "Change only the processing sound-speed bias. Truth rays stay fixed; watch where the "
            "reconstructed soundings move and how beamwise error grows toward the swath edges."
        ),
        "bias": "Processing lower-layer bias",
        "truth_lower": "Truth lower layer",
        "processing_lower": "Processing lower layer",
        "max_error": "Max sounding error",
        "observation": (
            "The Truth SVP and rays do not change when this control moves. Only the processing "
            "profile changes. A profile mismatch can curve or displace the reconstructed swath "
            "even though the real seabed is flat."
        ),
        "boundary": (
            "Two piecewise-constant layers with deterministic Snell-law propagation and the "
            "existing sounding-reconstruction adapter."
        ),
        "not_shown": (
            "Frequency-dependent absorption, continuous-gradient SVP, surface sound-speed error, "
            "vessel motion, and uncertainty are outside this lesson."
        ),
    },
    "pt-BR": {
        "scientific_view": (
            "Geometria monostática estacionária no plano principal, fundo plano, duas camadas de "
            "velocidade constante por trechos, velocidade ideal no transdutor e inclinação zero do array."
        ),
        "instruction": (
            "Altere apenas o erro de velocidade do som usado no processamento. Os raios de Truth "
            "permanecem fixos; observe o deslocamento das sondagens reconstruídas e o crescimento "
            "do erro por feixe em direção às bordas da faixa."
        ),
        "bias": "Erro na camada inferior do processamento",
        "truth_lower": "Camada inferior de Truth",
        "processing_lower": "Camada inferior do processamento",
        "max_error": "Erro máximo da sondagem",
        "observation": (
            "O SVP e os raios de Truth não mudam quando este controle é alterado. Apenas o perfil "
            "de processamento muda. Um SVP incorreto pode curvar ou deslocar a faixa reconstruída "
            "mesmo quando o fundo real é plano."
        ),
        "boundary": (
            "Duas camadas constantes por trechos, propagação determinística pela lei de Snell e o "
            "adapter existente de reconstrução da sondagem."
        ),
        "not_shown": (
            "Absorção dependente da frequência, SVP com gradiente contínuo, erro de velocidade do "
            "som na superfície, movimento da embarcação e incerteza estão fora desta aula."
        ),
    },
}


def build_propagation_lesson(
    FigureCanvas: type[Any] | None = None,
) -> tuple[Any, dict[str, Any], Callable[[str], None]]:
    """Build D4 as a standalone bilingual page without duplicating scientific models."""

    if FigureCanvas is None:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDoubleSpinBox,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSlider,
        QVBoxLayout,
        QWidget,
    )

    page = QWidget()
    root = QVBoxLayout(page)
    root.setContentsMargins(8, 2, 4, 2)
    root.setSpacing(6)

    heading = QLabel()
    heading.setStyleSheet("font-size: 19px; font-weight: 600;")
    root.addWidget(heading)

    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 15px; font-weight: 550;")
    root.addWidget(question)

    scientific_view = QLabel()
    scientific_view.setWordWrap(True)
    scientific_view.setStyleSheet("color: #53616d; font-size: 11px;")
    root.addWidget(scientific_view)

    body = QHBoxLayout()
    body.setSpacing(10)
    root.addLayout(body, 1)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(315)
    controls_frame.setMinimumWidth(270)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_layout.setSpacing(6)

    instruction = QLabel()
    instruction.setWordWrap(True)
    instruction.setStyleSheet("color: #53616d; font-size: 11px;")
    controls_layout.addWidget(instruction)

    form = QFormLayout()
    form.setVerticalSpacing(5)
    bias_label = QLabel()
    bias = QDoubleSpinBox()
    bias.setRange(-30.0, 30.0)
    bias.setSingleStep(1.0)
    bias.setDecimals(0)
    bias.setValue(_DEFAULTS.processing_lower_layer_bias_mps)
    bias.setSuffix(" m/s")
    form.addRow(bias_label, bias)

    bias_slider = QSlider(Qt.Orientation.Horizontal)
    bias_slider.setRange(-30, 30)
    bias_slider.setValue(round(bias.value()))
    form.addRow("", bias_slider)
    controls_layout.addLayout(form)

    reset = QPushButton()
    controls_layout.addWidget(reset)

    readout = QLabel()
    readout.setWordWrap(True)
    readout.setStyleSheet("font-size: 11px;")
    controls_layout.addWidget(readout)
    controls_layout.addStretch(1)
    body.addWidget(controls_frame)

    initial = prepare_propagation_explorer_snapshot(_DEFAULTS)
    figure, axes = plot_layered_svp_explorer_snapshot(initial)
    canvas = FigureCanvas(figure)
    body.addWidget(canvas, 1)

    footer = QHBoxLayout()
    footer.setSpacing(6)
    observation = QLabel()
    observation.setWordWrap(True)
    observation.setStyleSheet(
        "background: #f7f9fa; border-radius: 8px; padding: 7px; font-size: 11px;"
    )
    boundary = QLabel()
    boundary.setWordWrap(True)
    boundary.setStyleSheet(
        "background: #f7f9fa; border-radius: 8px; padding: 7px; font-size: 10px;"
    )
    footer.addWidget(observation, 2)
    footer.addWidget(boundary, 2)
    root.addLayout(footer)

    locale = "en"

    def current_controls() -> PropagationExplorerControls:
        return PropagationExplorerControls(
            processing_lower_layer_bias_mps=bias.value(),
            terrain_depth_m=_DEFAULTS.terrain_depth_m,
            interface_depth_m=_DEFAULTS.interface_depth_m,
            upper_layer_sound_speed_mps=_DEFAULTS.upper_layer_sound_speed_mps,
            lower_layer_sound_speed_mps=_DEFAULTS.lower_layer_sound_speed_mps,
            maximum_beam_angle_deg=_DEFAULTS.maximum_beam_angle_deg,
            beam_count=_DEFAULTS.beam_count,
        )

    def redraw() -> None:
        snapshot = prepare_propagation_explorer_snapshot(current_controls())
        draw_layered_svp_explorer_snapshot(snapshot, axes)
        max_error = max(float(beam.sounding_error_norm_m) for beam in snapshot.beams)
        text = _TEXT[locale]
        readout.setText(
            f"{text['truth_lower']} = {_DEFAULTS.lower_layer_sound_speed_mps:.0f} m/s<br>"
            f"{text['processing_lower']} = "
            f"{_DEFAULTS.lower_layer_sound_speed_mps + bias.value():.0f} m/s<br>"
            f"{text['max_error']} = {max_error:.3f} m"
        )
        canvas.draw_idle()

    def sync_bias_spinbox(value: float) -> None:
        target = round(value)
        if bias_slider.value() != target:
            bias_slider.blockSignals(True)
            bias_slider.setValue(target)
            bias_slider.blockSignals(False)
        redraw()

    def sync_bias_slider(value: int) -> None:
        target = float(value)
        if bias.value() != target:
            bias.blockSignals(True)
            bias.setValue(target)
            bias.blockSignals(False)
        redraw()

    bias.valueChanged.connect(sync_bias_spinbox)
    bias_slider.valueChanged.connect(sync_bias_slider)

    def reset_lesson() -> None:
        bias.setValue(_DEFAULTS.processing_lower_layer_bias_mps)
        redraw()

    reset.clicked.connect(reset_lesson)

    def apply_language(requested_locale: str) -> None:
        nonlocal locale
        locale = requested_locale if requested_locale in _TEXT else "en"
        localizer = Localizer(locale)
        text = _TEXT[locale]
        heading.setText(localizer.text("propagation.title"))
        question.setText(
            f"<b>{localizer.text('common.learning_question')}:</b> "
            f"{localizer.text('propagation.question')}"
        )
        scientific_view.setText(
            f"<b>{localizer.text('common.scientific_view')}:</b> {text['scientific_view']}"
        )
        instruction.setText(text["instruction"])
        bias_label.setText(text["bias"])
        reset.setText(localizer.text("common.reset"))
        observation.setText(
            f"<b>{localizer.text('common.what_to_look_for')}</b><br>{text['observation']}"
        )
        boundary.setText(
            f"<b>{localizer.text('common.scientific_boundary')}</b><br>{text['boundary']}<br>"
            f"{localizer.text('common.not_shown_yet')}: {text['not_shown']}"
        )
        redraw()

    apply_language("en")
    controls = {
        "processing_bias": bias,
        "processing_bias_slider": bias_slider,
        "reset": reset,
        "readout": readout,
    }
    return page, controls, apply_language

"""PySide6 learning page for Propagation Truth × Processing consequences."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hydrosim.app.localization import Localizer
from hydrosim.visualization import (
    PropagationExplorerControls,
    draw_layered_svp_explorer_snapshot,
    prepare_propagation_explorer_snapshot,
)
from hydrosim.visualization.layered_svp_explorer_plot import (
    plot_layered_svp_explorer_snapshot,
)


_DEFAULTS = PropagationExplorerControls()


def build_propagation_lesson(
    FigureCanvas: type[Any],
) -> tuple[Any, dict[str, Any], Callable[[str], None]]:
    """Build the compact bilingual Propagation lesson from existing calculations."""

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

    body = QHBoxLayout()
    body.setSpacing(10)
    root.addLayout(body, 1)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(270)
    controls_frame.setMinimumWidth(235)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_layout.setSpacing(6)

    controls_title = QLabel()
    controls_title.setStyleSheet("font-size: 14px; font-weight: 650;")
    controls_layout.addWidget(controls_title)

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
    bias.setSuffix(" m/s")
    bias.setValue(_DEFAULTS.processing_lower_layer_bias_mps)
    form.addRow(bias_label, bias)
    bias_slider = QSlider(Qt.Orientation.Horizontal)
    bias_slider.setRange(-30, 30)
    bias_slider.setValue(round(bias.value()))
    form.addRow("", bias_slider)
    controls_layout.addLayout(form)

    reset = QPushButton()
    reset.setMinimumHeight(28)
    controls_layout.addWidget(reset)

    readout = QLabel()
    readout.setWordWrap(True)
    readout.setStyleSheet("font-size: 11px;")
    controls_layout.addWidget(readout)
    controls_layout.addStretch(1)
    body.addWidget(controls_frame)

    initial_snapshot = prepare_propagation_explorer_snapshot(_DEFAULTS)
    figure, axes = plot_layered_svp_explorer_snapshot(initial_snapshot)
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

    def current_state() -> PropagationExplorerControls:
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
        snapshot = prepare_propagation_explorer_snapshot(current_state())
        draw_layered_svp_explorer_snapshot(snapshot, axes)
        max_error = max(float(beam.sounding_error_norm_m) for beam in snapshot.beams)
        localizer = Localizer(str(page.property("hydrosim_locale") or "en"))
        readout.setText(
            f"{localizer.text('propagation.truth_lower_layer')} = "
            f"{_DEFAULTS.lower_layer_sound_speed_mps:.0f} m/s<br>"
            f"{localizer.text('propagation.processing_lower_layer')} = "
            f"{_DEFAULTS.lower_layer_sound_speed_mps + bias.value():.0f} m/s<br>"
            f"{localizer.text('propagation.max_error')} = {max_error:.3f} m"
        )
        canvas.draw_idle()

    bias.valueChanged.connect(
        lambda value: bias_slider.setValue(round(value))
        if bias_slider.value() != round(value)
        else redraw()
    )
    bias_slider.valueChanged.connect(
        lambda value: bias.setValue(float(value)) if bias.value() != float(value) else None
    )

    def reset_lesson() -> None:
        bias.setValue(_DEFAULTS.processing_lower_layer_bias_mps)
        redraw()

    reset.clicked.connect(reset_lesson)

    def apply_language(locale: str) -> None:
        localizer = Localizer(locale)
        page.setProperty("hydrosim_locale", locale)
        heading.setText(localizer.text("propagation.title"))
        question.setText(localizer.text("propagation.question"))
        controls_title.setText(localizer.text("common.try_it"))
        instruction.setText(localizer.text("propagation.instruction"))
        bias_label.setText(localizer.text("propagation.processing_bias"))
        reset.setText(localizer.text("common.reset"))
        observation.setText(
            f"<b>{localizer.text('common.what_to_look_for')}</b><br>"
            f"{localizer.text('propagation.observation')}"
        )
        boundary.setText(
            f"<b>{localizer.text('common.scientific_boundary')}</b><br>"
            f"{localizer.text('propagation.boundary')}<br>"
            f"{localizer.text('propagation.not_shown')}"
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

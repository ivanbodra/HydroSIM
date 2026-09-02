"""PySide6 presentation page for the deterministic Motion learning slice."""

from __future__ import annotations

from collections.abc import Callable
from math import degrees, radians
from typing import Any

from hydrosim.app.localization import Localizer
from hydrosim.app.motion_lesson import MotionLessonControls, prepare_motion_lesson_snapshot
from hydrosim.visualization.motion_lesson_plot import (
    draw_motion_lesson_snapshot,
    plot_motion_lesson_snapshot,
)


def build_motion_lesson(
    FigureCanvas: type[Any] | None = None,
) -> tuple[Any, dict[str, Any], Callable[[str], None]]:
    """Build the compact Motion page using the existing Motion lesson adapter.

    ``FigureCanvas`` remains injectable for legacy integration/tests, while the default
    zero-argument form is a stable page-builder contract for the pedagogical shell.
    """

    if FigureCanvas is None:
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

    from PySide6.QtWidgets import (
        QDoubleSpinBox,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QLabel,
        QPushButton,
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
    controls_frame.setMaximumWidth(285)
    controls_frame.setMinimumWidth(250)
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

    def angle_control(minimum: float, maximum: float) -> QDoubleSpinBox:
        control = QDoubleSpinBox()
        control.setRange(minimum, maximum)
        control.setSingleStep(1.0)
        control.setDecimals(1)
        control.setSuffix("°")
        control.setValue(0.0)
        return control

    form = QFormLayout()
    form.setVerticalSpacing(6)

    roll_label = QLabel()
    roll = angle_control(-20.0, 20.0)
    form.addRow(roll_label, roll)

    pitch_label = QLabel()
    pitch = angle_control(-20.0, 20.0)
    form.addRow(pitch_label, pitch)

    yaw_label = QLabel()
    yaw = angle_control(-30.0, 30.0)
    form.addRow(yaw_label, yaw)

    heave_label = QLabel()
    heave = QDoubleSpinBox()
    heave.setRange(-3.0, 3.0)
    heave.setSingleStep(0.1)
    heave.setDecimals(1)
    heave.setSuffix(" m")
    heave.setValue(0.0)
    form.addRow(heave_label, heave)
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

    initial = prepare_motion_lesson_snapshot(MotionLessonControls())
    figure, ax = plot_motion_lesson_snapshot(initial)
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

    def current_controls() -> MotionLessonControls:
        return MotionLessonControls(
            roll_rad=radians(roll.value()),
            pitch_rad=radians(pitch.value()),
            yaw_deviation_rad=radians(yaw.value()),
            heave_m=heave.value(),
        )

    def redraw() -> None:
        snapshot = prepare_motion_lesson_snapshot(current_controls())
        draw_motion_lesson_snapshot(snapshot, ax)
        transducer = snapshot.transducer_position_n_m
        beam = snapshot.beam_direction_n
        readout.setText(
            f"Roll={degrees(snapshot.controls.roll_rad):+.1f}° · "
            f"Pitch={degrees(snapshot.controls.pitch_rad):+.1f}° · "
            f"Yaw={degrees(snapshot.controls.yaw_deviation_rad):+.1f}° · "
            f"Heave={snapshot.controls.heave_m:+.2f} m<br>"
            f"VRP Z={snapshot.vrp_position_n_m.z:+.2f} m · "
            f"Transducer=({transducer.x:+.2f}, {transducer.y:+.2f}, {transducer.z:+.2f}) m<br>"
            f"Beam n=({beam.x:+.2f}, {beam.y:+.2f}, {beam.z:+.2f})"
        )
        canvas.draw_idle()

    for control in (roll, pitch, yaw, heave):
        control.valueChanged.connect(lambda _value: redraw())

    def reset_lesson() -> None:
        for control in (roll, pitch, yaw, heave):
            control.blockSignals(True)
            control.setValue(0.0)
            control.blockSignals(False)
        redraw()

    reset.clicked.connect(reset_lesson)

    def apply_language(locale: str) -> None:
        localizer = Localizer(locale)
        heading.setText(localizer.text("motion.title"))
        question.setText(localizer.text("motion.question"))
        controls_title.setText(localizer.text("common.try_it"))
        instruction.setText(localizer.text("motion.instruction"))
        roll_label.setText(localizer.text("motion.roll"))
        pitch_label.setText(localizer.text("motion.pitch"))
        yaw_label.setText(localizer.text("motion.yaw"))
        heave_label.setText(localizer.text("motion.heave"))
        reset.setText(localizer.text("common.reset"))
        observation.setText(
            f"<b>{localizer.text('common.what_to_look_for')}</b><br>"
            f"{localizer.text('motion.observation')}"
        )
        boundary.setText(
            f"<b>{localizer.text('common.scientific_boundary')}</b><br>"
            f"{localizer.text('motion.boundary')}<br>{localizer.text('motion.not_shown')}"
        )

    redraw()
    apply_language("en")
    controls = {
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "heave": heave,
        "reset": reset,
        "readout": readout,
    }
    return page, controls, apply_language

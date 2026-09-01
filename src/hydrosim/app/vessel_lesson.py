"""PySide6 learning page for Vessel / Sensors / Vertical References."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hydrosim.app.localization import Localizer
from hydrosim.app.vessel_vertical_reference import (
    VesselVerticalReferenceConfiguration,
    prepare_vessel_vertical_reference_snapshot,
)
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.visualization.vessel_vertical_reference_plot import (
    draw_vessel_vertical_reference_snapshot,
    plot_vessel_vertical_reference_snapshot,
)


_DEFAULT_POSE = Pose(
    position=Vector3(x=0.0, y=0.0, z=0.0),
    attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
    frame="N",
)
_DEFAULT_CONFIGURATION = VesselVerticalReferenceConfiguration(
    lever_arm_vrp_to_gnss=Vector3(x=-1.8, y=0.0, z=-2.4),
    lever_arm_vrp_to_imu=Vector3(x=0.6, y=0.0, z=-0.4),
    lever_arm_vrp_to_transducer=Vector3(x=1.2, y=0.0, z=2.1),
    waterline_z_from_vrp_m=0.7,
    water_level_m_relative_to_datum=1.0,
)


def build_vessel_lesson(FigureCanvas: type[Any]) -> tuple[Any, dict[str, Any], Callable[[str], None]]:
    """Build the compact bilingual Vessel lesson without duplicating scientific logic."""

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
    transducer_label = QLabel()
    transducer_z = QDoubleSpinBox()
    transducer_z.setRange(0.5, 4.0)
    transducer_z.setSingleStep(0.1)
    transducer_z.setDecimals(1)
    transducer_z.setSuffix(" m")
    transducer_z.setValue(float(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.z))
    form.addRow(transducer_label, transducer_z)
    transducer_slider = QSlider(Qt.Orientation.Horizontal)
    transducer_slider.setRange(5, 40)
    transducer_slider.setValue(round(transducer_z.value() * 10.0))
    form.addRow("", transducer_slider)

    waterline_label = QLabel()
    waterline_z = QDoubleSpinBox()
    waterline_z.setRange(-0.5, 2.0)
    waterline_z.setSingleStep(0.1)
    waterline_z.setDecimals(1)
    waterline_z.setSuffix(" m")
    waterline_z.setValue(float(_DEFAULT_CONFIGURATION.waterline_z_from_vrp_m))
    form.addRow(waterline_label, waterline_z)

    water_level_label = QLabel()
    water_level = QDoubleSpinBox()
    water_level.setRange(-2.0, 3.0)
    water_level.setSingleStep(0.1)
    water_level.setDecimals(1)
    water_level.setSuffix(" m")
    water_level.setValue(float(_DEFAULT_CONFIGURATION.water_level_m_relative_to_datum))
    form.addRow(water_level_label, water_level)
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

    initial_snapshot = prepare_vessel_vertical_reference_snapshot(
        _DEFAULT_POSE,
        _DEFAULT_CONFIGURATION,
    )
    figure, axes = plot_vessel_vertical_reference_snapshot(initial_snapshot)
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

    def current_configuration() -> VesselVerticalReferenceConfiguration:
        return VesselVerticalReferenceConfiguration(
            lever_arm_vrp_to_gnss=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_gnss,
            lever_arm_vrp_to_imu=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_imu,
            lever_arm_vrp_to_transducer=Vector3(
                x=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.x,
                y=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.y,
                z=transducer_z.value(),
            ),
            waterline_z_from_vrp_m=waterline_z.value(),
            water_level_m_relative_to_datum=water_level.value(),
        )

    def redraw() -> None:
        snapshot = prepare_vessel_vertical_reference_snapshot(_DEFAULT_POSE, current_configuration())
        draw_vessel_vertical_reference_snapshot(snapshot, axes)
        readout.setText(
            f"Transducer Z = {snapshot.transducer_z_from_vrp_m:+.2f} m · "
            f"Depth below waterline = {snapshot.transducer_depth_below_waterline_m:.2f} m<br>"
            f"Hydrographic water level = {snapshot.water_level_m_relative_to_datum:+.2f} m"
        )
        canvas.draw_idle()

    transducer_z.valueChanged.connect(
        lambda value: transducer_slider.setValue(round(value * 10.0))
        if transducer_slider.value() != round(value * 10.0)
        else redraw()
    )
    transducer_slider.valueChanged.connect(
        lambda value: transducer_z.setValue(value / 10.0)
        if transducer_z.value() != value / 10.0
        else None
    )
    waterline_z.valueChanged.connect(lambda _value: redraw())
    water_level.valueChanged.connect(lambda _value: redraw())

    def reset_lesson() -> None:
        transducer_z.setValue(float(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.z))
        waterline_z.setValue(float(_DEFAULT_CONFIGURATION.waterline_z_from_vrp_m))
        water_level.setValue(float(_DEFAULT_CONFIGURATION.water_level_m_relative_to_datum))
        redraw()

    reset.clicked.connect(reset_lesson)

    def apply_language(locale: str) -> None:
        localizer = Localizer(locale)
        heading.setText(localizer.text("vessel.title"))
        question.setText(localizer.text("vessel.question"))
        controls_title.setText(localizer.text("common.try_it"))
        instruction.setText(localizer.text("vessel.instruction"))
        transducer_label.setText(localizer.text("vessel.transducer_z"))
        waterline_label.setText(localizer.text("vessel.waterline"))
        water_level_label.setText(localizer.text("vessel.water_level"))
        reset.setText(localizer.text("common.reset"))
        observation.setText(
            f"<b>{localizer.text('common.what_to_look_for')}</b><br>"
            f"{localizer.text('vessel.observation')}"
        )
        boundary.setText(
            f"<b>{localizer.text('common.scientific_boundary')}</b><br>"
            f"{localizer.text('vessel.boundary')}<br>{localizer.text('vessel.not_shown')}"
        )

    redraw()
    apply_language("en")
    controls = {
        "transducer_z": transducer_z,
        "transducer_slider": transducer_slider,
        "waterline_z": waterline_z,
        "water_level": water_level,
        "reset": reset,
        "readout": readout,
    }
    return page, controls, apply_language

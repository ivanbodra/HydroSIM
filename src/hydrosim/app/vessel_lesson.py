"""PySide6 learning page for Vessel / Sensors / Vertical References."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hydrosim.app.localization import Localizer
from hydrosim.app.vessel_vertical_reference import VesselVerticalReferenceConfiguration, prepare_vessel_vertical_reference_snapshot
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.visualization.vessel_vertical_reference_plot import draw_vessel_vertical_reference_snapshot, plot_vessel_vertical_reference_snapshot

_DEFAULT_POSE = Pose(position=Vector3(x=0.0, y=0.0, z=0.0), attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0), frame="N")
_DEFAULT_CONFIGURATION = VesselVerticalReferenceConfiguration(
    lever_arm_vrp_to_gnss=Vector3(x=-1.8, y=0.0, z=-2.4), lever_arm_vrp_to_imu=Vector3(x=0.6, y=0.0, z=-0.4),
    lever_arm_vrp_to_transducer=Vector3(x=1.2, y=0.0, z=2.1), waterline_z_from_vrp_m=0.7, static_draft_m=2.2, water_level_m_relative_to_datum=1.0,
)


def build_vessel_lesson(FigureCanvas: type[Any]) -> tuple[Any, dict[str, Any], Callable[[str], None]]:
    """Build the compact bilingual Vessel lesson without duplicating scientific logic."""
    from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

    page = QWidget(); root = QVBoxLayout(page); root.setContentsMargins(8, 2, 4, 2); root.setSpacing(6)
    heading = QLabel(); heading.setStyleSheet("font-size: 19px; font-weight: 600;"); root.addWidget(heading)
    question = QLabel(); question.setWordWrap(True); question.setStyleSheet("font-size: 15px; font-weight: 550;"); root.addWidget(question)
    body = QHBoxLayout(); body.setSpacing(10); root.addLayout(body, 1)
    controls_frame = QFrame(); controls_frame.setMaximumWidth(300); controls_frame.setMinimumWidth(260); controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame); controls_layout.setContentsMargins(10, 8, 10, 8); controls_layout.setSpacing(6)
    controls_title = QLabel(); controls_title.setStyleSheet("font-size: 14px; font-weight: 650;"); controls_layout.addWidget(controls_title)
    instruction = QLabel(); instruction.setWordWrap(True); instruction.setStyleSheet("color: #53616d; font-size: 11px;"); controls_layout.addWidget(instruction)
    form = QFormLayout(); form.setVerticalSpacing(5)

    def spin(value: float, minimum: float, maximum: float) -> QDoubleSpinBox:
        control = QDoubleSpinBox(); control.setRange(minimum, maximum); control.setSingleStep(0.1); control.setDecimals(1); control.setSuffix(" m"); control.setValue(value); return control

    transducer_x_label, transducer_y_label, transducer_z_label = QLabel(), QLabel(), QLabel()
    transducer_x = spin(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.x, -5.0, 5.0)
    transducer_y = spin(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.y, -5.0, 5.0)
    transducer_z = spin(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.z, -1.0, 5.0)
    form.addRow(transducer_x_label, transducer_x); form.addRow(transducer_y_label, transducer_y); form.addRow(transducer_z_label, transducer_z)
    waterline_label = QLabel(); waterline_z = spin(_DEFAULT_CONFIGURATION.waterline_z_from_vrp_m, -0.5, 2.0); form.addRow(waterline_label, waterline_z)
    static_draft_label = QLabel(); static_draft = spin(_DEFAULT_CONFIGURATION.static_draft_m, 0.0, 8.0); form.addRow(static_draft_label, static_draft)
    water_level_label = QLabel(); water_level = spin(_DEFAULT_CONFIGURATION.water_level_m_relative_to_datum, -2.0, 3.0); form.addRow(water_level_label, water_level)
    controls_layout.addLayout(form)
    reset = QPushButton(); reset.setMinimumHeight(28); controls_layout.addWidget(reset)
    readout = QLabel(); readout.setWordWrap(True); readout.setStyleSheet("font-size: 11px;"); controls_layout.addWidget(readout); controls_layout.addStretch(1); body.addWidget(controls_frame)

    initial_snapshot = prepare_vessel_vertical_reference_snapshot(_DEFAULT_POSE, _DEFAULT_CONFIGURATION)
    figure, axes = plot_vessel_vertical_reference_snapshot(initial_snapshot); canvas = FigureCanvas(figure); body.addWidget(canvas, 1)
    footer = QHBoxLayout(); footer.setSpacing(6)
    observation = QLabel(); observation.setWordWrap(True); observation.setStyleSheet("background: #f7f9fa; border-radius: 8px; padding: 7px; font-size: 11px;")
    boundary = QLabel(); boundary.setWordWrap(True); boundary.setStyleSheet("background: #f7f9fa; border-radius: 8px; padding: 7px; font-size: 10px;")
    footer.addWidget(observation, 2); footer.addWidget(boundary, 2); root.addLayout(footer)

    def current_configuration() -> VesselVerticalReferenceConfiguration:
        return VesselVerticalReferenceConfiguration(
            lever_arm_vrp_to_gnss=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_gnss, lever_arm_vrp_to_imu=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_imu,
            lever_arm_vrp_to_transducer=Vector3(x=transducer_x.value(), y=transducer_y.value(), z=transducer_z.value()),
            waterline_z_from_vrp_m=waterline_z.value(), static_draft_m=static_draft.value(), water_level_m_relative_to_datum=water_level.value(),
        )

    def redraw() -> None:
        snapshot = prepare_vessel_vertical_reference_snapshot(_DEFAULT_POSE, current_configuration()); draw_vessel_vertical_reference_snapshot(snapshot, axes)
        readout.setText(
            f"Transducer XYZ = ({snapshot.transducer_position_body_m.x:+.2f}, {snapshot.transducer_position_body_m.y:+.2f}, {snapshot.transducer_position_body_m.z:+.2f}) m<br>"
            f"Depth below waterline = {snapshot.transducer_depth_below_waterline_m:.2f} m · Static draft = {snapshot.static_draft_m:.2f} m · Keel Z = {snapshot.keel_z_from_vrp_m:+.2f} m<br>"
            f"Hydrographic water level = {snapshot.water_level_m_relative_to_datum:+.2f} m"
        ); canvas.draw_idle()

    for control in (transducer_x, transducer_y, transducer_z, waterline_z, static_draft, water_level): control.valueChanged.connect(lambda _value: redraw())

    def reset_lesson() -> None:
        transducer_x.setValue(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.x); transducer_y.setValue(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.y); transducer_z.setValue(_DEFAULT_CONFIGURATION.lever_arm_vrp_to_transducer.z)
        waterline_z.setValue(_DEFAULT_CONFIGURATION.waterline_z_from_vrp_m); static_draft.setValue(_DEFAULT_CONFIGURATION.static_draft_m); water_level.setValue(_DEFAULT_CONFIGURATION.water_level_m_relative_to_datum); redraw()
    reset.clicked.connect(reset_lesson)

    def apply_language(locale: str) -> None:
        localizer = Localizer(locale); heading.setText(localizer.text("vessel.title")); question.setText(localizer.text("vessel.question")); controls_title.setText(localizer.text("common.try_it")); instruction.setText(localizer.text("vessel.instruction"))
        transducer_x_label.setText(localizer.text("vessel.transducer_x")); transducer_y_label.setText(localizer.text("vessel.transducer_y")); transducer_z_label.setText(localizer.text("vessel.transducer_z")); static_draft_label.setText(localizer.text("vessel.static_draft"))
        waterline_label.setText(localizer.text("vessel.waterline")); water_level_label.setText(localizer.text("vessel.water_level")); reset.setText(localizer.text("common.reset"))
        observation.setText(f"<b>{localizer.text('common.what_to_look_for')}</b><br>{localizer.text('vessel.observation')}")
        boundary.setText(f"<b>{localizer.text('common.scientific_boundary')}</b><br>{localizer.text('vessel.boundary')}<br>{localizer.text('vessel.not_shown')}")

    redraw(); apply_language("en")
    controls = {"transducer_x": transducer_x, "transducer_y": transducer_y, "transducer_z": transducer_z, "waterline_z": waterline_z, "static_draft": static_draft, "water_level": water_level, "reset": reset, "readout": readout}
    return page, controls, apply_language

"""PySide6 learning page for Vessel / Sensors / Vertical References."""
from __future__ import annotations
from collections.abc import Callable
from typing import Any
from hydrosim.app.localization import Localizer
from hydrosim.app.vessel_vertical_reference import VesselVerticalReferenceConfiguration, prepare_vessel_vertical_reference_snapshot
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.visualization.vessel_vertical_reference_plot import draw_vessel_vertical_reference_snapshot, plot_vessel_vertical_reference_snapshot
_DEFAULT_POSE = Pose(position=Vector3(x=0.0,y=0.0,z=0.0), attitude=Attitude.from_degrees(roll=0.0,pitch=0.0,yaw=0.0), frame="N")
_DEFAULT_CONFIGURATION = VesselVerticalReferenceConfiguration(lever_arm_vrp_to_gnss=Vector3(x=-1.8,y=0.0,z=-2.4),lever_arm_vrp_to_imu=Vector3(x=0.6,y=0.0,z=-0.4),lever_arm_vrp_to_transducer=Vector3(x=1.2,y=0.0,z=2.1),waterline_z_from_vrp_m=0.7,static_draft_m=2.2,water_level_m_relative_to_datum=1.0)

def build_vessel_lesson(FigureCanvas:type[Any])->tuple[Any,dict[str,Any],Callable[[str],None]]:
    from PySide6.QtWidgets import QDoubleSpinBox,QFormLayout,QFrame,QHBoxLayout,QLabel,QPushButton,QVBoxLayout,QWidget
    page=QWidget(); root=QVBoxLayout(page); root.setContentsMargins(8,2,4,2); root.setSpacing(6)
    heading=QLabel(); heading.setStyleSheet("font-size: 19px; font-weight: 600;"); root.addWidget(heading)
    question=QLabel(); question.setWordWrap(True); question.setStyleSheet("font-size: 15px; font-weight: 550;"); root.addWidget(question)
    body=QHBoxLayout(); body.setSpacing(10); root.addLayout(body,1)
    controls_frame=QFrame(); controls_frame.setMaximumWidth(300); controls_frame.setMinimumWidth(260); controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout=QVBoxLayout(controls_frame); controls_layout.setContentsMargins(10,8,10,8); controls_layout.setSpacing(6)
    controls_title=QLabel(); controls_title.setStyleSheet("font-size: 14px; font-weight: 650;"); controls_layout.addWidget(controls_title)
    instruction=QLabel(); instruction.setWordWrap(True); instruction.setStyleSheet("color: #53616d; font-size: 11px;"); controls_layout.addWidget(instruction)
    form=QFormLayout(); form.setVerticalSpacing(5)
    def spin(value:float,minimum:float,maximum:float)->QDoubleSpinBox:
        c=QDoubleSpinBox(); c.setRange(minimum,maximum); c.setSingleStep(0.1); c.setDecimals(1); c.setSuffix(" m"); c.setValue(value); return c
    txl,tyl,tzl=QLabel(),QLabel(),QLabel(); tx=spin(1.2,-5,5); ty=spin(0,-5,5); tz=spin(2.1,-1,5)
    form.addRow(txl,tx); form.addRow(tyl,ty); form.addRow(tzl,tz)
    wll=QLabel(); wl=spin(0.7,-0.5,2); form.addRow(wll,wl)
    sdl=QLabel(); sd=spin(2.2,0,8); form.addRow(sdl,sd)
    hwl=QLabel(); hw=spin(1,-2,3); form.addRow(hwl,hw); controls_layout.addLayout(form)
    reset=QPushButton(); reset.setMinimumHeight(28); controls_layout.addWidget(reset)
    readout=QLabel(); readout.setWordWrap(True); readout.setStyleSheet("font-size: 11px;"); controls_layout.addWidget(readout); controls_layout.addStretch(1); body.addWidget(controls_frame)
    initial=prepare_vessel_vertical_reference_snapshot(_DEFAULT_POSE,_DEFAULT_CONFIGURATION); figure,axes=plot_vessel_vertical_reference_snapshot(initial); canvas=FigureCanvas(figure); body.addWidget(canvas,1)
    footer=QHBoxLayout(); observation=QLabel(); observation.setWordWrap(True); boundary=QLabel(); boundary.setWordWrap(True); footer.addWidget(observation,2); footer.addWidget(boundary,2); root.addLayout(footer)
    def configuration()->VesselVerticalReferenceConfiguration:
        return VesselVerticalReferenceConfiguration(lever_arm_vrp_to_gnss=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_gnss,lever_arm_vrp_to_imu=_DEFAULT_CONFIGURATION.lever_arm_vrp_to_imu,lever_arm_vrp_to_transducer=Vector3(x=tx.value(),y=ty.value(),z=tz.value()),waterline_z_from_vrp_m=wl.value(),static_draft_m=sd.value(),water_level_m_relative_to_datum=hw.value())
    def redraw()->None:
        s=prepare_vessel_vertical_reference_snapshot(_DEFAULT_POSE,configuration()); draw_vessel_vertical_reference_snapshot(s,axes)
        p=s.transducer_position; readout.setText(f"Transducer XYZ = ({p.x:+.2f}, {p.y:+.2f}, {p.z:+.2f}) m<br>Depth below waterline = {s.transducer_depth_below_waterline_m:.2f} m · Static draft = {s.static_draft_m:.2f} m · Keel Z = {s.keel_z_from_vrp_m:+.2f} m<br>Hydrographic water level = {s.water_level_m_relative_to_datum:+.2f} m"); canvas.draw_idle()
    for c in (tx,ty,tz,wl,sd,hw): c.valueChanged.connect(lambda _value:redraw())
    def reset_lesson()->None:
        tx.setValue(1.2); ty.setValue(0); tz.setValue(2.1); wl.setValue(0.7); sd.setValue(2.2); hw.setValue(1); redraw()
    reset.clicked.connect(reset_lesson)
    def apply_language(locale:str)->None:
        l=Localizer(locale); heading.setText(l.text("vessel.title")); question.setText(l.text("vessel.question")); controls_title.setText(l.text("common.try_it")); instruction.setText(l.text("vessel.instruction")); txl.setText(l.text("vessel.transducer_x")); tyl.setText(l.text("vessel.transducer_y")); tzl.setText(l.text("vessel.transducer_z")); sdl.setText(l.text("vessel.static_draft")); wll.setText(l.text("vessel.waterline")); hwl.setText(l.text("vessel.water_level")); reset.setText(l.text("common.reset")); observation.setText(f"<b>{l.text('common.what_to_look_for')}</b><br>{l.text('vessel.observation')}"); boundary.setText(f"<b>{l.text('common.scientific_boundary')}</b><br>{l.text('vessel.boundary')}<br>{l.text('vessel.not_shown')}")
    redraw(); apply_language("en"); return page,{"transducer_x":tx,"transducer_y":ty,"transducer_z":tz,"waterline_z":wl,"static_draft":sd,"water_level":hw,"reset":reset,"readout":readout},apply_language

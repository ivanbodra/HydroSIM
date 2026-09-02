"""PySide6 presentation for D7 Sonar Systems & Geometry.

All geometry state is composed from the canonical hydrosim.geometry adapters.
The page only presents those objects; it does not add sonar physics or vessel
attitude semantics.
"""

from __future__ import annotations

from collections.abc import Callable
from math import radians

from hydrosim.geometry import (
    Attitude,
    DualHeadGeometry,
    TransducerArray,
    TxSectorGeometry,
    TxSectorSetGeometry,
    Vector3,
    make_sbes_geometry,
    make_sonar_head_geometry,
)

_TEXT = {
    "en": {
        "title": "Sonar Systems & Geometry",
        "question": "How do SBES, single-head MBES, TX sectors, and dual-head installations differ geometrically?",
        "swath": "MBES swath",
        "cant": "Fixed head cant",
        "reset": "Reset",
        "sbes": "1. SBES — one nominal centre ray",
        "mbes": "2. Single-head MBES — RX fan",
        "sectors": "3. TX sectors — explicit support, distinct from RX beams",
        "dual": "4–5. Dual head — identities retained; combined coverage is derived",
        "boundary": "Head cant is fixed installation geometry. Dynamic vessel roll/pitch/yaw is intentionally not part of this lesson.",
    },
    "pt-BR": {
        "title": "Sistemas Sonar e Geometria",
        "question": "Como SBES, MBES de uma cabeça, setores TX e instalações de duas cabeças diferem geometricamente?",
        "swath": "Abertura MBES",
        "cant": "Inclinação fixa da cabeça",
        "reset": "Restaurar",
        "sbes": "1. SBES — um raio nominal central",
        "mbes": "2. MBES de uma cabeça — leque RX",
        "sectors": "3. Setores TX — suporte explícito, distinto dos feixes RX",
        "dual": "4–5. Duas cabeças — identidades preservadas; cobertura combinada é derivada",
        "boundary": "A inclinação das cabeças é geometria fixa de instalação. Roll/pitch/yaw dinâmicos da embarcação não fazem parte desta lição.",
    },
}


def _array(name: str) -> TransducerArray:
    return TransducerArray(
        name=name,
        role="txrx",
        n_x=1,
        n_y=16,
        d_x=0.0,
        d_y=0.006,
        element_longitudinal_size=0.006,
        element_transverse_size=0.006,
    )


def build_sonar_geometry_lesson() -> tuple[object, dict[str, object], Callable[[str], None]]:
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
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    page = QWidget()
    root = QVBoxLayout(page)
    root.setContentsMargins(8, 2, 4, 2)
    root.setSpacing(7)
    heading = QLabel()
    heading.setStyleSheet("font-size: 19px; font-weight: 600;")
    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 14px; font-weight: 550; color: #3f5962;")
    root.addWidget(heading)
    root.addWidget(question)

    body = QHBoxLayout()
    root.addLayout(body, 1)
    controls_frame = QFrame()
    controls_frame.setMinimumWidth(230)
    controls_frame.setMaximumWidth(270)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    form = QFormLayout()
    swath_label = QLabel()
    swath = QDoubleSpinBox()
    swath.setRange(30.0, 150.0)
    swath.setValue(120.0)
    swath.setSuffix("°")
    cant_label = QLabel()
    cant = QDoubleSpinBox()
    cant.setRange(0.0, 45.0)
    cant.setValue(20.0)
    cant.setSuffix("°")
    form.addRow(swath_label, swath)
    form.addRow(cant_label, cant)
    controls_layout.addLayout(form)
    reset = QPushButton()
    controls_layout.addWidget(reset)
    controls_layout.addStretch(1)
    body.addWidget(controls_frame)

    figure = Figure(figsize=(9.0, 6.5), constrained_layout=True)
    axes = figure.subplots(2, 2)
    canvas = FigureCanvas(figure)
    body.addWidget(canvas, 1)
    boundary = QLabel()
    boundary.setWordWrap(True)
    boundary.setStyleSheet("font-size: 10px; color: #53616d;")
    root.addWidget(boundary)
    current_locale = "en"

    def draw_ray(axis, direction, length=1.0, x0=0.0):
        axis.plot([x0, x0 + float(direction.y) * length], [0.0, float(direction.z) * length])

    def redraw() -> None:
        text = _TEXT[current_locale]
        for axis in axes.flat:
            axis.clear()
            axis.axhline(0.0, linewidth=0.7)
            axis.axvline(0.0, linewidth=0.7)
            axis.set_aspect("equal", adjustable="box")
            axis.set_xlabel("Across-track")
            axis.set_ylabel("Down")
            axis.invert_yaxis()

        base_array = _array("sbes-array")
        sbes = make_sbes_geometry(base_array)
        draw_ray(axes[0, 0], sbes.centre_ray.direction_sensor_frame)
        axes[0, 0].set_title(text["sbes"])

        single = make_sonar_head_geometry(
            system_id="mbes-single",
            head_id="head-a",
            lever_arm_ref_to_head=Vector3(x=0.0, y=0.0, z=0.0),
            fixed_orientation=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
            receive_array=_array("single-rx"),
            beam_count=21,
            total_swath_angle_rad=radians(swath.value()),
        )
        for direction_vector in single.fan_directions_reference_frame:
            draw_ray(axes[0, 1], direction_vector)
        axes[0, 1].set_title(text["mbes"])

        sectors = TxSectorSetGeometry(
            sectors=(
                TxSectorGeometry(sector_id="port", sector_index=0, system_id="mbes-single", head_id="head-a", array_id="single-rx", along_track_min_rad=-0.05, along_track_max_rad=0.05, across_track_min_rad=radians(-60), across_track_max_rad=radians(-20), centre_across_track_angle_rad=radians(-40)),
                TxSectorGeometry(sector_id="centre", sector_index=1, system_id="mbes-single", head_id="head-a", array_id="single-rx", along_track_min_rad=-0.05, along_track_max_rad=0.05, across_track_min_rad=radians(-20), across_track_max_rad=radians(20), centre_across_track_angle_rad=0.0),
                TxSectorGeometry(sector_id="starboard", sector_index=2, system_id="mbes-single", head_id="head-a", array_id="single-rx", along_track_min_rad=-0.05, along_track_max_rad=0.05, across_track_min_rad=radians(20), across_track_max_rad=radians(60), centre_across_track_angle_rad=radians(40)),
            )
        )
        for sector in sectors.sectors:
            axes[1, 0].axvspan(
                float(sector.across_track_min_rad),
                float(sector.across_track_max_rad),
                alpha=0.15,
            )
            axes[1, 0].axvline(float(sector.centre_across_track_angle_rad))
        axes[1, 0].set_xlabel("Across-track support (rad)")
        axes[1, 0].set_ylabel("TX support")
        axes[1, 0].set_title(text["sectors"])

        head_port = make_sonar_head_geometry(
            system_id="dual", head_id="port-head",
            lever_arm_ref_to_head=Vector3(x=0.0, y=-0.4, z=0.0),
            fixed_orientation=Attitude.from_degrees(roll=-cant.value(), pitch=0.0, yaw=0.0),
            receive_array=_array("port-rx"), beam_count=15,
            total_swath_angle_rad=radians(70.0),
        )
        head_starboard = make_sonar_head_geometry(
            system_id="dual", head_id="starboard-head",
            lever_arm_ref_to_head=Vector3(x=0.0, y=0.4, z=0.0),
            fixed_orientation=Attitude.from_degrees(roll=cant.value(), pitch=0.0, yaw=0.0),
            receive_array=_array("starboard-rx"), beam_count=15,
            total_swath_angle_rad=radians(70.0),
        )
        dual = DualHeadGeometry(system_id="dual", heads=(head_port, head_starboard))
        for head in dual.heads:
            x0 = float(head.lever_arm_ref_to_head.y)
            for direction_vector in head.fan_directions_reference_frame:
                draw_ray(axes[1, 1], direction_vector, x0=x0)
            axes[1, 1].text(x0, 0.0, head.head_id, fontsize=8)
        axes[1, 1].set_title(f"{text['dual']} · union={len(dual.combined_coverage_directions_reference_frame)} rays")
        canvas.draw_idle()

    swath.valueChanged.connect(lambda _value: redraw())
    cant.valueChanged.connect(lambda _value: redraw())

    def reset_controls() -> None:
        swath.setValue(120.0)
        cant.setValue(20.0)
        redraw()

    reset.clicked.connect(reset_controls)

    def apply_language(locale: str) -> None:
        nonlocal current_locale
        current_locale = locale if locale in _TEXT else "en"
        text = _TEXT[current_locale]
        heading.setText(text["title"])
        question.setText(text["question"])
        swath_label.setText(text["swath"])
        cant_label.setText(text["cant"])
        reset.setText(text["reset"])
        boundary.setText(text["boundary"])
        redraw()

    controls = {"swath": swath, "cant": cant, "reset": reset, "figure": figure}
    apply_language("en")
    return page, controls, apply_language

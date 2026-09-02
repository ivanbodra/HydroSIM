"""PySide6 presentation for D8 Sounding Formation / Detection Chain.

The page consumes :mod:`hydrosim.app.sounding_formation` state and keeps the
scientific boundary explicit: BottomDetection is Observed, processing pose/beam
are Configured, Cartesian reconstruction is Derived/reference, and simulator
geometry is Truth. Presentation code only reveals and highlights canonical
state; it does not recompute acoustic or sounding physics.
"""

from __future__ import annotations

from collections.abc import Callable
from math import degrees

from hydrosim.acquisition.bottom_detection import BottomDetection
from hydrosim.acquisition.models import AcquisitionPing
from hydrosim.app.sounding_formation import (
    STAGE_ORDER,
    SoundingFormationSnapshot,
    SoundingFormationStage,
)
from hydrosim.geometry.beams import BeamDefinition, BeamRay
from hydrosim.geometry.models import Attitude, Pose, Vector3
from hydrosim.geometry.soundings import SoundingComparison, SoundingState
from hydrosim.timing import PingTiming, SimulationTime

_TEXT = {
    "en": {
        "title": "Sounding Formation",
        "question": "How does one acoustic return become a positioned sounding?",
        "previous": "Previous",
        "next": "Next",
        "run": "Run",
        "pause": "Pause",
        "reset": "Reset",
        "truth": "Truth",
        "observed": "Observed measurement",
        "configured": "Configured processing state",
        "derived": "Derived/reference reconstruction",
        "identity": "Ping / beam / detection",
        "twtt": "TWTT",
        "angle": "Detected across-track angle",
        "truth_xyz": "Truth sounding (x, y, z)",
        "derived_xyz": "Derived/reference (x, y, z)",
        "residual": "Truth − Derived residual",
        "boundary": "Observed is the BottomDetection acoustic measurement tuple; the Cartesian reconstruction is Derived/reference, not an observed sounding.",
        "stages": (
            "Transmit", "Propagation", "Seabed return", "Receive", "Detection",
            "TWTT / Range", "Beam angle", "Pose association", "Reconstruction",
            "Truth × Reconstructed",
        ),
        "guidance": (
            "The ping trigger and transmit pose establish the acoustic event.",
            "The active beam defines the propagation direction used by the assembled chain.",
            "The simulator Truth sounding marks the seabed interaction point.",
            "The receive interval associates the returning signal with this ping.",
            "BottomDetection adds the measured acoustic observation and stable detection identity.",
            "The observed TWTT becomes the range-bearing measurement component; no Cartesian sounding is observed here.",
            "The detected across-track angle associates the observation with its receive beam.",
            "Configured processing pose and beam are associated with the observation.",
            "Configured geometry produces the deterministic Derived/reference Cartesian reconstruction.",
            "Truth and Derived/reference can now be compared without relabelling the reconstruction as Observed.",
        ),
    },
    "pt-BR": {
        "title": "Formação da Sondagem",
        "question": "Como um retorno acústico se transforma em uma sondagem posicionada?",
        "previous": "Anterior",
        "next": "Próximo",
        "run": "Executar",
        "pause": "Pausar",
        "reset": "Restaurar",
        "truth": "Verdade",
        "observed": "Medição observada",
        "configured": "Estado configurado de processamento",
        "derived": "Reconstrução derivada/de referência",
        "identity": "Ping / feixe / detecção",
        "twtt": "TWTT",
        "angle": "Ângulo transversal detectado",
        "truth_xyz": "Sondagem Truth (x, y, z)",
        "derived_xyz": "Derivada/referência (x, y, z)",
        "residual": "Resíduo Truth − Derivada",
        "boundary": "Observed é a tupla de medição acústica BottomDetection; a reconstrução cartesiana é Derived/referência, não uma sondagem observada.",
        "stages": (
            "Transmissão", "Propagação", "Retorno do fundo", "Recepção", "Detecção",
            "TWTT / Distância", "Ângulo do feixe", "Associação da pose", "Reconstrução",
            "Truth × Reconstruída",
        ),
        "guidance": (
            "O disparo do ping e a pose de transmissão estabelecem o evento acústico.",
            "O feixe ativo define a direção de propagação usada pela cadeia montada.",
            "A sondagem Truth do simulador marca o ponto de interação com o fundo.",
            "O intervalo de recepção associa o sinal de retorno a este ping.",
            "BottomDetection acrescenta a observação acústica medida e a identidade estável da detecção.",
            "O TWTT observado compõe a medição de distância; ainda não existe aqui uma sondagem cartesiana observada.",
            "O ângulo transversal detectado associa a observação ao seu feixe de recepção.",
            "A pose e o feixe configurados para processamento são associados à observação.",
            "A geometria configurada produz a reconstrução cartesiana Derived/de referência determinística.",
            "Truth e Derived/referência podem agora ser comparadas sem chamar a reconstrução de Observed.",
        ),
    },
}


def _reference_snapshot() -> SoundingFormationSnapshot:
    """Create one deterministic assembled D8 state for the first experience.

    Values are fixture inputs only. The presentation consumes canonical model
    objects and never derives alternate sounding or observation semantics.
    """

    pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
        frame="N",
    )
    timing = PingTiming(
        trigger_time=SimulationTime(seconds=0.0),
        tx_time=SimulationTime(seconds=0.0),
        rx_start_time=SimulationTime(seconds=0.01),
        rx_end_time=SimulationTime(seconds=0.10),
    )
    ping = AcquisitionPing(
        ping_index=12,
        timing=timing,
        tx_pose=pose,
        rx_start_pose=pose,
        rx_end_pose=pose,
    )
    beam = BeamRay(
        definition=BeamDefinition(index=7, across_track_angle=0.0, role="rx", array_name="rx"),
        direction_array_frame=Vector3(x=0.0, y=0.30, z=0.954),
        direction_sensor_frame=Vector3(x=0.0, y=0.30, z=0.954),
    )
    detection = BottomDetection(
        parent_beam_index=7,
        detection_index=2,
        detection_method="amplitude_peak",
        arrival_offset_seconds=0.04,
        tx_delay_seconds=0.0,
        twtt_seconds=0.04,
        detected_across_track_angle_rad=0.3047,
        normalized_amplitude=1.0,
    )
    truth = SoundingState(
        point=Vector3(x=0.0, y=9.40, z=29.85),
        sensor_origin=pose.position,
        beam_direction=beam.direction_sensor_frame,
        slant_range=31.30,
    )
    reconstructed = SoundingState(
        point=Vector3(x=0.0, y=9.30, z=29.90),
        sensor_origin=pose.position,
        beam_direction=beam.direction_sensor_frame,
        slant_range=31.30,
    )
    comparison = SoundingComparison(
        beam_index=7,
        true=truth,
        configured=reconstructed,
        error_vector=Vector3(x=0.0, y=0.10, z=-0.05),
        horizontal_error=0.10,
        vertical_error=-0.05,
        error_magnitude=0.1118,
    )
    return SoundingFormationSnapshot(
        ping=ping,
        beam=beam,
        detection=detection,
        associated_pose=pose,
        sounding=comparison,
    )


def build_sounding_formation_lesson() -> tuple[object, dict[str, object], Callable[[str], None]]:
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtWidgets import (
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
    root.setSpacing(6)

    heading = QLabel()
    heading.setStyleSheet("font-size: 19px; font-weight: 600;")
    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 14px; font-weight: 550; color: #3f5962;")
    root.addWidget(heading)
    root.addWidget(question)

    stage_row = QHBoxLayout()
    stage_labels: list[QLabel] = []
    for _stage in STAGE_ORDER:
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setMinimumHeight(38)
        stage_labels.append(label)
        stage_row.addWidget(label, 1)
    root.addLayout(stage_row)

    body = QHBoxLayout()
    root.addLayout(body, 1)
    figure = Figure(figsize=(8.3, 5.5), constrained_layout=True)
    axis = figure.subplots(1, 1)
    canvas = FigureCanvas(figure)
    body.addWidget(canvas, 3)

    side = QFrame()
    side.setMinimumWidth(285)
    side.setMaximumWidth(345)
    side.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    side_layout = QVBoxLayout(side)
    readout = QLabel()
    readout.setWordWrap(True)
    readout.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    side_layout.addWidget(readout)
    semantics = QLabel()
    semantics.setWordWrap(True)
    semantics.setStyleSheet("font-size: 11px; color: #455a64;")
    side_layout.addWidget(semantics)
    side_layout.addStretch(1)
    body.addWidget(side, 1)

    controls_row = QHBoxLayout()
    previous = QPushButton()
    next_button = QPushButton()
    run = QPushButton()
    reset = QPushButton()
    for button in (previous, next_button, run, reset):
        controls_row.addWidget(button)
    controls_row.addStretch(1)
    root.addLayout(controls_row)

    guidance = QLabel()
    guidance.setWordWrap(True)
    guidance.setStyleSheet("font-size: 11px; color: #3f5962;")
    root.addWidget(guidance)
    boundary = QLabel()
    boundary.setWordWrap(True)
    boundary.setStyleSheet("font-size: 10px; color: #687780;")
    root.addWidget(boundary)

    snapshot = _reference_snapshot()
    current_locale = "en"
    running = False
    timer = QTimer(page)
    timer.setInterval(700)

    def xyz(point: Vector3) -> str:
        return f"({point.x:.2f}, {point.y:.2f}, {point.z:.2f}) m"

    def redraw() -> None:
        text = _TEXT[current_locale]
        state = snapshot.observation_state
        stage_index = snapshot.stage_index

        for index, label in enumerate(stage_labels):
            active = index == stage_index
            label.setText(text["stages"][index])
            label.setStyleSheet(
                "padding: 4px; border-radius: 5px; font-size: 9px; "
                + ("font-weight: 700; background: #dceff5; border: 1px solid #4e7c8b;" if active else "background: #f2f4f5; color: #66757d;")
            )

        axis.clear()
        axis.set_title(text["stages"][stage_index])
        axis.set_xlabel("Across-track y (m)")
        axis.set_ylabel("Down z (m)")
        axis.invert_yaxis()
        axis.set_xlim(-4.0, 16.0)
        axis.set_ylim(36.0, -4.0)
        axis.plot([-4.0, 16.0], [30.4, 29.2], linewidth=1.5)
        axis.plot([-1.3, 1.3], [0.0, 0.0], linewidth=4.0)
        axis.scatter([0.0], [0.0], marker="v", s=50)

        truth = state.truth_sounding.point
        derived = state.reconstructed_sounding.point
        if stage_index >= 1:
            axis.plot([0.0, truth.y], [0.0, truth.z], linestyle="--", linewidth=1.3)
        if stage_index >= 2:
            axis.scatter([truth.y], [truth.z], s=55, label=text["truth"])
        if stage_index >= 8:
            axis.scatter([derived.y], [derived.z], marker="x", s=65, label=text["derived"])
        if stage_index >= 9:
            axis.plot([truth.y, derived.y], [truth.z, derived.z], linewidth=2.0)
        if stage_index >= 2:
            axis.legend(loc="lower left", fontsize=8)
        canvas.draw_idle()

        association = state.association
        rows = [f"<b>{text['identity']}:</b> {association.ping_index} / {association.beam_index} / {association.detection_index}"]
        if stage_index >= 4:
            rows.append(f"<b>{text['observed']}:</b> BottomDetection")
        if stage_index >= 5:
            rows.append(f"<b>{text['twtt']}:</b> {snapshot.twtt_seconds * 1000.0:.2f} ms")
        if stage_index >= 6 and snapshot.detected_angle_rad is not None:
            rows.append(f"<b>{text['angle']}:</b> {degrees(snapshot.detected_angle_rad):.2f}°")
        if stage_index >= 7:
            rows.append(f"<b>{text['configured']}:</b> Pose + BeamRay")
        if stage_index >= 8:
            rows.append(f"<b>{text['derived_xyz']}:</b> {xyz(derived)}")
        if stage_index >= 9:
            rows.append(f"<b>{text['truth_xyz']}:</b> {xyz(truth)}")
            err = snapshot.sounding.error_vector
            rows.append(f"<b>{text['residual']}:</b> {xyz(err)}")
        readout.setText("<br>".join(rows))
        semantics.setText(
            f"<b>{text['truth']}</b> → SoundingState<br>"
            f"<b>{text['observed']}</b> → BottomDetection<br>"
            f"<b>{text['configured']}</b> → Pose + BeamRay<br>"
            f"<b>{text['derived']}</b> → SoundingState"
        )
        guidance.setText(text["guidance"][stage_index])
        boundary.setText(text["boundary"])
        previous.setEnabled(stage_index > 0)
        next_button.setEnabled(stage_index < len(STAGE_ORDER) - 1)
        run.setText(text["pause"] if running else text["run"])

    def set_snapshot(value: SoundingFormationSnapshot) -> None:
        nonlocal snapshot
        snapshot = value
        redraw()

    def go_previous() -> None:
        set_snapshot(snapshot.previous_stage())

    def go_next() -> None:
        set_snapshot(snapshot.next_stage())

    def reset_lesson() -> None:
        nonlocal running
        running = False
        timer.stop()
        set_snapshot(snapshot.reset())

    def tick() -> None:
        nonlocal running
        if snapshot.stage_index >= len(STAGE_ORDER) - 1:
            running = False
            timer.stop()
            redraw()
            return
        go_next()

    def toggle_run() -> None:
        nonlocal running
        running = not running
        if running:
            timer.start()
        else:
            timer.stop()
        redraw()

    previous.clicked.connect(go_previous)
    next_button.clicked.connect(go_next)
    reset.clicked.connect(reset_lesson)
    run.clicked.connect(toggle_run)
    timer.timeout.connect(tick)

    def apply_language(locale: str) -> None:
        nonlocal current_locale
        current_locale = locale if locale in _TEXT else "en"
        text = _TEXT[current_locale]
        heading.setText(text["title"])
        question.setText(text["question"])
        previous.setText(text["previous"])
        next_button.setText(text["next"])
        reset.setText(text["reset"])
        redraw()

    controls = {
        "previous": previous,
        "next": next_button,
        "run": run,
        "reset": reset,
        "stage_labels": stage_labels,
        "readout": readout,
        "semantics": semantics,
        "guidance": guidance,
        "boundary": boundary,
        "figure": figure,
        "timer": timer,
        "snapshot": lambda: snapshot,
    }
    apply_language("en")
    return page, controls, apply_language
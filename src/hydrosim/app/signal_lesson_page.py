"""Concept-derived PySide6 presentation for PED-D2 Signal.

The page deliberately keeps waveform and matched-filter physics in the canonical
acquisition/visualization layers. This module only composes the learning scene.
"""

from __future__ import annotations

from collections.abc import Callable

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import prepare_signal_explorer_display_trace, prepare_signal_explorer_snapshot

_TEXT = {
    "en": {
        "back": "← System map",
        "eyebrow": "PED-D2 · PULSE & SIGNAL PROCESSING",
        "title": "See one acoustic event change shape",
        "question": "Switch CW ↔ Chirp, then follow the same pulse from transmit to return and processing.",
        "controls": "SIGNAL CONTROLS",
        "frequency": "Centre frequency",
        "duration": "Pulse duration",
        "bandwidth": "LFM bandwidth",
        "direction": "Sweep",
        "envelope": "Envelope",
        "up": "Up",
        "down": "Down",
        "rectangular": "Rectangular",
        "tukey": "Tukey",
        "reset": "Reset experiment",
        "transmit": "01 · TRANSMIT",
        "return": "02 · RETURN",
        "process": "03 · PROCESS",
        "waveform": "Outgoing waveform",
        "echo": "Returned echo",
        "compression": "Matched-filter response",
        "cw": "CW · constant rhythm",
        "chirp": "CHIRP · changing rhythm",
        "boundary": "Passband panels represent the acoustic waveform. Processing uses the canonical complex-baseband matched-filter response.",
    },
    "pt-BR": {
        "back": "← Mapa do sistema",
        "eyebrow": "PED-D2 · PULSO E PROCESSAMENTO DE SINAL",
        "title": "Veja um mesmo evento acústico mudar de forma",
        "question": "Alterne CW ↔ Chirp e acompanhe o mesmo pulso da transmissão ao retorno e ao processamento.",
        "controls": "CONTROLES DO SINAL",
        "frequency": "Frequência central",
        "duration": "Duração do pulso",
        "bandwidth": "Largura de banda LFM",
        "direction": "Varredura",
        "envelope": "Envoltória",
        "up": "Ascendente",
        "down": "Descendente",
        "rectangular": "Retangular",
        "tukey": "Tukey",
        "reset": "Restaurar experimento",
        "transmit": "01 · TRANSMIT",
        "return": "02 · RETURN",
        "process": "03 · PROCESS",
        "waveform": "Forma de onda transmitida",
        "echo": "Eco retornado",
        "compression": "Resposta do filtro casado",
        "cw": "CW · ritmo constante",
        "chirp": "CHIRP · ritmo variável",
        "boundary": "Os painéis em banda passante representam a onda acústica. O processamento usa a resposta canônica do filtro casado em banda-base complexa.",
    },
}


def build_signal_lesson() -> tuple[object, dict[str, object], Callable[[str], None]]:
    """Build the PED-D2 concept-lab page and return controls/localization hook."""

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel,
        QPushButton, QVBoxLayout, QWidget,
    )
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    page = QWidget()
    page.setStyleSheet(
        "QWidget { background: #07121d; color: #eaf2f7; }"
        "QLabel { color: #eaf2f7; }"
        "QFrame#controls { background: #0b1b28; border: 1px solid #17364a; border-radius: 14px; }"
        "QFrame#stage { background: #0a1824; border: 1px solid #17364a; border-radius: 14px; }"
        "QPushButton { background: #102535; color: #eaf2f7; border: 1px solid #29485c; border-radius: 9px; padding: 8px 12px; }"
        "QPushButton:hover { background: #173247; }"
        "QPushButton#modeOn { background: #1b6675; border-color: #46a7b8; }"
        "QComboBox, QDoubleSpinBox { background: #102535; color: #eaf2f7; border: 1px solid #29485c; border-radius: 6px; padding: 4px; }"
    )
    root = QVBoxLayout(page)
    root.setContentsMargins(18, 14, 18, 16)
    root.setSpacing(10)

    toolbar = QHBoxLayout()
    back = QPushButton()
    back.setMaximumWidth(150)
    breadcrumb = QLabel("Signal  /  Waveform laboratory")
    breadcrumb.setStyleSheet("color: #8fb3c6; font-size: 12px;")
    toolbar.addWidget(back)
    toolbar.addSpacing(8)
    toolbar.addWidget(breadcrumb)
    toolbar.addStretch(1)
    root.addLayout(toolbar)

    eyebrow = QLabel()
    eyebrow.setStyleSheet("color: #57bfd0; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
    title = QLabel()
    title.setStyleSheet("font-size: 27px; font-weight: 700;")
    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 14px; color: #a8bfcc;")
    root.addWidget(eyebrow)
    root.addWidget(title)
    root.addWidget(question)

    body = QHBoxLayout()
    body.setSpacing(12)
    root.addLayout(body, 1)

    controls_frame = QFrame(objectName="controls")
    controls_frame.setMinimumWidth(270)
    controls_frame.setMaximumWidth(310)
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(14, 14, 14, 14)
    controls_layout.setSpacing(9)
    controls_title = QLabel()
    controls_title.setStyleSheet("color: #7fc9d5; font-size: 12px; font-weight: 700;")
    controls_layout.addWidget(controls_title)

    mode_row = QHBoxLayout()
    cw_button = QPushButton("CW")
    chirp_button = QPushButton("CHIRP")
    mode_row.addWidget(cw_button)
    mode_row.addWidget(chirp_button)
    controls_layout.addLayout(mode_row)

    form = QFormLayout()
    form.setVerticalSpacing(9)
    frequency_label, duration_label, bandwidth_label, direction_label, envelope_label = (QLabel() for _ in range(5))
    frequency = QDoubleSpinBox(); frequency.setRange(50, 700); frequency.setValue(200); frequency.setSuffix(" kHz")
    duration = QDoubleSpinBox(); duration.setRange(0.1, 5.0); duration.setDecimals(1); duration.setValue(1.0); duration.setSuffix(" ms")
    bandwidth = QDoubleSpinBox(); bandwidth.setRange(10, 300); bandwidth.setValue(100); bandwidth.setSuffix(" kHz")
    direction = QComboBox(); direction.addItem("Up", "up"); direction.addItem("Down", "down")
    envelope = QComboBox(); envelope.addItem("Rectangular", "rectangular"); envelope.addItem("Tukey", "tukey")
    for label, widget in ((frequency_label, frequency), (duration_label, duration), (bandwidth_label, bandwidth), (direction_label, direction), (envelope_label, envelope)):
        form.addRow(label, widget)
    controls_layout.addLayout(form)
    controls_layout.addStretch(1)
    reset = QPushButton()
    controls_layout.addWidget(reset)
    body.addWidget(controls_frame)

    stage = QFrame(objectName="stage")
    stage_layout = QVBoxLayout(stage)
    stage_layout.setContentsMargins(12, 10, 12, 10)
    stage_layout.setSpacing(6)

    flow = QHBoxLayout()
    transmit_label, return_label, process_label = QLabel(), QLabel(), QLabel()
    for label in (transmit_label, return_label, process_label):
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #65c7d4; font-size: 10px; font-weight: 700;")
        flow.addWidget(label, 1)
        if label is not process_label:
            arrow = QLabel("→"); arrow.setAlignment(Qt.AlignmentFlag.AlignCenter); arrow.setStyleSheet("color:#52758a;"); flow.addWidget(arrow)
    stage_layout.addLayout(flow)

    figure = Figure(figsize=(10.0, 6.8), facecolor="#0a1824", constrained_layout=True)
    axes = figure.subplots(3, 1)
    canvas = FigureCanvas(figure)
    stage_layout.addWidget(canvas, 1)

    identity = QLabel()
    identity.setAlignment(Qt.AlignmentFlag.AlignCenter)
    identity.setStyleSheet("font-size: 12px; color: #9bb7c7; padding: 4px;")
    stage_layout.addWidget(identity)
    body.addWidget(stage, 1)

    boundary = QLabel(); boundary.setWordWrap(True); boundary.setStyleSheet("font-size: 10px; color: #6f8a9a;")
    root.addWidget(boundary)

    current_locale = "en"
    pulse_mode = "chirp"

    def pulse_objects():
        common = dict(center_frequency_hz=frequency.value() * 1e3, duration_seconds=duration.value() * 1e-3, envelope_model=str(envelope.currentData()))
        cw = ContinuousWavePulse(**common)
        lfm = LinearFMPulse(**common, bandwidth_hz=bandwidth.value() * 1e3, chirp_direction=str(direction.currentData()))
        return cw, lfm

    def style_axis(axis):
        axis.set_facecolor("#0a1824")
        axis.tick_params(colors="#7f9cad", labelsize=8)
        for spine in axis.spines.values(): spine.set_color("#24475a")
        axis.grid(True, color="#24475a", alpha=0.28)
        axis.xaxis.label.set_color("#9bb7c7"); axis.yaxis.label.set_color("#9bb7c7"); axis.title.set_color("#eaf2f7")

    def redraw():
        cw, lfm = pulse_objects()
        selected = cw if pulse_mode == "cw" else lfm
        highest = max(float(cw.center_frequency_hz), lfm.start_frequency_hz, lfm.end_frequency_hz)
        display = prepare_signal_explorer_display_trace(selected, sample_rate_hz=max(2.5e6, 6.0 * highest))
        processing = prepare_signal_explorer_snapshot(selected, sample_rate_hz=max(400e3, 2.5 * float(getattr(selected, "bandwidth_hz", 100e3))))
        text = _TEXT[current_locale]
        for axis in axes: axis.clear(); style_axis(axis)
        t_ms = [v * 1e3 for v in display.time_seconds]
        axes[0].plot(t_ms, display.passband_amplitude, linewidth=1.5)
        axes[0].set_title(text["waveform"]); axes[0].set_ylabel("Amplitude")
        delay = duration.value() * 0.32
        axes[1].plot([v + delay for v in t_ms], [0.58 * v for v in display.passband_amplitude], linewidth=1.5)
        axes[1].set_title(text["echo"]); axes[1].set_ylabel("Amplitude")
        axes[2].plot([v * 1e6 for v in processing.autocorrelation.lag_seconds], processing.autocorrelation.normalized_amplitude, linewidth=1.7)
        axes[2].set_title(text["compression"]); axes[2].set_xlabel("Lag (µs)"); axes[2].set_ylabel("Normalized")
        identity.setText(text["cw"] if pulse_mode == "cw" else text["chirp"])
        cw_button.setObjectName("modeOn" if pulse_mode == "cw" else "")
        chirp_button.setObjectName("modeOn" if pulse_mode == "chirp" else "")
        cw_button.style().unpolish(cw_button); cw_button.style().polish(cw_button)
        chirp_button.style().unpolish(chirp_button); chirp_button.style().polish(chirp_button)
        bandwidth.setEnabled(pulse_mode == "chirp"); direction.setEnabled(pulse_mode == "chirp")
        canvas.draw_idle()

    def set_mode(mode: str):
        nonlocal pulse_mode
        pulse_mode = mode
        redraw()

    def reset_controls():
        frequency.setValue(200); duration.setValue(1.0); bandwidth.setValue(100); direction.setCurrentIndex(0); envelope.setCurrentIndex(0); set_mode("chirp")

    cw_button.clicked.connect(lambda: set_mode("cw")); chirp_button.clicked.connect(lambda: set_mode("chirp"))
    for widget in (frequency, duration, bandwidth): widget.valueChanged.connect(lambda _value: redraw())
    direction.currentIndexChanged.connect(lambda _index: redraw()); envelope.currentIndexChanged.connect(lambda _index: redraw()); reset.clicked.connect(reset_controls)

    def apply_language(locale: str) -> None:
        nonlocal current_locale
        current_locale = locale if locale in _TEXT else "en"
        text = _TEXT[current_locale]
        back.setText(text["back"]); eyebrow.setText(text["eyebrow"]); title.setText(text["title"]); question.setText(text["question"])
        controls_title.setText(text["controls"]); frequency_label.setText(text["frequency"]); duration_label.setText(text["duration"]); bandwidth_label.setText(text["bandwidth"]); direction_label.setText(text["direction"]); envelope_label.setText(text["envelope"])
        direction.setItemText(0, text["up"]); direction.setItemText(1, text["down"]); envelope.setItemText(0, text["rectangular"]); envelope.setItemText(1, text["tukey"])
        reset.setText(text["reset"]); transmit_label.setText(text["transmit"]); return_label.setText(text["return"]); process_label.setText(text["process"]); boundary.setText(text["boundary"])
        redraw()

    controls = {"back": back, "cw": cw_button, "chirp": chirp_button, "frequency": frequency, "duration": duration, "bandwidth": bandwidth, "direction": direction, "envelope": envelope, "reset": reset, "figure": figure}
    apply_language("en")
    return page, controls, apply_language

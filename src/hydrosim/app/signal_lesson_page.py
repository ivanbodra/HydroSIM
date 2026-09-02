"""PySide6 presentation for the corrected D1 Signal lesson.

Presentation code consumes the canonical waveform/display API. Waveform physics,
chirp equations, envelope realization, and matched filtering remain downstream in
the acquisition and visualization layers.
"""

from __future__ import annotations

from collections.abc import Callable

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import (
    prepare_signal_explorer_display_trace,
    prepare_signal_explorer_snapshot,
)

_TEXT = {
    "en": {
        "title": "Signal — CW and LFM/chirp",
        "question": "How does a finite constant-frequency pulse differ from a chirp whose frequency sweeps during the pulse?",
        "controls": "Signal controls",
        "instruction": "Use one parameter set to compare the physical passband waveforms and their instantaneous frequency.",
        "pulse": "Pulse type / focus",
        "frequency": "Frequency / centre frequency",
        "duration": "Pulse duration",
        "bandwidth": "LFM bandwidth",
        "direction": "Sweep direction",
        "envelope": "Pulse envelope",
        "up": "Up",
        "down": "Down",
        "rectangular": "Rectangular",
        "tukey": "Tukey",
        "reset": "Reset",
        "cw_wave": "CW acoustic/passband waveform",
        "lfm_wave": "LFM acoustic/passband waveform",
        "inst_freq": "Instantaneous frequency",
        "processing": "Processing diagnostics — complex baseband matched-filter response",
        "boundary": "Passband traces are acoustic waveform representations. The matched-filter panel is a processing representation, not the transmitted acoustic waveform.",
    },
    "pt-BR": {
        "title": "Sinal — CW e LFM/chirp",
        "question": "Como um pulso finito de frequência constante difere de um chirp cuja frequência varia durante o pulso?",
        "controls": "Controles do sinal",
        "instruction": "Use um único conjunto de parâmetros para comparar as formas de onda físicas em banda passante e suas frequências instantâneas.",
        "pulse": "Tipo de pulso / foco",
        "frequency": "Frequência / frequência central",
        "duration": "Duração do pulso",
        "bandwidth": "Largura de banda LFM",
        "direction": "Direção da varredura",
        "envelope": "Envoltória do pulso",
        "up": "Ascendente",
        "down": "Descendente",
        "rectangular": "Retangular",
        "tukey": "Tukey",
        "reset": "Restaurar",
        "cw_wave": "Forma de onda acústica CW (banda passante)",
        "lfm_wave": "Forma de onda acústica LFM (banda passante)",
        "inst_freq": "Frequência instantânea",
        "processing": "Diagnósticos de processamento — resposta do filtro casado em banda-base complexa",
        "boundary": "As curvas em banda passante representam a forma de onda acústica. O painel do filtro casado é uma representação de processamento, não a onda acústica transmitida.",
    },
}


def build_signal_lesson() -> tuple[object, dict[str, object], Callable[[str], None]]:
    """Build D1 and return page, capture/test controls, and language hook."""

    from PySide6.QtWidgets import (
        QComboBox,
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
    body.setSpacing(10)
    root.addLayout(body, 1)

    controls_frame = QFrame()
    controls_frame.setMinimumWidth(245)
    controls_frame.setMaximumWidth(290)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_title = QLabel()
    controls_title.setStyleSheet("font-size: 14px; font-weight: 650;")
    instruction = QLabel()
    instruction.setWordWrap(True)
    instruction.setStyleSheet("color: #53616d; font-size: 11px;")
    controls_layout.addWidget(controls_title)
    controls_layout.addWidget(instruction)

    form = QFormLayout()
    form.setVerticalSpacing(6)
    pulse_label = QLabel()
    pulse_type = QComboBox()
    pulse_type.addItem("CW", "cw")
    pulse_type.addItem("LFM", "lfm")
    form.addRow(pulse_label, pulse_type)

    frequency_label = QLabel()
    frequency = QDoubleSpinBox()
    frequency.setRange(50.0, 700.0)
    frequency.setSingleStep(10.0)
    frequency.setDecimals(0)
    frequency.setValue(200.0)
    frequency.setSuffix(" kHz")
    form.addRow(frequency_label, frequency)

    duration_label = QLabel()
    duration = QDoubleSpinBox()
    duration.setRange(0.1, 5.0)
    duration.setSingleStep(0.1)
    duration.setDecimals(1)
    duration.setValue(1.0)
    duration.setSuffix(" ms")
    form.addRow(duration_label, duration)

    bandwidth_label = QLabel()
    bandwidth = QDoubleSpinBox()
    bandwidth.setRange(10.0, 300.0)
    bandwidth.setSingleStep(10.0)
    bandwidth.setDecimals(0)
    bandwidth.setValue(100.0)
    bandwidth.setSuffix(" kHz")
    form.addRow(bandwidth_label, bandwidth)

    direction_label = QLabel()
    direction = QComboBox()
    direction.addItem("Up", "up")
    direction.addItem("Down", "down")
    form.addRow(direction_label, direction)

    envelope_label = QLabel()
    envelope = QComboBox()
    envelope.addItem("Rectangular", "rectangular")
    envelope.addItem("Tukey", "tukey")
    form.addRow(envelope_label, envelope)
    controls_layout.addLayout(form)

    reset = QPushButton()
    controls_layout.addWidget(reset)
    controls_layout.addStretch(1)
    body.addWidget(controls_frame)

    figure = Figure(figsize=(9.0, 6.7), constrained_layout=True)
    axes = figure.subplots(4, 1, sharex=False)
    canvas = FigureCanvas(figure)
    body.addWidget(canvas, 1)

    boundary = QLabel()
    boundary.setWordWrap(True)
    boundary.setStyleSheet("font-size: 10px; color: #53616d;")
    root.addWidget(boundary)

    current_locale = "en"

    def pulses():
        common = dict(
            center_frequency_hz=frequency.value() * 1e3,
            duration_seconds=duration.value() * 1e-3,
            envelope_model=str(envelope.currentData()),
        )
        cw = ContinuousWavePulse(**common)
        lfm = LinearFMPulse(
            **common,
            bandwidth_hz=bandwidth.value() * 1e3,
            chirp_direction=str(direction.currentData()),
        )
        return cw, lfm

    def redraw() -> None:
        cw, lfm = pulses()
        highest_hz = max(
            float(cw.center_frequency_hz),
            lfm.start_frequency_hz,
            lfm.end_frequency_hz,
        )
        display_rate = max(2.5e6, 6.0 * highest_hz)
        cw_display = prepare_signal_explorer_display_trace(cw, sample_rate_hz=display_rate)
        lfm_display = prepare_signal_explorer_display_trace(lfm, sample_rate_hz=display_rate)

        selected = cw if pulse_type.currentData() == "cw" else lfm
        processing_rate = max(400e3, 2.5 * float(getattr(selected, "bandwidth_hz", 100e3)))
        processing = prepare_signal_explorer_snapshot(selected, sample_rate_hz=processing_rate)

        text = _TEXT[current_locale]
        for axis in axes:
            axis.clear()
            axis.grid(True, alpha=0.22)

        axes[0].plot(
            [value * 1e3 for value in cw_display.time_seconds],
            cw_display.passband_amplitude,
        )
        axes[0].set_ylabel("Amplitude")
        axes[0].set_title(text["cw_wave"])

        axes[1].plot(
            [value * 1e3 for value in lfm_display.time_seconds],
            lfm_display.passband_amplitude,
        )
        axes[1].set_ylabel("Amplitude")
        axes[1].set_title(text["lfm_wave"])

        axes[2].plot(
            [value * 1e3 for value in cw_display.time_seconds],
            [value / 1e3 for value in cw_display.instantaneous_frequency_hz],
            label="CW",
        )
        axes[2].plot(
            [value * 1e3 for value in lfm_display.time_seconds],
            [value / 1e3 for value in lfm_display.instantaneous_frequency_hz],
            label="LFM",
        )
        axes[2].set_ylabel("kHz")
        axes[2].set_title(text["inst_freq"])
        axes[2].legend(loc="best")

        axes[3].plot(
            [value * 1e6 for value in processing.autocorrelation.lag_seconds],
            processing.autocorrelation.normalized_amplitude,
        )
        axes[3].set_xlabel("Lag (µs)")
        axes[3].set_ylabel("Normalized")
        axes[3].set_title(text["processing"])
        canvas.draw_idle()

    def update_applicability() -> None:
        is_lfm = pulse_type.currentData() == "lfm"
        bandwidth.setEnabled(is_lfm)
        direction.setEnabled(is_lfm)
        redraw()

    def reset_controls() -> None:
        pulse_type.setCurrentIndex(0)
        frequency.setValue(200.0)
        duration.setValue(1.0)
        bandwidth.setValue(100.0)
        direction.setCurrentIndex(0)
        envelope.setCurrentIndex(0)
        update_applicability()

    for widget in (frequency, duration, bandwidth):
        widget.valueChanged.connect(lambda _value: redraw())
    direction.currentIndexChanged.connect(lambda _index: redraw())
    envelope.currentIndexChanged.connect(lambda _index: redraw())
    pulse_type.currentIndexChanged.connect(lambda _index: update_applicability())
    reset.clicked.connect(reset_controls)

    def apply_language(locale: str) -> None:
        nonlocal current_locale
        current_locale = locale if locale in _TEXT else "en"
        text = _TEXT[current_locale]
        heading.setText(text["title"])
        question.setText(text["question"])
        controls_title.setText(text["controls"])
        instruction.setText(text["instruction"])
        pulse_label.setText(text["pulse"])
        frequency_label.setText(text["frequency"])
        duration_label.setText(text["duration"])
        bandwidth_label.setText(text["bandwidth"])
        direction_label.setText(text["direction"])
        envelope_label.setText(text["envelope"])
        reset.setText(text["reset"])
        direction.setItemText(0, text["up"])
        direction.setItemText(1, text["down"])
        envelope.setItemText(0, text["rectangular"])
        envelope.setItemText(1, text["tukey"])
        boundary.setText(text["boundary"])
        redraw()

    controls = {
        "pulse_type": pulse_type,
        "frequency": frequency,
        "duration": duration,
        "bandwidth": bandwidth,
        "direction": direction,
        "envelope": envelope,
        "reset": reset,
        "figure": figure,
    }
    apply_language("en")
    update_applicability()
    return page, controls, apply_language

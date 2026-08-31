"""Guided desktop application shell for the HydroSIM Didactic Explorer.

The shell owns navigation, learning guidance, controls, and layout only. Scientific
calculations remain in the Scientific Core and visualization composition layers.
The Signal lesson is the first embedded vertical slice; later learning blocks
remain visible as planned product structure.
"""

from __future__ import annotations

from hydrosim.visualization import (
    SignalExplorerControls,
    draw_signal_explorer_comparison,
    prepare_signal_explorer_comparison,
)


_LESSONS = (
    ("Signal", "CW and chirp/LFM waveform and pulse-compression behavior."),
    ("Beam", "Array, beamwidth, footprint, and Mills Cross behavior."),
    ("Propagation", "Sound-speed profile, refraction, ray tracing, and attenuation."),
    ("Vessel", "Sensors, lever arms, waterline, draft, and vertical references."),
    ("Motion", "Roll, pitch, yaw, heave, latency, and sounding consequences."),
)

_SIGNAL_DEFAULTS = SignalExplorerControls()


def launch_didactic_explorer() -> None:
    """Launch the first integrated HydroSIM Didactic Explorer desktop window."""

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QDoubleSpinBox,
            QFormLayout,
            QFrame,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QListWidgetItem,
            QMainWindow,
            QPushButton,
            QSlider,
            QSplitter,
            QStackedWidget,
            QVBoxLayout,
            QWidget,
        )
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    except ImportError as exc:  # pragma: no cover - optional desktop dependencies
        raise ImportError(
            "PySide6 and Matplotlib are required for the HydroSIM desktop shell; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    from hydrosim.visualization.signal_explorer_plot import plot_signal_explorer_comparison

    app = QApplication.instance() or QApplication([])

    window = QMainWindow()
    window.setWindowTitle("HydroSIM — Didactic Explorer")
    window.resize(1440, 860)

    central = QWidget()
    root = QVBoxLayout(central)
    root.setContentsMargins(14, 14, 14, 14)
    root.setSpacing(10)

    title = QLabel("HydroSIM — Didactic Explorer")
    title.setStyleSheet("font-size: 22px; font-weight: 600;")
    subtitle = QLabel("Change one physical control. See what changes. Understand why.")
    subtitle.setStyleSheet("font-size: 12px;")
    root.addWidget(title)
    root.addWidget(subtitle)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    navigation = QListWidget()
    navigation.setMaximumWidth(210)
    for index, (lesson, _description) in enumerate(_LESSONS):
        suffix = "  • ready" if index == 0 else "  • planned"
        item = QListWidgetItem(lesson + suffix)
        item.setData(Qt.ItemDataRole.UserRole, lesson)
        navigation.addItem(item)
    splitter.addWidget(navigation)

    pages = QStackedWidget()
    splitter.addWidget(pages)
    splitter.setStretchFactor(1, 1)
    root.addWidget(splitter, 1)

    # Signal vertical slice -------------------------------------------------
    signal_page = QWidget()
    signal_root = QVBoxLayout(signal_page)
    signal_root.setSpacing(8)

    lesson_heading = QLabel("Signal — CW versus LFM chirp")
    lesson_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    signal_root.addWidget(lesson_heading)

    learning_question = QLabel(
        "<b>Learning question:</b> How do pulse duration and LFM bandwidth change "
        "the transmitted baseband signal and its pulse-compression response?"
    )
    learning_question.setWordWrap(True)
    signal_root.addWidget(learning_question)

    context = QLabel(
        "Scientific view: deterministic complex analytic/baseband waveform + normalized "
        "autocorrelation. Carrier frequency is fixed at 300 kHz in this lesson because "
        "the current baseband plots do not show a physical consequence of changing it."
    )
    context.setWordWrap(True)
    context.setStyleSheet("font-size: 11px;")
    signal_root.addWidget(context)

    signal_layout = QHBoxLayout()
    signal_root.addLayout(signal_layout, 1)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(315)
    controls_layout = QVBoxLayout(controls_frame)
    controls_title = QLabel("Try it")
    controls_title.setStyleSheet("font-size: 16px; font-weight: 600;")
    controls_layout.addWidget(controls_title)

    instruction = QLabel(
        "Change one control at a time. Watch the phase panel and the width of the "
        "matched-filter peak."
    )
    instruction.setWordWrap(True)
    controls_layout.addWidget(instruction)

    form = QFormLayout()

    duration = QDoubleSpinBox()
    duration.setRange(0.1, 5.0)
    duration.setSingleStep(0.1)
    duration.setDecimals(1)
    duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
    duration.setSuffix(" ms")
    form.addRow("Pulse duration", duration)

    duration_slider = QSlider(Qt.Orientation.Horizontal)
    duration_slider.setRange(1, 50)
    duration_slider.setValue(round(duration.value() * 10.0))
    form.addRow("", duration_slider)

    bandwidth = QDoubleSpinBox()
    bandwidth.setRange(10.0, 300.0)
    bandwidth.setSingleStep(10.0)
    bandwidth.setDecimals(0)
    bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
    bandwidth.setSuffix(" kHz")
    form.addRow("LFM bandwidth", bandwidth)

    bandwidth_slider = QSlider(Qt.Orientation.Horizontal)
    bandwidth_slider.setRange(10, 300)
    bandwidth_slider.setSingleStep(10)
    bandwidth_slider.setPageStep(20)
    bandwidth_slider.setValue(round(bandwidth.value()))
    form.addRow("", bandwidth_slider)
    controls_layout.addLayout(form)

    reset = QPushButton("Reset lesson")
    controls_layout.addWidget(reset)

    observation_title = QLabel("What to look for")
    observation_title.setStyleSheet("font-size: 14px; font-weight: 600;")
    controls_layout.addWidget(observation_title)
    observation = QLabel(
        "• Pulse duration changes the time extent of both finite pulses.\n"
        "• LFM bandwidth changes chirp phase evolution and the compressed response.\n"
        "• CW baseband stays phase-constant; this does not mean acoustic pressure is constant."
    )
    observation.setWordWrap(True)
    controls_layout.addWidget(observation)

    boundary = QLabel(
        "Not shown yet: frequency-dependent absorption, electronics, noise, and a general "
        "wave-equation field solution."
    )
    boundary.setWordWrap(True)
    boundary.setStyleSheet("font-size: 11px;")
    controls_layout.addWidget(boundary)
    controls_layout.addStretch(1)
    signal_layout.addWidget(controls_frame)

    cw, lfm = prepare_signal_explorer_comparison(_SIGNAL_DEFAULTS)
    figure, axes = plot_signal_explorer_comparison(cw, lfm)
    canvas = FigureCanvas(figure)
    signal_layout.addWidget(canvas, 1)

    def redraw_signal() -> None:
        bandwidth_hz = bandwidth.value() * 1e3
        state = SignalExplorerControls(
            center_frequency_hz=_SIGNAL_DEFAULTS.center_frequency_hz,
            duration_seconds=duration.value() * 1e-3,
            lfm_bandwidth_hz=bandwidth_hz,
            sample_rate_hz=max(_SIGNAL_DEFAULTS.sample_rate_hz, 1.25 * bandwidth_hz),
        )
        new_cw, new_lfm = prepare_signal_explorer_comparison(state)
        draw_signal_explorer_comparison(new_cw, new_lfm, axes)
        canvas.draw_idle()

    def duration_from_spin(value: float) -> None:
        slider_value = round(value * 10.0)
        if duration_slider.value() != slider_value:
            duration_slider.setValue(slider_value)
        redraw_signal()

    def duration_from_slider(value: int) -> None:
        spin_value = value / 10.0
        if duration.value() != spin_value:
            duration.setValue(spin_value)

    def bandwidth_from_spin(value: float) -> None:
        slider_value = round(value)
        if bandwidth_slider.value() != slider_value:
            bandwidth_slider.setValue(slider_value)
        redraw_signal()

    def bandwidth_from_slider(value: int) -> None:
        if bandwidth.value() != float(value):
            bandwidth.setValue(float(value))

    def reset_signal() -> None:
        duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
        bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
        redraw_signal()

    duration.valueChanged.connect(duration_from_spin)
    duration_slider.valueChanged.connect(duration_from_slider)
    bandwidth.valueChanged.connect(bandwidth_from_spin)
    bandwidth_slider.valueChanged.connect(bandwidth_from_slider)
    reset.clicked.connect(reset_signal)
    pages.addWidget(signal_page)

    # Visible product structure for future vertical slices -----------------
    for lesson, description in _LESSONS[1:]:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(lesson)
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        status = QLabel("Planned learning block")
        status.setStyleSheet("font-size: 12px; font-weight: 600;")
        body = QLabel(
            description
            + "\n\nThis view is intentionally unavailable until its first end-to-end "
            "learning slice is integrated and tested."
        )
        body.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(status)
        layout.addWidget(body)
        layout.addStretch(1)
        pages.addWidget(page)

    navigation.currentRowChanged.connect(pages.setCurrentIndex)
    navigation.setCurrentRow(0)

    window.setCentralWidget(central)
    window.show()
    window.hydrosim_pages = pages
    window.hydrosim_navigation = navigation
    window.hydrosim_signal_controls = {
        "duration": duration,
        "duration_slider": duration_slider,
        "bandwidth": bandwidth,
        "bandwidth_slider": bandwidth_slider,
        "reset": reset,
    }

    # Keep the main window reachable for interactive sessions and tests.
    app.hydrosim_didactic_explorer_window = window
    app.exec()

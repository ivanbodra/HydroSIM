"""Minimal desktop application shell for the HydroSIM Didactic Explorer.

The shell owns navigation and layout only. Scientific calculations remain in the
Scientific Core and visualization composition layers. The Signal lesson is the
first embedded vertical slice; later learning blocks intentionally appear as
placeholders so the product structure is visible before their implementation.
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


def launch_didactic_explorer() -> None:
    """Launch the first integrated HydroSIM Didactic Explorer desktop window."""

    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QDoubleSpinBox,
            QFormLayout,
            QFrame,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QMainWindow,
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
    window.resize(1400, 820)

    central = QWidget()
    root = QVBoxLayout(central)
    root.setContentsMargins(12, 12, 12, 12)
    root.setSpacing(10)

    title = QLabel("HydroSIM — Didactic Explorer")
    title.setStyleSheet("font-size: 22px; font-weight: 600;")
    subtitle = QLabel("Control → physical phenomenon → observable consequence")
    subtitle.setStyleSheet("font-size: 12px;")
    root.addWidget(title)
    root.addWidget(subtitle)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    navigation = QListWidget()
    navigation.setMaximumWidth(190)
    for lesson, _description in _LESSONS:
        navigation.addItem(lesson)
    splitter.addWidget(navigation)

    pages = QStackedWidget()
    splitter.addWidget(pages)
    splitter.setStretchFactor(1, 1)
    root.addWidget(splitter, 1)

    # Signal vertical slice -------------------------------------------------
    signal_page = QWidget()
    signal_layout = QHBoxLayout(signal_page)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(280)
    controls_layout = QVBoxLayout(controls_frame)
    controls_title = QLabel("Signal controls")
    controls_title.setStyleSheet("font-size: 16px; font-weight: 600;")
    controls_layout.addWidget(controls_title)

    form = QFormLayout()
    waveform = QComboBox()
    waveform.addItems(["CW + LFM comparison"])
    form.addRow("Lesson", waveform)

    frequency = QDoubleSpinBox()
    frequency.setRange(50.0, 700.0)
    frequency.setValue(300.0)
    frequency.setSuffix(" kHz")
    form.addRow("Center frequency", frequency)

    duration = QDoubleSpinBox()
    duration.setRange(0.1, 5.0)
    duration.setSingleStep(0.1)
    duration.setValue(1.0)
    duration.setSuffix(" ms")
    form.addRow("Pulse duration", duration)

    bandwidth = QDoubleSpinBox()
    bandwidth.setRange(10.0, 300.0)
    bandwidth.setValue(100.0)
    bandwidth.setSuffix(" kHz")
    form.addRow("LFM bandwidth", bandwidth)
    controls_layout.addLayout(form)

    note = QLabel(
        "The UI changes inputs only. Waveform sampling and matched-filter behavior "
        "are recalculated through the Scientific Core."
    )
    note.setWordWrap(True)
    controls_layout.addWidget(note)
    controls_layout.addStretch(1)
    signal_layout.addWidget(controls_frame)

    initial = SignalExplorerControls()
    cw, lfm = prepare_signal_explorer_comparison(initial)
    figure, axes = plot_signal_explorer_comparison(cw, lfm)
    canvas = FigureCanvas(figure)
    signal_layout.addWidget(canvas, 1)

    def redraw_signal() -> None:
        bandwidth_hz = bandwidth.value() * 1e3
        state = SignalExplorerControls(
            center_frequency_hz=frequency.value() * 1e3,
            duration_seconds=duration.value() * 1e-3,
            lfm_bandwidth_hz=bandwidth_hz,
            sample_rate_hz=max(initial.sample_rate_hz, 1.25 * bandwidth_hz),
        )
        new_cw, new_lfm = prepare_signal_explorer_comparison(state)
        draw_signal_explorer_comparison(new_cw, new_lfm, axes)
        canvas.draw_idle()

    frequency.valueChanged.connect(redraw_signal)
    duration.valueChanged.connect(redraw_signal)
    bandwidth.valueChanged.connect(redraw_signal)
    pages.addWidget(signal_page)

    # Visible product structure for future vertical slices -----------------
    for lesson, description in _LESSONS[1:]:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(lesson)
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        body = QLabel(description + "\n\nThis vertical slice has not been integrated yet.")
        body.setWordWrap(True)
        layout.addWidget(heading)
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
        "frequency": frequency,
        "duration": duration,
        "bandwidth": bandwidth,
    }

    # Keep the main window reachable for interactive sessions and tests.
    app.hydrosim_didactic_explorer_window = window
    app.exec()

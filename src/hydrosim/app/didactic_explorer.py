"""Guided desktop application shell for the HydroSIM Didactic Explorer.

The shell owns navigation, learning guidance, controls, and layout only. Scientific
calculations remain in the Scientific Core and visualization composition layers.
"""

from __future__ import annotations

from hydrosim.visualization import (
    BeamExplorerControls,
    SignalExplorerControls,
    draw_beam_explorer_snapshot,
    draw_signal_explorer_comparison,
    prepare_beam_explorer_snapshot,
    prepare_signal_explorer_comparison,
)


_LESSONS = (
    ("Signal", "CW and chirp/LFM waveform and pulse-compression behavior."),
    ("Beam", "Frequency, aperture, beam pattern, side lobes, and Mills Cross behavior."),
    ("Propagation", "Sound-speed profile, refraction, ray tracing, and attenuation."),
    ("Vessel", "Sensors, lever arms, waterline, draft, and vertical references."),
    ("Motion", "Roll, pitch, yaw, heave, latency, and sounding consequences."),
)

_SIGNAL_DEFAULTS = SignalExplorerControls()
_BEAM_DEFAULTS = BeamExplorerControls()


def launch_didactic_explorer() -> None:
    """Launch the integrated HydroSIM Didactic Explorer desktop window."""

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
            QSpinBox,
            QSplitter,
            QStackedWidget,
            QVBoxLayout,
            QWidget,
        )
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "PySide6 and Matplotlib are required for the HydroSIM desktop shell; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    from hydrosim.visualization.beam_explorer_plot import plot_beam_explorer_snapshot
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
    root.addWidget(title)
    root.addWidget(QLabel("Change one physical control. See what changes. Understand why."))

    splitter = QSplitter(Qt.Orientation.Horizontal)
    navigation = QListWidget()
    navigation.setMaximumWidth(210)
    for index, (lesson, _description) in enumerate(_LESSONS):
        suffix = "  • ready" if index in {0, 1} else "  • planned"
        item = QListWidgetItem(lesson + suffix)
        item.setData(Qt.ItemDataRole.UserRole, lesson)
        navigation.addItem(item)
    splitter.addWidget(navigation)
    pages = QStackedWidget()
    splitter.addWidget(pages)
    splitter.setStretchFactor(1, 1)
    root.addWidget(splitter, 1)

    # Signal lesson ---------------------------------------------------------
    signal_page = QWidget()
    signal_root = QVBoxLayout(signal_page)
    signal_heading = QLabel("Signal — CW versus LFM chirp")
    signal_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    signal_root.addWidget(signal_heading)
    question = QLabel(
        "<b>Learning question:</b> How do pulse duration and LFM bandwidth change "
        "the transmitted baseband signal and its pulse-compression response?"
    )
    question.setWordWrap(True)
    signal_root.addWidget(question)
    context = QLabel(
        "Scientific view: deterministic complex analytic/baseband waveform + normalized "
        "autocorrelation. Carrier frequency is fixed at 300 kHz in this lesson because "
        "the current baseband plots do not show a physical consequence of changing it."
    )
    context.setWordWrap(True)
    signal_root.addWidget(context)

    signal_layout = QHBoxLayout()
    signal_root.addLayout(signal_layout, 1)
    controls_frame = QFrame()
    controls_frame.setMaximumWidth(315)
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.addWidget(QLabel("Try it"))
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
    bandwidth_slider.setValue(round(bandwidth.value()))
    form.addRow("", bandwidth_slider)
    controls_layout.addLayout(form)
    signal_reset = QPushButton("Reset lesson")
    controls_layout.addWidget(signal_reset)
    signal_observation = QLabel(
        "<b>What to look for</b><br>Pulse duration changes pulse extent. LFM bandwidth "
        "changes chirp phase evolution and the compressed response.<br><br>"
        "<b>Not shown yet:</b> frequency-dependent absorption, electronics, noise, and a "
        "general wave-equation field solution."
    )
    signal_observation.setWordWrap(True)
    controls_layout.addWidget(signal_observation)
    controls_layout.addStretch(1)
    signal_layout.addWidget(controls_frame)

    cw, lfm = prepare_signal_explorer_comparison(_SIGNAL_DEFAULTS)
    signal_figure, signal_axes = plot_signal_explorer_comparison(cw, lfm)
    signal_canvas = FigureCanvas(signal_figure)
    signal_layout.addWidget(signal_canvas, 1)

    def redraw_signal() -> None:
        bandwidth_hz = bandwidth.value() * 1e3
        state = SignalExplorerControls(
            center_frequency_hz=_SIGNAL_DEFAULTS.center_frequency_hz,
            duration_seconds=duration.value() * 1e-3,
            lfm_bandwidth_hz=bandwidth_hz,
            sample_rate_hz=max(_SIGNAL_DEFAULTS.sample_rate_hz, 1.25 * bandwidth_hz),
        )
        new_cw, new_lfm = prepare_signal_explorer_comparison(state)
        draw_signal_explorer_comparison(new_cw, new_lfm, signal_axes)
        signal_canvas.draw_idle()

    duration.valueChanged.connect(
        lambda value: duration_slider.setValue(round(value * 10.0))
        if duration_slider.value() != round(value * 10.0)
        else redraw_signal()
    )
    duration_slider.valueChanged.connect(
        lambda value: duration.setValue(value / 10.0) if duration.value() != value / 10.0 else None
    )
    bandwidth.valueChanged.connect(
        lambda value: bandwidth_slider.setValue(round(value))
        if bandwidth_slider.value() != round(value)
        else redraw_signal()
    )
    bandwidth_slider.valueChanged.connect(
        lambda value: bandwidth.setValue(float(value)) if bandwidth.value() != float(value) else None
    )

    def reset_signal() -> None:
        duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
        bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
        redraw_signal()

    signal_reset.clicked.connect(reset_signal)
    pages.addWidget(signal_page)

    # Beam lesson -----------------------------------------------------------
    beam_page = QWidget()
    beam_root = QVBoxLayout(beam_page)
    beam_heading = QLabel("Beam — frequency, wavelength, and aperture")
    beam_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    beam_root.addWidget(beam_heading)
    beam_question = QLabel(
        "<b>Learning question:</b> For a fixed physical element spacing, how do frequency "
        "and aperture size change the main lobe and secondary lobes of a Mills-Cross beam?"
    )
    beam_question.setWordWrap(True)
    beam_root.addWidget(beam_question)
    beam_context = QLabel(
        "Scientific view: normalized narrowband far-field TX/RX array response. Sound speed, "
        "element spacing, element size, broadside steering, and array orientation are fixed."
    )
    beam_context.setWordWrap(True)
    beam_root.addWidget(beam_context)

    beam_layout = QHBoxLayout()
    beam_root.addLayout(beam_layout, 1)
    beam_controls_frame = QFrame()
    beam_controls_frame.setMaximumWidth(315)
    beam_controls = QVBoxLayout(beam_controls_frame)
    beam_instruction = QLabel(
        "Change frequency first, then the number of elements. Compare main-lobe width and "
        "watch for additional strong lobes as d/λ increases."
    )
    beam_instruction.setWordWrap(True)
    beam_controls.addWidget(beam_instruction)
    beam_form = QFormLayout()

    beam_frequency = QDoubleSpinBox()
    beam_frequency.setRange(75.0, 300.0)
    beam_frequency.setSingleStep(5.0)
    beam_frequency.setDecimals(0)
    beam_frequency.setValue(_BEAM_DEFAULTS.frequency_hz / 1e3)
    beam_frequency.setSuffix(" kHz")
    beam_form.addRow("Frequency", beam_frequency)
    beam_frequency_slider = QSlider(Qt.Orientation.Horizontal)
    beam_frequency_slider.setRange(75, 300)
    beam_frequency_slider.setValue(round(beam_frequency.value()))
    beam_form.addRow("", beam_frequency_slider)

    beam_elements = QSpinBox()
    beam_elements.setRange(4, 32)
    beam_elements.setValue(_BEAM_DEFAULTS.elements_per_arm)
    beam_form.addRow("Elements per arm", beam_elements)
    beam_elements_slider = QSlider(Qt.Orientation.Horizontal)
    beam_elements_slider.setRange(4, 32)
    beam_elements_slider.setValue(beam_elements.value())
    beam_form.addRow("", beam_elements_slider)
    beam_controls.addLayout(beam_form)
    beam_reset = QPushButton("Reset lesson")
    beam_controls.addWidget(beam_reset)
    beam_readout = QLabel()
    beam_readout.setWordWrap(True)
    beam_controls.addWidget(beam_readout)
    beam_note = QLabel(
        "<b>What to look for</b><br>Higher frequency shortens wavelength. More elements increase "
        "the physical aperture. Both can narrow the main response; fixed spacing can also make "
        "grating-lobe behavior visible when spacing becomes large relative to wavelength.<br><br>"
        "<b>Not shown yet:</b> footprint on a seabed, steering, propagation loss, refraction, "
        "multisector transmission, or vendor-specific transducer geometry."
    )
    beam_note.setWordWrap(True)
    beam_controls.addWidget(beam_note)
    beam_controls.addStretch(1)
    beam_layout.addWidget(beam_controls_frame)

    beam_snapshot = prepare_beam_explorer_snapshot(_BEAM_DEFAULTS)
    beam_figure, beam_axes = plot_beam_explorer_snapshot(beam_snapshot)
    beam_canvas = FigureCanvas(beam_figure)
    beam_layout.addWidget(beam_canvas, 1)

    def redraw_beam() -> None:
        state = BeamExplorerControls(
            frequency_hz=beam_frequency.value() * 1e3,
            elements_per_arm=beam_elements.value(),
            sound_speed_mps=_BEAM_DEFAULTS.sound_speed_mps,
            element_spacing_m=_BEAM_DEFAULTS.element_spacing_m,
            element_size_m=_BEAM_DEFAULTS.element_size_m,
            angular_extent_deg=_BEAM_DEFAULTS.angular_extent_deg,
            angular_sample_count=_BEAM_DEFAULTS.angular_sample_count,
        )
        snapshot = prepare_beam_explorer_snapshot(state)
        draw_beam_explorer_snapshot(snapshot, beam_axes)
        beam_readout.setText(
            f"λ = {snapshot.wavelength_m * 1e3:.2f} mm<br>"
            f"d/λ = {snapshot.spacing_over_wavelength:.2f}<br>"
            f"Element-center span = {snapshot.element_center_span_m * 100:.1f} cm"
        )
        beam_canvas.draw_idle()

    beam_frequency.valueChanged.connect(
        lambda value: beam_frequency_slider.setValue(round(value))
        if beam_frequency_slider.value() != round(value)
        else redraw_beam()
    )
    beam_frequency_slider.valueChanged.connect(
        lambda value: beam_frequency.setValue(float(value))
        if beam_frequency.value() != float(value)
        else None
    )
    beam_elements.valueChanged.connect(
        lambda value: beam_elements_slider.setValue(value)
        if beam_elements_slider.value() != value
        else redraw_beam()
    )
    beam_elements_slider.valueChanged.connect(
        lambda value: beam_elements.setValue(value) if beam_elements.value() != value else None
    )

    def reset_beam() -> None:
        beam_frequency.setValue(_BEAM_DEFAULTS.frequency_hz / 1e3)
        beam_elements.setValue(_BEAM_DEFAULTS.elements_per_arm)
        redraw_beam()

    beam_reset.clicked.connect(reset_beam)
    redraw_beam()
    pages.addWidget(beam_page)

    # Planned slices --------------------------------------------------------
    for lesson, description in _LESSONS[2:]:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(lesson)
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(heading)
        layout.addWidget(QLabel("Planned learning block"))
        body = QLabel(
            description + "\n\nThis view remains unavailable until its first end-to-end "
            "learning slice is integrated and tested."
        )
        body.setWordWrap(True)
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
        "reset": signal_reset,
    }
    window.hydrosim_beam_controls = {
        "frequency": beam_frequency,
        "frequency_slider": beam_frequency_slider,
        "elements": beam_elements,
        "elements_slider": beam_elements_slider,
        "reset": beam_reset,
    }
    app.hydrosim_didactic_explorer_window = window
    app.exec()

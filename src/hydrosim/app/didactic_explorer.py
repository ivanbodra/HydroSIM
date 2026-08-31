"""Guided desktop application shell for the HydroSIM Didactic Explorer.

The shell owns navigation, learning guidance, controls, and layout only. Scientific
calculations remain in the Scientific Core and visualization composition layers.
"""

from __future__ import annotations

from hydrosim.app.localization import Localizer
from hydrosim.app.signal_compare import SignalLessonComparison, SignalLessonSnapshot
from hydrosim.visualization import (
    BeamExplorerControls,
    PropagationExplorerControls,
    SignalExplorerControls,
    draw_beam_explorer_snapshot,
    draw_layered_svp_explorer_snapshot,
    draw_signal_explorer_comparison,
    prepare_beam_explorer_snapshot,
    prepare_propagation_explorer_snapshot,
    prepare_signal_explorer_comparison,
)


_LESSONS = (
    ("Signal", "CW and chirp/LFM waveform and pulse-compression behavior."),
    ("Beam", "Frequency, aperture, beam pattern, side lobes, and footprint behavior."),
    ("Propagation", "Sound-speed profile, refraction, ray tracing, and sounding reconstruction."),
    ("Vessel", "Sensors, lever arms, waterline, draft, and vertical references."),
    ("Motion", "Roll, pitch, yaw, heave, latency, and sounding consequences."),
)

_SIGNAL_DEFAULTS = SignalExplorerControls()
_BEAM_DEFAULTS = BeamExplorerControls()
_PROPAGATION_DEFAULTS = PropagationExplorerControls()


def launch_didactic_explorer() -> None:
    """Launch the integrated HydroSIM Didactic Explorer desktop window."""

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
    from hydrosim.visualization.layered_svp_explorer_plot import plot_layered_svp_explorer_snapshot
    from hydrosim.visualization.signal_explorer_plot import plot_signal_explorer_comparison

    app = QApplication.instance() or QApplication([])
    window = QMainWindow()
    window.resize(1440, 860)

    central = QWidget()
    root = QVBoxLayout(central)
    root.setContentsMargins(18, 16, 18, 16)
    root.setSpacing(10)

    header = QHBoxLayout()
    header_text = QVBoxLayout()
    title = QLabel()
    title.setStyleSheet("font-size: 23px; font-weight: 650;")
    tagline = QLabel()
    tagline.setStyleSheet("color: #53616d;")
    header_text.addWidget(title)
    header_text.addWidget(tagline)
    header.addLayout(header_text)
    header.addStretch(1)
    language_label = QLabel()
    language_selector = QComboBox()
    language_selector.addItem("EN", "en")
    language_selector.addItem("PT-BR", "pt-BR")
    language_selector.setMinimumWidth(86)
    header.addWidget(language_label)
    header.addWidget(language_selector)
    root.addLayout(header)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    navigation = QListWidget()
    navigation.setMaximumWidth(210)
    splitter.addWidget(navigation)
    pages = QStackedWidget()
    splitter.addWidget(pages)
    splitter.setStretchFactor(1, 1)
    root.addWidget(splitter, 1)

    # Signal lesson ---------------------------------------------------------
    signal_page = QWidget()
    signal_root = QVBoxLayout(signal_page)
    signal_root.setContentsMargins(12, 4, 8, 4)
    signal_root.setSpacing(10)

    signal_heading = QLabel()
    signal_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    signal_root.addWidget(signal_heading)

    question_frame = QFrame()
    question_frame.setObjectName("learningQuestion")
    question_frame.setStyleSheet(
        "QFrame#learningQuestion { background: #eef6f8; border-radius: 8px; padding: 4px; }"
    )
    question_layout = QVBoxLayout(question_frame)
    question_label = QLabel()
    question_label.setStyleSheet("font-size: 12px; font-weight: 650; color: #3f5962;")
    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 18px; font-weight: 550;")
    question_layout.addWidget(question_label)
    question_layout.addWidget(question)
    signal_root.addWidget(question_frame)

    signal_layout = QHBoxLayout()
    signal_layout.setSpacing(14)
    signal_root.addLayout(signal_layout, 1)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(320)
    controls_frame.setMinimumWidth(275)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(14, 14, 14, 14)
    try_it_label = QLabel()
    try_it_label.setStyleSheet("font-size: 16px; font-weight: 650;")
    controls_layout.addWidget(try_it_label)
    instruction = QLabel()
    instruction.setWordWrap(True)
    controls_layout.addWidget(instruction)

    form = QFormLayout()
    duration_label = QLabel()
    duration = QDoubleSpinBox()
    duration.setRange(0.1, 5.0)
    duration.setSingleStep(0.1)
    duration.setDecimals(1)
    duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
    duration.setSuffix(" ms")
    form.addRow(duration_label, duration)
    duration_slider = QSlider(Qt.Orientation.Horizontal)
    duration_slider.setRange(1, 50)
    duration_slider.setValue(round(duration.value() * 10.0))
    form.addRow("", duration_slider)

    bandwidth_label = QLabel()
    bandwidth = QDoubleSpinBox()
    bandwidth.setRange(10.0, 300.0)
    bandwidth.setSingleStep(10.0)
    bandwidth.setDecimals(0)
    bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
    bandwidth.setSuffix(" kHz")
    form.addRow(bandwidth_label, bandwidth)
    bandwidth_slider = QSlider(Qt.Orientation.Horizontal)
    bandwidth_slider.setRange(10, 300)
    bandwidth_slider.setValue(round(bandwidth.value()))
    form.addRow("", bandwidth_slider)
    controls_layout.addLayout(form)

    baseline_hint = QLabel()
    baseline_hint.setWordWrap(True)
    controls_layout.addWidget(baseline_hint)
    baseline_actions = QHBoxLayout()
    signal_set_baseline = QPushButton()
    signal_clear_baseline = QPushButton()
    signal_clear_baseline.setEnabled(False)
    baseline_actions.addWidget(signal_set_baseline)
    baseline_actions.addWidget(signal_clear_baseline)
    controls_layout.addLayout(baseline_actions)

    signal_reset = QPushButton()
    signal_reset.setMinimumHeight(34)
    controls_layout.addWidget(signal_reset)
    controls_layout.addStretch(1)
    signal_layout.addWidget(controls_frame)

    cw, lfm = prepare_signal_explorer_comparison(_SIGNAL_DEFAULTS)
    signal_figure, signal_axes = plot_signal_explorer_comparison(cw, lfm)
    signal_canvas = FigureCanvas(signal_figure)
    signal_layout.addWidget(signal_canvas, 1)

    learning_footer = QHBoxLayout()
    learning_footer.setSpacing(10)

    observation_frame = QFrame()
    observation_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    observation_layout = QVBoxLayout(observation_frame)
    observation_title = QLabel()
    observation_title.setStyleSheet("font-weight: 650;")
    signal_observation = QLabel()
    signal_observation.setWordWrap(True)
    observation_layout.addWidget(observation_title)
    observation_layout.addWidget(signal_observation)
    learning_footer.addWidget(observation_frame, 2)

    quantitative_frame = QFrame()
    quantitative_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    quantitative_layout = QVBoxLayout(quantitative_frame)
    quantitative_title = QLabel()
    quantitative_title.setStyleSheet("font-weight: 650;")
    signal_readout = QLabel()
    signal_readout.setWordWrap(True)
    signal_comparison_readout = QLabel()
    signal_comparison_readout.setWordWrap(True)
    quantitative_layout.addWidget(quantitative_title)
    quantitative_layout.addWidget(signal_readout)
    quantitative_layout.addWidget(signal_comparison_readout)
    learning_footer.addWidget(quantitative_frame, 1)

    boundary_frame = QFrame()
    boundary_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    boundary_layout = QVBoxLayout(boundary_frame)
    boundary_title = QLabel()
    boundary_title.setStyleSheet("font-weight: 650;")
    boundary_text = QLabel()
    boundary_text.setWordWrap(True)
    boundary_layout.addWidget(boundary_title)
    boundary_layout.addWidget(boundary_text)
    learning_footer.addWidget(boundary_frame, 1)
    signal_root.addLayout(learning_footer)

    signal_baseline: SignalLessonSnapshot | None = None

    def current_signal_snapshot() -> SignalLessonSnapshot:
        return SignalLessonSnapshot(
            duration_seconds=duration.value() * 1e-3,
            lfm_bandwidth_hz=bandwidth.value() * 1e3,
        )

    def update_signal_comparison_display() -> None:
        localizer = Localizer(str(language_selector.currentData() or "en"))
        if signal_baseline is None:
            signal_comparison_readout.setText(
                f"{localizer.text('signal.baseline_empty')}<br>"
                f"<i>{localizer.text('signal.baseline_note')}</i>"
            )
            signal_clear_baseline.setEnabled(False)
            return

        current = current_signal_snapshot()
        comparison = SignalLessonComparison(baseline=signal_baseline, current=current)
        signal_clear_baseline.setEnabled(True)
        signal_comparison_readout.setText(
            f"<b>{localizer.text('common.baseline')}</b>: "
            f"T={signal_baseline.duration_seconds * 1e3:.1f} ms, "
            f"B={signal_baseline.lfm_bandwidth_hz / 1e3:.0f} kHz, "
            f"TB={signal_baseline.time_bandwidth_product:.1f}<br>"
            f"<b>{localizer.text('common.current')}</b>: "
            f"T={current.duration_seconds * 1e3:.1f} ms, "
            f"B={current.lfm_bandwidth_hz / 1e3:.0f} kHz, "
            f"TB={current.time_bandwidth_product:.1f}<br>"
            f"<b>Δ</b>: T={comparison.duration_change_seconds * 1e3:+.1f} ms, "
            f"B={comparison.bandwidth_change_hz / 1e3:+.0f} kHz, "
            f"TB={comparison.time_bandwidth_change:+.1f}<br>"
            f"<i>{localizer.text('signal.baseline_note')}</i>"
        )

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
        time_bandwidth = state.duration_seconds * state.lfm_bandwidth_hz
        reciprocal_bandwidth_us = 1e6 / state.lfm_bandwidth_hz
        signal_readout.setText(
            f"T = {state.duration_seconds * 1e3:.1f} ms<br>"
            f"B = {state.lfm_bandwidth_hz / 1e3:.0f} kHz<br>"
            f"TB = {time_bandwidth:.1f}<br>"
            f"1/B = {reciprocal_bandwidth_us:.1f} μs"
        )
        update_signal_comparison_display()
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

    def set_signal_baseline() -> None:
        nonlocal signal_baseline
        signal_baseline = current_signal_snapshot()
        update_signal_comparison_display()

    def clear_signal_baseline() -> None:
        nonlocal signal_baseline
        signal_baseline = None
        update_signal_comparison_display()

    def reset_signal() -> None:
        duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
        bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
        redraw_signal()

    signal_set_baseline.clicked.connect(set_signal_baseline)
    signal_clear_baseline.clicked.connect(clear_signal_baseline)
    signal_reset.clicked.connect(reset_signal)
    pages.addWidget(signal_page)

    # Beam lesson -----------------------------------------------------------
    beam_page = QWidget()
    beam_root = QVBoxLayout(beam_page)
    beam_heading = QLabel("Beam — frequency, wavelength, aperture, and footprint")
    beam_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    beam_root.addWidget(beam_heading)
    beam_question = QLabel(
        "<b>Learning question:</b> How do frequency and aperture change beamwidth and the "
        "resulting -3 dB footprint on a flat seabed?"
    )
    beam_question.setWordWrap(True)
    beam_root.addWidget(beam_question)
    beam_context = QLabel(
        "Scientific view: normalized narrowband far-field TX/RX array response plus the "
        "existing flat-bottom beamwidth footprint approximation at fixed depth."
    )
    beam_context.setWordWrap(True)
    beam_root.addWidget(beam_context)
    beam_layout = QHBoxLayout()
    beam_root.addLayout(beam_layout, 1)
    beam_controls_frame = QFrame()
    beam_controls_frame.setMaximumWidth(315)
    beam_controls = QVBoxLayout(beam_controls_frame)
    beam_instruction = QLabel(
        "Change frequency first, then the number of elements. Compare main-lobe width "
        "and the footprint dimensions."
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
        "<b>What to look for</b><br>Higher frequency shortens wavelength. More elements "
        "increase aperture. Narrower -3 dB beamwidths reduce the approximate nadir footprint."
        "<br><br><b>Not shown yet:</b> steering, refraction, multisector transmission, "
        "bottom scattering, or vendor-specific transducer geometry."
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
            seafloor_depth_m=_BEAM_DEFAULTS.seafloor_depth_m,
        )
        snapshot = prepare_beam_explorer_snapshot(state)
        draw_beam_explorer_snapshot(snapshot, beam_axes)
        beam_readout.setText(
            f"λ = {snapshot.wavelength_m * 1e3:.2f} mm<br>"
            f"d/λ = {snapshot.spacing_over_wavelength:.2f}<br>"
            f"-3 dB beamwidth = {snapshot.along_track_beamwidth_deg:.2f}°<br>"
            f"Footprint = {snapshot.footprint.beam_limited_along_track_width_m:.2f} × "
            f"{snapshot.footprint.beam_limited_across_track_width_m:.2f} m"
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

    # Propagation lesson ----------------------------------------------------
    propagation_page = QWidget()
    propagation_root = QVBoxLayout(propagation_page)
    propagation_heading = QLabel("Propagation — SVP mismatch and reconstructed swath")
    propagation_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    propagation_root.addWidget(propagation_heading)
    propagation_question = QLabel(
        "<b>Learning question:</b> What happens when the water column is physically unchanged, "
        "but the lower-layer sound speed used during processing is wrong?"
    )
    propagation_question.setWordWrap(True)
    propagation_root.addWidget(propagation_question)
    propagation_context = QLabel(
        "Scientific view: stationary monostatic principal-plane geometry, flat bottom, two "
        "piecewise-constant layers, ideal transducer sound speed, and zero array tilt."
    )
    propagation_context.setWordWrap(True)
    propagation_root.addWidget(propagation_context)
    propagation_layout = QHBoxLayout()
    propagation_root.addLayout(propagation_layout, 1)
    propagation_controls_frame = QFrame()
    propagation_controls_frame.setMaximumWidth(315)
    propagation_controls = QVBoxLayout(propagation_controls_frame)
    propagation_instruction = QLabel(
        "Change only the processing sound-speed bias. Truth rays stay fixed; watch where the "
        "reconstructed soundings move and how beamwise error grows toward the swath edges."
    )
    propagation_instruction.setWordWrap(True)
    propagation_controls.addWidget(propagation_instruction)
    propagation_form = QFormLayout()
    propagation_bias = QDoubleSpinBox()
    propagation_bias.setRange(-30.0, 30.0)
    propagation_bias.setSingleStep(1.0)
    propagation_bias.setDecimals(0)
    propagation_bias.setValue(_PROPAGATION_DEFAULTS.processing_lower_layer_bias_mps)
    propagation_bias.setSuffix(" m/s")
    propagation_form.addRow("Processing lower-layer bias", propagation_bias)
    propagation_bias_slider = QSlider(Qt.Orientation.Horizontal)
    propagation_bias_slider.setRange(-30, 30)
    propagation_bias_slider.setValue(round(propagation_bias.value()))
    propagation_form.addRow("", propagation_bias_slider)
    propagation_controls.addLayout(propagation_form)
    propagation_reset = QPushButton("Reset lesson")
    propagation_controls.addWidget(propagation_reset)
    propagation_readout = QLabel()
    propagation_readout.setWordWrap(True)
    propagation_controls.addWidget(propagation_readout)
    propagation_note = QLabel(
        "<b>What to look for</b><br>The Truth SVP and rays do not change when this control moves. "
        "Only the processing profile changes. A profile mismatch can curve or displace the "
        "reconstructed swath even though the real seabed is flat.<br><br>"
        "<b>Not shown yet:</b> frequency-dependent absorption, continuous-gradient SVP, "
        "surface sound-speed error, vessel motion, or uncertainty."
    )
    propagation_note.setWordWrap(True)
    propagation_controls.addWidget(propagation_note)
    propagation_controls.addStretch(1)
    propagation_layout.addWidget(propagation_controls_frame)

    propagation_snapshot = prepare_propagation_explorer_snapshot(_PROPAGATION_DEFAULTS)
    propagation_figure, propagation_axes = plot_layered_svp_explorer_snapshot(propagation_snapshot)
    propagation_canvas = FigureCanvas(propagation_figure)
    propagation_layout.addWidget(propagation_canvas, 1)

    def redraw_propagation() -> None:
        state = PropagationExplorerControls(
            processing_lower_layer_bias_mps=propagation_bias.value(),
            terrain_depth_m=_PROPAGATION_DEFAULTS.terrain_depth_m,
            interface_depth_m=_PROPAGATION_DEFAULTS.interface_depth_m,
            upper_layer_sound_speed_mps=_PROPAGATION_DEFAULTS.upper_layer_sound_speed_mps,
            lower_layer_sound_speed_mps=_PROPAGATION_DEFAULTS.lower_layer_sound_speed_mps,
            maximum_beam_angle_deg=_PROPAGATION_DEFAULTS.maximum_beam_angle_deg,
            beam_count=_PROPAGATION_DEFAULTS.beam_count,
        )
        snapshot = prepare_propagation_explorer_snapshot(state)
        draw_layered_svp_explorer_snapshot(snapshot, propagation_axes)
        max_error = max(float(beam.sounding_error_norm_m) for beam in snapshot.beams)
        propagation_readout.setText(
            f"Truth lower layer = {_PROPAGATION_DEFAULTS.lower_layer_sound_speed_mps:.0f} m/s<br>"
            f"Processing lower layer = "
            f"{_PROPAGATION_DEFAULTS.lower_layer_sound_speed_mps + propagation_bias.value():.0f} m/s<br>"
            f"Max sounding error = {max_error:.3f} m"
        )
        propagation_canvas.draw_idle()

    propagation_bias.valueChanged.connect(
        lambda value: propagation_bias_slider.setValue(round(value))
        if propagation_bias_slider.value() != round(value)
        else redraw_propagation()
    )
    propagation_bias_slider.valueChanged.connect(
        lambda value: propagation_bias.setValue(float(value))
        if propagation_bias.value() != float(value)
        else None
    )

    def reset_propagation() -> None:
        propagation_bias.setValue(_PROPAGATION_DEFAULTS.processing_lower_layer_bias_mps)
        redraw_propagation()

    propagation_reset.clicked.connect(reset_propagation)
    redraw_propagation()
    pages.addWidget(propagation_page)

    # Planned slices --------------------------------------------------------
    planned_headings: list[QLabel] = []
    planned_labels: list[QLabel] = []
    for lesson, description in _LESSONS[3:]:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(lesson)
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(heading)
        planned = QLabel("Planned learning block")
        layout.addWidget(planned)
        body = QLabel(
            description + "\n\nThis view remains unavailable until its first end-to-end "
            "learning slice is integrated and tested."
        )
        body.setWordWrap(True)
        layout.addWidget(body)
        layout.addStretch(1)
        planned_headings.append(heading)
        planned_labels.append(planned)
        pages.addWidget(page)

    def apply_language(locale: str) -> None:
        """Update presentation text without touching simulation controls or state."""

        localizer = Localizer(locale)
        window.setWindowTitle(localizer.text("app.title"))
        title.setText(localizer.text("app.title"))
        tagline.setText(localizer.text("app.tagline"))
        language_label.setText(localizer.text("common.language"))

        nav_keys = ("signal", "beam", "propagation", "vessel", "motion")
        for index, key in enumerate(nav_keys):
            status_key = "status.ready" if index in {0, 1, 2} else "status.planned"
            navigation.item(index).setText(
                f"{localizer.text(f'nav.{key}')}  • {localizer.text(status_key)}"
            )

        signal_heading.setText(localizer.text("signal.title"))
        question_label.setText(localizer.text("common.learning_question").upper())
        question.setText(localizer.text("signal.question_focus"))
        try_it_label.setText(localizer.text("common.try_it"))
        instruction.setText(localizer.text("signal.instruction"))
        duration_label.setText(localizer.text("signal.pulse_duration"))
        bandwidth_label.setText(localizer.text("signal.lfm_bandwidth"))
        baseline_hint.setText(localizer.text("signal.compare_hint"))
        signal_set_baseline.setText(localizer.text("common.set_baseline"))
        signal_clear_baseline.setText(localizer.text("common.clear_baseline"))
        signal_reset.setText(localizer.text("common.reset"))
        observation_title.setText(localizer.text("common.what_to_look_for"))
        signal_observation.setText(localizer.text("signal.observation"))
        quantitative_title.setText(localizer.text("common.quantitative"))
        boundary_title.setText(localizer.text("common.scientific_boundary"))
        boundary_text.setText(
            f"{localizer.text('signal.scientific_boundary')}<br><br>"
            f"{localizer.text('signal.not_shown')}"
        )
        update_signal_comparison_display()

        beam_heading.setText(localizer.text("beam.title"))
        beam_question.setText(
            f"<b>{localizer.text('common.learning_question')}:</b> "
            f"{localizer.text('beam.question')}"
        )
        propagation_heading.setText(localizer.text("propagation.title"))
        propagation_question.setText(
            f"<b>{localizer.text('common.learning_question')}:</b> "
            f"{localizer.text('propagation.question')}"
        )
        planned_headings[0].setText(localizer.text("nav.vessel"))
        planned_headings[1].setText(localizer.text("nav.motion"))

    def on_language_changed(_index: int) -> None:
        apply_language(str(language_selector.currentData()))

    language_selector.currentIndexChanged.connect(on_language_changed)
    navigation.currentRowChanged.connect(pages.setCurrentIndex)
    for index, (lesson, _description) in enumerate(_LESSONS):
        item = QListWidgetItem(lesson + ("  • ready" if index in {0, 1, 2} else "  • planned"))
        item.setData(Qt.ItemDataRole.UserRole, lesson)
        navigation.addItem(item)

    navigation.setCurrentRow(0)
    redraw_signal()
    apply_language("en")

    window.setCentralWidget(central)
    window.show()
    window.hydrosim_pages = pages
    window.hydrosim_navigation = navigation
    window.hydrosim_language_selector = language_selector
    window.hydrosim_signal_controls = {
        "duration": duration,
        "duration_slider": duration_slider,
        "bandwidth": bandwidth,
        "bandwidth_slider": bandwidth_slider,
        "set_baseline": signal_set_baseline,
        "clear_baseline": signal_clear_baseline,
        "comparison_readout": signal_comparison_readout,
        "reset": signal_reset,
    }
    window.hydrosim_beam_controls = {
        "frequency": beam_frequency,
        "frequency_slider": beam_frequency_slider,
        "elements": beam_elements,
        "elements_slider": beam_elements_slider,
        "reset": beam_reset,
    }
    window.hydrosim_propagation_controls = {
        "processing_bias": propagation_bias,
        "processing_bias_slider": propagation_bias_slider,
        "reset": propagation_reset,
    }
    app.hydrosim_didactic_explorer_window = window
    app.exec()

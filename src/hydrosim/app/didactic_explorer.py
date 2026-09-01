"""Guided desktop application shell for the HydroSIM Didactic Explorer.

The shell owns navigation, learning guidance, controls, and layout only. Scientific
calculations remain in the Scientific Core and visualization composition layers.
"""

from __future__ import annotations

from hydrosim.app.localization import Localizer
from hydrosim.app.motion_lesson_page import build_motion_lesson
from hydrosim.app.signal_compare import SignalLessonComparison, SignalLessonSnapshot
from hydrosim.app.vessel_lesson import build_vessel_lesson
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
    root.setContentsMargins(14, 10, 14, 12)
    root.setSpacing(6)

    header = QHBoxLayout()
    header.setSpacing(8)
    header_text = QVBoxLayout()
    header_text.setSpacing(0)
    title = QLabel()
    title.setStyleSheet("font-size: 21px; font-weight: 650;")
    tagline = QLabel()
    tagline.setStyleSheet("color: #53616d; font-size: 12px;")
    header_text.addWidget(title)
    header_text.addWidget(tagline)
    header.addLayout(header_text)
    header.addStretch(1)
    language_label = QLabel()
    language_selector = QComboBox()
    language_selector.addItem("EN", "en")
    language_selector.addItem("PT-BR", "pt-BR")
    language_selector.setMinimumWidth(80)
    header.addWidget(language_label)
    header.addWidget(language_selector)
    root.addLayout(header)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    navigation = QListWidget()
    navigation.setMaximumWidth(165)
    splitter.addWidget(navigation)
    pages = QStackedWidget()
    splitter.addWidget(pages)
    splitter.setStretchFactor(1, 1)
    root.addWidget(splitter, 1)

    # Signal lesson ---------------------------------------------------------
    signal_page = QWidget()
    signal_root = QVBoxLayout(signal_page)
    signal_root.setContentsMargins(8, 2, 4, 2)
    signal_root.setSpacing(6)

    signal_heading = QLabel()
    signal_heading.setStyleSheet("font-size: 19px; font-weight: 600;")
    signal_root.addWidget(signal_heading)

    question_frame = QFrame()
    question_frame.setObjectName("learningQuestion")
    question_frame.setStyleSheet("QFrame#learningQuestion { background: transparent; }")
    question_layout = QHBoxLayout(question_frame)
    question_layout.setContentsMargins(0, 0, 0, 2)
    question_layout.setSpacing(8)
    question_label = QLabel()
    question_label.setStyleSheet("font-size: 11px; font-weight: 650; color: #3f5962;")
    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 15px; font-weight: 550;")
    question_layout.addWidget(question_label)
    question_layout.addWidget(question, 1)
    signal_root.addWidget(question_frame)

    signal_layout = QHBoxLayout()
    signal_layout.setSpacing(10)
    signal_root.addLayout(signal_layout, 1)

    controls_frame = QFrame()
    controls_frame.setMaximumWidth(255)
    controls_frame.setMinimumWidth(225)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_layout.setSpacing(6)
    try_it_label = QLabel()
    try_it_label.setStyleSheet("font-size: 14px; font-weight: 650;")
    controls_layout.addWidget(try_it_label)
    instruction = QLabel()
    instruction.setWordWrap(True)
    instruction.setStyleSheet("color: #53616d; font-size: 11px;")
    controls_layout.addWidget(instruction)

    form = QFormLayout()
    form.setVerticalSpacing(5)
    form.setHorizontalSpacing(8)

    carrier_frequency_label = QLabel()
    carrier_frequency = QDoubleSpinBox()
    carrier_frequency.setRange(50.0, 700.0)
    carrier_frequency.setSingleStep(10.0)
    carrier_frequency.setDecimals(0)
    carrier_frequency.setValue(_SIGNAL_DEFAULTS.center_frequency_hz / 1e3)
    carrier_frequency.setSuffix(" kHz")
    form.addRow(carrier_frequency_label, carrier_frequency)
    carrier_frequency_slider = QSlider(Qt.Orientation.Horizontal)
    carrier_frequency_slider.setRange(50, 700)
    carrier_frequency_slider.setValue(round(carrier_frequency.value()))
    form.addRow("", carrier_frequency_slider)

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
    baseline_hint.setVisible(False)
    controls_layout.addWidget(baseline_hint)
    baseline_actions = QHBoxLayout()
    baseline_actions.setSpacing(6)
    signal_set_baseline = QPushButton()
    signal_clear_baseline = QPushButton()
    signal_clear_baseline.setEnabled(False)
    baseline_actions.addWidget(signal_set_baseline)
    baseline_actions.addWidget(signal_clear_baseline)
    controls_layout.addLayout(baseline_actions)

    signal_reset = QPushButton()
    signal_reset.setMinimumHeight(28)
    controls_layout.addWidget(signal_reset)
    controls_layout.addStretch(1)
    signal_layout.addWidget(controls_frame)

    cw, lfm = prepare_signal_explorer_comparison(_SIGNAL_DEFAULTS)
    signal_figure, signal_axes = plot_signal_explorer_comparison(cw, lfm)
    signal_canvas = FigureCanvas(signal_figure)
    signal_layout.addWidget(signal_canvas, 1)

    learning_footer = QHBoxLayout()
    learning_footer.setSpacing(6)

    observation_frame = QFrame()
    observation_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    observation_layout = QVBoxLayout(observation_frame)
    observation_layout.setContentsMargins(8, 6, 8, 6)
    observation_layout.setSpacing(2)
    observation_title = QLabel()
    observation_title.setStyleSheet("font-weight: 650; font-size: 11px;")
    signal_observation = QLabel()
    signal_observation.setWordWrap(True)
    signal_observation.setStyleSheet("font-size: 11px;")
    observation_layout.addWidget(observation_title)
    observation_layout.addWidget(signal_observation)
    learning_footer.addWidget(observation_frame, 2)

    quantitative_frame = QFrame()
    quantitative_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    quantitative_layout = QVBoxLayout(quantitative_frame)
    quantitative_layout.setContentsMargins(8, 6, 8, 6)
    quantitative_layout.setSpacing(2)
    quantitative_title = QLabel()
    quantitative_title.setStyleSheet("font-weight: 650; font-size: 11px;")
    signal_readout = QLabel()
    signal_readout.setWordWrap(True)
    signal_readout.setStyleSheet("font-size: 11px;")
    signal_comparison_readout = QLabel()
    signal_comparison_readout.setWordWrap(True)
    signal_comparison_readout.setStyleSheet("font-size: 10px;")
    quantitative_layout.addWidget(quantitative_title)
    quantitative_layout.addWidget(signal_readout)
    quantitative_layout.addWidget(signal_comparison_readout)
    learning_footer.addWidget(quantitative_frame, 3)

    boundary_frame = QFrame()
    boundary_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    boundary_layout = QVBoxLayout(boundary_frame)
    boundary_layout.setContentsMargins(8, 6, 8, 6)
    boundary_layout.setSpacing(2)
    boundary_title = QLabel()
    boundary_title.setStyleSheet("font-weight: 650; font-size: 11px;")
    boundary_text = QLabel()
    boundary_text.setWordWrap(True)
    boundary_text.setStyleSheet("font-size: 10px;")
    boundary_layout.addWidget(boundary_title)
    boundary_layout.addWidget(boundary_text)
    learning_footer.addWidget(boundary_frame, 2)
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
                f"{localizer.text('signal.baseline_empty')} · "
                f"<i>{localizer.text('signal.baseline_note')}</i>"
            )
            signal_clear_baseline.setEnabled(False)
            return

        current = current_signal_snapshot()
        comparison = SignalLessonComparison(baseline=signal_baseline, current=current)
        signal_clear_baseline.setEnabled(True)
        signal_comparison_readout.setText(
            f"<b>{localizer.text('common.baseline')}</b> "
            f"T={signal_baseline.duration_seconds * 1e3:.1f} ms, "
            f"B={signal_baseline.lfm_bandwidth_hz / 1e3:.0f} kHz, "
            f"TB={signal_baseline.time_bandwidth_product:.1f} · "
            f"<b>{localizer.text('common.current')}</b> "
            f"T={current.duration_seconds * 1e3:.1f} ms, "
            f"B={current.lfm_bandwidth_hz / 1e3:.0f} kHz, "
            f"TB={current.time_bandwidth_product:.1f}<br>"
            f"<b>Δ</b> T={comparison.duration_change_seconds * 1e3:+.1f} ms, "
            f"B={comparison.bandwidth_change_hz / 1e3:+.0f} kHz, "
            f"TB={comparison.time_bandwidth_change:+.1f} · "
            f"<i>{localizer.text('signal.baseline_note')}</i>"
        )

    def redraw_signal() -> None:
        bandwidth_hz = bandwidth.value() * 1e3
        state = SignalExplorerControls(
            center_frequency_hz=carrier_frequency.value() * 1e3,
            duration_seconds=duration.value() * 1e-3,
            lfm_bandwidth_hz=bandwidth_hz,
            sample_rate_hz=max(_SIGNAL_DEFAULTS.sample_rate_hz, 1.25 * bandwidth_hz),
        )
        new_cw, new_lfm = prepare_signal_explorer_comparison(state)
        draw_signal_explorer_comparison(new_cw, new_lfm, signal_axes)
        time_bandwidth = state.duration_seconds * state.lfm_bandwidth_hz
        reciprocal_bandwidth_us = 1e6 / state.lfm_bandwidth_hz
        reference_wavelength_m = _BEAM_DEFAULTS.sound_speed_mps / state.center_frequency_hz
        signal_readout.setText(
            f"f={state.center_frequency_hz / 1e3:.0f} kHz · "
            f"λ@{_BEAM_DEFAULTS.sound_speed_mps:.0f} m/s={reference_wavelength_m * 1e3:.2f} mm · "
            f"T={state.duration_seconds * 1e3:.1f} ms · "
            f"B={state.lfm_bandwidth_hz / 1e3:.0f} kHz · "
            f"TB={time_bandwidth:.1f} · "
            f"1/B={reciprocal_bandwidth_us:.1f} μs"
        )
        update_signal_comparison_display()
        signal_canvas.draw_idle()

    def sync_signal_spinbox_to_slider(spinbox, slider, scale: float) -> None:
        target = round(spinbox.value() * scale)
        if slider.value() != target:
            slider.blockSignals(True)
            slider.setValue(target)
            slider.blockSignals(False)
        redraw_signal()

    def sync_signal_slider_to_spinbox(slider, spinbox, scale: float) -> None:
        target = slider.value() / scale
        if spinbox.value() != target:
            spinbox.blockSignals(True)
            spinbox.setValue(target)
            spinbox.blockSignals(False)
        redraw_signal()

    carrier_frequency.valueChanged.connect(
        lambda _value: sync_signal_spinbox_to_slider(
            carrier_frequency, carrier_frequency_slider, 1.0
        )
    )
    carrier_frequency_slider.valueChanged.connect(
        lambda _value: sync_signal_slider_to_spinbox(
            carrier_frequency_slider, carrier_frequency, 1.0
        )
    )
    duration.valueChanged.connect(
        lambda _value: sync_signal_spinbox_to_slider(duration, duration_slider, 10.0)
    )
    duration_slider.valueChanged.connect(
        lambda _value: sync_signal_slider_to_spinbox(duration_slider, duration, 10.0)
    )
    bandwidth.valueChanged.connect(
        lambda _value: sync_signal_spinbox_to_slider(bandwidth, bandwidth_slider, 1.0)
    )
    bandwidth_slider.valueChanged.connect(
        lambda _value: sync_signal_slider_to_spinbox(bandwidth_slider, bandwidth, 1.0)
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
        carrier_frequency.blockSignals(True)
        duration.blockSignals(True)
        bandwidth.blockSignals(True)
        carrier_frequency.setValue(_SIGNAL_DEFAULTS.center_frequency_hz / 1e3)
        duration.setValue(_SIGNAL_DEFAULTS.duration_seconds * 1e3)
        bandwidth.setValue(_SIGNAL_DEFAULTS.lfm_bandwidth_hz / 1e3)
        carrier_frequency.blockSignals(False)
        duration.blockSignals(False)
        bandwidth.blockSignals(False)
        carrier_frequency_slider.setValue(round(carrier_frequency.value()))
        duration_slider.setValue(round(duration.value() * 10.0))
        bandwidth_slider.setValue(round(bandwidth.value()))
        redraw_signal()

    signal_set_baseline.clicked.connect(set_signal_baseline)
    signal_clear_baseline.clicked.connect(clear_signal_baseline)
    signal_reset.clicked.connect(reset_signal)
    pages.addWidget(signal_page)

    # Beam lesson -----------------------------------------------------------
    beam_page = QWidget()
    beam_root = QVBoxLayout(beam_page)
    beam_root.setContentsMargins(8, 2, 4, 2)
    beam_root.setSpacing(6)
    beam_heading = QLabel()
    beam_heading.setStyleSheet("font-size: 20px; font-weight: 600;")
    beam_root.addWidget(beam_heading)
    beam_question = QLabel()
    beam_question.setWordWrap(True)
    beam_root.addWidget(beam_question)
    beam_context = QLabel()
    beam_context.setWordWrap(True)
    beam_context.setStyleSheet("color: #53616d; font-size: 11px;")
    beam_root.addWidget(beam_context)
    beam_layout = QHBoxLayout()
    beam_layout.setSpacing(10)
    beam_root.addLayout(beam_layout, 1)
    beam_controls_frame = QFrame()
    beam_controls_frame.setMaximumWidth(340)
    beam_controls_frame.setMinimumWidth(300)
    beam_controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    beam_controls = QVBoxLayout(beam_controls_frame)
    beam_controls.setContentsMargins(10, 8, 10, 8)
    beam_controls.setSpacing(6)
    beam_try_it = QLabel()
    beam_try_it.setStyleSheet("font-size: 14px; font-weight: 650;")
    beam_controls.addWidget(beam_try_it)
    beam_instruction = QLabel()
    beam_instruction.setWordWrap(True)
    beam_instruction.setStyleSheet("color: #53616d; font-size: 11px;")
    beam_controls.addWidget(beam_instruction)
    beam_form = QFormLayout()
    beam_form.setVerticalSpacing(5)
    beam_form.setHorizontalSpacing(8)

    beam_frequency_label = QLabel()
    beam_frequency = QDoubleSpinBox()
    beam_frequency.setRange(75.0, 300.0)
    beam_frequency.setSingleStep(5.0)
    beam_frequency.setDecimals(0)
    beam_frequency.setValue(_BEAM_DEFAULTS.frequency_hz / 1e3)
    beam_frequency.setSuffix(" kHz")
    beam_form.addRow(beam_frequency_label, beam_frequency)
    beam_frequency_slider = QSlider(Qt.Orientation.Horizontal)
    beam_frequency_slider.setRange(75, 300)
    beam_frequency_slider.setValue(round(beam_frequency.value()))
    beam_form.addRow("", beam_frequency_slider)

    beam_elements_label = QLabel()
    beam_elements = QSpinBox()
    beam_elements.setRange(4, 32)
    beam_elements.setValue(_BEAM_DEFAULTS.elements_per_arm)
    beam_form.addRow(beam_elements_label, beam_elements)
    beam_elements_slider = QSlider(Qt.Orientation.Horizontal)
    beam_elements_slider.setRange(4, 32)
    beam_elements_slider.setValue(beam_elements.value())
    beam_form.addRow("", beam_elements_slider)

    beam_spacing_label = QLabel()
    beam_spacing = QDoubleSpinBox()
    beam_spacing.setRange(1.0, 15.0)
    beam_spacing.setSingleStep(0.5)
    beam_spacing.setDecimals(1)
    beam_spacing.setValue(_BEAM_DEFAULTS.element_spacing_m * 1e3)
    beam_spacing.setSuffix(" mm")
    beam_form.addRow(beam_spacing_label, beam_spacing)
    beam_spacing_slider = QSlider(Qt.Orientation.Horizontal)
    beam_spacing_slider.setRange(10, 150)
    beam_spacing_slider.setValue(round(beam_spacing.value() * 10.0))
    beam_form.addRow("", beam_spacing_slider)

    beam_steering_label = QLabel()
    beam_steering = QDoubleSpinBox()
    beam_steering.setRange(-45.0, 45.0)
    beam_steering.setSingleStep(1.0)
    beam_steering.setDecimals(0)
    beam_steering.setValue(_BEAM_DEFAULTS.across_track_steering_angle_deg)
    beam_steering.setSuffix("°")
    beam_form.addRow(beam_steering_label, beam_steering)
    beam_steering_slider = QSlider(Qt.Orientation.Horizontal)
    beam_steering_slider.setRange(-45, 45)
    beam_steering_slider.setValue(round(beam_steering.value()))
    beam_form.addRow("", beam_steering_slider)
    beam_controls.addLayout(beam_form)

    beam_geometry = QLabel()
    beam_geometry.setWordWrap(True)
    beam_geometry.setStyleSheet("font-size: 11px; font-weight: 550;")
    beam_controls.addWidget(beam_geometry)
    beam_reset = QPushButton()
    beam_controls.addWidget(beam_reset)
    beam_readout = QLabel()
    beam_readout.setWordWrap(True)
    beam_readout.setStyleSheet("font-size: 10px;")
    beam_controls.addWidget(beam_readout)
    beam_note = QLabel()
    beam_note.setWordWrap(True)
    beam_note.setStyleSheet("font-size: 10px;")
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
            element_spacing_m=beam_spacing.value() * 1e-3,
            element_size_m=_BEAM_DEFAULTS.element_size_m,
            angular_extent_deg=_BEAM_DEFAULTS.angular_extent_deg,
            angular_sample_count=_BEAM_DEFAULTS.angular_sample_count,
            seafloor_depth_m=_BEAM_DEFAULTS.seafloor_depth_m,
            pulse_duration_seconds=_BEAM_DEFAULTS.pulse_duration_seconds,
            across_track_steering_angle_deg=beam_steering.value(),
        )
        snapshot = prepare_beam_explorer_snapshot(state)
        draw_beam_explorer_snapshot(snapshot, beam_axes)
        localizer = Localizer(str(language_selector.currentData() or "en"))
        steering = state.across_track_steering_angle_deg
        if steering > 0.0:
            direction = localizer.text("beam.port")
        elif steering < 0.0:
            direction = localizer.text("beam.starboard")
        else:
            direction = localizer.text("beam.nadir")
        across_bw_deg = snapshot.across_track_half_power_beamwidth_rad * 180.0 / 3.141592653589793
        beam_readout.setText(
            f"{localizer.text('beam.wavelength')}: {snapshot.wavelength_m * 1e3:.2f} mm<br>"
            f"{localizer.text('beam.spacing_ratio')}: {snapshot.spacing_over_wavelength:.2f}<br>"
            f"{localizer.text('beam.aperture_span')}: {snapshot.element_center_span_m * 1e3:.1f} mm<br>"
            f"{localizer.text('beam.beamwidth')}: {snapshot.along_track_beamwidth_deg:.2f}° × "
            f"{across_bw_deg:.2f}°<br>"
            f"{localizer.text('beam.footprint')}: "
            f"{snapshot.footprint.beam_limited_along_track_width_m:.2f} × "
            f"{snapshot.footprint.beam_limited_across_track_width_m:.2f} m<br>"
            f"{localizer.text('beam.steering_direction')}: {direction} ({steering:+.0f}°)<br>"
            f"{localizer.text('beam.seabed_offset')}: "
            f"{snapshot.steered_across_track_center_offset_m:+.2f} m"
        )
        beam_canvas.draw_idle()

    def sync_beam_spinbox_to_slider(spinbox, slider, scale: float) -> None:
        target = round(spinbox.value() * scale)
        if slider.value() != target:
            slider.blockSignals(True)
            slider.setValue(target)
            slider.blockSignals(False)
        redraw_beam()

    def sync_beam_slider_to_spinbox(slider, spinbox, scale: float) -> None:
        target = slider.value() / scale
        if spinbox.value() != target:
            spinbox.blockSignals(True)
            spinbox.setValue(target)
            spinbox.blockSignals(False)
        redraw_beam()

    beam_frequency.valueChanged.connect(
        lambda _value: sync_beam_spinbox_to_slider(beam_frequency, beam_frequency_slider, 1.0)
    )
    beam_frequency_slider.valueChanged.connect(
        lambda _value: sync_beam_slider_to_spinbox(beam_frequency_slider, beam_frequency, 1.0)
    )
    beam_elements.valueChanged.connect(
        lambda _value: sync_beam_spinbox_to_slider(beam_elements, beam_elements_slider, 1.0)
    )
    beam_elements_slider.valueChanged.connect(
        lambda _value: sync_beam_slider_to_spinbox(beam_elements_slider, beam_elements, 1.0)
    )
    beam_spacing.valueChanged.connect(
        lambda _value: sync_beam_spinbox_to_slider(beam_spacing, beam_spacing_slider, 10.0)
    )
    beam_spacing_slider.valueChanged.connect(
        lambda _value: sync_beam_slider_to_spinbox(beam_spacing_slider, beam_spacing, 10.0)
    )
    beam_steering.valueChanged.connect(
        lambda _value: sync_beam_spinbox_to_slider(beam_steering, beam_steering_slider, 1.0)
    )
    beam_steering_slider.valueChanged.connect(
        lambda _value: sync_beam_slider_to_spinbox(beam_steering_slider, beam_steering, 1.0)
    )

    def reset_beam() -> None:
        beam_frequency.blockSignals(True)
        beam_elements.blockSignals(True)
        beam_spacing.blockSignals(True)
        beam_steering.blockSignals(True)
        beam_frequency.setValue(_BEAM_DEFAULTS.frequency_hz / 1e3)
        beam_elements.setValue(_BEAM_DEFAULTS.elements_per_arm)
        beam_spacing.setValue(_BEAM_DEFAULTS.element_spacing_m * 1e3)
        beam_steering.setValue(_BEAM_DEFAULTS.across_track_steering_angle_deg)
        beam_frequency.blockSignals(False)
        beam_elements.blockSignals(False)
        beam_spacing.blockSignals(False)
        beam_steering.blockSignals(False)
        beam_frequency_slider.setValue(round(beam_frequency.value()))
        beam_elements_slider.setValue(beam_elements.value())
        beam_spacing_slider.setValue(round(beam_spacing.value() * 10.0))
        beam_steering_slider.setValue(round(beam_steering.value()))
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

    # Vessel lesson ---------------------------------------------------------
    vessel_page, vessel_controls, apply_vessel_language = build_vessel_lesson(FigureCanvas)
    pages.addWidget(vessel_page)

    # Motion lesson ---------------------------------------------------------
    motion_page, motion_controls, apply_motion_language = build_motion_lesson(FigureCanvas)
    pages.addWidget(motion_page)

    def apply_language(locale: str) -> None:
        """Update presentation text without touching simulation controls or state."""

        localizer = Localizer(locale)
        window.setWindowTitle(localizer.text("app.title"))
        title.setText(localizer.text("app.title"))
        tagline.setText(localizer.text("app.tagline"))
        language_label.setText(localizer.text("common.language"))

        nav_keys = ("signal", "beam", "propagation", "vessel", "motion")
        for index, key in enumerate(nav_keys):
            navigation.item(index).setText(
                f"{localizer.text(f'nav.{key}')}  • {localizer.text('status.ready')}"
            )

        signal_heading.setText(localizer.text("signal.title"))
        question_label.setText(localizer.text("common.learning_question").upper())
        question.setText(localizer.text("signal.question_focus"))
        try_it_label.setText(localizer.text("common.try_it"))
        instruction.setText(localizer.text("signal.instruction"))
        carrier_frequency_label.setText(localizer.text("signal.carrier_frequency"))
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
            f"{localizer.text('signal.scientific_boundary')}<br>"
            f"{localizer.text('signal.not_shown')}"
        )
        update_signal_comparison_display()

        beam_heading.setText(localizer.text("beam.title"))
        beam_question.setText(
            f"<b>{localizer.text('common.learning_question')}:</b> "
            f"{localizer.text('beam.question')}"
        )
        beam_context.setText(
            f"<b>{localizer.text('common.scientific_view')}:</b> "
            f"{localizer.text('beam.scientific_view')}"
        )
        beam_try_it.setText(localizer.text("common.try_it"))
        beam_instruction.setText(localizer.text("beam.instruction"))
        beam_frequency_label.setText(localizer.text("beam.frequency"))
        beam_elements_label.setText(localizer.text("beam.elements_per_arm"))
        beam_spacing_label.setText(localizer.text("beam.element_spacing"))
        beam_steering_label.setText(localizer.text("beam.steering"))
        beam_geometry.setText(localizer.text("beam.geometry"))
        beam_reset.setText(localizer.text("common.reset"))
        beam_note.setText(
            f"<b>{localizer.text('common.what_to_look_for')}:</b> "
            f"{localizer.text('beam.observation')}<br><br>"
            f"<b>{localizer.text('common.scientific_boundary')}:</b> "
            f"{localizer.text('beam.boundary')}<br><br>"
            f"<b>{localizer.text('common.not_shown_yet')}:</b> {localizer.text('beam.not_shown')}"
        )
        redraw_beam()

        propagation_heading.setText(localizer.text("propagation.title"))
        propagation_question.setText(
            f"<b>{localizer.text('common.learning_question')}:</b> "
            f"{localizer.text('propagation.question')}"
        )
        apply_vessel_language(locale)
        apply_motion_language(locale)

    def on_language_changed(_index: int) -> None:
        apply_language(str(language_selector.currentData()))

    language_selector.currentIndexChanged.connect(on_language_changed)
    navigation.currentRowChanged.connect(pages.setCurrentIndex)
    for lesson, _description in _LESSONS:
        item = QListWidgetItem(lesson + "  • ready")
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
        "frequency": carrier_frequency,
        "frequency_slider": carrier_frequency_slider,
        "duration": duration,
        "duration_slider": duration_slider,
        "bandwidth": bandwidth,
        "bandwidth_slider": bandwidth_slider,
        "readout": signal_readout,
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
        "spacing": beam_spacing,
        "spacing_slider": beam_spacing_slider,
        "steering": beam_steering,
        "steering_slider": beam_steering_slider,
        "readout": beam_readout,
        "geometry": beam_geometry,
        "reset": beam_reset,
    }
    window.hydrosim_propagation_controls = {
        "processing_bias": propagation_bias,
        "processing_bias_slider": propagation_bias_slider,
        "reset": propagation_reset,
    }
    window.hydrosim_vessel_controls = vessel_controls
    window.hydrosim_motion_controls = motion_controls
    app.hydrosim_didactic_explorer_window = window
    app.exec()
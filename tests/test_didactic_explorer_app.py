from pathlib import Path
import tomllib


def _source() -> str:
    return Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")


def test_didactic_explorer_shell_declares_all_learning_blocks():
    source = _source()

    for lesson in ("Signal", "Beam", "Propagation", "Vessel", "Motion"):
        assert f'(\"{lesson}\",' in source


def test_didactic_explorer_shell_uses_stable_signal_renderer_boundary():
    source = _source()

    assert "prepare_signal_explorer_comparison" in source
    assert "draw_signal_explorer_comparison" in source
    assert "canvas.figure =" not in source
    assert "Scientific Core" in source


def test_signal_lesson_exposes_controls_with_visible_current_consequences():
    source = _source()
    signal_source = source.split("# Signal lesson", 1)[1].split("# Beam lesson", 1)[0]

    assert "carrier_frequency = QDoubleSpinBox()" in signal_source
    assert "duration = QDoubleSpinBox()" in signal_source
    assert "bandwidth = QDoubleSpinBox()" in signal_source
    assert "center_frequency_hz=carrier_frequency.value() * 1e3" in signal_source
    assert "reference_wavelength_m = _BEAM_DEFAULTS.sound_speed_mps / state.center_frequency_hz" in signal_source
    assert "λ@" in signal_source


def test_signal_lesson_uses_guided_learning_hierarchy():
    source = _source()

    assert 'question_frame.setObjectName("learningQuestion")' in source
    assert "observation_frame" in source
    assert "quantitative_frame" in source
    assert "boundary_frame" in source
    assert "signal_reset" in source
    assert "QSlider" in source


def test_language_switch_is_presentation_only():
    source = _source()

    assert "QComboBox" in source
    assert 'language_selector.addItem("EN", "en")' in source
    assert 'language_selector.addItem("PT-BR", "pt-BR")' in source
    assert "def apply_language(locale: str)" in source
    language_function = source.split("def apply_language(locale: str)", 1)[1].split(
        "def on_language_changed", 1
    )[0]
    assert "setValue(" not in language_function
    assert "prepare_signal_explorer_comparison" not in language_function


def test_signal_quantitative_panel_derives_readouts_from_current_controls():
    source = _source()

    assert "time_bandwidth = state.duration_seconds * state.lfm_bandwidth_hz" in source
    assert "reciprocal_bandwidth_us" in source
    assert "reference_wavelength_m" in source
    assert 'f"TB={time_bandwidth:.1f}' in source


def test_signal_frequency_control_is_bilingual_and_resettable():
    source = _source()

    assert 'carrier_frequency_label.setText(localizer.text("signal.carrier_frequency"))' in source
    assert '"frequency": carrier_frequency' in source
    assert '"frequency_slider": carrier_frequency_slider' in source
    assert "carrier_frequency.setValue(_SIGNAL_DEFAULTS.center_frequency_hz / 1e3)" in source


def test_all_five_learning_blocks_are_integrated_as_ready():
    source = _source()

    assert "build_motion_lesson" in source
    assert "pages.addWidget(motion_page)" in source
    assert 'item = QListWidgetItem(lesson + "  • ready")' in source
    assert "status.ready" in source
    assert "status.planned" not in source
    assert "Planned learning block" not in source


def test_didactic_explorer_has_console_entry_point():
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert config["project"]["scripts"]["hydrosim-didactic"] == (
        "hydrosim.app.didactic_explorer:launch_didactic_explorer"
    )


def test_didactic_explorer_supports_python_module_launch():
    source = Path("src/hydrosim/app/__main__.py").read_text(encoding="utf-8")

    assert "launch_didactic_explorer()" in source

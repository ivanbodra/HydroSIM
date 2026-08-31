"""Focused structural checks for the Didactic Explorer Beam learning slice."""

import inspect

from hydrosim.app import didactic_explorer


def _source() -> str:
    return inspect.getsource(didactic_explorer.launch_didactic_explorer)


def test_beam_visible_copy_is_routed_through_localization() -> None:
    source = _source()

    assert 'beam_heading.setText(localizer.text("beam.title"))' in source
    assert "beam_question.setText(" in source
    assert "localizer.text('beam.question')" in source
    assert 'beam_instruction.setText(localizer.text("beam.instruction"))' in source
    assert 'beam_frequency_label.setText(localizer.text("beam.frequency"))' in source
    assert 'beam_elements_label.setText(localizer.text("beam.elements_per_arm"))' in source
    assert 'beam_observation.setText(localizer.text("beam.observation"))' in source
    assert "localizer.text('beam.scientific_boundary')" in source
    assert "localizer.text('beam.not_shown')" in source


def test_beam_quantitative_readout_uses_localized_labels() -> None:
    source = _source()
    redraw_beam = source.split("    def redraw_beam() -> None:", 1)[1].split(
        "    beam_frequency.valueChanged.connect", 1
    )[0]

    for key in ("beam.wavelength", "beam.spacing_ratio", "beam.beamwidth", "beam.footprint"):
        assert f"localizer.text('{key}')" in redraw_beam

    assert 'f"-3 dB beamwidth =' not in redraw_beam
    assert 'f"Footprint =' not in redraw_beam


def test_language_switch_does_not_reset_beam_controls() -> None:
    source = _source()
    apply_language = source.split("    def apply_language(locale: str) -> None:", 1)[1].split(
        "    def on_language_changed", 1
    )[0]

    assert "beam_frequency.setValue" not in apply_language
    assert "beam_elements.setValue" not in apply_language
    assert "redraw_beam()" in apply_language

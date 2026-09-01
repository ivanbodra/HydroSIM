from pathlib import Path

from hydrosim.app.localization import Localizer
from hydrosim.visualization import BeamExplorerControls, prepare_beam_explorer_snapshot


def _app_source() -> str:
    return Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")


def test_beam_lesson_exposes_required_spacing_and_steering_controls():
    source = _app_source()
    beam_source = source.split("# Beam lesson", 1)[1].split("# Propagation lesson", 1)[0]

    assert "beam_spacing = QDoubleSpinBox()" in beam_source
    assert "element_spacing_m=beam_spacing.value() * 1e-3" in beam_source
    assert "beam_steering = QDoubleSpinBox()" in beam_source
    assert "across_track_steering_angle_deg=beam_steering.value()" in beam_source
    assert '"spacing": beam_spacing' in source
    assert '"steering": beam_steering' in source


def test_beam_lesson_makes_mills_cross_tx_rx_geometry_explicit():
    source = _app_source()

    assert 'beam_geometry.setText(localizer.text("beam.geometry"))' in source
    for locale in ("en", "pt-BR"):
        geometry = Localizer(locale).text("beam.geometry")
        assert "TX" in geometry
        assert "RX" in geometry
        assert "TX × RX" in geometry


def test_beam_lesson_new_user_facing_text_is_bilingual():
    keys = (
        "beam.element_spacing",
        "beam.steering",
        "beam.geometry",
        "beam.observation",
        "beam.boundary",
        "beam.steering_direction",
        "beam.seabed_offset",
    )

    for key in keys:
        english = Localizer("en").text(key)
        portuguese = Localizer("pt-BR").text(key)
        assert english
        assert portuguese
        assert english != portuguese


def test_beam_steering_control_has_immediate_canonical_snapshot_consequence():
    nadir = prepare_beam_explorer_snapshot(
        BeamExplorerControls(across_track_steering_angle_deg=0.0)
    )
    port = prepare_beam_explorer_snapshot(
        BeamExplorerControls(across_track_steering_angle_deg=20.0)
    )
    starboard = prepare_beam_explorer_snapshot(
        BeamExplorerControls(across_track_steering_angle_deg=-20.0)
    )

    assert nadir.steered_across_track_center_offset_m == 0.0
    assert port.steered_across_track_center_offset_m > 0.0
    assert starboard.steered_across_track_center_offset_m < 0.0
    assert port.response_scan.peak_across_track_angle_rad > 0.0
    assert starboard.response_scan.peak_across_track_angle_rad < 0.0


def test_beam_reset_restores_spacing_and_steering_defaults():
    source = _app_source()
    beam_source = source.split("def reset_beam()", 1)[1].split("beam_reset.clicked", 1)[0]

    assert "beam_spacing.setValue(_BEAM_DEFAULTS.element_spacing_m * 1e3)" in beam_source
    assert "beam_steering.setValue(_BEAM_DEFAULTS.across_track_steering_angle_deg)" in beam_source

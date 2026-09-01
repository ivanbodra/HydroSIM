from pathlib import Path

from hydrosim.app.localization import Localizer


def _source() -> str:
    return Path("src/hydrosim/app/vessel_lesson.py").read_text(encoding="utf-8")


def test_vessel_exposes_full_transducer_installation_and_static_draft() -> None:
    source = _source()

    for control in ("transducer_x", "transducer_y", "transducer_z", "static_draft"):
        assert f'"{control}"' in source
    assert "x=transducer_x.value()" in source
    assert "y=transducer_y.value()" in source
    assert "z=transducer_z.value()" in source
    assert "static_draft_m=static_draft.value()" in source


def test_vessel_readout_exposes_required_observable_consequences() -> None:
    source = _source()

    assert "Transducer XYZ" in source
    assert "snapshot.transducer_depth_below_waterline_m" in source
    assert "snapshot.static_draft_m" in source
    assert "snapshot.keel_z_from_vrp_m" in source
    assert "snapshot.water_level_m_relative_to_datum" in source


def test_vessel_required_new_labels_are_bilingual() -> None:
    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        for key in (
            "vessel.transducer_x",
            "vessel.transducer_y",
            "vessel.transducer_z",
            "vessel.static_draft",
        ):
            assert localizer.text(key)


def test_vessel_scope_keeps_dynamic_effects_out() -> None:
    source = _source().lower()
    controls = source.split("controls = {", 1)[1].split("return page", 1)[0]

    for excluded in ("roll", "pitch", "yaw", "heave", "squat"):
        assert f'"{excluded}"' not in controls

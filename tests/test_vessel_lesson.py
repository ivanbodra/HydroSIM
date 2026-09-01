from pathlib import Path


def _source() -> str:
    return Path("src/hydrosim/app/vessel_lesson.py").read_text(encoding="utf-8")


def test_vessel_lesson_exposes_full_transducer_lever_arm_and_static_draft() -> None:
    source = _source()
    for control in ("transducer_x", "transducer_y", "transducer_z", "static_draft"):
        assert f'"{control}"' in source
    assert "Vector3(x=tx.value(),y=ty.value(),z=tz.value())" in source
    assert "static_draft_m=sd.value()" in source
    assert "keel_z_from_vrp_m" in source


def test_vessel_lesson_keeps_hydrographic_water_level_separate() -> None:
    source = _source()
    assert "water_level_m_relative_to_datum=hw.value()" in source
    assert "datum-to-VRP relationship" not in source


def test_vessel_lesson_is_bilingual_for_new_required_controls() -> None:
    localization = Path("src/hydrosim/app/localization.py").read_text(encoding="utf-8")
    assert localization.count('"vessel.static_draft"') == 2
    assert localization.count('"vessel.transducer_x"') == 2
    assert localization.count('"vessel.transducer_y"') == 2

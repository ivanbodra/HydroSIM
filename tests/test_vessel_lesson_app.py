from pathlib import Path


def test_vessel_lesson_is_integrated_as_ready_slice():
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    assert "build_vessel_lesson" in source
    assert "pages.addWidget(vessel_page)" in source
    assert 'index in {0, 1, 2, 3}' in source
    assert "window.hydrosim_vessel_controls = vessel_controls" in source


def test_vessel_lesson_uses_shared_adapter_and_keeps_datum_separate():
    source = Path("src/hydrosim/app/vessel_lesson.py").read_text(encoding="utf-8")
    renderer = Path("src/hydrosim/visualization/vessel_vertical_reference_plot.py").read_text(
        encoding="utf-8"
    )

    assert "prepare_vessel_vertical_reference_snapshot" in source
    assert "VesselVerticalReferenceConfiguration" in source
    assert "No datum ↔ VRP relation inferred" in renderer
    assert "positive down" in renderer
    assert "Motion" not in source


def test_vessel_lesson_exposes_only_static_reference_controls():
    source = Path("src/hydrosim/app/vessel_lesson.py").read_text(encoding="utf-8")

    controls_block = source.split("return page,{", 1)[1].split("},apply_language", 1)[0]
    for control in (
        "transducer_x",
        "transducer_y",
        "transducer_z",
        "waterline_z",
        "static_draft",
        "water_level",
    ):
        assert f'"{control}"' in controls_block
    for excluded in ("roll", "pitch", "yaw", "heave", "squat"):
        assert f'"{excluded}"' not in controls_block.lower()

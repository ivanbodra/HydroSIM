from pathlib import Path


def test_d3_page_consumes_application_adapter_without_scientific_reimplementation():
    source = Path("src/hydrosim/app/sonar_equation_lesson_page.py").read_text(encoding="utf-8")

    assert "prepare_sonar_equation_lesson_snapshot" in source
    assert "SonarEquationLessonControls" in source
    assert "evaluate_d3_sonar_equation" not in source
    assert "ainslie_mccolm" not in source
    assert "one_way_transmission_loss" not in source


def test_d3_page_exposes_required_causal_controls_outputs_and_reset():
    source = Path("src/hydrosim/app/sonar_equation_lesson_page.py").read_text(encoding="utf-8")

    for key in (
        '"source_level"',
        '"range"',
        '"frequency"',
        '"scattering_strength"',
        '"area"',
        '"noise"',
        '"received_level"',
        '"snr"',
        '"contribution_table"',
        '"reset"',
    ):
        assert key in source
    assert "default_sonar_equation_lesson_snapshot" in source
    assert "snapshot.transmission_loss_db" in source


def test_d3_page_is_bilingual_and_preserves_snr_semantics():
    source = Path("src/hydrosim/app/sonar_equation_lesson_page.py").read_text(encoding="utf-8")

    assert '"Sonar Equation — acoustic losses and received level"' in source
    assert '"Equação Sonar — perdas acústicas e nível recebido"' in source
    assert "not a probability of detection" in source
    assert "não uma probabilidade de detecção" in source


def test_capture_workflow_can_select_real_sonar_equation_page():
    source = Path("tools/capture_didactic_explorer.py").read_text(encoding="utf-8")

    assert '"Sonar Equation": 2' in source
    assert 'lesson == "Sonar Equation"' in source
    assert 'controls["range"].setValue(120.0)' in source
    assert 'controls["frequency"].setValue(400.0)' in source

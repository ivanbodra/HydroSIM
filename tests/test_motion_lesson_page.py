from pathlib import Path

from hydrosim.app.localization import Localizer
from hydrosim.app.motion_lesson import MotionLessonControls, prepare_motion_lesson_snapshot
from hydrosim.visualization.motion_lesson_plot import plot_motion_lesson_snapshot


def test_motion_page_consumes_existing_adapter_only() -> None:
    source = Path("src/hydrosim/app/motion_lesson_page.py").read_text(encoding="utf-8")

    assert "MotionLessonControls" in source
    assert "prepare_motion_lesson_snapshot" in source
    assert "VesselMotionModel" not in source
    assert "HarmonicSignal" not in source


def test_motion_page_exposes_only_first_slice_controls() -> None:
    source = Path("src/hydrosim/app/motion_lesson_page.py").read_text(encoding="utf-8")

    controls = source.split("controls = {", 1)[1].split("return page", 1)[0]
    for control in ("roll", "pitch", "yaw", "heave"):
        assert f'"{control}"' in controls
    for excluded in ("latency", "compensation", "sea_state", "squat"):
        assert f'"{excluded}"' not in controls


def test_motion_copy_is_bilingual() -> None:
    keys = (
        "motion.title",
        "motion.question",
        "motion.instruction",
        "motion.roll",
        "motion.pitch",
        "motion.yaw",
        "motion.heave",
        "motion.observation",
        "motion.boundary",
        "motion.not_shown",
    )
    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        for key in keys:
            assert localizer.text(key)


def test_motion_renderer_accepts_shared_snapshot() -> None:
    snapshot = prepare_motion_lesson_snapshot(
        MotionLessonControls(roll_rad=0.05, pitch_rad=-0.03, yaw_deviation_rad=0.08, heave_m=0.4)
    )
    figure, ax = plot_motion_lesson_snapshot(snapshot)

    assert figure is not None
    assert ax.name == "3d"
    assert ax.get_title()


def test_real_shell_exposes_motion_controls_and_language_wiring() -> None:
    source = Path("src/hydrosim/app/didactic_explorer.py").read_text(encoding="utf-8")

    assert "motion_page, motion_controls, apply_motion_language = build_motion_lesson" in source
    assert "pages.addWidget(motion_page)" in source
    assert "apply_motion_language(locale)" in source
    assert "window.hydrosim_motion_controls = motion_controls" in source

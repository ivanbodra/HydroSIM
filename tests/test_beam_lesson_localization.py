"""Focused localization checks for the Didactic Explorer Beam lesson."""

from hydrosim.app.localization import Localizer


BEAM_KEYS = (
    "beam.title",
    "beam.question",
    "beam.instruction",
    "beam.frequency",
    "beam.elements_per_arm",
    "beam.observation",
    "beam.scientific_boundary",
    "beam.not_shown",
    "beam.wavelength",
    "beam.spacing_ratio",
    "beam.beamwidth",
    "beam.footprint",
)


def test_beam_lesson_copy_is_available_in_both_supported_locales() -> None:
    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        for key in BEAM_KEYS:
            assert localizer.text(key).strip()


def test_beam_learning_question_is_localized() -> None:
    english = Localizer("en").text("beam.question")
    portuguese = Localizer("pt-BR").text("beam.question")

    assert english != portuguese
    assert "frequency" in english.lower()
    assert "frequência" in portuguese.lower()


def test_beam_boundary_names_existing_model_limits() -> None:
    english = Localizer("en").text("beam.scientific_boundary").lower()
    portuguese = Localizer("pt-BR").text("beam.scientific_boundary").lower()

    assert "far-field" in english
    assert "narrowband" in english
    assert "campo distante" in portuguese
    assert "banda estreita" in portuguese

from hydrosim.app.localization import Localizer


def test_propagation_lesson_copy_is_available_in_both_supported_locales() -> None:
    keys = (
        "propagation.title",
        "propagation.question",
        "propagation.instruction",
        "propagation.processing_bias",
        "propagation.truth_lower_layer",
        "propagation.processing_lower_layer",
        "propagation.max_error",
        "propagation.observation",
        "propagation.boundary",
        "propagation.not_shown",
    )

    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        for key in keys:
            assert localizer.text(key)


def test_propagation_copy_keeps_truth_and_processing_separate() -> None:
    en = Localizer("en")
    pt = Localizer("pt-BR")

    assert "Truth" in en.text("propagation.observation")
    assert "processing" in en.text("propagation.observation")
    assert "Verdade" in pt.text("propagation.observation")
    assert "processamento" in pt.text("propagation.observation")

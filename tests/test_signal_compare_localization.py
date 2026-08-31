from hydrosim.app.localization import Localizer


def test_signal_compare_copy_exists_in_both_supported_locales():
    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)

        assert localizer.text("common.baseline")
        assert localizer.text("common.current")
        assert localizer.text("common.set_baseline")
        assert localizer.text("common.clear_baseline")
        assert localizer.text("signal.compare_hint")
        assert localizer.text("signal.baseline_empty")
        assert localizer.text("signal.baseline_note")


def test_signal_compare_copy_explicitly_preserves_scientific_state_boundary():
    english = Localizer("en").text("signal.baseline_note")
    portuguese = Localizer("pt-BR").text("signal.baseline_note")

    assert "pedagogical" in english
    assert "scientific" in english
    assert "pedagógica" in portuguese
    assert "científicos" in portuguese

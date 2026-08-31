from hydrosim.app.localization import Localizer


def test_signal_learning_copy_stays_concise() -> None:
    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        assert len(localizer.text("signal.instruction")) <= 60
        assert len(localizer.text("signal.observation")) <= 90
        assert len(localizer.text("signal.not_shown")) <= 110

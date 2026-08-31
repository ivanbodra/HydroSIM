from __future__ import annotations

import pytest

from hydrosim.app.localization import DEFAULT_LOCALE, Localizer, SUPPORTED_LOCALES


def test_supported_locales_are_bilingual() -> None:
    assert DEFAULT_LOCALE == "en"
    assert SUPPORTED_LOCALES == ("en", "pt-BR")


def test_portuguese_localization_resolves_user_facing_text() -> None:
    localizer = Localizer("pt-BR")

    assert localizer.text("nav.signal") == "Sinal"
    assert localizer.text("common.what_to_look_for") == "O que observar"


def test_missing_localized_key_falls_back_to_english(monkeypatch: pytest.MonkeyPatch) -> None:
    from hydrosim.app import localization

    monkeypatch.delitem(localization._TRANSLATIONS["pt-BR"], "signal.title")

    assert Localizer("pt-BR").text("signal.title") == localization._TRANSLATIONS["en"]["signal.title"]


def test_unknown_key_is_explicit_failure() -> None:
    with pytest.raises(KeyError):
        Localizer("en").text("does.not.exist")


def test_unsupported_locale_is_rejected() -> None:
    with pytest.raises(ValueError):
        Localizer("es")

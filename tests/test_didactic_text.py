"""Tests for localized Didactic Explorer presentation copy."""

from hydrosim.app.didactic_text import SIGNAL_TEXT_KEYS, text


def test_signal_text_keys_resolve_in_supported_languages() -> None:
    for language in ("en", "pt-BR"):
        for key in SIGNAL_TEXT_KEYS.values():
            assert text(key, language)


def test_signal_learning_question_is_localized() -> None:
    english = text(SIGNAL_TEXT_KEYS["question"], "en")
    portuguese = text(SIGNAL_TEXT_KEYS["question"], "pt-BR")

    assert english != portuguese
    assert "bandwidth" in english.lower()
    assert "largura" in portuguese.lower()

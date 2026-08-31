"""Presentation-layer localization helpers for HydroSIM applications.

Scientific identifiers, models, schema keys, and computational state remain canonical
English. This module translates only user-facing presentation strings.
"""

from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_LOCALES = ("en", "pt-BR")
DEFAULT_LOCALE = "en"

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "HydroSIM — Didactic Explorer",
        "app.tagline": "Change one control. See the consequence.",
        "nav.signal": "Signal",
        "nav.beam": "Beam",
        "nav.propagation": "Propagation",
        "nav.vessel": "Vessel",
        "nav.motion": "Motion",
        "status.ready": "ready",
        "status.planned": "planned",
        "common.learning_question": "Learning question",
        "common.what_to_look_for": "What to look for",
        "common.scientific_view": "Scientific view",
        "common.scientific_boundary": "Scientific boundary",
        "common.quantitative": "Quantitative",
        "common.reset": "Reset",
        "common.try_it": "Controls",
        "common.not_shown_yet": "Not shown yet",
        "common.language": "Language",
        "common.english": "English",
        "common.portuguese": "Português",
        "common.baseline": "Baseline",
        "common.current": "Current",
        "common.set_baseline": "Set baseline",
        "common.clear_baseline": "Clear baseline",
        "signal.title": "Signal — waveform and pulse compression",
        "signal.question": (
            "How do pulse duration and LFM bandwidth change the transmitted baseband "
            "signal and its pulse-compression response?"
        ),
        "signal.question_focus": "How does LFM bandwidth affect pulse compression?",
        "signal.scientific_boundary": "Analytical deterministic baseband model",
        "signal.instruction": "Change one control and watch the response.",
        "signal.pulse_duration": "Pulse duration",
        "signal.lfm_bandwidth": "LFM bandwidth",
        "signal.observation": "More LFM bandwidth narrows the matched-filter peak.",
        "signal.not_shown": "Absorption, electronics, noise, and full-field wave propagation are outside this lesson.",
        "signal.compare_hint": (
            "Freeze the current controls as a teaching baseline, then change one parameter "
            "to compare the current state against it."
        ),
        "signal.baseline_empty": "No teaching baseline is currently frozen.",
        "signal.baseline_note": (
            "Baseline and Current are pedagogical comparison states, not HydroSIM scientific states."
        ),
        "beam.title": "Beam — frequency, wavelength, aperture, and footprint",
        "beam.question": (
            "How do frequency and aperture change beamwidth and the resulting -3 dB "
            "footprint on a flat seabed?"
        ),
        "propagation.title": "Propagation — SVP mismatch and reconstructed swath",
        "propagation.question": (
            "What happens when the water column is physically unchanged, but the "
            "lower-layer sound speed used during processing is wrong?"
        ),
    },
    "pt-BR": {
        "app.title": "HydroSIM — Explorador Didático",
        "app.tagline": "Altere um controle. Veja a consequência.",
        "nav.signal": "Sinal",
        "nav.beam": "Feixe",
        "nav.propagation": "Propagação",
        "nav.vessel": "Embarcação",
        "nav.motion": "Movimento",
        "status.ready": "disponível",
        "status.planned": "planejado",
        "common.learning_question": "Pergunta de aprendizagem",
        "common.what_to_look_for": "O que observar",
        "common.scientific_view": "Representação científica",
        "common.scientific_boundary": "Limite científico",
        "common.quantitative": "Quantitativo",
        "common.reset": "Restaurar",
        "common.try_it": "Controles",
        "common.not_shown_yet": "Ainda não representado",
        "common.language": "Idioma",
        "common.english": "English",
        "common.portuguese": "Português",
        "common.baseline": "Referência",
        "common.current": "Atual",
        "common.set_baseline": "Fixar referência",
        "common.clear_baseline": "Limpar referência",
        "signal.title": "Sinal — forma de onda e compressão de pulso",
        "signal.question": (
            "Como a duração do pulso e a largura de banda LFM alteram o sinal transmitido "
            "em banda base e sua resposta de compressão de pulso?"
        ),
        "signal.question_focus": "Como a largura de banda LFM afeta a compressão de pulso?",
        "signal.scientific_boundary": "Modelo analítico determinístico em banda base",
        "signal.instruction": "Altere um controle e observe a resposta.",
        "signal.pulse_duration": "Duração do pulso",
        "signal.lfm_bandwidth": "Largura de banda LFM",
        "signal.observation": "Mais largura de banda LFM estreita o pico do filtro casado.",
        "signal.not_shown": "Absorção, eletrônica, ruído e propagação completa de campo estão fora desta aula.",
        "signal.compare_hint": (
            "Fixe os controles atuais como referência didática e depois altere um parâmetro "
            "para comparar o estado atual com essa referência."
        ),
        "signal.baseline_empty": "Nenhuma referência didática está fixada no momento.",
        "signal.baseline_note": (
            "Referência e Atual são estados de comparação pedagógica, não estados científicos do HydroSIM."
        ),
        "beam.title": "Feixe — frequência, comprimento de onda, abertura e footprint",
        "beam.question": (
            "Como a frequência e a abertura alteram a largura do feixe e o footprint de "
            "-3 dB resultante sobre um fundo plano?"
        ),
        "propagation.title": "Propagação — erro de SVP e faixa reconstruída",
        "propagation.question": (
            "O que acontece quando a coluna d'água permanece fisicamente inalterada, mas "
            "a velocidade do som da camada inferior usada no processamento está errada?"
        ),
    },
}


@dataclass(frozen=True)
class Localizer:
    """Resolve user-facing text while preserving canonical internal identifiers."""

    locale: str = DEFAULT_LOCALE

    def __post_init__(self) -> None:
        if self.locale not in SUPPORTED_LOCALES:
            raise ValueError(
                f"Unsupported locale {self.locale!r}; expected one of {SUPPORTED_LOCALES!r}"
            )

    def text(self, key: str) -> str:
        """Return localized text, falling back to canonical English when necessary."""

        localized = _TRANSLATIONS[self.locale]
        if key in localized:
            return localized[key]
        try:
            return _TRANSLATIONS[DEFAULT_LOCALE][key]
        except KeyError as exc:
            raise KeyError(f"Unknown HydroSIM UI translation key: {key}") from exc

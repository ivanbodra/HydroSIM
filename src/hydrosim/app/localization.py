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
        "app.tagline": "Change one physical control. See what changes. Understand why.",
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
        "common.reset": "Reset lesson",
        "common.try_it": "Try it",
        "common.not_shown_yet": "Not shown yet",
        "common.language": "Language",
        "common.english": "English",
        "common.portuguese": "Português",
        "common.baseline": "Baseline",
        "common.current": "Current",
        "common.set_baseline": "Set baseline",
        "common.clear_baseline": "Clear baseline",
        "signal.title": "Signal — CW versus LFM chirp",
        "signal.question": "How do pulse duration and LFM bandwidth change the transmitted baseband signal and its pulse-compression response?",
        "signal.question_focus": "How does LFM bandwidth affect pulse compression?",
        "signal.scientific_boundary": "Analytical / deterministic baseband model",
        "signal.instruction": "Change one control at a time and watch how the compressed response changes.",
        "signal.pulse_duration": "Pulse duration",
        "signal.lfm_bandwidth": "LFM bandwidth",
        "signal.observation": "Increasing LFM bandwidth changes the chirp phase evolution and narrows the normalized matched-filter peak.",
        "signal.not_shown": "Frequency-dependent absorption, electronics, noise, and a general wave-equation field solution are not represented in this lesson.",
        "signal.compare_hint": "Freeze the current controls as a teaching baseline, then change one parameter to compare the current state against it.",
        "signal.baseline_empty": "No teaching baseline is currently frozen.",
        "signal.baseline_note": "Baseline and Current are pedagogical comparison states, not HydroSIM scientific states.",
        "beam.title": "Beam — frequency, wavelength, aperture, and footprint",
        "beam.question": "How do frequency and aperture change beamwidth and the resulting -3 dB footprint on a flat seabed?",
        "beam.instruction": "Change one control at a time. Start with frequency, then element count, and watch the main lobe and footprint respond.",
        "beam.frequency": "Frequency",
        "beam.elements_per_arm": "Elements per arm",
        "beam.observation": "Higher frequency shortens wavelength. Increasing element count enlarges the physical aperture. Both can narrow the main lobe and reduce the approximate nadir footprint.",
        "beam.scientific_boundary": "Normalized narrowband far-field TX/RX array response with the existing flat-bottom -3 dB footprint approximation at fixed depth.",
        "beam.not_shown": "Steering, refraction, multisector transmission, bottom scattering, and vendor-specific transducer geometry are not represented in this lesson.",
        "beam.wavelength": "Wavelength",
        "beam.spacing_ratio": "Element spacing / wavelength",
        "beam.beamwidth": "-3 dB beamwidth",
        "beam.footprint": "Footprint",
        "propagation.title": "Propagation — SVP mismatch and reconstructed swath",
        "propagation.question": "What happens when the water column is physically unchanged, but the lower-layer sound speed used during processing is wrong?",
    },
    "pt-BR": {
        "app.title": "HydroSIM — Explorador Didático",
        "app.tagline": "Altere um controle físico. Veja o que muda. Entenda por quê.",
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
        "common.reset": "Restaurar aula",
        "common.try_it": "Experimente",
        "common.not_shown_yet": "Ainda não representado",
        "common.language": "Idioma",
        "common.english": "English",
        "common.portuguese": "Português",
        "common.baseline": "Referência",
        "common.current": "Atual",
        "common.set_baseline": "Fixar referência",
        "common.clear_baseline": "Limpar referência",
        "signal.title": "Sinal — CW versus chirp LFM",
        "signal.question": "Como a duração do pulso e a largura de banda LFM alteram o sinal transmitido em banda base e sua resposta de compressão de pulso?",
        "signal.question_focus": "Como a largura de banda LFM afeta a compressão de pulso?",
        "signal.scientific_boundary": "Modelo analítico / determinístico em banda base",
        "signal.instruction": "Altere um controle por vez e observe como a resposta comprimida se modifica.",
        "signal.pulse_duration": "Duração do pulso",
        "signal.lfm_bandwidth": "Largura de banda LFM",
        "signal.observation": "Aumentar a largura de banda LFM modifica a evolução de fase do chirp e estreita o pico normalizado do filtro casado.",
        "signal.not_shown": "Absorção dependente da frequência, eletrônica, ruído e uma solução geral de campo pela equação de onda não são representados nesta aula.",
        "signal.compare_hint": "Fixe os controles atuais como referência didática e depois altere um parâmetro para comparar o estado atual com essa referência.",
        "signal.baseline_empty": "Nenhuma referência didática está fixada no momento.",
        "signal.baseline_note": "Referência e Atual são estados de comparação pedagógica, não estados científicos do HydroSIM.",
        "beam.title": "Feixe — frequência, comprimento de onda, abertura e footprint",
        "beam.question": "Como a frequência e a abertura alteram a largura do feixe e o footprint de -3 dB resultante sobre um fundo plano?",
        "beam.instruction": "Altere um controle por vez. Comece pela frequência, depois pelo número de elementos, e observe a resposta do lóbulo principal e do footprint.",
        "beam.frequency": "Frequência",
        "beam.elements_per_arm": "Elementos por braço",
        "beam.observation": "Uma frequência maior reduz o comprimento de onda. Aumentar o número de elementos amplia a abertura física. Ambos podem estreitar o lóbulo principal e reduzir o footprint aproximado no nadir.",
        "beam.scientific_boundary": "Resposta normalizada de arranjo TX/RX em campo distante e banda estreita, com a aproximação existente do footprint de -3 dB sobre fundo plano em profundidade fixa.",
        "beam.not_shown": "Steering, refração, transmissão multissetorial, espalhamento pelo fundo e geometria específica de fabricantes não são representados nesta aula.",
        "beam.wavelength": "Comprimento de onda",
        "beam.spacing_ratio": "Espaçamento entre elementos / comprimento de onda",
        "beam.beamwidth": "Largura de feixe a -3 dB",
        "beam.footprint": "Footprint",
        "propagation.title": "Propagação — erro de SVP e faixa reconstruída",
        "propagation.question": "O que acontece quando a coluna d'água permanece fisicamente inalterada, mas a velocidade do som da camada inferior usada no processamento está errada?",
    },
}


@dataclass(frozen=True)
class Localizer:
    """Resolve user-facing text while preserving canonical internal identifiers."""

    locale: str = DEFAULT_LOCALE

    def __post_init__(self) -> None:
        if self.locale not in SUPPORTED_LOCALES:
            raise ValueError(f"Unsupported locale {self.locale!r}; expected one of {SUPPORTED_LOCALES!r}")

    def text(self, key: str) -> str:
        """Return localized text, falling back to canonical English when necessary."""

        localized = _TRANSLATIONS[self.locale]
        if key in localized:
            return localized[key]
        try:
            return _TRANSLATIONS[DEFAULT_LOCALE][key]
        except KeyError as exc:
            raise KeyError(f"Unknown HydroSIM UI translation key: {key}") from exc

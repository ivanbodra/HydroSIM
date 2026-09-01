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
        "signal.carrier_frequency": "Carrier frequency",
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
        "vessel.title": "Vessel — sensors and vertical references",
        "vessel.question": "How do sensor lever arms, static draft, waterline, and water level relate without mixing reference systems?",
        "vessel.instruction": "Change the transducer X/Y/Z installation, static draft, configured waterline, or hydrographic water level and observe the corresponding consequence.",
        "vessel.transducer_x": "Transducer X lever arm",
        "vessel.transducer_y": "Transducer Y lever arm",
        "vessel.transducer_z": "Transducer Z lever arm",
        "vessel.static_draft": "Static draft",
        "vessel.vrp": "Vessel reference point (VRP)",
        "vessel.gnss": "GNSS antenna",
        "vessel.imu": "IMU",
        "vessel.transducer": "Transducer",
        "vessel.waterline": "Configured waterline",
        "vessel.water_level": "Hydrographic water level",
        "vessel.transducer_depth": "Transducer below waterline",
        "vessel.observation": "Sensor positions and static draft are tied to vessel geometry; hydrographic water level remains a separate datum-referenced quantity.",
        "vessel.boundary": "Static geometry only. Positive-down body Z; no datum-to-VRP relationship is inferred.",
        "vessel.not_shown": "Motion, dynamic draft, squat, and time-varying vertical effects are outside this lesson.",
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
        "signal.carrier_frequency": "Frequência da portadora",
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
        "vessel.title": "Embarcação — sensores e referências verticais",
        "vessel.question": "Como os lever arms dos sensores, o calado estático, a linha d'água e o nível d'água se relacionam sem misturar sistemas de referência?",
        "vessel.instruction": "Altere a instalação X/Y/Z do transdutor, o calado estático, a linha d'água configurada ou o nível d'água hidrográfico e observe a consequência correspondente.",
        "vessel.transducer_x": "Lever arm X do transdutor",
        "vessel.transducer_y": "Lever arm Y do transdutor",
        "vessel.transducer_z": "Lever arm Z do transdutor",
        "vessel.static_draft": "Calado estático",
        "vessel.vrp": "Ponto de referência da embarcação (VRP)",
        "vessel.gnss": "Antena GNSS",
        "vessel.imu": "IMU",
        "vessel.transducer": "Transdutor",
        "vessel.waterline": "Linha d'água configurada",
        "vessel.water_level": "Nível d'água hidrográfico",
        "vessel.transducer_depth": "Transdutor abaixo da linha d'água",
        "vessel.observation": "As posições dos sensores e o calado estático pertencem à geometria da embarcação; o nível d'água hidrográfico permanece uma grandeza separada, referida ao datum.",
        "vessel.boundary": "Apenas geometria estática. Z do corpo positivo para baixo; nenhuma relação datum–VRP é inferida.",
        "vessel.not_shown": "Movimento, calado dinâmico, squat e efeitos verticais variáveis no tempo estão fora desta aula.",
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

"""PySide6 presentation for the D3 Sonar Equation lesson.

This module contains presentation wiring only. All sonar-equation calculations are
delegated to :mod:`hydrosim.app.sonar_equation_lesson`.
"""

from __future__ import annotations

from collections.abc import Callable

from hydrosim.app.sonar_equation_lesson import (
    SonarEquationLessonControls,
    default_sonar_equation_lesson_snapshot,
    prepare_sonar_equation_lesson_snapshot,
)


_TEXT = {
    "en": {
        "title": "Sonar Equation — acoustic losses and received level",
        "question": "How do source level, range, frequency, backscatter, and noise combine to set received level and SNR?",
        "controls": "Controls",
        "instruction": "Change one causal term and observe the signed contribution chain.",
        "sl": "Source level (SL)",
        "range": "Acoustic path",
        "frequency": "Frequency",
        "ss": "Scattering strength",
        "area": "Contributing seabed area",
        "noise": "Noise level (NL)",
        "reset": "Reset",
        "rl": "Received level (RL)",
        "snr": "Signal-to-noise ratio (SNR)",
        "chain": "Signed contribution breakdown",
        "term": "Term",
        "value": "Contribution",
        "propagation": "Propagation detail",
        "boundary": "Deterministic level-domain lesson. SNR is a level difference, not a probability of detection.",
        "source-level": "Source level",
        "tx-relative-gain": "TX relative beam-pattern correction",
        "outbound-tl": "Outbound transmission loss",
        "backscatter": "Seabed area backscatter",
        "inbound-tl": "Inbound transmission loss",
        "rx-relative-gain": "RX relative beam-pattern correction",
        "noise": "Noise comparison",
    },
    "pt-BR": {
        "title": "Equação Sonar — perdas acústicas e nível recebido",
        "question": "Como nível de fonte, distância, frequência, retroespalhamento e ruído se combinam para definir o nível recebido e a SNR?",
        "controls": "Controles",
        "instruction": "Altere um termo causal e observe a cadeia de contribuições com sinal.",
        "sl": "Nível de fonte (SL)",
        "range": "Caminho acústico",
        "frequency": "Frequência",
        "ss": "Intensidade de espalhamento",
        "area": "Área contribuinte do fundo",
        "noise": "Nível de ruído (NL)",
        "reset": "Restaurar",
        "rl": "Nível recebido (RL)",
        "snr": "Relação sinal-ruído (SNR)",
        "chain": "Decomposição das contribuições com sinal",
        "term": "Termo",
        "value": "Contribuição",
        "propagation": "Detalhe da propagação",
        "boundary": "Aula determinística no domínio de níveis. SNR é uma diferença de níveis, não uma probabilidade de detecção.",
        "source-level": "Nível de fonte",
        "tx-relative-gain": "Correção relativa do padrão de feixe TX",
        "outbound-tl": "Perda de transmissão na ida",
        "backscatter": "Retroespalhamento de área do fundo",
        "inbound-tl": "Perda de transmissão na volta",
        "rx-relative-gain": "Correção relativa do padrão de feixe RX",
        "noise": "Comparação com o ruído",
    },
}


def build_sonar_equation_lesson() -> tuple[object, dict[str, object], Callable[[str], None]]:
    """Build the D3 page and return page, test/capture controls, and language hook."""

    from PySide6.QtWidgets import (
        QDoubleSpinBox,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    defaults = SonarEquationLessonControls()
    page = QWidget()
    root = QVBoxLayout(page)
    root.setContentsMargins(8, 2, 4, 2)
    root.setSpacing(7)

    heading = QLabel()
    heading.setStyleSheet("font-size: 19px; font-weight: 600;")
    root.addWidget(heading)

    question = QLabel()
    question.setWordWrap(True)
    question.setStyleSheet("font-size: 14px; font-weight: 550; color: #3f5962;")
    root.addWidget(question)

    body = QHBoxLayout()
    body.setSpacing(10)
    root.addLayout(body, 1)

    controls_frame = QFrame()
    controls_frame.setMinimumWidth(245)
    controls_frame.setMaximumWidth(285)
    controls_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    controls_layout = QVBoxLayout(controls_frame)
    controls_layout.setContentsMargins(10, 8, 10, 8)
    controls_title = QLabel()
    controls_title.setStyleSheet("font-size: 14px; font-weight: 650;")
    instruction = QLabel()
    instruction.setWordWrap(True)
    instruction.setStyleSheet("color: #53616d; font-size: 11px;")
    controls_layout.addWidget(controls_title)
    controls_layout.addWidget(instruction)

    form = QFormLayout()
    form.setVerticalSpacing(6)

    def spin(minimum: float, maximum: float, value: float, step: float, suffix: str, decimals: int = 1):
        widget = QDoubleSpinBox()
        widget.setRange(minimum, maximum)
        widget.setDecimals(decimals)
        widget.setSingleStep(step)
        widget.setValue(value)
        widget.setSuffix(suffix)
        return widget

    sl_label = QLabel()
    source_level = spin(150.0, 250.0, float(defaults.source_level_db_re_1upa_at_1m), 1.0, " dB", 1)
    form.addRow(sl_label, source_level)
    range_label = QLabel()
    range_m = spin(1.0, 2000.0, float(defaults.range_m), 5.0, " m", 1)
    form.addRow(range_label, range_m)
    frequency_label = QLabel()
    frequency_khz = spin(10.0, 1000.0, float(defaults.frequency_hz) / 1e3, 10.0, " kHz", 0)
    form.addRow(frequency_label, frequency_khz)
    ss_label = QLabel()
    scattering = spin(-80.0, 0.0, float(defaults.scattering_strength_db_per_m2), 1.0, " dB/m²", 1)
    form.addRow(ss_label, scattering)
    area_label = QLabel()
    area = spin(0.1, 1000.0, float(defaults.contributing_area_m2), 0.5, " m²", 1)
    form.addRow(area_label, area)
    noise_label = QLabel()
    noise = spin(0.0, 160.0, float(defaults.noise_level_db_re_1upa), 1.0, " dB", 1)
    form.addRow(noise_label, noise)
    controls_layout.addLayout(form)

    reset = QPushButton()
    controls_layout.addWidget(reset)
    controls_layout.addStretch(1)
    body.addWidget(controls_frame)

    outcome = QVBoxLayout()
    outcome.setSpacing(7)
    body.addLayout(outcome, 1)

    primary = QHBoxLayout()
    rl_frame = QFrame()
    rl_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    rl_layout = QVBoxLayout(rl_frame)
    rl_title = QLabel()
    rl_value = QLabel()
    rl_value.setStyleSheet("font-size: 30px; font-weight: 700;")
    rl_layout.addWidget(rl_title)
    rl_layout.addWidget(rl_value)
    primary.addWidget(rl_frame)

    snr_frame = QFrame()
    snr_frame.setStyleSheet("QFrame { background: #f7f9fa; border-radius: 8px; }")
    snr_layout = QVBoxLayout(snr_frame)
    snr_title = QLabel()
    snr_value = QLabel()
    snr_value.setStyleSheet("font-size: 30px; font-weight: 700;")
    snr_layout.addWidget(snr_title)
    snr_layout.addWidget(snr_value)
    primary.addWidget(snr_frame)
    outcome.addLayout(primary)

    chain_title = QLabel()
    chain_title.setStyleSheet("font-size: 13px; font-weight: 650;")
    outcome.addWidget(chain_title)
    table = QTableWidget(7, 2)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    table.setMinimumHeight(235)
    outcome.addWidget(table, 1)

    propagation_title = QLabel()
    propagation_title.setStyleSheet("font-size: 12px; font-weight: 650;")
    propagation_detail = QLabel()
    propagation_detail.setWordWrap(True)
    propagation_detail.setStyleSheet("font-size: 11px; color: #53616d;")
    boundary = QLabel()
    boundary.setWordWrap(True)
    boundary.setStyleSheet("font-size: 10px; color: #53616d;")
    outcome.addWidget(propagation_title)
    outcome.addWidget(propagation_detail)
    outcome.addWidget(boundary)

    locale = "en"
    contribution_keys = (
        "source-level",
        "tx-relative-gain",
        "outbound-tl",
        "backscatter",
        "inbound-tl",
        "rx-relative-gain",
        "noise",
    )

    def controls_state() -> SonarEquationLessonControls:
        return SonarEquationLessonControls(
            frequency_hz=frequency_khz.value() * 1e3,
            range_m=range_m.value(),
            source_level_db_re_1upa_at_1m=source_level.value(),
            noise_level_db_re_1upa=noise.value(),
            scattering_strength_db_per_m2=scattering.value(),
            contributing_area_m2=area.value(),
        )

    def redraw() -> None:
        snapshot = prepare_sonar_equation_lesson_snapshot(controls_state())
        rl_value.setText(f"{snapshot.received_level_db_re_1upa:.1f} dB")
        snr_value.setText(f"{snapshot.snr_db:.1f} dB")
        text = _TEXT[locale]
        for row, contribution in enumerate(snapshot.contributions):
            table.setItem(row, 0, QTableWidgetItem(text[contribution.key]))
            table.setItem(row, 1, QTableWidgetItem(f"{float(contribution.value_db):+.1f} dB"))
        result = snapshot.result
        propagation_detail.setText(
            f"α={float(result.absorption_db_per_km):.2f} dB/km · "
            f"out: spreading {float(result.outbound_spreading_loss_db):.1f} dB + "
            f"absorption {float(result.outbound_absorption_loss_db):.1f} dB · "
            f"in: spreading {float(result.inbound_spreading_loss_db):.1f} dB + "
            f"absorption {float(result.inbound_absorption_loss_db):.1f} dB · "
            f"2-way TL={snapshot.transmission_loss_db:.1f} dB"
        )

    def apply_language(value: str) -> None:
        nonlocal locale
        locale = value if value in _TEXT else "en"
        text = _TEXT[locale]
        heading.setText(text["title"])
        question.setText(text["question"])
        controls_title.setText(text["controls"])
        instruction.setText(text["instruction"])
        sl_label.setText(text["sl"])
        range_label.setText(text["range"])
        frequency_label.setText(text["frequency"])
        ss_label.setText(text["ss"])
        area_label.setText(text["area"])
        noise_label.setText(text["noise"])
        reset.setText(text["reset"])
        rl_title.setText(text["rl"])
        snr_title.setText(text["snr"])
        chain_title.setText(text["chain"])
        table.setHorizontalHeaderLabels((text["term"], text["value"]))
        propagation_title.setText(text["propagation"])
        boundary.setText(text["boundary"])
        redraw()

    def reset_controls() -> None:
        snapshot = default_sonar_equation_lesson_snapshot()
        widgets_and_values = (
            (source_level, float(snapshot.controls.source_level_db_re_1upa_at_1m)),
            (range_m, float(snapshot.controls.range_m)),
            (frequency_khz, float(snapshot.controls.frequency_hz) / 1e3),
            (scattering, float(snapshot.controls.scattering_strength_db_per_m2)),
            (area, float(snapshot.controls.contributing_area_m2)),
            (noise, float(snapshot.controls.noise_level_db_re_1upa)),
        )
        for widget, value in widgets_and_values:
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)
        redraw()

    for widget in (source_level, range_m, frequency_khz, scattering, area, noise):
        widget.valueChanged.connect(lambda _value: redraw())
    reset.clicked.connect(reset_controls)
    apply_language("en")

    controls = {
        "source_level": source_level,
        "range": range_m,
        "frequency": frequency_khz,
        "scattering_strength": scattering,
        "area": area,
        "noise": noise,
        "received_level": rl_value,
        "snr": snr_value,
        "contribution_table": table,
        "propagation_detail": propagation_detail,
        "reset": reset,
    }
    return page, controls, apply_language

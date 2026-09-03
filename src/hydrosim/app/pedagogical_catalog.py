"""Canonical learner-facing catalog for the pedagogical HydroSIM generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Locale = Literal["en", "pt-BR"]
ModuleId = Literal["didactic", "patch-test", "acquisition"]
Availability = Literal["available", "coming-soon"]


@dataclass(frozen=True)
class PedagogicalExperience:
    id: str
    module: ModuleId
    name_en: str
    name_pt_br: str
    availability: Availability = "coming-soon"
    page_builder: str | None = None

    def name(self, locale: Locale) -> str:
        return self.name_pt_br if locale == "pt-BR" else self.name_en


_DIDACTIC_NAMES = (
    ("PED-D1", "Acoustic Wave & Frequency", "Onda Acústica e Frequência"),
    ("PED-D2", "Pulse & Signal Processing", "Pulso e Processamento de Sinal"),
    ("PED-D3", "Sonar Equation & Propagation Loss", "Equação Sonar e Perdas de Propagação"),
    ("PED-D4", "Sound Speed & Refraction", "Velocidade do Som e Refração"),
    ("PED-D5", "Acoustic Detection Fundamentals", "Fundamentos de Detecção Acústica"),
    ("PED-D6", "Transducer & Array Construction", "Transdutor e Construção de Arrays"),
    ("PED-D7", "Beamforming & Electronic Steering", "Beamforming e Direcionamento Eletrônico"),
    ("PED-D8", "Echosounders — SBES vs MBES", "Ecobatímetros — SBES vs MBES"),
    ("PED-D9", "Bottom Detection", "Detecção do Fundo"),
    ("PED-D10", "Multisector MBES", "MBES Multissetorial"),
    ("PED-D11", "Vessel & Sensor Configuration", "Embarcação e Configuração de Sensores"),
    ("PED-D12", "Vessel Motion", "Movimentos da Embarcação"),
    ("PED-D13", "PU & Sensor Integration", "PU e Integração de Sensores"),
    ("PED-D14", "Timing, Synchronization & Latency", "Timing, Sincronização e Latência"),
    ("PED-D15", "Sounding Formation", "Formação da Sondagem"),
    ("PED-D16", "Survey Planning", "Planejamento do Levantamento"),
    ("PED-D17", "Survey Coverage & Acquisition Trade-offs", "Cobertura e Compromissos de Aquisição"),
    ("PED-D18", "Uncertainty / TPU", "Incerteza / TPU"),
)

_PATCH_NAMES = (
    ("P1", "Patch-Test Fundamentals & Error Signatures", "Fundamentos do Patch Test e Assinaturas de Erro"),
    ("P2", "Patch-Test Area & Line Planning", "Área e Planejamento de Linhas do Patch Test"),
    ("P3", "Synthetic Patch-Test Acquisition", "Aquisição Sintética do Patch Test"),
    ("P4", "Manual Patch-Test Calibration", "Calibração Manual do Patch Test"),
    ("P5", "Exercise Assessment", "Avaliação do Exercício"),
    ("P6", "RISC Simulator", "Simulador RISC"),
)

_ACQUISITION_NAMES = (
    ("A1", "Survey Area / True Seafloor", "Área do Levantamento / Fundo Verdadeiro"),
    ("A2", "Vessel & Installation", "Embarcação e Instalação"),
    ("A3", "Sonar Configuration", "Configuração do Sonar"),
    ("A4", "Environment", "Ambiente"),
    ("A5", "Survey Planning", "Planejamento do Levantamento"),
    ("A6", "Acquisition", "Aquisição"),
    ("A7", "Synthetic Raw Data Generation", "Geração de Dados Brutos Sintéticos"),
)

_BUILDERS = {
    "PED-D2": "hydrosim.app.signal_lesson_page.build_signal_lesson",
    "PED-D3": "hydrosim.app.sonar_equation_lesson_page.build_sonar_equation_lesson",
    "PED-D4": "hydrosim.app.propagation_lesson_page.build_propagation_lesson",
    "PED-D8": "hydrosim.app.sonar_geometry_lesson_page.build_sonar_geometry_lesson",
    "PED-D11": "hydrosim.app.vessel_lesson.build_vessel_lesson",
    "PED-D12": "hydrosim.app.motion_lesson_page.build_motion_lesson",
    "PED-D15": "hydrosim.app.sounding_formation_lesson_page.build_sounding_formation_lesson",
}


def _make(module: ModuleId, rows: tuple[tuple[str, str, str], ...]) -> tuple[PedagogicalExperience, ...]:
    return tuple(
        PedagogicalExperience(
            id=experience_id,
            module=module,
            name_en=name_en,
            name_pt_br=name_pt_br,
            availability="available" if experience_id in _BUILDERS else "coming-soon",
            page_builder=_BUILDERS.get(experience_id),
        )
        for experience_id, name_en, name_pt_br in rows
    )


PEDAGOGICAL_EXPERIENCES = (
    *_make("didactic", _DIDACTIC_NAMES),
    *_make("patch-test", _PATCH_NAMES),
    *_make("acquisition", _ACQUISITION_NAMES),
)


def experience_by_id(experience_id: str) -> PedagogicalExperience:
    for experience in PEDAGOGICAL_EXPERIENCES:
        if experience.id == experience_id:
            return experience
    raise KeyError(experience_id)


def experiences_for(module: ModuleId) -> tuple[PedagogicalExperience, ...]:
    return tuple(item for item in PEDAGOGICAL_EXPERIENCES if item.module == module)

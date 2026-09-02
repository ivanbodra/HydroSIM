"""Presentation-agnostic state for the D3 Sonar Equation lesson.

The application layer owns only learner-facing configuration and derived lesson
state. All acoustic-loss and level calculations are delegated to the canonical
``hydrosim.sonar_equation.d3_adapter`` scientific capability.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.sonar_equation.backscatter import AreaBackscatterInput
from hydrosim.sonar_equation.d3_adapter import (
    D3SonarEquationInput,
    D3SonarEquationResult,
    evaluate_d3_sonar_equation,
)


class SonarEquationLessonControls(BaseModel):
    """Required first-experience controls for D3 v0.1."""

    model_config = ConfigDict(frozen=True)

    frequency_hz: FiniteFloat = Field(default=300_000.0, gt=0.0)
    range_m: FiniteFloat = Field(default=50.0, gt=0.0)
    source_level_db_re_1upa_at_1m: FiniteFloat = 220.0
    noise_level_db_re_1upa: FiniteFloat = 60.0
    scattering_strength_db_per_m2: FiniteFloat = -30.0
    contributing_area_m2: FiniteFloat = Field(default=1.0, gt=0.0)
    tx_relative_beam_gain_db: FiniteFloat = Field(default=0.0, le=0.0)
    rx_relative_beam_gain_db: FiniteFloat = Field(default=0.0, le=0.0)


class SonarEquationContribution(BaseModel):
    """One signed contribution shown in the D3 causal level chain."""

    model_config = ConfigDict(frozen=True)

    key: str
    value_db: FiniteFloat


class SonarEquationLessonSnapshot(BaseModel):
    """Configured D3 state plus scientific result and contribution breakdown."""

    model_config = ConfigDict(frozen=True)

    controls: SonarEquationLessonControls
    result: D3SonarEquationResult
    contributions: tuple[SonarEquationContribution, ...]

    @property
    def received_level_db_re_1upa(self) -> float:
        return float(self.result.received_level_db_re_1upa)

    @property
    def snr_db(self) -> float:
        return float(self.result.snr_db)

    @property
    def transmission_loss_db(self) -> float:
        """Reciprocal two-way TL for the baseline equal-path lesson geometry."""

        value = self.result.two_way_transmission_loss_db
        if value is None:
            raise ValueError("D3 lesson baseline requires reciprocal equal outbound/inbound paths")
        return float(value)


def _scientific_input(controls: SonarEquationLessonControls) -> D3SonarEquationInput:
    return D3SonarEquationInput(
        frequency_hz=controls.frequency_hz,
        source_level_db_re_1upa_at_1m=controls.source_level_db_re_1upa_at_1m,
        noise_level_db_re_1upa=controls.noise_level_db_re_1upa,
        outbound_path_length_m=controls.range_m,
        inbound_path_length_m=controls.range_m,
        backscatter=AreaBackscatterInput(
            scattering_strength_db_per_m2=controls.scattering_strength_db_per_m2,
            contributing_area_m2=controls.contributing_area_m2,
            frequency_hz=controls.frequency_hz,
        ),
        tx_relative_beam_gain_db=controls.tx_relative_beam_gain_db,
        rx_relative_beam_gain_db=controls.rx_relative_beam_gain_db,
    )


def prepare_sonar_equation_lesson_snapshot(
    controls: SonarEquationLessonControls,
) -> SonarEquationLessonSnapshot:
    """Evaluate D3 exclusively through the canonical scientific adapter."""

    result = evaluate_d3_sonar_equation(_scientific_input(controls))
    contributions = (
        SonarEquationContribution(key="source-level", value_db=result.source_level_db_re_1upa_at_1m),
        SonarEquationContribution(key="tx-relative-gain", value_db=result.tx_relative_beam_gain_db),
        SonarEquationContribution(key="outbound-tl", value_db=-float(result.outbound_total_loss_db)),
        SonarEquationContribution(key="backscatter", value_db=result.backscatter_strength_db),
        SonarEquationContribution(key="inbound-tl", value_db=-float(result.inbound_total_loss_db)),
        SonarEquationContribution(key="rx-relative-gain", value_db=result.rx_relative_beam_gain_db),
        SonarEquationContribution(key="noise", value_db=-float(result.noise_level_db_re_1upa)),
    )
    return SonarEquationLessonSnapshot(
        controls=controls,
        result=result,
        contributions=contributions,
    )


def default_sonar_equation_lesson_snapshot() -> SonarEquationLessonSnapshot:
    """Return the deterministic D3 reset state."""

    return prepare_sonar_equation_lesson_snapshot(SonarEquationLessonControls())

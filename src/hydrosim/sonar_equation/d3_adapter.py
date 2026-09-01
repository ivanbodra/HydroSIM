"""Canonical D3 sonar-equation composition for the Didactic Explorer.

This module composes existing HydroSIM transmission-loss and area-backscatter
primitives with the Ainslie-McColm v0.1 absorption model. It intentionally stays
in the level domain and does not add receiver electronics, reverberation,
detection thresholds, bottom-type inference, or stochastic noise.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.acquisition.transmission_loss import (
    OneWayTransmissionLoss,
    PropagationLossModel,
    one_way_transmission_loss,
)

from .absorption import AinslieMcColmEnvironment, ainslie_mccolm_absorption_db_per_km
from .backscatter import AreaBackscatterInput, AreaBackscatterResult, area_backscatter_term


class D3SonarEquationInput(BaseModel):
    """Configured inputs for one D3 seabed-area echo calculation."""

    model_config = ConfigDict(frozen=True)

    frequency_hz: FiniteFloat = Field(gt=0.0)
    source_level_db_re_1upa_at_1m: FiniteFloat
    noise_level_db_re_1upa: FiniteFloat
    outbound_path_length_m: FiniteFloat = Field(gt=0.0)
    inbound_path_length_m: FiniteFloat = Field(gt=0.0)
    backscatter: AreaBackscatterInput
    tx_relative_beam_gain_db: FiniteFloat = Field(default=0.0, le=0.0)
    rx_relative_beam_gain_db: FiniteFloat = Field(default=0.0, le=0.0)
    absorption_environment: AinslieMcColmEnvironment = AinslieMcColmEnvironment()


class D3SonarEquationResult(BaseModel):
    """Contribution breakdown, received echo level, and SNR for D3 v0.1."""

    model_config = ConfigDict(frozen=True)

    frequency_hz: FiniteFloat = Field(gt=0.0)
    absorption_db_per_km: FiniteFloat = Field(ge=0.0)
    source_level_db_re_1upa_at_1m: FiniteFloat
    tx_relative_beam_gain_db: FiniteFloat = Field(le=0.0)
    outbound_spreading_loss_db: FiniteFloat
    outbound_absorption_loss_db: FiniteFloat = Field(ge=0.0)
    outbound_total_loss_db: FiniteFloat
    backscatter_strength_db: FiniteFloat
    inbound_spreading_loss_db: FiniteFloat
    inbound_absorption_loss_db: FiniteFloat = Field(ge=0.0)
    inbound_total_loss_db: FiniteFloat
    rx_relative_beam_gain_db: FiniteFloat = Field(le=0.0)
    received_level_db_re_1upa: FiniteFloat
    noise_level_db_re_1upa: FiniteFloat
    snr_db: FiniteFloat
    two_way_transmission_loss_db: FiniteFloat | None = None
    backscatter: AreaBackscatterResult


def _loss(path_length_m: float, absorption_db_per_km: float) -> OneWayTransmissionLoss:
    return one_way_transmission_loss(
        path_length_m=path_length_m,
        model=PropagationLossModel(absorption_db_per_km=absorption_db_per_km),
    )


def evaluate_d3_sonar_equation(value: D3SonarEquationInput) -> D3SonarEquationResult:
    """Evaluate the canonical D3 v0.1 contribution chain.

    ``RL = SL + G_tx - TL_out + BS - TL_in + G_rx`` and ``SNR = RL - NL``.
    The area-integrated ``BS`` term is consumed from ``AreaBackscatterResult``;
    no sediment or scattering-strength inference occurs here.
    """

    absorption = ainslie_mccolm_absorption_db_per_km(
        frequency_hz=float(value.frequency_hz),
        environment=value.absorption_environment,
    )
    outbound = _loss(float(value.outbound_path_length_m), absorption)
    inbound = _loss(float(value.inbound_path_length_m), absorption)
    backscatter = area_backscatter_term(value.backscatter)

    received = (
        float(value.source_level_db_re_1upa_at_1m)
        + float(value.tx_relative_beam_gain_db)
        - float(outbound.total_loss_db)
        + float(backscatter.backscatter_strength_db)
        - float(inbound.total_loss_db)
        + float(value.rx_relative_beam_gain_db)
    )
    snr = received - float(value.noise_level_db_re_1upa)

    reciprocal = None
    if abs(float(value.outbound_path_length_m) - float(value.inbound_path_length_m)) <= 1e-12:
        reciprocal = float(outbound.total_loss_db) + float(inbound.total_loss_db)

    return D3SonarEquationResult(
        frequency_hz=value.frequency_hz,
        absorption_db_per_km=absorption,
        source_level_db_re_1upa_at_1m=value.source_level_db_re_1upa_at_1m,
        tx_relative_beam_gain_db=value.tx_relative_beam_gain_db,
        outbound_spreading_loss_db=outbound.spreading_loss_db,
        outbound_absorption_loss_db=outbound.absorption_loss_db,
        outbound_total_loss_db=outbound.total_loss_db,
        backscatter_strength_db=backscatter.backscatter_strength_db,
        inbound_spreading_loss_db=inbound.spreading_loss_db,
        inbound_absorption_loss_db=inbound.absorption_loss_db,
        inbound_total_loss_db=inbound.total_loss_db,
        rx_relative_beam_gain_db=value.rx_relative_beam_gain_db,
        received_level_db_re_1upa=received,
        noise_level_db_re_1upa=value.noise_level_db_re_1upa,
        snr_db=snr,
        two_way_transmission_loss_db=reciprocal,
        backscatter=backscatter,
    )

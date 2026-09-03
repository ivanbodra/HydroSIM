"""Application adapter for the PED-D3 sonar-equation learner experience.

This module performs only request validation, unit conversion, sampling, and
serialization. All sonar-equation physics remains in the canonical Scientific
Core under :mod:`hydrosim.sonar_equation`.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.sonar_equation.absorption import AinslieMcColmEnvironment
from hydrosim.sonar_equation.backscatter import AreaBackscatterInput
from hydrosim.sonar_equation.d3_adapter import D3SonarEquationInput, evaluate_d3_sonar_equation


class D3SonarEquationRequest(BaseModel):
    """Configured learner controls plus explicit fixed context for PED-D3."""

    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    range_m: float = Field(default=100.0, gt=0.0)
    source_level_db_re_1upa_at_1m: float = 210.0
    noise_level_db_re_1upa: float = 60.0
    comparison_frequency_khz: float = Field(default=400.0, gt=0.0)
    curve_min_range_m: float = Field(default=10.0, gt=0.0)
    curve_max_range_m: float = Field(default=500.0, gt=0.0)
    curve_sample_count: int = Field(default=64, ge=8, le=512)
    scattering_strength_db_per_m2: float = -30.0
    contributing_area_m2: float = Field(default=1.0, gt=0.0)
    temperature_c: float = 10.0
    salinity: float = 35.0
    representative_depth_km: float = Field(default=0.0, ge=0.0)
    ph: float = 8.0
    tx_relative_beam_gain_db: float = Field(default=0.0, le=0.0)
    rx_relative_beam_gain_db: float = Field(default=0.0, le=0.0)


class D3TraceSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    x: tuple[float, ...]
    y: tuple[float, ...]
    x_unit: str
    y_unit: str


class D3ContributionBreakdown(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_level_db: float
    tx_relative_beam_gain_db: float
    outbound_spreading_loss_db: float
    outbound_absorption_loss_db: float
    outbound_total_loss_db: float
    backscatter_strength_db: float
    inbound_spreading_loss_db: float
    inbound_absorption_loss_db: float
    inbound_total_loss_db: float
    rx_relative_beam_gain_db: float
    noise_level_db: float


class D3FrequencyComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    frequency_khz: float
    absorption_db_per_km: float
    two_way_transmission_loss_db: float


class D3SonarEquationResponse(BaseModel):
    """Stable render-ready PED-D3 contract derived from canonical Core outputs."""

    model_config = ConfigDict(frozen=True)

    received_level_db_re_1upa: float
    snr_db: float
    absorption_db_per_km: float
    two_way_transmission_loss_db: float
    received_level_vs_range: D3TraceSeries
    snr_vs_range: D3TraceSeries
    frequency_loss_comparison: tuple[D3FrequencyComparison, D3FrequencyComparison]
    contribution_breakdown: D3ContributionBreakdown
    metadata: dict[str, float | str]


def _uniform_ranges(start: float, stop: float, count: int) -> tuple[float, ...]:
    if stop < start:
        raise ValueError("curve_max_range_m must be greater than or equal to curve_min_range_m")
    if count == 1:
        return (start,)
    step = (stop - start) / float(count - 1)
    return tuple(start + index * step for index in range(count))


def _evaluate(request: D3SonarEquationRequest, *, frequency_khz: float, range_m: float):
    environment = AinslieMcColmEnvironment(
        temperature_c=request.temperature_c,
        salinity=request.salinity,
        depth_km=request.representative_depth_km,
        ph=request.ph,
    )
    backscatter = AreaBackscatterInput(
        scattering_strength_db_per_m2=request.scattering_strength_db_per_m2,
        contributing_area_m2=request.contributing_area_m2,
        frequency_hz=frequency_khz * 1e3,
    )
    return evaluate_d3_sonar_equation(
        D3SonarEquationInput(
            frequency_hz=frequency_khz * 1e3,
            source_level_db_re_1upa_at_1m=request.source_level_db_re_1upa_at_1m,
            noise_level_db_re_1upa=request.noise_level_db_re_1upa,
            outbound_path_length_m=range_m,
            inbound_path_length_m=range_m,
            backscatter=backscatter,
            tx_relative_beam_gain_db=request.tx_relative_beam_gain_db,
            rx_relative_beam_gain_db=request.rx_relative_beam_gain_db,
            absorption_environment=environment,
        )
    )


def prepare_d3_sonar_equation_response(
    request: D3SonarEquationRequest,
) -> D3SonarEquationResponse:
    """Sample canonical D3 outputs for the production React learner slice."""

    configured = _evaluate(request, frequency_khz=request.frequency_khz, range_m=request.range_m)
    ranges = _uniform_ranges(
        request.curve_min_range_m,
        request.curve_max_range_m,
        request.curve_sample_count,
    )
    curve_results = tuple(
        _evaluate(request, frequency_khz=request.frequency_khz, range_m=range_m)
        for range_m in ranges
    )

    comparison_results = tuple(
        _evaluate(request, frequency_khz=frequency_khz, range_m=request.range_m)
        for frequency_khz in (request.frequency_khz, request.comparison_frequency_khz)
    )

    two_way = configured.two_way_transmission_loss_db
    if two_way is None:  # equal reciprocal paths are enforced by this application adapter
        raise RuntimeError("canonical D3 result did not provide reciprocal two-way loss")

    return D3SonarEquationResponse(
        received_level_db_re_1upa=configured.received_level_db_re_1upa,
        snr_db=configured.snr_db,
        absorption_db_per_km=configured.absorption_db_per_km,
        two_way_transmission_loss_db=two_way,
        received_level_vs_range=D3TraceSeries(
            x=ranges,
            y=tuple(result.received_level_db_re_1upa for result in curve_results),
            x_unit="m",
            y_unit="dB re 1 µPa",
        ),
        snr_vs_range=D3TraceSeries(
            x=ranges,
            y=tuple(result.snr_db for result in curve_results),
            x_unit="m",
            y_unit="dB",
        ),
        frequency_loss_comparison=tuple(
            D3FrequencyComparison(
                frequency_khz=frequency_khz,
                absorption_db_per_km=result.absorption_db_per_km,
                two_way_transmission_loss_db=float(result.two_way_transmission_loss_db),
            )
            for frequency_khz, result in zip(
                (request.frequency_khz, request.comparison_frequency_khz),
                comparison_results,
                strict=True,
            )
        ),
        contribution_breakdown=D3ContributionBreakdown(
            source_level_db=configured.source_level_db_re_1upa_at_1m,
            tx_relative_beam_gain_db=configured.tx_relative_beam_gain_db,
            outbound_spreading_loss_db=configured.outbound_spreading_loss_db,
            outbound_absorption_loss_db=configured.outbound_absorption_loss_db,
            outbound_total_loss_db=configured.outbound_total_loss_db,
            backscatter_strength_db=configured.backscatter_strength_db,
            inbound_spreading_loss_db=configured.inbound_spreading_loss_db,
            inbound_absorption_loss_db=configured.inbound_absorption_loss_db,
            inbound_total_loss_db=configured.inbound_total_loss_db,
            rx_relative_beam_gain_db=configured.rx_relative_beam_gain_db,
            noise_level_db=configured.noise_level_db_re_1upa,
        ),
        metadata={
            "frequency_khz": request.frequency_khz,
            "range_m": request.range_m,
            "source_level_db_re_1upa_at_1m": request.source_level_db_re_1upa_at_1m,
            "noise_level_db_re_1upa": request.noise_level_db_re_1upa,
            "scattering_strength_db_per_m2": request.scattering_strength_db_per_m2,
            "contributing_area_m2": request.contributing_area_m2,
            "temperature_c": request.temperature_c,
            "salinity": request.salinity,
            "representative_depth_km": request.representative_depth_km,
            "ph": request.ph,
            "state_semantics": "Configured inputs/context; Derived outputs",
            "scientific_model": "canonical D3 sonar equation / Ainslie-McColm absorption",
        },
    )

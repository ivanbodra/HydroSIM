"""Application adapter for the PED-D10 multisector MBES lesson.

This module serializes the authoritative PED-D10 scientific contract without
introducing vendor scheduling or frontend-owned acoustic physics.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition.wave_kinematics import AcousticWaveKinematics
from hydrosim.geometry.sonar_systems import TxSectorGeometry, TxSectorSetGeometry
from hydrosim.timing import SimulationTime


class D10SectorRequest(BaseModel):
    """Configured state for one transmit sector."""

    model_config = ConfigDict(extra="forbid")

    sector_id: str = Field(min_length=1)
    centre_across_track_deg: float
    across_track_min_deg: float
    across_track_max_deg: float
    frequency_khz: float = Field(gt=0.0)
    pulse_duration_ms: float = Field(gt=0.0)
    sector_tx_delay_ms: float = Field(ge=0.0)
    relative_power: float | None = None


class D10MultisectorRequest(BaseModel):
    """Minimal vendor-neutral PED-D10 configured state."""

    model_config = ConfigDict(extra="forbid")

    tx_time_seconds: float = 10.0
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    system_id: str = Field(default="ped-d10", min_length=1)
    head_id: str = Field(default="head-1", min_length=1)
    array_id: str = Field(default="tx-array", min_length=1)
    sectors: tuple[D10SectorRequest, ...] = Field(min_length=1)


class D10SectorResponse(BaseModel):
    """Configured and Derived state for one sector, ready for presentation."""

    model_config = ConfigDict(frozen=True)

    sector_id: str
    sector_index: int
    centre_across_track_deg: float
    across_track_min_deg: float
    across_track_max_deg: float
    frequency_khz: float
    pulse_duration_ms: float
    sector_tx_delay_ms: float
    relative_power: float | None
    sector_tx_time_seconds: float
    sector_tx_end_seconds: float
    transmit_group: int
    wavelength_m: float


class D10CoverageSupport(BaseModel):
    model_config = ConfigDict(frozen=True)

    sector_id: str
    across_track_min_deg: float
    across_track_max_deg: float


class D10MultisectorResponse(BaseModel):
    """Stable render-ready contract for the first PED-D10 vertical slice."""

    model_config = ConfigDict(frozen=True)

    tx_time_seconds: float
    sound_speed_mps: float
    sectors: tuple[D10SectorResponse, ...]
    coverage_supports: tuple[D10CoverageSupport, ...]
    transmit_groups: tuple[tuple[str, ...], ...]
    metadata: dict[str, str]


def prepare_d10_multisector_response(request: D10MultisectorRequest) -> D10MultisectorResponse:
    """Derive timing, sequence groups, wavelength and canonical TX geometry."""

    tx_time = SimulationTime(seconds=request.tx_time_seconds)
    sector_geometries = tuple(
        TxSectorGeometry(
            sector_id=sector.sector_id,
            sector_index=index,
            system_id=request.system_id,
            head_id=request.head_id,
            array_id=request.array_id,
            centre_along_track_angle_rad=0.0,
            centre_across_track_angle_rad=radians(sector.centre_across_track_deg),
            along_track_min_rad=0.0,
            along_track_max_rad=0.0,
            across_track_min_rad=radians(sector.across_track_min_deg),
            across_track_max_rad=radians(sector.across_track_max_deg),
            presentation_order=index,
        )
        for index, sector in enumerate(request.sectors)
    )
    geometry = TxSectorSetGeometry(sectors=sector_geometries)

    unique_delays = sorted({float(sector.sector_tx_delay_ms) for sector in request.sectors})
    delay_to_group = {delay: index for index, delay in enumerate(unique_delays)}
    groups = tuple(
        tuple(
            sector.sector_id
            for sector in request.sectors
            if float(sector.sector_tx_delay_ms) == delay
        )
        for delay in unique_delays
    )

    responses: list[D10SectorResponse] = []
    for index, (sector, sector_geometry) in enumerate(zip(request.sectors, geometry.sectors, strict=True)):
        delay_seconds = sector.sector_tx_delay_ms * 1e-3
        sector_tx_time = tx_time.shifted(delay_seconds)
        pulse_duration_seconds = sector.pulse_duration_ms * 1e-3
        wavelength = AcousticWaveKinematics(
            frequency_hz=sector.frequency_khz * 1e3,
            sound_speed_mps=request.sound_speed_mps,
        ).wavelength_m
        responses.append(
            D10SectorResponse(
                sector_id=sector.sector_id,
                sector_index=index,
                centre_across_track_deg=degrees(sector_geometry.centre_across_track_angle_rad),
                across_track_min_deg=degrees(sector_geometry.across_track_min_rad),
                across_track_max_deg=degrees(sector_geometry.across_track_max_rad),
                frequency_khz=sector.frequency_khz,
                pulse_duration_ms=sector.pulse_duration_ms,
                sector_tx_delay_ms=sector.sector_tx_delay_ms,
                relative_power=sector.relative_power,
                sector_tx_time_seconds=float(sector_tx_time.seconds),
                sector_tx_end_seconds=float(sector_tx_time.seconds + pulse_duration_seconds),
                transmit_group=delay_to_group[float(sector.sector_tx_delay_ms)],
                wavelength_m=wavelength,
            )
        )

    coverage = tuple(
        D10CoverageSupport(
            sector_id=sector.sector_id,
            across_track_min_deg=degrees(support[2]),
            across_track_max_deg=degrees(support[3]),
        )
        for sector, support in zip(geometry.sectors, geometry.coverage_supports, strict=True)
    )

    return D10MultisectorResponse(
        tx_time_seconds=request.tx_time_seconds,
        sound_speed_mps=request.sound_speed_mps,
        sectors=tuple(responses),
        coverage_supports=coverage,
        transmit_groups=groups,
        metadata={
            "frame": "head/transducer; +X Forward, +Y Starboard, +Z Down",
            "across_track_sign": "positive Port; negative Starboard",
            "timing_semantics": "sector_tx_time = tx_time + sector_tx_delay",
            "state_semantics": "Configured sector inputs; Derived timing/wavelength/coverage",
            "relative_power_semantics": "configured relative quantity only; not RL/SNR/detectability",
        },
    )

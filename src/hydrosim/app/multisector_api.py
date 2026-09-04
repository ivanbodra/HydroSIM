"""Application bridge for PED-D10 multisector MBES.

This module serializes the authoritative PED-D10 scientific contract using the
canonical TX-sector geometry model. It does not add vendor scheduling or acoustic
physics.
"""

from __future__ import annotations

from math import pi

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.geometry import TxSectorGeometry, TxSectorSetGeometry


class D10SectorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector_id: str = Field(min_length=1)
    across_track_min_deg: float
    across_track_max_deg: float
    centre_across_track_deg: float
    frequency_khz: float = Field(gt=0.0)
    pulse_duration_ms: float = Field(gt=0.0)
    tx_delay_ms: float = Field(ge=0.0)
    relative_power: float | None = Field(default=None, ge=0.0)


class D10MultisectorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tx_time_s: float = 0.0
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    sectors: tuple[D10SectorRequest, ...]

    @model_validator(mode="after")
    def _validate_sectors(self) -> "D10MultisectorRequest":
        if not self.sectors:
            raise ValueError("at least one TX sector is required")
        return self


class D10SectorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    sector_id: str
    sector_index: int
    across_track_min_deg: float
    across_track_max_deg: float
    centre_across_track_deg: float
    frequency_khz: float
    wavelength_m: float
    pulse_duration_ms: float
    tx_delay_ms: float
    tx_time_s: float
    tx_end_time_s: float
    relative_power: float | None


class D10MultisectorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    sectors: tuple[D10SectorResponse, ...]
    transmit_groups: tuple[tuple[str, ...], ...]
    coverage_supports_deg: tuple[tuple[float, float], ...]
    metadata: dict[str, str | float]


def _rad(value_deg: float) -> float:
    return value_deg * pi / 180.0


def prepare_d10_multisector_response(request: D10MultisectorRequest) -> D10MultisectorResponse:
    """Return render-ready Configured/Derived PED-D10 state."""

    geometries = tuple(
        TxSectorGeometry(
            sector_id=sector.sector_id,
            sector_index=index,
            system_id="ped-d10",
            head_id="head-a",
            array_id="tx-array",
            along_track_min_rad=0.0,
            along_track_max_rad=0.0,
            across_track_min_rad=_rad(sector.across_track_min_deg),
            across_track_max_rad=_rad(sector.across_track_max_deg),
            centre_across_track_angle_rad=_rad(sector.centre_across_track_deg),
            presentation_order=index,
        )
        for index, sector in enumerate(request.sectors)
    )
    sector_set = TxSectorSetGeometry(sectors=geometries)

    responses = tuple(
        D10SectorResponse(
            sector_id=sector.sector_id,
            sector_index=index,
            across_track_min_deg=sector.across_track_min_deg,
            across_track_max_deg=sector.across_track_max_deg,
            centre_across_track_deg=sector.centre_across_track_deg,
            frequency_khz=sector.frequency_khz,
            wavelength_m=request.sound_speed_mps / (sector.frequency_khz * 1e3),
            pulse_duration_ms=sector.pulse_duration_ms,
            tx_delay_ms=sector.tx_delay_ms,
            tx_time_s=request.tx_time_s + sector.tx_delay_ms * 1e-3,
            tx_end_time_s=request.tx_time_s + (sector.tx_delay_ms + sector.pulse_duration_ms) * 1e-3,
            relative_power=sector.relative_power,
        )
        for index, sector in enumerate(request.sectors)
    )

    epochs = sorted({item.tx_time_s for item in responses})
    transmit_groups = tuple(
        tuple(item.sector_id for item in responses if abs(item.tx_time_s - epoch) <= 1e-12)
        for epoch in epochs
    )
    coverage_supports_deg = tuple(
        (support[2] * 180.0 / pi, support[3] * 180.0 / pi)
        for support in sector_set.coverage_supports
    )

    return D10MultisectorResponse(
        sectors=responses,
        transmit_groups=transmit_groups,
        coverage_supports_deg=coverage_supports_deg,
        metadata={
            "tx_time_s": request.tx_time_s,
            "sound_speed_mps": request.sound_speed_mps,
            "frame": "+X Forward, +Y Starboard, +Z Down",
            "across_track_sign": "positive Port; negative Starboard",
            "state_semantics": "Configured sectors; Derived timing, wavelength and coverage",
            "fidelity": "vendor-neutral first slice; TX sectors remain distinct from RX beams",
        },
    )

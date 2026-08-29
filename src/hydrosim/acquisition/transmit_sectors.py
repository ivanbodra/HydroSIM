"""Vendor-neutral transmit-sector geometry for multibeam acquisition.

A transmit sector is a steering/time hypothesis applied to one physical TX
aperture. It is not a separate transducer. This module intentionally models
only deterministic sector geometry and timing; waveform-specific frequency,
bandwidth and pulse-shape behavior belong to later acquisition layers.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from hydrosim.geometry import Vector3

from .angular_pattern_2d import sensor_angular_direction


class TransmitSector(BaseModel):
    """One electronically steered transmit sector."""

    model_config = ConfigDict(frozen=True)

    sector_index: int = Field(ge=0)
    name: str = Field(min_length=1)
    steering_along_track_angle_rad: FiniteFloat = 0.0
    steering_across_track_angle_rad: FiniteFloat = 0.0
    tx_delay_seconds: FiniteFloat = Field(default=0.0, ge=0.0)

    @property
    def steering_direction_sensor_frame(self) -> Vector3:
        return sensor_angular_direction(
            self.steering_along_track_angle_rad,
            self.steering_across_track_angle_rad,
        )


class TransmitSectorSet(BaseModel):
    """Ordered sectors emitted from one physical transmit aperture."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="transmit_sectors", min_length=1)
    sectors: tuple[TransmitSector, ...]

    @model_validator(mode="after")
    def _validate_sector_set(self) -> "TransmitSectorSet":
        if not self.sectors:
            raise ValueError("transmit sector set must contain at least one sector")
        indices = [sector.sector_index for sector in self.sectors]
        if len(indices) != len(set(indices)):
            raise ValueError("transmit sector indices must be unique")
        names = [sector.name for sector in self.sectors]
        if len(names) != len(set(names)):
            raise ValueError("transmit sector names must be unique")
        return self


def make_uniform_transmit_sectors(
    *,
    start_along_track_angle_rad: float,
    end_along_track_angle_rad: float,
    sector_count: int,
    across_track_angle_rad: float = 0.0,
    first_tx_delay_seconds: float = 0.0,
    inter_sector_delay_seconds: float = 0.0,
    name: str = "uniform_transmit_sectors",
) -> TransmitSectorSet:
    """Create uniformly spaced along-track TX sectors with explicit delays.

    This is a neutral reference configuration, not a vendor transmission mode.
    Sector timing is represented relative to the ping's common TX reference:
    sector_tx_time = tx_time + tx_delay_seconds.
    """

    if sector_count < 1:
        raise ValueError("sector_count must be >= 1")
    if first_tx_delay_seconds < 0.0 or inter_sector_delay_seconds < 0.0:
        raise ValueError("transmit-sector delays must be non-negative")

    start = float(start_along_track_angle_rad)
    end = float(end_along_track_angle_rad)
    if sector_count == 1:
        angles = ((start + end) / 2.0,)
    else:
        if end <= start:
            raise ValueError(
                "end_along_track_angle_rad must be greater than start_along_track_angle_rad"
            )
        step = (end - start) / (sector_count - 1)
        angles = tuple(start + index * step for index in range(sector_count))

    sectors = tuple(
        TransmitSector(
            sector_index=index,
            name=f"sector_{index}",
            steering_along_track_angle_rad=angle,
            steering_across_track_angle_rad=across_track_angle_rad,
            tx_delay_seconds=first_tx_delay_seconds + index * inter_sector_delay_seconds,
        )
        for index, angle in enumerate(angles)
    )
    return TransmitSectorSet(name=name, sectors=sectors)

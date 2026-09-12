"""Beamwidth-defined directional-response proxy for pedagogical configurations."""

from __future__ import annotations

from math import exp, log, sqrt

from pydantic import BaseModel, ConfigDict, Field


class BeamwidthDirectionalSample(BaseModel):
    """Normalized one-way response at one sensor-frame angle."""

    model_config = ConfigDict(frozen=True)

    angle_deg: float
    normalized_field_amplitude: float = Field(ge=0.0, le=1.0)
    normalized_power: float = Field(ge=0.0, le=1.0)


def beamwidth_gaussian_power(*, angle_deg: float, steering_deg: float, hpbw_deg: float) -> float:
    """Normalized Gaussian power proxy whose full half-power width is ``hpbw_deg``."""
    if hpbw_deg <= 0.0:
        raise ValueError("hpbw_deg must be positive")
    offset = (float(angle_deg) - float(steering_deg)) / float(hpbw_deg)
    return exp(-4.0 * log(2.0) * offset * offset)


def beamwidth_gaussian_response(
    *, angle_deg: float, steering_deg: float, hpbw_deg: float
) -> BeamwidthDirectionalSample:
    """Return normalized field amplitude and power for the beamwidth proxy."""
    power = beamwidth_gaussian_power(
        angle_deg=angle_deg, steering_deg=steering_deg, hpbw_deg=hpbw_deg
    )
    return BeamwidthDirectionalSample(
        angle_deg=float(angle_deg),
        normalized_field_amplitude=sqrt(power),
        normalized_power=power,
    )

"""Beamwidth-defined directional-response proxy for pedagogical sonar models.

This helper is deliberately separate from physical array-factor models. It is used
when a system provides a nominal full half-power beamwidth but no registered
physical aperture from which a directional pattern can be computed.
"""

from __future__ import annotations

from math import exp, log, sqrt

from pydantic import BaseModel, ConfigDict, Field


class BeamwidthPatternSample(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: float
    normalized_amplitude: float = Field(ge=0.0, le=1.0)
    normalized_power: float = Field(ge=0.0, le=1.0)


def gaussian_power_from_beamwidth(
    *, angle_deg: float, steering_angle_deg: float, half_power_beamwidth_deg: float
) -> float:
    """Return normalized Gaussian power for a full half-power beamwidth."""

    beta = float(half_power_beamwidth_deg)
    if beta <= 0.0:
        raise ValueError("half_power_beamwidth_deg must be > 0")
    offset = (float(angle_deg) - float(steering_angle_deg)) / beta
    return exp(-4.0 * log(2.0) * offset * offset)


def gaussian_beamwidth_pattern(
    *,
    angles_deg: tuple[float, ...],
    steering_angle_deg: float,
    half_power_beamwidth_deg: float,
) -> tuple[BeamwidthPatternSample, ...]:
    """Evaluate the normalized beamwidth-defined proxy on a supplied angle grid."""

    samples: list[BeamwidthPatternSample] = []
    for angle in angles_deg:
        power = gaussian_power_from_beamwidth(
            angle_deg=angle,
            steering_angle_deg=steering_angle_deg,
            half_power_beamwidth_deg=half_power_beamwidth_deg,
        )
        samples.append(
            BeamwidthPatternSample(
                angle_deg=float(angle),
                normalized_amplitude=sqrt(power),
                normalized_power=power,
            )
        )
    return tuple(samples)

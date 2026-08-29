"""Reference flat-seafloor rectangular beamwidth approximation.

This module keeps a compact beamwidth-based approximation for didactic use and
for comparisons with conventional sonar footprint formulae. It must not be read
as a hard physical boundary of insonification: acoustic energy generally exists
outside the -3 dB beamwidth, including the remainder of the main lobe and
sidelobes.

Accordingly, the rectangular ``effective_area_m2`` produced here is an explicit
beamwidth/pulse approximation. The preferred higher-fidelity pathway is the full
2D TX×RX pattern projection, which integrates normalized power over the seafloor
to obtain an equivalent contributing area for footprint demonstrations.

No bottom-scattering, sediment, target-strength, or reflectivity model belongs to
this acquisition-layer calculation.
"""

from __future__ import annotations

from math import pi, sin, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class FlatSeafloorFootprintModel(BaseModel):
    """Half-power beamwidth and pulse parameters for the rectangular approximation."""

    model_config = ConfigDict(frozen=True)

    transmit_along_track_beamwidth_rad: FiniteFloat = Field(gt=0.0, lt=pi)
    receive_across_track_beamwidth_rad: FiniteFloat = Field(gt=0.0, lt=pi)
    nadir_pulse_projection_threshold_rad: FiniteFloat = Field(default=1e-3, gt=0.0)


class InsonifiedFootprint(BaseModel):
    """Legacy-named rectangular beamwidth/pulse approximation on a flat bottom."""

    model_config = ConfigDict(frozen=True)

    vertical_separation_m: FiniteFloat = Field(gt=0.0)
    along_track_center_angle_rad: FiniteFloat
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0, lt=pi / 2.0)
    beam_limited_along_track_width_m: FiniteFloat = Field(gt=0.0)
    beam_limited_across_track_width_m: FiniteFloat = Field(gt=0.0)
    pulse_limited_across_track_width_m: FiniteFloat | None = Field(default=None, gt=0.0)
    effective_across_track_width_m: FiniteFloat = Field(gt=0.0)
    effective_area_m2: FiniteFloat = Field(gt=0.0)
    across_track_limiting_mechanism: str


def _flat_bottom_angular_width(vertical_separation_m: float, center: float, beamwidth: float) -> float:
    half = 0.5 * beamwidth
    lower = center - half
    upper = center + half
    if lower <= -0.5 * pi or upper >= 0.5 * pi:
        raise ValueError("beam half-power edges must remain within the downward hemisphere")
    width = vertical_separation_m * (tan(upper) - tan(lower))
    if width <= 0.0:
        raise ValueError("computed beam footprint width must be positive")
    return width


def estimate_flat_seafloor_footprint(
    *,
    model: FlatSeafloorFootprintModel,
    vertical_separation_m: float,
    transmit_along_track_center_angle_rad: float,
    incidence_angle_from_normal_rad: float,
    pulse_duration_seconds: float,
    sound_speed_mps: float,
) -> InsonifiedFootprint:
    """Estimate the compact rectangular -3 dB/pulse approximation."""

    h = float(vertical_separation_m)
    theta = float(incidence_angle_from_normal_rad)
    tau = float(pulse_duration_seconds)
    c = float(sound_speed_mps)
    if h <= 0.0:
        raise ValueError("vertical_separation_m must be positive")
    if theta < 0.0 or theta >= 0.5 * pi:
        raise ValueError("incidence angle must satisfy 0 <= theta < pi/2")
    if tau <= 0.0 or c <= 0.0:
        raise ValueError("pulse duration and sound speed must be positive")

    along_width = _flat_bottom_angular_width(
        h,
        float(transmit_along_track_center_angle_rad),
        float(model.transmit_along_track_beamwidth_rad),
    )
    across_width = _flat_bottom_angular_width(
        h,
        theta,
        float(model.receive_across_track_beamwidth_rad),
    )

    pulse_width = None
    effective_across = across_width
    mechanism = "receive_beam"
    if theta >= float(model.nadir_pulse_projection_threshold_rad):
        pulse_width = c * tau / (2.0 * sin(theta))
        if pulse_width < across_width:
            effective_across = pulse_width
            mechanism = "pulse"

    return InsonifiedFootprint(
        vertical_separation_m=h,
        along_track_center_angle_rad=transmit_along_track_center_angle_rad,
        incidence_angle_from_normal_rad=theta,
        beam_limited_along_track_width_m=along_width,
        beam_limited_across_track_width_m=across_width,
        pulse_limited_across_track_width_m=pulse_width,
        effective_across_track_width_m=effective_across,
        effective_area_m2=along_width * effective_across,
        across_track_limiting_mechanism=mechanism,
    )

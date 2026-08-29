"""Reference flat-seafloor insonified-footprint geometry.

This module estimates the effective seafloor patch used by the area-backscatter
model from explicit beamwidth and pulse-duration inputs. It is intentionally a
local flat-bottom approximation and does not replace full TX/RX beam-pattern
integration over terrain.

For a horizontal seafloor at vertical separation h and a beam-centre incidence
angle theta measured from the local normal, the beam-limited across-track width is
computed from the two half-power edge rays:

    W_rx = h [tan(theta + beta_rx/2) - tan(theta - beta_rx/2)].

The along-track width is evaluated analogously from the TX half-power beamwidth
about its steering angle. For oblique incidence, the pulse-limited radial extent is
approximated by

    W_pulse = c tau / (2 sin(theta)),

and the effective across-track width is min(W_rx, W_pulse). Near nadir this pulse
projection is ill-conditioned, so the first reference model remains beam-limited.
"""

from __future__ import annotations

from math import pi, sin, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .bottom_interaction import SeafloorAreaBackscatter


class FlatSeafloorFootprintModel(BaseModel):
    """Half-power beamwidth and pulse parameters for a local flat-bottom patch."""

    model_config = ConfigDict(frozen=True)

    transmit_along_track_beamwidth_rad: FiniteFloat = Field(gt=0.0, lt=pi)
    receive_across_track_beamwidth_rad: FiniteFloat = Field(gt=0.0, lt=pi)
    nadir_pulse_projection_threshold_rad: FiniteFloat = Field(default=1e-3, gt=0.0)


class InsonifiedFootprint(BaseModel):
    """Reference rectangular effective patch on a horizontal seafloor."""

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
    """Estimate a rectangular effective TX×RX/pulse footprint on a flat bottom."""

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


def seafloor_backscatter_from_footprint(
    *,
    scattering_strength_db_per_m2: float,
    footprint: InsonifiedFootprint,
) -> SeafloorAreaBackscatter:
    """Build the existing area-backscatter model from a derived footprint."""

    return SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=footprint.effective_area_m2,
        incidence_angle_from_normal_rad=footprint.incidence_angle_from_normal_rad,
    )

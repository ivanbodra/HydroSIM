"""Didactic area-backscatter term for the sonar-equation module.

HydroSIM does not attempt to predict seafloor backscatter from bottom type inside
the acquisition simulator. Backscatter depends on more than sediment class,
including frequency, grazing/incidence angle, roughness scales, acoustic
properties, and other environmental factors.

This module therefore treats scattering strength S_b as an explicit input to a
sonar-equation demonstration. The basic area term is

    BS = S_b + 10 log10(A / 1 m^2).

Frequency and grazing angle may be retained as context for a chosen S_b value but
are not used to generate S_b unless a separately documented model is introduced
later.
"""

from __future__ import annotations

from math import log10, pi

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class AreaBackscatterInput(BaseModel):
    """Explicit inputs for the didactic area-backscatter sonar-equation term."""

    model_config = ConfigDict(frozen=True)

    scattering_strength_db_per_m2: FiniteFloat
    contributing_area_m2: FiniteFloat = Field(gt=0.0)
    frequency_hz: FiniteFloat | None = Field(default=None, gt=0.0)
    grazing_angle_rad: FiniteFloat | None = Field(default=None, ge=0.0, le=pi / 2.0)


class AreaBackscatterResult(BaseModel):
    """Area-integrated backscatter term derived from explicit S_b and area."""

    model_config = ConfigDict(frozen=True)

    scattering_strength_db_per_m2: FiniteFloat
    contributing_area_m2: FiniteFloat = Field(gt=0.0)
    area_gain_db: FiniteFloat
    backscatter_strength_db: FiniteFloat
    frequency_hz: FiniteFloat | None = Field(default=None, gt=0.0)
    grazing_angle_rad: FiniteFloat | None = Field(default=None, ge=0.0, le=pi / 2.0)


def area_backscatter_term(value: AreaBackscatterInput) -> AreaBackscatterResult:
    """Evaluate ``BS = S_b + 10 log10(A / 1 m^2)``.

    ``frequency_hz`` and ``grazing_angle_rad`` are contextual metadata only. This
    function deliberately does not infer scattering strength from them.
    """

    area = float(value.contributing_area_m2)
    area_gain_db = 10.0 * log10(area)
    bs = float(value.scattering_strength_db_per_m2) + area_gain_db
    return AreaBackscatterResult(
        scattering_strength_db_per_m2=value.scattering_strength_db_per_m2,
        contributing_area_m2=area,
        area_gain_db=area_gain_db,
        backscatter_strength_db=bs,
        frequency_hz=value.frequency_hz,
        grazing_angle_rad=value.grazing_angle_rad,
    )

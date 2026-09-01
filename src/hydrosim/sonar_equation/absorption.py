"""Frequency-dependent seawater absorption for the D3 sonar-equation lesson.

The v0.1 model implements the simplified Ainslie & McColm (1998) empirical
formula selected by ``docs/science/sonar_equation_v0_1_contract.md``.

Inputs use frequency in Hz, temperature in degrees Celsius, salinity in practical
salinity units (approximately ppt for this empirical relation), representative
depth in km, and pH. The returned absorption coefficient is in dB/km.
"""

from __future__ import annotations

from math import exp, sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class AinslieMcColmEnvironment(BaseModel):
    """Validated environmental context for the v0.1 absorption approximation."""

    model_config = ConfigDict(frozen=True)

    temperature_c: FiniteFloat = Field(default=10.0, gt=-6.0, lt=35.0)
    salinity: FiniteFloat = Field(default=35.0, gt=5.0, lt=50.0)
    depth_km: FiniteFloat = Field(default=0.0, ge=0.0, lt=7.0)
    ph: FiniteFloat = Field(default=8.0, gt=7.7, lt=8.3)


def ainslie_mccolm_absorption_db_per_km(
    *,
    frequency_hz: float,
    environment: AinslieMcColmEnvironment | None = None,
) -> float:
    """Return Ainslie-McColm seawater absorption in dB/km.

    The implementation follows the equations recorded in the canonical D3
    scientific contract. ``frequency_hz`` must be positive; the empirical
    environmental domain is enforced by :class:`AinslieMcColmEnvironment`.
    """

    frequency = float(frequency_hz)
    if frequency <= 0.0:
        raise ValueError("frequency_hz must be positive")

    env = environment or AinslieMcColmEnvironment()
    f_khz = frequency / 1000.0
    temperature = float(env.temperature_c)
    salinity = float(env.salinity)
    depth = float(env.depth_km)
    ph = float(env.ph)

    f1 = 0.78 * sqrt(salinity / 35.0) * exp(temperature / 26.0)
    f2 = 42.0 * exp(temperature / 17.0)

    boric_acid = (
        0.106
        * exp((ph - 8.0) / 0.56)
        * (f1 * f_khz * f_khz / (f1 * f1 + f_khz * f_khz))
    )
    magnesium_sulfate = (
        0.52
        * (1.0 + temperature / 43.0)
        * (salinity / 35.0)
        * exp(-depth / 6.0)
        * (f2 * f_khz * f_khz / (f2 * f2 + f_khz * f_khz))
    )
    pure_water = 0.00049 * exp(-(temperature / 27.0 + depth / 17.0)) * f_khz * f_khz
    return float(boric_acid + magnesium_sulfate + pure_water)

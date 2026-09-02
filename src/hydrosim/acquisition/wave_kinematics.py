"""Minimal acoustic-wave kinematics for PED-D1/PED-D2.

This module models normalized one-dimensional harmonic-wave kinematics only. It
introduces no propagation loss, transducer response, calibrated pressure, noise,
scattering, or bottom-detection behavior.
"""

from __future__ import annotations

from math import cos, isfinite, pi

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class AcousticWaveKinematics(BaseModel):
    """Configured 1-D positive-x travelling-wave kinematics.

    ``normalized_amplitude`` is dimensionless. The analytic field follows
    ``A cos(2*pi*f*t - 2*pi*x/lambda + phi0)`` so the minus spatial-phase sign
    explicitly denotes propagation in the positive-x direction.
    """

    model_config = ConfigDict(frozen=True)

    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(default=1500.0, gt=0.0)
    normalized_amplitude: FiniteFloat = Field(default=1.0, ge=0.0)
    initial_phase_rad: FiniteFloat = 0.0

    @property
    def period_seconds(self) -> float:
        """Return the configured harmonic period ``1/f`` in seconds."""

        return 1.0 / float(self.frequency_hz)

    @property
    def wavelength_m(self) -> float:
        """Return wavelength ``c/f`` in the configured homogeneous medium."""

        return float(self.sound_speed_mps) / float(self.frequency_hz)

    def normalized_field(self, *, x_m: float, time_seconds: float) -> float:
        """Evaluate the dimensionless travelling-wave amplitude at ``(x, t)``."""

        x = float(x_m)
        time = float(time_seconds)
        if not isfinite(x) or not isfinite(time):
            raise ValueError("x_m and time_seconds must be finite")
        phase = (
            2.0 * pi * float(self.frequency_hz) * time
            - 2.0 * pi * x / self.wavelength_m
            + float(self.initial_phase_rad)
        )
        return float(self.normalized_amplitude) * cos(phase)


def monostatic_two_way_range_offset(*, lag_seconds: float, sound_speed_mps: float = 1500.0) -> float:
    """Convert signed time lag to signed monostatic two-way range offset.

    The conversion is ``Delta R = c * Delta t / 2``. Signed lag is preserved so
    correlation lags before and after zero remain distinguishable.
    """

    lag = float(lag_seconds)
    sound_speed = float(sound_speed_mps)
    if not isfinite(lag):
        raise ValueError("lag_seconds must be finite")
    if not isfinite(sound_speed) or sound_speed <= 0.0:
        raise ValueError("sound_speed_mps must be finite and positive")
    return sound_speed * lag / 2.0

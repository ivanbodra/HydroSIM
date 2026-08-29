"""Far-field directivity of ideal rectangular acoustic elements.

The first HydroSIM element-factor model treats one physical array element as a
uniform rectangular piston/aperture in the array-local XY plane, with +Z as its
normal. It is deliberately independent of array spacing and beamforming weights.
"""

from __future__ import annotations

from math import pi, sin

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import ArrayElement, Vector3


class RectangularElementFactor(BaseModel):
    """Normalized one-way pressure directivity of one rectangular element."""

    model_config = ConfigDict(frozen=True)

    longitudinal_factor: FiniteFloat
    transverse_factor: FiniteFloat
    amplitude: FiniteFloat
    power: FiniteFloat


def _sinc_unnormalized(argument: float) -> float:
    """Return sin(x)/x with its continuous value at x=0."""

    if abs(argument) <= 1e-15:
        return 1.0
    return sin(argument) / argument


def rectangular_element_factor(
    *,
    element: ArrayElement,
    direction_array_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
) -> RectangularElementFactor:
    """Evaluate the ideal far-field rectangular-element factor.

    ``direction_array_frame`` points from the element toward the field/source
    direction. The element face lies in local XY and its normal is +Z. For a
    normalized unit direction ``u`` the pressure factor is

        sinc((k a / 2) u_x) * sinc((k b / 2) u_y),

    where ``a`` and ``b`` are the longitudinal and transverse face dimensions,
    ``k = 2*pi/lambda``, and sinc(x)=sin(x)/x.

    The returned ``amplitude`` is the absolute normalized pressure magnitude;
    ``power`` is its square. This is a one-way element factor, not a complete
    array or two-way sonar beam pattern.
    """

    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be > 0")
    if sound_speed_mps <= 0.0:
        raise ValueError("sound_speed_mps must be > 0")

    norm = (
        float(direction_array_frame.x) ** 2
        + float(direction_array_frame.y) ** 2
        + float(direction_array_frame.z) ** 2
    ) ** 0.5
    if norm <= 0.0:
        raise ValueError("direction_array_frame must be non-zero")

    ux = float(direction_array_frame.x) / norm
    uy = float(direction_array_frame.y) / norm
    wavelength = float(sound_speed_mps) / float(frequency_hz)
    k = 2.0 * pi / wavelength

    longitudinal = _sinc_unnormalized(0.5 * k * float(element.longitudinal_size) * ux)
    transverse = _sinc_unnormalized(0.5 * k * float(element.transverse_size) * uy)
    signed = longitudinal * transverse
    amplitude = abs(signed)

    return RectangularElementFactor(
        longitudinal_factor=longitudinal,
        transverse_factor=transverse,
        amplitude=amplitude,
        power=amplitude * amplitude,
    )

"""Deterministic aperture weighting for ideal HydroSIM arrays.

This module only generates named element weights. The coherent array-factor
physics remains owned by :mod:`hydrosim.acquisition.array_factor`.
"""

from __future__ import annotations

from math import cos, pi
from typing import Literal

ApertureWeighting = Literal["uniform", "hann"]


def deterministic_aperture_weights(
    element_count: int,
    weighting: ApertureWeighting = "uniform",
) -> tuple[complex, ...]:
    """Return deterministic 1-D aperture weights in element order.

    ``uniform`` returns unit weights. ``hann`` follows the authoritative PED-D6
    contract. A single-element aperture always returns one unit weight so the
    canonical array-factor normalization remains defined.
    """

    count = int(element_count)
    if count < 1:
        raise ValueError("element_count must be >= 1")

    if weighting == "uniform" or count == 1:
        return tuple(1.0 + 0.0j for _ in range(count))
    if weighting != "hann":
        raise ValueError(f"unsupported aperture weighting: {weighting}")

    return tuple(
        complex(0.5 * (1.0 - cos(2.0 * pi * index / (count - 1))), 0.0)
        for index in range(count)
    )

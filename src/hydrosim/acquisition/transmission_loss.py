"""Deterministic propagation-amplitude loss for HydroSIM.

This first amplitude layer deliberately separates propagation loss from bottom
scattering, target strength, source level, receiver sensitivity, noise and
electronics.

For one propagation leg of path length r, spherical spreading referenced to r0 is

    TL_spreading = 20 log10(r / r0)  [dB]

and homogeneous absorption specified by alpha in dB/km contributes

    TL_absorption = alpha * r_km      [dB].

The total one-way pressure-amplitude ratio is therefore

    A/A0 = 10^(-TL/20).

For the current reciprocal reference chain, outbound and inbound losses add in dB.
The absorption coefficient is an explicit input rather than a hidden empirical
frequency model. Frequency/environment-dependent absorption models can be added
later with their assumptions and sources documented independently.
"""

from __future__ import annotations

from math import log10

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


class PropagationLossModel(BaseModel):
    """Spherical spreading plus explicitly supplied homogeneous absorption."""

    model_config = ConfigDict(frozen=True)

    absorption_db_per_km: FiniteFloat = Field(default=0.0, ge=0.0)
    spreading_reference_distance_m: FiniteFloat = Field(default=1.0, gt=0.0)


class OneWayTransmissionLoss(BaseModel):
    """One-way propagation loss and equivalent pressure-amplitude ratio."""

    model_config = ConfigDict(frozen=True)

    path_length_m: FiniteFloat = Field(gt=0.0)
    spreading_loss_db: FiniteFloat
    absorption_loss_db: FiniteFloat = Field(ge=0.0)
    total_loss_db: FiniteFloat
    amplitude_ratio: FiniteFloat = Field(gt=0.0)


class ReciprocalTransmissionLoss(BaseModel):
    """Two-way loss for identical outbound and inbound propagation paths."""

    model_config = ConfigDict(frozen=True)

    one_way: OneWayTransmissionLoss
    two_way_total_loss_db: FiniteFloat
    two_way_amplitude_ratio: FiniteFloat = Field(gt=0.0)


def one_way_transmission_loss(
    *,
    path_length_m: float,
    model: PropagationLossModel,
) -> OneWayTransmissionLoss:
    """Evaluate spherical spreading and absorption over one path."""

    distance = float(path_length_m)
    if distance <= 0.0:
        raise ValueError("path_length_m must be positive")

    reference = float(model.spreading_reference_distance_m)
    spreading_db = 20.0 * log10(distance / reference)
    absorption_db = float(model.absorption_db_per_km) * distance / 1000.0
    total_db = spreading_db + absorption_db
    amplitude_ratio = 10.0 ** (-total_db / 20.0)

    return OneWayTransmissionLoss(
        path_length_m=distance,
        spreading_loss_db=spreading_db,
        absorption_loss_db=absorption_db,
        total_loss_db=total_db,
        amplitude_ratio=amplitude_ratio,
    )


def reciprocal_transmission_loss(
    *,
    one_way_path_length_m: float,
    model: PropagationLossModel,
) -> ReciprocalTransmissionLoss:
    """Evaluate the current reciprocal two-way propagation-loss reference."""

    one_way = one_way_transmission_loss(path_length_m=one_way_path_length_m, model=model)
    two_way_db = 2.0 * float(one_way.total_loss_db)
    two_way_amplitude = 10.0 ** (-two_way_db / 20.0)
    return ReciprocalTransmissionLoss(
        one_way=one_way,
        two_way_total_loss_db=two_way_db,
        two_way_amplitude_ratio=two_way_amplitude,
    )

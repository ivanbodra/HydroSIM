"""Explicit bottom-interaction amplitude models for HydroSIM.

This layer deliberately separates two physically different abstractions:

* point-target strength (TS), expressed in dB for a discrete target; and
* seafloor area backscatter, expressed as scattering strength per unit area
  combined with an explicitly supplied insonified area.

No empirical angular backscatter law is hidden here. Incidence angle is retained
as scientific metadata for the seafloor model, while the user/model supplies the
scattering strength applicable at that incidence. Likewise, footprint/ensonified
area is an explicit input and is not inferred from beamwidth or pulse length yet.
"""

from __future__ import annotations

from math import log10, pi

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator


class PointTargetStrength(BaseModel):
    """Discrete point-target strength referenced in the usual dB convention."""

    model_config = ConfigDict(frozen=True)

    target_strength_db: FiniteFloat


class SeafloorAreaBackscatter(BaseModel):
    """Area-scattering description for one insonified seafloor patch.

    ``scattering_strength_db_per_m2`` is the backscatter strength for one square
    metre under the chosen convention/model. The integrated patch strength is

        BS_patch = S_b + 10 log10(A / 1 m^2).

    The incidence angle is measured from the local seafloor normal. It is stored
    explicitly but does not modify S_b automatically in this reference layer.
    """

    model_config = ConfigDict(frozen=True)

    scattering_strength_db_per_m2: FiniteFloat
    insonified_area_m2: FiniteFloat = Field(gt=0.0)
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0, le=pi / 2.0)


class BottomInteractionResponse(BaseModel):
    """Equivalent pressure-amplitude multiplier from one bottom interaction."""

    model_config = ConfigDict(frozen=True)

    interaction_kind: str
    effective_backscatter_strength_db: FiniteFloat
    amplitude_ratio: FiniteFloat = Field(gt=0.0)
    insonified_area_m2: FiniteFloat | None = Field(default=None, gt=0.0)
    incidence_angle_from_normal_rad: FiniteFloat | None = Field(default=None, ge=0.0, le=pi / 2.0)


def evaluate_point_target_strength(model: PointTargetStrength) -> BottomInteractionResponse:
    """Convert point-target TS in dB to a pressure-like amplitude ratio."""

    strength_db = float(model.target_strength_db)
    return BottomInteractionResponse(
        interaction_kind="point_target",
        effective_backscatter_strength_db=strength_db,
        amplitude_ratio=10.0 ** (strength_db / 20.0),
    )


def evaluate_seafloor_area_backscatter(
    model: SeafloorAreaBackscatter,
) -> BottomInteractionResponse:
    """Integrate per-area seafloor scattering strength over an explicit patch."""

    area = float(model.insonified_area_m2)
    if area <= 0.0:
        raise ValueError("insonified_area_m2 must be positive")
    strength_db = float(model.scattering_strength_db_per_m2) + 10.0 * log10(area)
    return BottomInteractionResponse(
        interaction_kind="seafloor_area",
        effective_backscatter_strength_db=strength_db,
        amplitude_ratio=10.0 ** (strength_db / 20.0),
        insonified_area_m2=area,
        incidence_angle_from_normal_rad=model.incidence_angle_from_normal_rad,
    )


BottomInteractionModel = PointTargetStrength | SeafloorAreaBackscatter


def evaluate_bottom_interaction(model: BottomInteractionModel) -> BottomInteractionResponse:
    """Evaluate either supported bottom-interaction abstraction."""

    if isinstance(model, PointTargetStrength):
        return evaluate_point_target_strength(model)
    return evaluate_seafloor_area_backscatter(model)

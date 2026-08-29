"""Explicit bottom-interaction amplitude models for HydroSIM.

This layer deliberately separates two physically different abstractions:

* point-target strength (TS), expressed in dB for a discrete target; and
* seafloor area backscatter, expressed as scattering strength per unit area
  combined with an explicitly defined scattering area.

The area term is not necessarily a hard-edged physical footprint. It may represent
a uniform geometric patch or an equivalent area obtained by integrating a
normalized beam/pulse/matched-filter weighting over the seafloor. ``area_semantics``
records that choice explicitly so a -3 dB contour is never silently treated as the
boundary between insonified and non-insonified bottom.

No empirical angular backscatter law is hidden here. Incidence angle is retained
as scientific metadata while the user/model supplies the scattering strength
applicable at that incidence.
"""

from __future__ import annotations

from math import log10, pi
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat


SeafloorAreaSemantics = Literal[
    "uniform_geometric_patch",
    "equivalent_pattern_weighted",
    "equivalent_pattern_and_pulse_weighted",
    "equivalent_pattern_and_matched_filter_weighted",
]


class PointTargetStrength(BaseModel):
    """Discrete point-target strength referenced in the usual dB convention."""

    model_config = ConfigDict(frozen=True)

    target_strength_db: FiniteFloat


class SeafloorAreaBackscatter(BaseModel):
    """Area-scattering description under an explicit area convention.

    ``scattering_strength_db_per_m2`` is the backscatter strength for one square
    metre under the chosen convention/model. The integrated strength is

        BS = S_b + 10 log10(A_equiv / 1 m^2).

    For ``uniform_geometric_patch``, ``insonified_area_m2`` is a literal uniform
    patch area. For any ``equivalent_*`` semantic it is the area which, if
    illuminated at the reference/peak weighting, gives the same integrated power
    as the distributed weighting specified by ``area_semantics``.

    The legacy field name ``insonified_area_m2`` is retained for API continuity;
    ``area_semantics`` is normative for interpretation.
    """

    model_config = ConfigDict(frozen=True)

    scattering_strength_db_per_m2: FiniteFloat
    insonified_area_m2: FiniteFloat = Field(gt=0.0)
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0, le=pi / 2.0)
    area_semantics: SeafloorAreaSemantics = "uniform_geometric_patch"


class BottomInteractionResponse(BaseModel):
    """Equivalent pressure-amplitude multiplier from one bottom interaction."""

    model_config = ConfigDict(frozen=True)

    interaction_kind: str
    effective_backscatter_strength_db: FiniteFloat
    amplitude_ratio: FiniteFloat = Field(gt=0.0)
    insonified_area_m2: FiniteFloat | None = Field(default=None, gt=0.0)
    area_semantics: SeafloorAreaSemantics | None = None
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
    """Integrate per-area scattering strength over the explicitly defined area."""

    area = float(model.insonified_area_m2)
    if area <= 0.0:
        raise ValueError("insonified_area_m2 must be positive")
    strength_db = float(model.scattering_strength_db_per_m2) + 10.0 * log10(area)
    return BottomInteractionResponse(
        interaction_kind="seafloor_area",
        effective_backscatter_strength_db=strength_db,
        amplitude_ratio=10.0 ** (strength_db / 20.0),
        insonified_area_m2=area,
        area_semantics=model.area_semantics,
        incidence_angle_from_normal_rad=model.incidence_angle_from_normal_rad,
    )


BottomInteractionModel = PointTargetStrength | SeafloorAreaBackscatter


def evaluate_bottom_interaction(model: BottomInteractionModel) -> BottomInteractionResponse:
    """Evaluate either supported bottom-interaction abstraction."""

    if isinstance(model, PointTargetStrength):
        return evaluate_point_target_strength(model)
    return evaluate_seafloor_area_backscatter(model)

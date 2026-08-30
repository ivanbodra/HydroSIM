"""Controlled family of processing-SVP errors for flat-bottom swath diagnostics.

Profile cases are explicit experiment coordinates. HydroSIM does not infer that a
synthetic case represents a particular oceanographic regime. Each case carries the
complete processing profile used by the reconstruction so the experiment remains
reproducible and traceable.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_svp_swath_curvature import LayeredSvpSwathCurvature, run_layered_svp_swath_curvature


SvpErrorClassification = Literal[
    "reference",
    "uniform_offset",
    "layer_speed_perturbation",
    "interface_displacement",
    "synthetic_profile",
]


class ControlledProcessingSvpCase(BaseModel):
    """One explicit processing-profile coordinate in a controlled experiment."""

    model_config = ConfigDict(frozen=True)

    case_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    classification: SvpErrorClassification
    processing_profile: LayeredSoundSpeedProfile


class LayeredSvpErrorFamilyCaseResult(BaseModel):
    """Swath-curvature response associated with one explicit processing profile."""

    model_config = ConfigDict(frozen=True)

    case_id: str
    description: str
    classification: SvpErrorClassification
    swath_curvature: LayeredSvpSwathCurvature


class LayeredSvpErrorFamilyResponse(BaseModel):
    """Deterministically ordered response for a family of processing-SVP cases."""

    model_config = ConfigDict(frozen=True)

    case_ids: tuple[str, ...]
    cases: tuple[LayeredSvpErrorFamilyCaseResult, ...]


def run_layered_svp_error_family(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    processing_profile_cases: Iterable[ControlledProcessingSvpCase],
    profile_start_depth_m: float,
) -> LayeredSvpErrorFamilyResponse:
    """Evaluate a reproducible family of processing profiles against one Truth SVP.

    Case order is preserved exactly as supplied. Case IDs must be unique. The same
    angle axis, Truth profile, geometry, and profile start depth are used for every
    member so differences between responses are attributable to the explicit
    processing-profile coordinate.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    cases = tuple(processing_profile_cases)
    if not cases:
        raise ValueError("processing_profile_cases must not be empty")

    case_ids = tuple(case.case_id for case in cases)
    if len(set(case_ids)) != len(case_ids):
        raise ValueError("processing_profile_cases must have unique case_id values")

    results = []
    for case in cases:
        swath = run_layered_svp_swath_curvature(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angles_rad=angles,
            true_profile=true_profile,
            processing_profile=case.processing_profile,
            profile_start_depth_m=profile_start_depth_m,
        )
        results.append(
            LayeredSvpErrorFamilyCaseResult(
                case_id=case.case_id,
                description=case.description,
                classification=case.classification,
                swath_curvature=swath,
            )
        )

    return LayeredSvpErrorFamilyResponse(case_ids=case_ids, cases=tuple(results))

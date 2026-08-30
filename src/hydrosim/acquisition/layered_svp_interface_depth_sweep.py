"""Controlled sweep of one processing-SVP interface depth.

The Truth profile remains fixed. For each requested interface depth, HydroSIM creates
one processing profile by moving exactly one existing horizontal interface while
preserving the adjacent layer sound speeds and all other interfaces. The resulting
flat-bottom swath curvature is then evaluated with the existing profile-only
reference experiment.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile, SoundSpeedLayer
from .layered_svp_swath_curvature import LayeredSvpSwathCurvature, run_layered_svp_swath_curvature


class LayeredSvpInterfaceDepthSweepPoint(BaseModel):
    """One processing-interface coordinate and its reconstructed swath response."""

    model_config = ConfigDict(frozen=True)

    interface_depth_m: FiniteFloat = Field(gt=0.0)
    interface_depth_error_m: FiniteFloat
    mean_edge_minus_nadir_vertical_error_m: FiniteFloat
    swath_curvature: LayeredSvpSwathCurvature


class LayeredSvpInterfaceDepthSweep(BaseModel):
    """Deterministic response to moving one processing-profile interface."""

    model_config = ConfigDict(frozen=True)

    interface_index: int = Field(ge=0)
    truth_interface_depth_m: FiniteFloat = Field(gt=0.0)
    interface_depths_m: tuple[FiniteFloat, ...]
    points: tuple[LayeredSvpInterfaceDepthSweepPoint, ...]


def move_layered_profile_interface(
    *,
    profile: LayeredSoundSpeedProfile,
    interface_index: int,
    interface_depth_m: float,
) -> LayeredSoundSpeedProfile:
    """Return a profile with one interior interface moved and speeds unchanged.

    `interface_index` identifies the boundary after `layers[interface_index]` and
    before `layers[interface_index + 1]`. The new boundary must remain strictly
    inside the combined vertical extent of those two layers so neither becomes
    zero-thickness or inverted.
    """

    index = int(interface_index)
    if index < 0 or index >= len(profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    depth = float(interface_depth_m)
    upper = profile.layers[index]
    lower = profile.layers[index + 1]
    lower_bound = float(upper.top_depth_m)
    upper_bound = float(lower.bottom_depth_m)
    if not lower_bound < depth < upper_bound:
        raise ValueError("interface_depth_m must stay within the adjacent-layer extent")

    layers = list(profile.layers)
    layers[index] = SoundSpeedLayer(
        top_depth_m=upper.top_depth_m,
        bottom_depth_m=depth,
        sound_speed_mps=upper.sound_speed_mps,
    )
    layers[index + 1] = SoundSpeedLayer(
        top_depth_m=depth,
        bottom_depth_m=lower.bottom_depth_m,
        sound_speed_mps=lower.sound_speed_mps,
    )
    return LayeredSoundSpeedProfile(
        layers=tuple(layers),
        continuity_tolerance_m=profile.continuity_tolerance_m,
    )


def run_layered_svp_interface_depth_sweep(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    processing_interface_depths_m: Iterable[float],
    profile_start_depth_m: float,
) -> LayeredSvpInterfaceDepthSweep:
    """Sweep one processing-interface depth against a fixed Truth profile."""

    index = int(interface_index)
    if index < 0 or index >= len(true_profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    depths = tuple(float(value) for value in processing_interface_depths_m)
    if not depths:
        raise ValueError("processing_interface_depths_m must not be empty")
    angles = tuple(float(value) for value in configured_across_track_angles_rad)

    truth_depth = float(true_profile.layers[index].bottom_depth_m)
    points = []
    for depth in depths:
        processing_profile = move_layered_profile_interface(
            profile=true_profile,
            interface_index=index,
            interface_depth_m=depth,
        )
        swath = run_layered_svp_swath_curvature(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angles_rad=angles,
            true_profile=true_profile,
            processing_profile=processing_profile,
            profile_start_depth_m=profile_start_depth_m,
        )
        points.append(
            LayeredSvpInterfaceDepthSweepPoint(
                interface_depth_m=depth,
                interface_depth_error_m=depth - truth_depth,
                mean_edge_minus_nadir_vertical_error_m=(
                    swath.mean_edge_minus_nadir_vertical_error_m
                ),
                swath_curvature=swath,
            )
        )

    return LayeredSvpInterfaceDepthSweep(
        interface_index=index,
        truth_interface_depth_m=truth_depth,
        interface_depths_m=depths,
        points=tuple(points),
    )

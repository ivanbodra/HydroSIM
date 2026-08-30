"""Controlled 2-D map of processing-SVP interface depth and sound-speed contrast.

The Truth profile remains fixed. For each requested processing interface depth and
adjacent-layer sound-speed contrast, HydroSIM moves one interior interface and then
sets the lower adjacent layer speed relative to the unchanged upper-layer speed.
All unrelated layers remain unchanged. Flat-bottom swath curvature is evaluated with
the existing profile-only reference experiment.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile, SoundSpeedLayer
from .layered_svp_interface_depth_sweep import move_layered_profile_interface
from .layered_svp_swath_curvature import LayeredSvpSwathCurvature, run_layered_svp_swath_curvature


class LayeredSvpInterfaceContrastMapPoint(BaseModel):
    """One interface-depth/contrast coordinate and its swath response."""

    model_config = ConfigDict(frozen=True)

    interface_depth_m: FiniteFloat = Field(gt=0.0)
    interface_depth_error_m: FiniteFloat
    sound_speed_contrast_mps: FiniteFloat
    sound_speed_contrast_error_mps: FiniteFloat
    mean_edge_minus_nadir_vertical_error_m: FiniteFloat
    swath_curvature: LayeredSvpSwathCurvature


class LayeredSvpInterfaceContrastMap(BaseModel):
    """Deterministic 2-D response over interface depth and adjacent-layer contrast."""

    model_config = ConfigDict(frozen=True)

    interface_index: int = Field(ge=0)
    truth_interface_depth_m: FiniteFloat = Field(gt=0.0)
    truth_sound_speed_contrast_mps: FiniteFloat
    interface_depths_m: tuple[FiniteFloat, ...]
    sound_speed_contrasts_mps: tuple[FiniteFloat, ...]
    points: tuple[LayeredSvpInterfaceContrastMapPoint, ...]


def set_layered_profile_interface_contrast(
    *,
    profile: LayeredSoundSpeedProfile,
    interface_index: int,
    sound_speed_contrast_mps: float,
) -> LayeredSoundSpeedProfile:
    """Set lower-minus-upper sound-speed contrast at one interior interface.

    The upper adjacent layer speed is retained. The lower adjacent layer speed is
    replaced by c_lower = c_upper + contrast. Layer geometry and all unrelated layers
    are preserved. The resulting lower-layer speed must remain strictly positive.
    """

    index = int(interface_index)
    if index < 0 or index >= len(profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    upper = profile.layers[index]
    lower = profile.layers[index + 1]
    lower_speed = float(upper.sound_speed_mps) + float(sound_speed_contrast_mps)
    if lower_speed <= 0.0:
        raise ValueError("sound_speed_contrast_mps produces a non-positive lower-layer speed")

    layers = list(profile.layers)
    layers[index + 1] = SoundSpeedLayer(
        top_depth_m=lower.top_depth_m,
        bottom_depth_m=lower.bottom_depth_m,
        sound_speed_mps=lower_speed,
    )
    return LayeredSoundSpeedProfile(
        layers=tuple(layers),
        continuity_tolerance_m=profile.continuity_tolerance_m,
    )


def run_layered_svp_interface_contrast_map(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    interface_index: int,
    processing_interface_depths_m: Iterable[float],
    processing_sound_speed_contrasts_mps: Iterable[float],
    profile_start_depth_m: float,
) -> LayeredSvpInterfaceContrastMap:
    """Map swath curvature over processing interface depth and layer contrast.

    Point order is deterministic: interface depth outer, sound-speed contrast inner.
    The contrast coordinate is defined as lower adjacent layer speed minus upper
    adjacent layer speed at the selected processing interface.
    """

    index = int(interface_index)
    if index < 0 or index >= len(true_profile.layers) - 1:
        raise ValueError("interface_index must identify an interior layer boundary")

    depths = tuple(float(value) for value in processing_interface_depths_m)
    contrasts = tuple(float(value) for value in processing_sound_speed_contrasts_mps)
    if not depths:
        raise ValueError("processing_interface_depths_m must not be empty")
    if not contrasts:
        raise ValueError("processing_sound_speed_contrasts_mps must not be empty")
    angles = tuple(float(value) for value in configured_across_track_angles_rad)

    truth_upper = true_profile.layers[index]
    truth_lower = true_profile.layers[index + 1]
    truth_depth = float(truth_upper.bottom_depth_m)
    truth_contrast = float(truth_lower.sound_speed_mps) - float(truth_upper.sound_speed_mps)

    points = []
    for depth in depths:
        moved_profile = move_layered_profile_interface(
            profile=true_profile,
            interface_index=index,
            interface_depth_m=depth,
        )
        for contrast in contrasts:
            processing_profile = set_layered_profile_interface_contrast(
                profile=moved_profile,
                interface_index=index,
                sound_speed_contrast_mps=contrast,
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
                LayeredSvpInterfaceContrastMapPoint(
                    interface_depth_m=depth,
                    interface_depth_error_m=depth - truth_depth,
                    sound_speed_contrast_mps=contrast,
                    sound_speed_contrast_error_mps=contrast - truth_contrast,
                    mean_edge_minus_nadir_vertical_error_m=(
                        swath.mean_edge_minus_nadir_vertical_error_m
                    ),
                    swath_curvature=swath,
                )
            )

    return LayeredSvpInterfaceContrastMap(
        interface_index=index,
        truth_interface_depth_m=truth_depth,
        truth_sound_speed_contrast_mps=truth_contrast,
        interface_depths_m=depths,
        sound_speed_contrasts_mps=contrasts,
        points=tuple(points),
    )

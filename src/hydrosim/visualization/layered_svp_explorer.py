"""Prepare a didactic layered-SVP sounding experiment for visualization.

This module composes existing HydroSIM scientific models; it does not introduce
new acoustic physics. It exposes the Truth ray, detected two-way travel time,
reconstructed sounding, and calculated-minus-Truth error for each configured
across-track beam so a UI can show the complete causal chain in one view.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.acquisition import (
    LayeredRayPath,
    LayeredSoundSpeedProfile,
    run_layered_sound_speed_reference_experiment,
)
from hydrosim.geometry import FlatTerrain, Pose, Vector3


class LayeredSvpExplorerBeam(BaseModel):
    """Visualization-ready state for one beam in the didactic SVP experiment."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    truth_ray_path: LayeredRayPath
    truth_bottom_point: Vector3
    true_twtt_seconds: FiniteFloat = Field(gt=0.0)
    reconstructed_bottom_point: Vector3
    across_track_error_m: FiniteFloat
    vertical_error_m: FiniteFloat
    sounding_error_norm_m: FiniteFloat = Field(ge=0.0)


class LayeredSvpExplorerSnapshot(BaseModel):
    """One complete, render-ready snapshot of the controlled SVP experiment."""

    model_config = ConfigDict(frozen=True)

    sensor_pose: Pose
    terrain_depth_m: FiniteFloat
    profile_start_depth_m: FiniteFloat = Field(ge=0.0)
    true_profile: LayeredSoundSpeedProfile
    processing_profile: LayeredSoundSpeedProfile
    beams: tuple[LayeredSvpExplorerBeam, ...]
    experiment_scope: str = (
        "stationary_monostatic_reciprocal_principal_plane_flat_bottom_"
        "ideal_transducer_sound_speed_zero_array_tilt"
    )


def prepare_layered_svp_explorer_snapshot(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSvpExplorerSnapshot:
    """Compose existing Truth/processing models into one didactic snapshot.

    The beam order supplied by the caller is preserved. The transducer sound-speed
    measurement is ideal and array tilt is fixed at zero so this first integrated
    view isolates only the difference between Truth and processing SVPs. Those
    constraints are intentional application choices, not new scientific models.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")

    beams = []
    for angle in angles:
        result = run_layered_sound_speed_reference_experiment(
            sensor_pose=sensor_pose,
            terrain=terrain,
            configured_across_track_angle_rad=angle,
            true_profile=true_profile,
            processing_profile=processing_profile,
            profile_start_depth_m=profile_start_depth_m,
            principal_plane_array_tilt_rad=0.0,
        )
        error = result.sounding_error
        beams.append(
            LayeredSvpExplorerBeam(
                configured_across_track_angle_rad=angle,
                truth_ray_path=result.true_ray_path,
                truth_bottom_point=result.truth_bottom_point,
                true_twtt_seconds=result.true_twtt_seconds,
                reconstructed_bottom_point=result.calculated_sounding.sounding.point,
                across_track_error_m=error.y,
                vertical_error_m=error.z,
                sounding_error_norm_m=result.sounding_error_norm_m,
            )
        )

    return LayeredSvpExplorerSnapshot(
        sensor_pose=sensor_pose,
        terrain_depth_m=terrain.depth,
        profile_start_depth_m=profile_start_depth_m,
        true_profile=true_profile,
        processing_profile=processing_profile,
        beams=tuple(beams),
    )

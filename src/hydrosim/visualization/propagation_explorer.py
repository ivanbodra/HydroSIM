"""Composition state for the first HydroSIM Propagation Explorer lesson.

This module introduces no new propagation physics. It builds a controlled
layered-SVP experiment from the existing piecewise-constant ray tracer and the
existing Truth-versus-processing sounding reconstruction experiment.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3

from .layered_svp_explorer import (
    LayeredSvpExplorerSnapshot,
    prepare_layered_svp_explorer_snapshot,
)


PROCESSING_SVP_SUPPORT_DEPTH_M = 11_000.0


@dataclass(frozen=True)
class PropagationExplorerControls:
    """Small control state for the first SVP/refraction lesson."""

    processing_lower_layer_bias_mps: float = 0.0
    terrain_depth_m: float = 60.0
    interface_depth_m: float = 20.0
    upper_layer_sound_speed_mps: float = 1500.0
    lower_layer_sound_speed_mps: float = 1480.0
    maximum_beam_angle_deg: float = 60.0
    beam_count: int = 9

    def validate(self) -> None:
        if self.terrain_depth_m <= 0.0:
            raise ValueError("terrain_depth_m must be positive")
        if not 0.0 < self.interface_depth_m < self.terrain_depth_m:
            raise ValueError("interface_depth_m must lie inside the water column")
        if self.upper_layer_sound_speed_mps <= 0.0 or self.lower_layer_sound_speed_mps <= 0.0:
            raise ValueError("sound speeds must be positive")
        if self.lower_layer_sound_speed_mps + self.processing_lower_layer_bias_mps <= 0.0:
            raise ValueError("biased processing sound speed must be positive")
        if not 0.0 < self.maximum_beam_angle_deg < 80.0:
            raise ValueError("maximum_beam_angle_deg must lie between 0 and 80 degrees")
        if self.beam_count < 3 or self.beam_count % 2 == 0:
            raise ValueError("beam_count must be an odd integer >= 3")


def _profile(
    *,
    controls: PropagationExplorerControls,
    lower_speed_mps: float,
    bottom_depth_m: float,
) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(
                top_depth_m=0.0,
                bottom_depth_m=controls.interface_depth_m,
                sound_speed_mps=controls.upper_layer_sound_speed_mps,
            ),
            SoundSpeedLayer(
                top_depth_m=controls.interface_depth_m,
                bottom_depth_m=bottom_depth_m,
                sound_speed_mps=lower_speed_mps,
            ),
        )
    )


def prepare_propagation_explorer_snapshot(
    controls: PropagationExplorerControls | None = None,
) -> LayeredSvpExplorerSnapshot:
    """Build the first guided Propagation Explorer snapshot.

    Truth is fixed to a two-layer water column. The learner changes only the
    lower-layer sound speed used in processing, so the visualization isolates a
    processing-SVP mismatch while the physical Truth rays remain unchanged.

    The synthetic Processing SVP is explicitly extended to 11,000 m with the
    deepest configured sound speed held constant. This is Configured processing
    support, not Truth or an additional observed profile measurement.
    """

    state = controls or PropagationExplorerControls()
    state.validate()

    truth_profile = _profile(
        controls=state,
        lower_speed_mps=state.lower_layer_sound_speed_mps,
        bottom_depth_m=state.terrain_depth_m,
    )
    processing_profile = _profile(
        controls=state,
        lower_speed_mps=state.lower_layer_sound_speed_mps
        + state.processing_lower_layer_bias_mps,
        bottom_depth_m=max(state.terrain_depth_m, PROCESSING_SVP_SUPPORT_DEPTH_M),
    )

    step = 2.0 * state.maximum_beam_angle_deg / (state.beam_count - 1)
    angles = tuple(
        radians(-state.maximum_beam_angle_deg + index * step)
        for index in range(state.beam_count)
    )

    return prepare_layered_svp_explorer_snapshot(
        sensor_pose=Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            frame="N",
        ),
        terrain=FlatTerrain(depth=state.terrain_depth_m),
        configured_across_track_angles_rad=angles,
        true_profile=truth_profile,
        processing_profile=processing_profile,
        profile_start_depth_m=0.0,
    )

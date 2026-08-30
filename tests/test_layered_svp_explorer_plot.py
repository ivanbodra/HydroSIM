from math import radians

import pytest

from hydrosim.acquisition import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.geometry import Attitude, FlatTerrain, Pose, Vector3
from hydrosim.visualization import (
    plot_layered_svp_explorer_snapshot,
    prepare_layered_svp_explorer_snapshot,
)

pytest.importorskip("matplotlib")


def _profile(c1: float, c2: float) -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=40.0, sound_speed_mps=c1),
            SoundSpeedLayer(top_depth_m=40.0, bottom_depth_m=200.0, sound_speed_mps=c2),
        )
    )


def test_renderer_builds_three_didactic_panels() -> None:
    snapshot = prepare_layered_svp_explorer_snapshot(
        sensor_pose=Pose(
            position=Vector3(x=0.0, y=0.0, z=0.0),
            attitude=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
            frame="N",
        ),
        terrain=FlatTerrain(depth=120.0),
        configured_across_track_angles_rad=tuple(radians(v) for v in (-60, -30, 0, 30, 60)),
        true_profile=_profile(1500.0, 1540.0),
        processing_profile=_profile(1500.0, 1490.0),
        profile_start_depth_m=0.0,
    )

    figure, axes = plot_layered_svp_explorer_snapshot(snapshot)
    try:
        assert len(axes) == 3
        assert axes[0].get_title() == "Sound-speed profiles"
        assert axes[1].get_title() == "Truth rays and reconstructed swath"
        assert axes[2].get_title() == "Beamwise sounding error"
        assert len(axes[2].lines) == 3  # zero reference + two error series
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)

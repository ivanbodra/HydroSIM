import pytest

from hydrosim.acquisition.layered_propagation import LayeredSoundSpeedProfile, SoundSpeedLayer
from hydrosim.acquisition.sound_speed_processing import use_manual_sound_speed_at_transducer
from hydrosim.acquisition.sound_speed_profile_boundary import (
    profile_boundary_from_profile,
    profile_boundary_from_sound_speed_at_transducer,
)


def _profile() -> LayeredSoundSpeedProfile:
    return LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=20.0, sound_speed_mps=1490.0),
            SoundSpeedLayer(top_depth_m=20.0, bottom_depth_m=100.0, sound_speed_mps=1510.0),
        )
    )


def test_profile_boundary_can_come_from_processing_profile() -> None:
    boundary = profile_boundary_from_profile(profile=_profile(), depth_m=0.0)
    assert boundary.sound_speed_mps == pytest.approx(1490.0)
    assert boundary.source == "processing_profile"


def test_transducer_boundary_does_not_modify_finite_thickness_profile_layer() -> None:
    profile = _profile()
    used = use_manual_sound_speed_at_transducer(1502.0)
    boundary = profile_boundary_from_sound_speed_at_transducer(
        sound_speed_at_transducer=used,
        depth_m=0.0,
    )
    assert boundary.sound_speed_mps == pytest.approx(1502.0)
    assert boundary.source == "sound_speed_at_transducer"
    assert profile.layer_at_depth(0.0).sound_speed_mps == pytest.approx(1490.0)
    assert profile.layer_at_depth(10.0).sound_speed_mps == pytest.approx(1490.0)

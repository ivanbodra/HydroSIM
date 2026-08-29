from math import radians, sin

import pytest

from hydrosim.acquisition import (
    SurfaceSoundSpeedSteering,
    ideal_receive_steering,
    resolve_surface_sound_speed_steering,
)
from hydrosim.geometry import Attitude, TransducerArray


def _receive_array() -> TransducerArray:
    return TransducerArray(
        name="rx_sss",
        role="rx",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.01,
        element_longitudinal_size=0.005,
        element_transverse_size=0.005,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def test_equal_surface_sound_speeds_preserve_configured_angle() -> None:
    angle = radians(35.0)
    result = resolve_surface_sound_speed_steering(
        configured_angle_rad=angle,
        configured_sound_speed_mps=1500.0,
        physical_surface_sound_speed_mps=1500.0,
    )

    assert isinstance(result, SurfaceSoundSpeedSteering)
    assert result.physical_angle_rad == pytest.approx(angle)
    assert result.angle_error_rad == pytest.approx(0.0)
    assert result.imposed_slowness_seconds_per_m == pytest.approx(sin(angle) / 1500.0)


def test_higher_physical_surface_speed_increases_off_normal_physical_angle() -> None:
    configured_angle = radians(40.0)
    result = resolve_surface_sound_speed_steering(
        configured_angle_rad=configured_angle,
        configured_sound_speed_mps=1480.0,
        physical_surface_sound_speed_mps=1520.0,
    )

    assert result.physical_angle_rad > configured_angle
    assert sin(result.physical_angle_rad) / 1520.0 == pytest.approx(
        sin(configured_angle) / 1480.0
    )


def test_surface_sound_speed_model_preserves_signed_steering_convention() -> None:
    result = resolve_surface_sound_speed_steering(
        configured_angle_rad=radians(-30.0),
        configured_sound_speed_mps=1500.0,
        physical_surface_sound_speed_mps=1470.0,
    )

    assert result.physical_angle_rad < 0.0
    assert abs(result.physical_angle_rad) < radians(30.0)


def test_receive_delay_law_uses_configured_sss_while_physical_angle_uses_actual_sss() -> None:
    configured_angle = radians(45.0)
    configured_c = 1480.0
    physical_c = 1520.0

    hypothesis = ideal_receive_steering(
        receive_array=_receive_array(),
        across_track_angle_rad=configured_angle,
        sound_speed_mps=configured_c,
    )
    surface = resolve_surface_sound_speed_steering(
        configured_angle_rad=configured_angle,
        configured_sound_speed_mps=configured_c,
        physical_surface_sound_speed_mps=physical_c,
    )

    assert hypothesis.sound_speed_mps == pytest.approx(configured_c)
    assert surface.imposed_slowness_seconds_per_m == pytest.approx(
        sin(configured_angle) / configured_c
    )
    assert sin(surface.physical_angle_rad) / physical_c == pytest.approx(
        surface.imposed_slowness_seconds_per_m
    )


def test_nonpropagating_surface_steering_law_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-propagating"):
        resolve_surface_sound_speed_steering(
            configured_angle_rad=radians(80.0),
            configured_sound_speed_mps=1400.0,
            physical_surface_sound_speed_mps=1600.0,
        )

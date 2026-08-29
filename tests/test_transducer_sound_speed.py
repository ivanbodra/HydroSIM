from math import radians, sin

import pytest

from hydrosim.acquisition import (
    TransducerSoundSpeedDirection,
    TransducerSoundSpeedSteering,
    ideal_receive_steering,
    resolve_transducer_sound_speed_direction,
    resolve_transducer_sound_speed_steering,
    sensor_angular_direction,
)
from hydrosim.geometry import Attitude, TransducerArray


def _receive_array() -> TransducerArray:
    return TransducerArray(
        name="rx_transducer_sound_speed",
        role="rx",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.01,
        element_longitudinal_size=0.005,
        element_transverse_size=0.005,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def test_equal_transducer_sound_speeds_preserve_configured_angle() -> None:
    angle = radians(35.0)
    result = resolve_transducer_sound_speed_steering(
        configured_angle_rad=angle,
        configured_sound_speed_mps=1500.0,
        physical_sound_speed_at_transducer_mps=1500.0,
    )

    assert isinstance(result, TransducerSoundSpeedSteering)
    assert result.physical_angle_rad == pytest.approx(angle)
    assert result.angle_error_rad == pytest.approx(0.0)
    assert result.imposed_tangential_slowness_seconds_per_m == pytest.approx(sin(angle) / 1500.0)


def test_higher_physical_transducer_speed_increases_off_normal_physical_angle() -> None:
    configured_angle = radians(40.0)
    result = resolve_transducer_sound_speed_steering(
        configured_angle_rad=configured_angle,
        configured_sound_speed_mps=1480.0,
        physical_sound_speed_at_transducer_mps=1520.0,
    )

    assert result.physical_angle_rad > configured_angle
    assert sin(result.physical_angle_rad) / 1520.0 == pytest.approx(
        sin(configured_angle) / 1480.0
    )


def test_transducer_sound_speed_model_preserves_signed_steering_convention() -> None:
    result = resolve_transducer_sound_speed_steering(
        configured_angle_rad=radians(-30.0),
        configured_sound_speed_mps=1500.0,
        physical_sound_speed_at_transducer_mps=1470.0,
    )

    assert result.physical_angle_rad < 0.0
    assert abs(result.physical_angle_rad) < radians(30.0)


def test_receive_delay_law_uses_configured_transducer_sound_speed() -> None:
    configured_angle = radians(45.0)
    configured_c = 1480.0
    physical_c = 1520.0

    hypothesis = ideal_receive_steering(
        receive_array=_receive_array(),
        across_track_angle_rad=configured_angle,
        sound_speed_mps=configured_c,
    )
    resolved = resolve_transducer_sound_speed_steering(
        configured_angle_rad=configured_angle,
        configured_sound_speed_mps=configured_c,
        physical_sound_speed_at_transducer_mps=physical_c,
    )

    assert hypothesis.sound_speed_mps == pytest.approx(configured_c)
    assert resolved.imposed_tangential_slowness_seconds_per_m == pytest.approx(
        sin(configured_angle) / configured_c
    )
    assert sin(resolved.physical_angle_rad) / physical_c == pytest.approx(
        resolved.imposed_tangential_slowness_seconds_per_m
    )


def test_full_3d_direction_scales_tangential_slowness_without_separate_angle_corrections() -> None:
    configured = sensor_angular_direction(radians(20.0), radians(35.0))
    configured_c = 1480.0
    physical_c = 1520.0

    result = resolve_transducer_sound_speed_direction(
        configured_direction_array_frame=configured,
        configured_sound_speed_mps=configured_c,
        physical_sound_speed_at_transducer_mps=physical_c,
    )

    assert isinstance(result, TransducerSoundSpeedDirection)
    physical = result.physical_direction_array_frame
    assert physical.x / physical_c == pytest.approx(configured.x / configured_c)
    assert physical.y / physical_c == pytest.approx(configured.y / configured_c)
    assert physical.z > 0.0
    assert physical.x * physical.x + physical.y * physical.y + physical.z * physical.z == pytest.approx(1.0)


def test_equal_transducer_sound_speed_preserves_full_3d_direction() -> None:
    configured = sensor_angular_direction(radians(15.0), radians(-25.0))
    result = resolve_transducer_sound_speed_direction(
        configured_direction_array_frame=configured,
        configured_sound_speed_mps=1500.0,
        physical_sound_speed_at_transducer_mps=1500.0,
    )

    assert result.physical_direction_array_frame.is_close(configured, atol=1e-12)


def test_nonpropagating_transducer_steering_law_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-propagating"):
        resolve_transducer_sound_speed_steering(
            configured_angle_rad=radians(80.0),
            configured_sound_speed_mps=1400.0,
            physical_sound_speed_at_transducer_mps=1600.0,
        )

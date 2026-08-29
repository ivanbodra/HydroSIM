from math import radians, sin

import pytest

from hydrosim.acquisition.sound_speed_at_transducer import (
    PrincipalPlaneReceiveAngleEstimate,
    PrincipalPlaneSteeringTruthComparison,
    SteeringTruthComparison,
    compare_principal_plane_steering_with_truth,
    compare_steering_direction_with_truth,
    estimate_principal_plane_receive_angle,
)
from hydrosim.acquisition.angular_pattern_2d import sensor_angular_direction


def test_equal_sonar_and_true_sound_speed_preserve_angle() -> None:
    angle = radians(35.0)
    result = compare_principal_plane_steering_with_truth(
        configured_angle_rad=angle,
        sound_speed_used_by_sonar_mps=1500.0,
        true_local_sound_speed_mps=1500.0,
    )
    assert isinstance(result, PrincipalPlaneSteeringTruthComparison)
    assert result.physical_angle_rad == pytest.approx(angle)
    assert result.angle_error_rad == pytest.approx(0.0)


def test_erroneous_sonar_sound_speed_changes_physical_angle_in_truth() -> None:
    configured_angle = radians(40.0)
    result = compare_principal_plane_steering_with_truth(
        configured_angle_rad=configured_angle,
        sound_speed_used_by_sonar_mps=1480.0,
        true_local_sound_speed_mps=1520.0,
    )
    assert result.physical_angle_rad > configured_angle
    assert sin(result.physical_angle_rad) / 1520.0 == pytest.approx(sin(configured_angle) / 1480.0)


def test_receive_estimate_uses_true_wavefront_but_sonar_sound_speed_mapping() -> None:
    result = estimate_principal_plane_receive_angle(
        physical_arrival_angle_rad=radians(40.0),
        true_local_sound_speed_mps=1520.0,
        sound_speed_used_by_sonar_mps=1480.0,
    )
    assert isinstance(result, PrincipalPlaneReceiveAngleEstimate)
    assert sin(result.estimated_angle_rad) / 1480.0 == pytest.approx(sin(radians(40.0)) / 1520.0)
    assert result.estimated_angle_rad < radians(40.0)


def test_same_sound_speed_error_in_tx_and_rx_recovers_configured_angle_in_homogeneous_reference() -> None:
    configured = radians(35.0)
    tx = compare_principal_plane_steering_with_truth(
        configured_angle_rad=configured,
        sound_speed_used_by_sonar_mps=1480.0,
        true_local_sound_speed_mps=1520.0,
    )
    rx = estimate_principal_plane_receive_angle(
        physical_arrival_angle_rad=tx.physical_angle_rad,
        true_local_sound_speed_mps=1520.0,
        sound_speed_used_by_sonar_mps=1480.0,
    )
    assert rx.estimated_angle_rad == pytest.approx(configured)


def test_full_3d_truth_direction_preserves_imposed_tangential_slowness() -> None:
    configured = sensor_angular_direction(radians(20.0), radians(35.0))
    result = compare_steering_direction_with_truth(
        configured_direction_array_frame=configured,
        sound_speed_used_by_sonar_mps=1480.0,
        true_local_sound_speed_mps=1520.0,
    )
    assert isinstance(result, SteeringTruthComparison)
    physical = result.physical_direction_array_frame
    assert physical.x / 1520.0 == pytest.approx(configured.x / 1480.0)
    assert physical.y / 1520.0 == pytest.approx(configured.y / 1480.0)
    assert physical.x * physical.x + physical.y * physical.y + physical.z * physical.z == pytest.approx(1.0)


def test_nonpropagating_truth_state_is_rejected() -> None:
    with pytest.raises(ValueError, match="non-propagating"):
        compare_principal_plane_steering_with_truth(
            configured_angle_rad=radians(80.0),
            sound_speed_used_by_sonar_mps=1400.0,
            true_local_sound_speed_mps=1600.0,
        )

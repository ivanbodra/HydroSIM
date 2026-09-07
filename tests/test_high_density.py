from math import radians

import pytest

from hydrosim.acquisition.high_density import (
    detect_high_density_from_phase,
    invert_split_aperture_phase_angle,
    phase_for_split_aperture_angle,
)
from hydrosim.geometry import Vector3


FREQUENCY_HZ = 200_000.0
SOUND_SPEED_MPS = 1500.0
BASELINE = Vector3(x=0.0, y=0.01, z=0.0)


def test_high_density_phase_forward_inverse_closure_preserves_port_sign() -> None:
    target = radians(12.0)
    phase = phase_for_split_aperture_angle(
        target,
        steering_angle_rad=0.0,
        baseline_m=BASELINE,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )
    recovered = invert_split_aperture_phase_angle(
        phase,
        steering_angle_rad=0.0,
        support_min_angle_rad=radians(-30.0),
        support_max_angle_rad=radians(30.0),
        baseline_m=BASELINE,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )

    assert recovered is not None
    assert recovered == pytest.approx(target, abs=1e-10)
    assert recovered > 0.0


def test_high_density_retains_multiple_phase_points_from_one_phase_trajectory() -> None:
    angles = tuple(radians(value) for value in (-10.0, -5.0, 0.0, 5.0, 10.0))
    phases = tuple(
        phase_for_split_aperture_angle(
            angle,
            steering_angle_rad=0.0,
            baseline_m=BASELINE,
            frequency_hz=FREQUENCY_HZ,
            sound_speed_mps=SOUND_SPEED_MPS,
        )
        for angle in angles
    )
    result = detect_high_density_from_phase(
        high_density_enabled=True,
        sample_times_seconds=(0.100, 0.1005, 0.101, 0.1015, 0.102),
        differential_phase_rad=phases,
        support_magnitude=(1.0, 1.0, 1.0, 1.0, 1.0),
        steering_angle_rad=0.0,
        support_min_angle_rad=radians(-15.0),
        support_max_angle_rad=radians(15.0),
        baseline_m=BASELINE,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
        reference_footprint_width_m=4.0,
    )

    assert result.status == "available"
    assert result.candidate_count == 5
    assert result.retained_count > 1
    assert result.target_spacing_m == pytest.approx(2.0)
    assert all(item.method == "phase_high_density" for item in result.detections)
    assert max(item.detected_across_track_angle_rad for item in result.detections) > 0.0
    assert min(item.detected_across_track_angle_rad for item in result.detections) < 0.0


def test_high_density_disabled_emits_no_high_density_detections() -> None:
    result = detect_high_density_from_phase(
        high_density_enabled=False,
        sample_times_seconds=(0.1, 0.2),
        differential_phase_rad=(-0.1, 0.1),
        support_magnitude=(1.0, 1.0),
        steering_angle_rad=0.0,
        support_min_angle_rad=radians(-10.0),
        support_max_angle_rad=radians(10.0),
        baseline_m=BASELINE,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
        reference_footprint_width_m=4.0,
    )

    assert result.status == "disabled"
    assert result.detections == ()

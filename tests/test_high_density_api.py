from math import radians

from hydrosim.acquisition.high_density import phase_for_split_aperture_angle
from hydrosim.app.bottom_detection_api import (
    D9BottomDetectionRequest,
    prepare_d9_bottom_detection_response,
)
from hydrosim.app.high_density_api import D9HighDensityRequest
from hydrosim.geometry import Vector3


def test_d9_bottom_detection_bridge_returns_distinct_high_density_comparison() -> None:
    baseline = Vector3(x=0.0, y=0.01, z=0.0)
    angles = tuple(radians(value) for value in (-10.0, -5.0, 0.0, 5.0, 10.0))
    phases = tuple(
        phase_for_split_aperture_angle(
            angle,
            steering_angle_rad=0.0,
            baseline_m=baseline,
            frequency_hz=200_000.0,
            sound_speed_mps=1500.0,
        )
        for angle in angles
    )
    response = prepare_d9_bottom_detection_response(
        D9BottomDetectionRequest(
            correlation_real=(0.0, 0.2, 1.0, 0.2, 0.0),
            reference_sample_count=1,
            sample_rate_hz=1000.0,
            high_density=D9HighDensityRequest(
                high_density_enabled=True,
                phase_sample_time_ms=(100.0, 100.5, 101.0, 101.5, 102.0),
                differential_phase_rad=phases,
                support_magnitude=(1.0, 1.0, 1.0, 1.0, 1.0),
                steering_across_track_angle_deg=0.0,
                support_min_angle_deg=-15.0,
                support_max_angle_deg=15.0,
                split_aperture_baseline_m=(0.0, 0.01, 0.0),
                frequency_khz=200.0,
                sound_speed_mps=1500.0,
                reference_footprint_width_m=4.0,
            ),
        )
    )

    assert response.high_density is not None
    assert response.high_density.status == "available"
    assert response.high_density.comparison.high_density_detection_count > 1
    assert response.high_density.comparison.density_multiplier > 1.0
    assert response.high_density.metadata["high_density_distinct_from_multiple_detection"] is True

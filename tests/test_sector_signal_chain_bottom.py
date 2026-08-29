import pytest

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LayeredSoundSpeedProfile,
    PointTargetStrength,
    SectorWaveformAssignment,
    SectorWaveformPlan,
    SoundSpeedLayer,
    make_uniform_transmit_sectors,
    simulate_sector_waveform_propagation_ping,
)
from hydrosim.geometry import make_reference_mills_cross


def test_point_target_strength_scales_integrated_matched_filter_peak() -> None:
    configuration = make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=0.005,
        receive_spacing=0.005,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
    )
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=0.0,
        end_along_track_angle_rad=0.0,
        sector_count=1,
    )
    waveform_plan = SectorWaveformPlan(
        assignments=(
            SectorWaveformAssignment(
                sector_index=0,
                pulse=ContinuousWavePulse(
                    center_frequency_hz=150_000.0,
                    duration_seconds=0.001,
                ),
            ),
        )
    )
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(
                top_depth_m=0.0,
                bottom_depth_m=100.0,
                sound_speed_mps=1500.0,
            ),
        )
    )

    ping = simulate_sector_waveform_propagation_ping(
        configuration=configuration,
        sector_set=sectors,
        waveform_plan=waveform_plan,
        profile=profile,
        target_depth_m=10.0,
        receive_steering_across_track_angles_rad=(-0.1, 0.0, 0.1),
        sample_rate_hz=200_000.0,
        bottom_interaction_model=PointTargetStrength(target_strength_db=-20.0),
    )

    result = ping.sectors[0]
    assert result.bottom_interaction is not None
    assert result.bottom_interaction.amplitude_ratio == pytest.approx(0.1)
    assert result.received_echo_amplitude == pytest.approx(0.1)
    assert result.matched_filter.normalized_peak_amplitude == pytest.approx(0.1)

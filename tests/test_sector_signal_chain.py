import pytest

from hydrosim.acquisition import (
    ContinuousWavePulse,
    LayeredSoundSpeedProfile,
    LinearFMPulse,
    SectorWaveformAssignment,
    SectorWaveformPlan,
    SoundSpeedLayer,
    make_uniform_transmit_sectors,
    simulate_sector_waveform_propagation_ping,
)
from hydrosim.geometry import make_reference_mills_cross


def _configuration():
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="signal_chain_mills_cross",
    )


def _constant_profile():
    return LayeredSoundSpeedProfile(
        layers=(SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=100.0, sound_speed_mps=1500.0),)
    )


def test_integrated_chain_recovers_sector_delay_plus_reciprocal_twtt() -> None:
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=0.0,
        end_along_track_angle_rad=0.0,
        sector_count=1,
        first_tx_delay_seconds=0.001,
    )
    plan = SectorWaveformPlan(
        assignments=(
            SectorWaveformAssignment(
                sector_index=0,
                pulse=LinearFMPulse(
                    center_frequency_hz=150_000.0,
                    bandwidth_hz=20_000.0,
                    duration_seconds=0.001,
                ),
            ),
        )
    )
    sample_rate = 200_000.0
    result = simulate_sector_waveform_propagation_ping(
        configuration=_configuration(),
        sector_set=sectors,
        waveform_plan=plan,
        profile=_constant_profile(),
        target_depth_m=30.0,
        receive_steering_across_track_angles_rad=(-0.2, 0.0, 0.2),
        sample_rate_hz=sample_rate,
    )

    sector = result.sectors[0]
    assert sector.one_way_travel_time_seconds == pytest.approx(30.0 / 1500.0)
    assert sector.reciprocal_twtt_seconds == pytest.approx(2.0 * 30.0 / 1500.0)
    assert sector.echo_arrival_offset_seconds == pytest.approx(0.001 + 2.0 * 30.0 / 1500.0)
    assert sector.matched_filter.peak_lag_samples == sector.echo_delay_samples
    assert sector.matched_filter.normalized_peak_amplitude == pytest.approx(1.0)
    assert abs(float(sector.timing_quantization_error_seconds)) <= 0.5 / sample_rate
    assert sector.strongest_receive_beam_index == 1


def test_each_sector_can_use_an_independent_waveform_and_refracted_path() -> None:
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=-0.15,
        end_along_track_angle_rad=0.15,
        sector_count=2,
        inter_sector_delay_seconds=0.0005,
    )
    plan = SectorWaveformPlan(
        assignments=(
            SectorWaveformAssignment(
                sector_index=0,
                pulse=ContinuousWavePulse(center_frequency_hz=120_000.0, duration_seconds=0.0005),
            ),
            SectorWaveformAssignment(
                sector_index=1,
                pulse=LinearFMPulse(
                    center_frequency_hz=180_000.0,
                    bandwidth_hz=30_000.0,
                    duration_seconds=0.0005,
                ),
            ),
        )
    )
    profile = LayeredSoundSpeedProfile(
        layers=(
            SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=20.0, sound_speed_mps=1480.0),
            SoundSpeedLayer(top_depth_m=20.0, bottom_depth_m=60.0, sound_speed_mps=1520.0),
        )
    )

    result = simulate_sector_waveform_propagation_ping(
        configuration=_configuration(),
        sector_set=sectors,
        waveform_plan=plan,
        profile=profile,
        target_depth_m=50.0,
        receive_steering_across_track_angles_rad=(-0.2, 0.0, 0.2),
        sample_rate_hz=400_000.0,
    )

    assert [float(item.center_frequency_hz) for item in result.sectors] == pytest.approx(
        [120_000.0, 180_000.0]
    )
    assert all(len(item.propagation_path.segments) == 2 for item in result.sectors)
    assert all(item.propagation_path.horizontal_distance_m > 0.0 for item in result.sectors)
    assert result.sectors[1].echo_arrival_offset_seconds > result.sectors[0].reciprocal_twtt_seconds


def test_waveform_plan_must_cover_every_sector_exactly_once() -> None:
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=-0.1,
        end_along_track_angle_rad=0.1,
        sector_count=2,
    )
    incomplete = SectorWaveformPlan(
        assignments=(
            SectorWaveformAssignment(
                sector_index=0,
                pulse=ContinuousWavePulse(center_frequency_hz=150_000.0, duration_seconds=0.001),
            ),
        )
    )

    with pytest.raises(ValueError, match="exactly one pulse"):
        simulate_sector_waveform_propagation_ping(
            configuration=_configuration(),
            sector_set=sectors,
            waveform_plan=incomplete,
            profile=_constant_profile(),
            target_depth_m=30.0,
            receive_steering_across_track_angles_rad=(-0.1, 0.0, 0.1),
            sample_rate_hz=200_000.0,
        )

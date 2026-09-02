from math import pi

import pytest

from hydrosim.acquisition.wave_kinematics import (
    AcousticWaveKinematics,
    monostatic_two_way_range_offset,
)
from hydrosim.acquisition.waveform import LinearFMPulse, waveform_autocorrelation
from hydrosim.acquisition.waveform_metrics import autocorrelation_power_fwhm


def test_wave_kinematics_period_wavelength_and_positive_x_phase_convention():
    wave = AcousticWaveKinematics(
        frequency_hz=1000.0,
        sound_speed_mps=1500.0,
        normalized_amplitude=2.0,
        initial_phase_rad=0.0,
    )

    assert wave.period_seconds == pytest.approx(0.001)
    assert wave.wavelength_m == pytest.approx(1.5)
    assert wave.normalized_field(x_m=0.0, time_seconds=0.0) == pytest.approx(2.0)
    assert wave.normalized_field(x_m=wave.wavelength_m / 4.0, time_seconds=0.0) == pytest.approx(0.0, abs=1e-12)
    assert wave.normalized_field(x_m=0.0, time_seconds=wave.period_seconds / 4.0) == pytest.approx(0.0, abs=1e-12)
    assert wave.normalized_field(x_m=wave.wavelength_m / 4.0, time_seconds=wave.period_seconds / 4.0) == pytest.approx(2.0)


def test_wave_kinematics_phase_and_positive_domain_validation():
    shifted = AcousticWaveKinematics(frequency_hz=10.0, initial_phase_rad=pi)
    assert shifted.normalized_field(x_m=0.0, time_seconds=0.0) == pytest.approx(-1.0)

    with pytest.raises(ValueError):
        AcousticWaveKinematics(frequency_hz=0.0)
    with pytest.raises(ValueError):
        AcousticWaveKinematics(frequency_hz=1.0, sound_speed_mps=0.0)


def test_monostatic_two_way_range_offset_preserves_lag_sign():
    assert monostatic_two_way_range_offset(lag_seconds=0.002, sound_speed_mps=1500.0) == pytest.approx(1.5)
    assert monostatic_two_way_range_offset(lag_seconds=-0.002, sound_speed_mps=1500.0) == pytest.approx(-1.5)
    with pytest.raises(ValueError):
        monostatic_two_way_range_offset(lag_seconds=0.001, sound_speed_mps=0.0)


def test_autocorrelation_power_fwhm_is_interpolated_and_range_convertible():
    pulse = LinearFMPulse(
        center_frequency_hz=100_000.0,
        bandwidth_hz=20_000.0,
        duration_seconds=0.002,
    )
    response = waveform_autocorrelation(pulse, sample_rate_hz=200_000.0)
    metric = autocorrelation_power_fwhm(response, sound_speed_mps=1500.0)

    assert metric.left_half_power_lag_seconds < 0.0
    assert metric.right_half_power_lag_seconds > 0.0
    assert metric.temporal_width_seconds > 0.0
    assert metric.equivalent_two_way_range_width_m == pytest.approx(
        1500.0 * metric.temporal_width_seconds / 2.0
    )

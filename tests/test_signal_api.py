import pytest

from hydrosim.app.signal_api import (
    SignalRequest,
    WaveKinematicsRequest,
    prepare_signal_response,
    prepare_wave_kinematics_response,
)


def test_lfm_response_exposes_application_ready_traces():
    response = prepare_signal_response(
        SignalRequest(
            pulse_type="lfm",
            center_frequency_khz=200.0,
            duration_ms=1.0,
            bandwidth_khz=100.0,
            chirp_direction="down",
            envelope_model="tukey",
        )
    )

    assert response.pulse_type == "lfm"
    assert response.waveform.x_unit == "ms"
    assert response.instantaneous_frequency.y_unit == "kHz"
    assert response.matched_filter.x_unit == "us"
    assert len(response.waveform.x) == len(response.waveform.y)
    assert len(response.instantaneous_frequency.x) == len(response.instantaneous_frequency.y)
    assert response.instantaneous_frequency.y[0] > response.instantaneous_frequency.y[-1]
    assert response.metadata["chirp_direction"] == "down"
    assert response.metadata["waveform_representation"] == "real_acoustic_passband"
    assert response.metadata["processing_representation"] == "complex_analytic_baseband"


def test_cw_response_keeps_frequency_constant_and_ignores_lfm_controls():
    response = prepare_signal_response(
        SignalRequest(
            pulse_type="cw",
            center_frequency_khz=100.0,
            duration_ms=0.5,
            bandwidth_khz=250.0,
            chirp_direction="down",
        )
    )

    assert response.metadata["bandwidth_khz"] == 0.0
    assert response.metadata["chirp_direction"] == "none"
    frequencies = response.instantaneous_frequency.y
    assert frequencies
    assert max(frequencies) == min(frequencies) == 100.0


def test_wave_kinematics_response_exposes_canonical_period_wavelength_and_traces():
    response = prepare_wave_kinematics_response(
        WaveKinematicsRequest(
            frequency_khz=100.0,
            sound_speed_mps=1500.0,
            normalized_amplitude=0.75,
            initial_phase_rad=0.0,
            sample_count=101,
            display_cycles=2.0,
        )
    )

    assert response.period_seconds == pytest.approx(10e-6)
    assert response.wavelength_m == pytest.approx(0.015)
    assert response.temporal_waveform.x_unit == "ms"
    assert response.temporal_waveform.y_unit == "normalized amplitude"
    assert response.spatial_waveform.x_unit == "m"
    assert response.spatial_waveform.y_unit == "normalized amplitude"
    assert len(response.temporal_waveform.x) == 101
    assert len(response.spatial_waveform.x) == 101
    assert response.temporal_waveform.y[0] == pytest.approx(0.75)
    assert response.spatial_waveform.y[0] == pytest.approx(0.75)
    assert response.metadata["field_representation"] == "normalized_1d_harmonic_plane_wave"
    assert response.metadata["propagation_direction"] == "+x"
    assert response.metadata["state_semantics"] == "Configured inputs; Derived outputs"


def test_wave_kinematics_phase_and_positive_x_field_are_core_derived():
    quarter_cycle = prepare_wave_kinematics_response(
        WaveKinematicsRequest(
            frequency_khz=100.0,
            sound_speed_mps=1500.0,
            normalized_amplitude=1.0,
            initial_phase_rad=0.0,
            sample_count=33,
            display_cycles=1.0,
            snapshot_time_fraction_of_period=0.25,
        )
    )

    quarter_cycle_index = 8
    assert quarter_cycle.temporal_waveform.y[quarter_cycle_index] == pytest.approx(
        0.0, abs=1e-12
    )
    assert quarter_cycle.spatial_waveform.y[0] == pytest.approx(0.0, abs=1e-12)
    assert quarter_cycle.spatial_waveform.y[quarter_cycle_index] == pytest.approx(1.0)


def test_wave_kinematics_range_lag_uses_canonical_monostatic_conversion():
    response = prepare_wave_kinematics_response(
        WaveKinematicsRequest(
            frequency_khz=200.0,
            sound_speed_mps=1500.0,
            range_lag_us=1000.0,
        )
    )

    assert response.range_offset_m == pytest.approx(0.75)

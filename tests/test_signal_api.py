from hydrosim.app.signal_api import SignalRequest, prepare_signal_response


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

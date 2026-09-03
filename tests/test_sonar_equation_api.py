import pytest

from hydrosim.app.sonar_equation_api import (
    D3SonarEquationRequest,
    prepare_d3_sonar_equation_response,
)


def test_d3_response_exposes_render_ready_canonical_outputs():
    response = prepare_d3_sonar_equation_response(
        D3SonarEquationRequest(
            frequency_khz=200.0,
            range_m=100.0,
            source_level_db_re_1upa_at_1m=210.0,
            noise_level_db_re_1upa=60.0,
            comparison_frequency_khz=400.0,
            curve_min_range_m=20.0,
            curve_max_range_m=200.0,
            curve_sample_count=10,
        )
    )

    assert response.received_level_vs_range.x_unit == "m"
    assert response.received_level_vs_range.y_unit == "dB re 1 µPa"
    assert response.snr_vs_range.y_unit == "dB"
    assert len(response.received_level_vs_range.x) == 10
    assert len(response.received_level_vs_range.y) == 10
    assert len(response.snr_vs_range.y) == 10
    assert response.snr_db == pytest.approx(
        response.received_level_db_re_1upa - 60.0
    )
    assert response.two_way_transmission_loss_db == pytest.approx(
        2.0 * response.contribution_breakdown.outbound_total_loss_db
    )
    assert response.metadata["state_semantics"] == "Configured inputs/context; Derived outputs"


def test_d3_range_curve_decreases_received_level_and_snr():
    response = prepare_d3_sonar_equation_response(
        D3SonarEquationRequest(
            curve_min_range_m=25.0,
            curve_max_range_m=250.0,
            curve_sample_count=20,
        )
    )

    received = response.received_level_vs_range.y
    snr = response.snr_vs_range.y
    assert all(left > right for left, right in zip(received, received[1:]))
    assert all(left > right for left, right in zip(snr, snr[1:]))


def test_d3_source_and_noise_controls_preserve_level_domain_relationships():
    baseline = prepare_d3_sonar_equation_response(D3SonarEquationRequest())
    louder = prepare_d3_sonar_equation_response(
        D3SonarEquationRequest(source_level_db_re_1upa_at_1m=216.0)
    )
    noisier = prepare_d3_sonar_equation_response(
        D3SonarEquationRequest(noise_level_db_re_1upa=66.0)
    )

    assert louder.received_level_db_re_1upa - baseline.received_level_db_re_1upa == pytest.approx(6.0)
    assert louder.snr_db - baseline.snr_db == pytest.approx(6.0)
    assert noisier.received_level_db_re_1upa == pytest.approx(baseline.received_level_db_re_1upa)
    assert noisier.snr_db - baseline.snr_db == pytest.approx(-6.0)


def test_d3_frequency_comparison_comes_from_canonical_absorption_and_loss():
    response = prepare_d3_sonar_equation_response(
        D3SonarEquationRequest(frequency_khz=100.0, comparison_frequency_khz=400.0)
    )

    low, high = response.frequency_loss_comparison
    assert low.frequency_khz == 100.0
    assert high.frequency_khz == 400.0
    assert high.absorption_db_per_km > low.absorption_db_per_km
    assert high.two_way_transmission_loss_db > low.two_way_transmission_loss_db

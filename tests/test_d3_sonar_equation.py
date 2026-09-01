from __future__ import annotations

import pytest
from pydantic import ValidationError

from hydrosim.sonar_equation import (
    AinslieMcColmEnvironment,
    AreaBackscatterInput,
    D3SonarEquationInput,
    ainslie_mccolm_absorption_db_per_km,
    evaluate_d3_sonar_equation,
)


def _input(**overrides):
    payload = dict(
        frequency_hz=100_000.0,
        source_level_db_re_1upa_at_1m=210.0,
        noise_level_db_re_1upa=80.0,
        outbound_path_length_m=100.0,
        inbound_path_length_m=100.0,
        backscatter=AreaBackscatterInput(
            scattering_strength_db_per_m2=-30.0,
            contributing_area_m2=10.0,
            frequency_hz=100_000.0,
        ),
    )
    payload.update(overrides)
    return D3SonarEquationInput(**payload)


def test_ainslie_mccolm_reference_value_at_default_environment() -> None:
    alpha = ainslie_mccolm_absorption_db_per_km(frequency_hz=100_000.0)
    assert alpha == pytest.approx(34.3410215561, rel=1e-10)


def test_absorption_increases_over_didactic_frequency_comparison() -> None:
    low = ainslie_mccolm_absorption_db_per_km(frequency_hz=10_000.0)
    high = ainslie_mccolm_absorption_db_per_km(frequency_hz=100_000.0)
    assert high > low > 0.0


def test_absorption_environment_enforces_documented_domain() -> None:
    with pytest.raises(ValidationError):
        AinslieMcColmEnvironment(temperature_c=40.0)
    with pytest.raises(ValidationError):
        AinslieMcColmEnvironment(salinity=2.0)
    with pytest.raises(ValidationError):
        AinslieMcColmEnvironment(ph=8.5)
    with pytest.raises(ValidationError):
        AinslieMcColmEnvironment(depth_km=7.5)


def test_d3_level_chain_and_reciprocal_loss_close_exactly() -> None:
    result = evaluate_d3_sonar_equation(_input())
    expected_received = (
        result.source_level_db_re_1upa_at_1m
        + result.tx_relative_beam_gain_db
        - result.outbound_total_loss_db
        + result.backscatter_strength_db
        - result.inbound_total_loss_db
        + result.rx_relative_beam_gain_db
    )
    assert result.received_level_db_re_1upa == pytest.approx(expected_received)
    assert result.snr_db == pytest.approx(result.received_level_db_re_1upa - result.noise_level_db_re_1upa)
    assert result.two_way_transmission_loss_db == pytest.approx(2.0 * result.outbound_total_loss_db)
    assert result.backscatter_strength_db == pytest.approx(-20.0)


def test_longer_path_and_higher_frequency_reduce_received_level() -> None:
    baseline = evaluate_d3_sonar_equation(_input())
    longer = evaluate_d3_sonar_equation(
        _input(outbound_path_length_m=200.0, inbound_path_length_m=200.0)
    )
    higher_frequency = evaluate_d3_sonar_equation(_input(frequency_hz=300_000.0))
    assert longer.received_level_db_re_1upa < baseline.received_level_db_re_1upa
    assert higher_frequency.received_level_db_re_1upa < baseline.received_level_db_re_1upa


def test_off_axis_relative_beam_levels_cannot_increase_received_level() -> None:
    boresight = evaluate_d3_sonar_equation(_input())
    off_axis = evaluate_d3_sonar_equation(
        _input(tx_relative_beam_gain_db=-3.0, rx_relative_beam_gain_db=-6.0)
    )
    assert off_axis.received_level_db_re_1upa == pytest.approx(
        boresight.received_level_db_re_1upa - 9.0
    )


def test_nonreciprocal_paths_do_not_report_reciprocal_two_way_shortcut() -> None:
    result = evaluate_d3_sonar_equation(_input(inbound_path_length_m=120.0))
    assert result.two_way_transmission_loss_db is None

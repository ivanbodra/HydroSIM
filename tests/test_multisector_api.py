from math import isclose

from pydantic import ValidationError
import pytest

from hydrosim.app.multisector_api import (
    D10MultisectorRequest,
    D10SectorRequest,
    prepare_d10_multisector_response,
)


def _sector(
    sector_id: str,
    centre: float,
    lower: float,
    upper: float,
    frequency_khz: float,
    delay_ms: float,
) -> D10SectorRequest:
    return D10SectorRequest(
        sector_id=sector_id,
        centre_across_track_deg=centre,
        across_track_min_deg=lower,
        across_track_max_deg=upper,
        frequency_khz=frequency_khz,
        pulse_duration_ms=1.0,
        sector_tx_delay_ms=delay_ms,
    )


def test_ped_d10_analytical_timing_anchor_and_frequency_ratio() -> None:
    response = prepare_d10_multisector_response(
        D10MultisectorRequest(
            tx_time_seconds=10.0,
            sound_speed_mps=1500.0,
            sectors=(
                _sector("port", 30.0, 15.0, 45.0, 200.0, 0.0),
                _sector("centre", 0.0, -15.0, 15.0, 300.0, 2.0),
                _sector("starboard", -30.0, -45.0, -15.0, 400.0, 5.0),
            ),
        )
    )

    assert [sector.sector_tx_time_seconds for sector in response.sectors] == pytest.approx(
        [10.0, 10.002, 10.005]
    )
    assert response.transmit_groups == (("port",), ("centre",), ("starboard",))
    assert isclose(response.sectors[0].wavelength_m, 2.0 * response.sectors[2].wavelength_m)
    assert response.coverage_supports[0].across_track_min_deg == pytest.approx(15.0)
    assert response.coverage_supports[2].across_track_max_deg == pytest.approx(-15.0)


def test_equal_delays_are_one_simultaneous_transmit_group() -> None:
    response = prepare_d10_multisector_response(
        D10MultisectorRequest(
            sectors=(
                _sector("a", 10.0, 0.0, 20.0, 200.0, 2.0),
                _sector("b", -10.0, -20.0, 0.0, 200.0, 2.0),
            )
        )
    )

    assert response.transmit_groups == (("a", "b"),)
    assert {sector.transmit_group for sector in response.sectors} == {0}
    assert response.sectors[0].sector_tx_time_seconds == pytest.approx(
        response.sectors[1].sector_tx_time_seconds
    )


def test_negative_sector_delay_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _sector("bad", 0.0, -10.0, 10.0, 200.0, -0.1)


def test_geometry_contract_rejects_centre_outside_support() -> None:
    with pytest.raises(ValueError, match="centre must lie inside"):
        prepare_d10_multisector_response(
            D10MultisectorRequest(
                sectors=(_sector("bad", 30.0, -10.0, 10.0, 200.0, 0.0),)
            )
        )

from __future__ import annotations

import pytest

from hydrosim.app.multisector_api import (
    D10MultisectorRequest,
    D10SectorRequest,
    prepare_d10_multisector_response,
)


def _sector(sector_id: str, lo: float, hi: float, centre: float, frequency: float, delay: float):
    return D10SectorRequest(
        sector_id=sector_id,
        across_track_min_deg=lo,
        across_track_max_deg=hi,
        centre_across_track_deg=centre,
        frequency_khz=frequency,
        pulse_duration_ms=1.0,
        tx_delay_ms=delay,
    )


def test_d10_contract_preserves_timing_order_and_wavelength_anchor() -> None:
    response = prepare_d10_multisector_response(
        D10MultisectorRequest(
            tx_time_s=10.0,
            sound_speed_mps=1500.0,
            sectors=(
                _sector("starboard", -60, -20, -40, 100, 0),
                _sector("centre", -20, 20, 0, 200, 2),
                _sector("port", 20, 60, 40, 400, 5),
            ),
        )
    )
    assert [item.tx_time_s for item in response.sectors] == pytest.approx([10.0, 10.002, 10.005])
    assert response.transmit_groups == (("starboard",), ("centre",), ("port",))
    assert response.sectors[0].wavelength_m == pytest.approx(0.015)
    assert response.sectors[1].wavelength_m == pytest.approx(0.0075)
    assert response.sectors[2].wavelength_m == pytest.approx(0.00375)
    expected_supports = ((-60, -20), (-20, 20), (20, 60))
    for actual, expected in zip(response.coverage_supports_deg, expected_supports, strict=True):
        assert actual == pytest.approx(expected)


def test_d10_equal_delays_are_simultaneous_not_artificially_sequenced() -> None:
    response = prepare_d10_multisector_response(
        D10MultisectorRequest(
            sectors=(
                _sector("a", -30, 0, -15, 200, 1),
                _sector("b", 0, 30, 15, 200, 1),
            )
        )
    )
    assert response.transmit_groups == (("a", "b"),)


def test_d10_rejects_sector_centre_outside_canonical_support() -> None:
    with pytest.raises(ValueError, match="centre must lie inside"):
        prepare_d10_multisector_response(
            D10MultisectorRequest(sectors=(_sector("bad", -20, 20, 30, 200, 0),))
        )

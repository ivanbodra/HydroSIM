import math

import pytest

from hydrosim.acquisition import TransmitSector, TransmitSectorSet, make_uniform_transmit_sectors


def test_uniform_transmit_sectors_have_explicit_steering_and_timing() -> None:
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=-0.2,
        end_along_track_angle_rad=0.2,
        sector_count=3,
        first_tx_delay_seconds=0.001,
        inter_sector_delay_seconds=0.0002,
    )

    assert [float(s.steering_along_track_angle_rad) for s in sectors.sectors] == pytest.approx(
        [-0.2, 0.0, 0.2]
    )
    assert [float(s.tx_delay_seconds) for s in sectors.sectors] == pytest.approx(
        [0.001, 0.0012, 0.0014]
    )

    aft, broadside, forward = sectors.sectors
    assert aft.steering_direction_sensor_frame.x < 0.0
    assert broadside.steering_direction_sensor_frame.x == pytest.approx(0.0)
    assert forward.steering_direction_sensor_frame.x > 0.0
    for sector in sectors.sectors:
        u = sector.steering_direction_sensor_frame
        assert math.sqrt(u.x * u.x + u.y * u.y + u.z * u.z) == pytest.approx(1.0)


def test_single_sector_uses_midpoint_without_requiring_nonzero_span() -> None:
    sectors = make_uniform_transmit_sectors(
        start_along_track_angle_rad=-0.1,
        end_along_track_angle_rad=0.1,
        sector_count=1,
    )
    assert float(sectors.sectors[0].steering_along_track_angle_rad) == pytest.approx(0.0)


def test_sector_set_rejects_duplicate_indices_and_names() -> None:
    a = TransmitSector(sector_index=0, name="a")
    b_same_index = TransmitSector(sector_index=0, name="b")
    with pytest.raises(ValueError, match="indices"):
        TransmitSectorSet(sectors=(a, b_same_index))

    b_same_name = TransmitSector(sector_index=1, name="a")
    with pytest.raises(ValueError, match="names"):
        TransmitSectorSet(sectors=(a, b_same_name))


def test_sector_delays_cannot_be_negative() -> None:
    with pytest.raises(ValueError):
        TransmitSector(sector_index=0, name="bad", tx_delay_seconds=-1e-6)

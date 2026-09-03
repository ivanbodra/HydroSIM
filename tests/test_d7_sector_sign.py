from math import degrees

from hydrosim.app.sonar_geometry_lesson_page import _tx_sectors


def test_d7_tx_sector_ids_follow_canonical_across_track_sign() -> None:
    sectors = {sector.sector_id: sector for sector in _tx_sectors().sectors}

    assert degrees(sectors["port"].centre_across_track_angle_rad) == 40.0
    assert degrees(sectors["starboard"].centre_across_track_angle_rad) == -40.0
    assert sectors["port"].across_track_min_rad > 0.0
    assert sectors["starboard"].across_track_max_rad < 0.0

from pathlib import Path


def test_d7_tx_sector_ids_follow_canonical_across_track_signs() -> None:
    """Positive across-track is Port; negative across-track is Starboard."""
    source = Path("src/hydrosim/app/sonar_geometry_lesson_page.py").read_text(encoding="utf-8")

    assert 'sector_id="starboard", sector_index=0' in source
    assert 'across_track_min_rad=radians(-60), across_track_max_rad=radians(-20)' in source
    assert 'sector_id="port", sector_index=2' in source
    assert 'across_track_min_rad=radians(20), across_track_max_rad=radians(60)' in source

    assert 'sector_id="port", sector_index=0' not in source
    assert 'sector_id="starboard", sector_index=2' not in source

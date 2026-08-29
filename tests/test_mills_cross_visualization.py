from math import isclose

import numpy as np

from hydrosim.acquisition import scan_mills_cross_two_way_pattern_2d
from hydrosim.geometry import make_reference_mills_cross
from hydrosim.visualization import prepare_mills_cross_pattern_panels


def _scan():
    wavelength = 0.01
    configuration = make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="visualization_test",
    )
    return scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.15,
        along_track_end_angle_rad=0.15,
        along_track_sample_count=3,
        across_track_start_angle_rad=-0.15,
        across_track_end_angle_rad=0.15,
        across_track_sample_count=3,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )


def test_panel_matrices_follow_along_by_across_grid_order():
    panels = prepare_mills_cross_pattern_panels(_scan(), scale="power")

    assert panels.transmit.shape == (3, 3)
    assert panels.receive.shape == (3, 3)
    assert panels.two_way.shape == (3, 3)
    assert np.all(np.diff(panels.across_track_angles_deg) > 0.0)
    assert np.all(np.diff(panels.along_track_angles_deg) > 0.0)
    assert isclose(panels.two_way[1, 1], 1.0, abs_tol=1e-12)


def test_reference_mills_cross_panels_show_crossed_one_way_selectivity():
    panels = prepare_mills_cross_pattern_panels(_scan(), scale="power")

    center = (1, 1)
    along_only = (2, 1)
    across_only = (1, 2)

    assert panels.transmit[along_only] < panels.transmit[center]
    assert isclose(panels.transmit[across_only], panels.transmit[center], rel_tol=0.02)
    assert panels.receive[across_only] < panels.receive[center]
    assert isclose(panels.receive[along_only], panels.receive[center], rel_tol=0.02)
    assert panels.two_way[2, 2] < panels.two_way[along_only]
    assert panels.two_way[2, 2] < panels.two_way[across_only]


def test_db_display_uses_common_floor_without_changing_scan_values():
    scan = _scan()
    original_center_power = next(
        sample.normalized_power
        for sample in scan.samples
        if isclose(sample.along_track_angle_rad, 0.0, abs_tol=1e-12)
        and isclose(sample.across_track_angle_rad, 0.0, abs_tol=1e-12)
    )

    panels = prepare_mills_cross_pattern_panels(scan, scale="db", floor_db=-30.0)

    assert panels.minimum_value == -30.0
    assert panels.maximum_value == 0.0
    assert np.min(panels.transmit) >= -30.0
    assert np.min(panels.receive) >= -30.0
    assert np.min(panels.two_way) >= -30.0
    assert isclose(panels.two_way[1, 1], 0.0, abs_tol=1e-12)
    assert isclose(original_center_power, 1.0, abs_tol=1e-12)


def test_invalid_db_floor_is_rejected():
    try:
        prepare_mills_cross_pattern_panels(_scan(), scale="db", floor_db=0.0)
    except ValueError as exc:
        assert "floor_db" in str(exc)
    else:
        raise AssertionError("non-negative dB display floor should be rejected")

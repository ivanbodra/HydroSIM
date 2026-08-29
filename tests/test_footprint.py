from math import radians, tan

import pytest

from hydrosim.acquisition import (
    FlatSeafloorFootprintModel,
    estimate_flat_seafloor_footprint,
)


def test_nadir_footprint_is_beam_limited() -> None:
    model = FlatSeafloorFootprintModel(
        transmit_along_track_beamwidth_rad=radians(2.0),
        receive_across_track_beamwidth_rad=radians(1.0),
    )
    footprint = estimate_flat_seafloor_footprint(
        model=model,
        vertical_separation_m=100.0,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=0.0,
        pulse_duration_seconds=0.001,
        sound_speed_mps=1500.0,
    )

    expected_along = 200.0 * tan(radians(1.0))
    expected_across = 200.0 * tan(radians(0.5))
    assert footprint.beam_limited_along_track_width_m == pytest.approx(expected_along)
    assert footprint.beam_limited_across_track_width_m == pytest.approx(expected_across)
    assert footprint.pulse_limited_across_track_width_m is None
    assert footprint.across_track_limiting_mechanism == "receive_beam"
    assert footprint.effective_area_m2 == pytest.approx(expected_along * expected_across)


def test_oblique_short_pulse_can_limit_across_track_extent() -> None:
    model = FlatSeafloorFootprintModel(
        transmit_along_track_beamwidth_rad=radians(2.0),
        receive_across_track_beamwidth_rad=radians(10.0),
    )
    footprint = estimate_flat_seafloor_footprint(
        model=model,
        vertical_separation_m=100.0,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=radians(45.0),
        pulse_duration_seconds=0.0001,
        sound_speed_mps=1500.0,
    )

    assert footprint.pulse_limited_across_track_width_m is not None
    assert footprint.pulse_limited_across_track_width_m < footprint.beam_limited_across_track_width_m
    assert footprint.effective_across_track_width_m == pytest.approx(
        footprint.pulse_limited_across_track_width_m
    )
    assert footprint.across_track_limiting_mechanism == "pulse"

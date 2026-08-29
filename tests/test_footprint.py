from math import radians, tan

import pytest

from hydrosim.acquisition import (
    FlatSeafloorFootprintModel,
    estimate_flat_seafloor_footprint,
    evaluate_seafloor_area_backscatter,
    seafloor_backscatter_from_footprint,
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


def test_derived_footprint_feeds_area_backscatter_model() -> None:
    model = FlatSeafloorFootprintModel(
        transmit_along_track_beamwidth_rad=radians(1.0),
        receive_across_track_beamwidth_rad=radians(1.0),
    )
    footprint = estimate_flat_seafloor_footprint(
        model=model,
        vertical_separation_m=50.0,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=radians(20.0),
        pulse_duration_seconds=0.001,
        sound_speed_mps=1500.0,
    )
    backscatter = seafloor_backscatter_from_footprint(
        scattering_strength_db_per_m2=-30.0,
        footprint=footprint,
    )
    response = evaluate_seafloor_area_backscatter(backscatter)

    assert backscatter.insonified_area_m2 == pytest.approx(footprint.effective_area_m2)
    assert backscatter.incidence_angle_from_normal_rad == pytest.approx(radians(20.0))
    assert response.insonified_area_m2 == pytest.approx(footprint.effective_area_m2)

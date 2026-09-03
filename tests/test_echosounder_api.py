from math import radians

import pytest

from hydrosim.acquisition.footprint import (
    FlatSeafloorFootprintModel,
    estimate_flat_seafloor_footprint,
)
from hydrosim.app.echosounder_api import (
    D8EchosounderRequest,
    prepare_d8_echosounder_response,
)


def test_d8_sbes_is_one_nadir_center_with_finite_footprint() -> None:
    response = prepare_d8_echosounder_response(D8EchosounderRequest())

    assert len(response.sbes.beams) == 1
    assert response.sbes.beams[0].steering_angle_deg == pytest.approx(0.0)
    assert response.sbes.beams[0].endpoint_across_track_m == pytest.approx(0.0)
    assert response.sbes.geometric_beam_center_swath_width_m == pytest.approx(0.0)
    assert response.sbes.beams[0].footprint.effective_area_m2 > 0.0


def test_d8_symmetric_odd_equiangular_mbes_preserves_port_starboard_signs() -> None:
    response = prepare_d8_echosounder_response(
        D8EchosounderRequest(
            mbes_beam_count=5,
            minimum_angle_deg=-40.0,
            maximum_angle_deg=40.0,
            spacing_method="equiangular",
        )
    )
    beams = response.mbes.beams

    assert beams[0].steering_angle_deg < 0.0
    assert beams[0].endpoint_across_track_m < 0.0
    assert beams[2].steering_angle_deg == pytest.approx(0.0, abs=1e-12)
    assert beams[2].endpoint_across_track_m == pytest.approx(0.0, abs=1e-12)
    assert beams[-1].steering_angle_deg > 0.0
    assert beams[-1].endpoint_across_track_m > 0.0
    assert abs(beams[0].endpoint_across_track_m) == pytest.approx(
        abs(beams[-1].endpoint_across_track_m)
    )


def test_d8_equiangular_keeps_angle_step_constant_not_bottom_spacing() -> None:
    response = prepare_d8_echosounder_response(
        D8EchosounderRequest(
            mbes_beam_count=7,
            minimum_angle_deg=-60.0,
            maximum_angle_deg=60.0,
            spacing_method="equiangular",
        )
    )
    angles = [beam.steering_angle_deg for beam in response.mbes.beams]
    angle_steps = [b - a for a, b in zip(angles, angles[1:], strict=False)]
    spacings = response.mbes.adjacent_across_track_spacings_m

    assert max(angle_steps) - min(angle_steps) < 1e-12
    assert max(spacings) - min(spacings) > 1.0


def test_d8_equidistant_uses_core_target_positions_and_constant_endpoint_spacing() -> None:
    response = prepare_d8_echosounder_response(
        D8EchosounderRequest(
            mbes_beam_count=7,
            minimum_angle_deg=-60.0,
            maximum_angle_deg=60.0,
            spacing_method="equidistant",
        )
    )
    targets = response.mbes.target_across_track_positions_m
    assert targets is not None

    endpoint_spacings = response.mbes.adjacent_across_track_spacings_m
    target_spacings = [b - a for a, b in zip(targets, targets[1:], strict=False)]
    assert endpoint_spacings == pytest.approx(target_spacings, rel=1e-10, abs=1e-10)
    assert max(endpoint_spacings) - min(endpoint_spacings) < 1e-8

    angles = [beam.steering_angle_deg for beam in response.mbes.beams]
    angle_steps = [b - a for a, b in zip(angles, angles[1:], strict=False)]
    assert max(angle_steps) - min(angle_steps) > 0.1


def test_d8_swath_is_endpoint_extent_and_increases_with_depth() -> None:
    shallow = prepare_d8_echosounder_response(
        D8EchosounderRequest(vertical_separation_m=50.0)
    )
    deep = prepare_d8_echosounder_response(
        D8EchosounderRequest(vertical_separation_m=150.0)
    )

    endpoints = [beam.endpoint_across_track_m for beam in shallow.mbes.beams]
    assert shallow.mbes.geometric_beam_center_swath_width_m == pytest.approx(
        max(endpoints) - min(endpoints)
    )
    assert (
        deep.mbes.geometric_beam_center_swath_width_m
        > shallow.mbes.geometric_beam_center_swath_width_m
    )


def test_d8_nadir_footprint_serializes_canonical_core_result() -> None:
    request = D8EchosounderRequest(
        vertical_separation_m=80.0,
        pulse_duration_ms=0.3,
        sound_speed_mps=1480.0,
        transmit_along_track_beamwidth_deg=3.0,
        receive_across_track_beamwidth_deg=2.0,
    )
    response = prepare_d8_echosounder_response(request)
    expected = estimate_flat_seafloor_footprint(
        model=FlatSeafloorFootprintModel(
            transmit_along_track_beamwidth_rad=radians(3.0),
            receive_across_track_beamwidth_rad=radians(2.0),
        ),
        vertical_separation_m=80.0,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=0.0,
        pulse_duration_seconds=0.3e-3,
        sound_speed_mps=1480.0,
    )
    actual = response.sbes.beams[0].footprint

    assert actual.beam_limited_along_track_width_m == pytest.approx(
        expected.beam_limited_along_track_width_m
    )
    assert actual.beam_limited_across_track_width_m == pytest.approx(
        expected.beam_limited_across_track_width_m
    )
    assert actual.effective_area_m2 == pytest.approx(expected.effective_area_m2)
    assert actual.across_track_limiting_mechanism == expected.across_track_limiting_mechanism


def test_d8_invalid_equidistant_sector_fails_without_spacing_fallback() -> None:
    request = D8EchosounderRequest(
        spacing_method="equidistant",
        minimum_angle_deg=5.0,
        maximum_angle_deg=60.0,
    )

    with pytest.raises(ValueError, match="requires a sector spanning nadir"):
        prepare_d8_echosounder_response(request)

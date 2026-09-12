import pytest

from hydrosim.acquisition.beamwidth_pattern import gaussian_power_from_beamwidth
from hydrosim.app.echosounder_directional_api import (
    D7SelectedDirectionalRequest,
    prepare_d7_selected_directional_response,
)


def test_gaussian_proxy_has_exact_full_half_power_width() -> None:
    beta = 4.0
    assert gaussian_power_from_beamwidth(
        angle_deg=10.0, steering_angle_deg=10.0, half_power_beamwidth_deg=beta
    ) == pytest.approx(1.0)
    assert gaussian_power_from_beamwidth(
        angle_deg=12.0, steering_angle_deg=10.0, half_power_beamwidth_deg=beta
    ) == pytest.approx(0.5)
    assert gaussian_power_from_beamwidth(
        angle_deg=8.0, steering_angle_deg=10.0, half_power_beamwidth_deg=beta
    ) == pytest.approx(0.5)


def test_selected_rx_follows_canonical_port_positive_beam_and_tx_stays_nadir() -> None:
    response = prepare_d7_selected_directional_response(
        D7SelectedDirectionalRequest(
            mbes_beam_count=5,
            minimum_angle_deg=-40.0,
            maximum_angle_deg=40.0,
            selected_mbes_beam_index=4,
            transmit_across_track_beamwidth_deg=10.0,
            receive_across_track_beamwidth_deg=8.0,
            response_sample_count=161,
        )
    )

    assert response.selected_steering_angle_deg == pytest.approx(40.0)
    tx_peak = response.tx_one_way.angle_deg[response.tx_one_way.normalized_power.index(max(response.tx_one_way.normalized_power))]
    rx_peak = response.rx_one_way.angle_deg[response.rx_one_way.normalized_power.index(max(response.rx_one_way.normalized_power))]
    assert tx_peak == pytest.approx(0.0)
    assert rx_peak == pytest.approx(response.selected_steering_angle_deg)
    assert response.metadata["pattern_source"] == "beamwidth_gaussian_proxy"


def test_two_way_proxy_is_pointwise_product_of_one_way_responses() -> None:
    response = prepare_d7_selected_directional_response(
        D7SelectedDirectionalRequest(
            mbes_beam_count=3,
            minimum_angle_deg=-30.0,
            maximum_angle_deg=30.0,
            selected_mbes_beam_index=1,
            response_sample_count=121,
        )
    )

    for tx_power, rx_power, two_way_power in zip(
        response.tx_one_way.normalized_power,
        response.rx_one_way.normalized_power,
        response.two_way.normalized_power,
        strict=True,
    ):
        assert two_way_power == pytest.approx(tx_power * rx_power)


def test_selected_beam_identity_is_tied_to_geometry_and_bounds_checked() -> None:
    response = prepare_d7_selected_directional_response(
        D7SelectedDirectionalRequest(mbes_beam_count=7, selected_mbes_beam_index=3)
    )
    assert response.selected_steering_angle_deg == pytest.approx(
        response.geometry.mbes.beams[3].steering_angle_deg
    )
    assert response.selected_endpoint_across_track_m == pytest.approx(
        response.geometry.mbes.beams[3].endpoint_across_track_m
    )

    with pytest.raises(ValueError, match="outside the canonical MBES beam plan"):
        prepare_d7_selected_directional_response(
            D7SelectedDirectionalRequest(mbes_beam_count=3, selected_mbes_beam_index=3)
        )

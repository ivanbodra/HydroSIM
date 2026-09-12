import pytest

from hydrosim.acquisition.beamwidth_pattern import beamwidth_gaussian_response
from hydrosim.app.d7_directional_response_api import (
    D7DirectionalResponseRequest,
    prepare_d7_directional_response,
)


def test_gaussian_proxy_has_exact_half_power_width() -> None:
    center = beamwidth_gaussian_response(angle_deg=10.0, steering_deg=10.0, hpbw_deg=4.0)
    left = beamwidth_gaussian_response(angle_deg=8.0, steering_deg=10.0, hpbw_deg=4.0)
    right = beamwidth_gaussian_response(angle_deg=12.0, steering_deg=10.0, hpbw_deg=4.0)
    assert center.normalized_power == pytest.approx(1.0)
    assert left.normalized_power == pytest.approx(0.5)
    assert right.normalized_power == pytest.approx(0.5)


def test_selected_rx_uses_canonical_port_positive_beam_and_tx_stays_nadir() -> None:
    response = prepare_d7_directional_response(
        D7DirectionalResponseRequest(
            mbes_beam_count=5,
            minimum_angle_deg=-40.0,
            maximum_angle_deg=40.0,
            selected_beam_index=3,
            angular_sample_count=81,
        )
    )
    assert response.selected_receive_steering_deg == pytest.approx(20.0)
    assert response.transmit_steering_deg == pytest.approx(0.0)
    assert response.rx.angle_deg[response.rx.normalized_power.index(max(response.rx.normalized_power))] == pytest.approx(20.0)
    assert response.tx.angle_deg[response.tx.normalized_power.index(max(response.tx.normalized_power))] == pytest.approx(0.0)


def test_two_way_response_is_pointwise_tx_rx_product() -> None:
    response = prepare_d7_directional_response(
        D7DirectionalResponseRequest(angular_sample_count=121)
    )
    assert response.two_way.normalized_power == pytest.approx(
        tuple(a * b for a, b in zip(response.tx.normalized_power, response.rx.normalized_power, strict=True))
    )
    assert response.two_way.normalized_field_amplitude == pytest.approx(
        tuple(
            a * b
            for a, b in zip(
                response.tx.normalized_field_amplitude,
                response.rx.normalized_field_amplitude,
                strict=True,
            )
        )
    )
    assert response.metadata["pattern_source"] == "beamwidth_gaussian_proxy"
    assert response.metadata["physical_array_inference"] == "none"


def test_selected_beam_index_must_exist() -> None:
    with pytest.raises(ValueError, match="selected_beam_index"):
        prepare_d7_directional_response(
            D7DirectionalResponseRequest(mbes_beam_count=5, selected_beam_index=5)
        )

import pytest

from hydrosim.app.beamforming_multibeam_api import (
    D6SharedRxMultibeamRequest,
    prepare_d6_shared_rx_multibeam_response,
)


def test_multibeam_reuses_one_rx_channel_snapshot() -> None:
    response = prepare_d6_shared_rx_multibeam_response(
        D6SharedRxMultibeamRequest(
            element_count=6,
            source_angle_deg=12.0,
            steering_angles_deg=(-20.0, 0.0, 20.0),
        )
    )

    assert len(response.shared_channels) == 6
    assert len(response.virtual_beams) == 3
    assert response.metadata["channel_snapshot"] == "one shared physical RX element snapshot"
    assert response.reference_channel_index == 0
    assert response.shared_channels[0].relative_arrival_offset_us == pytest.approx(0.0, abs=1e-12)


def test_each_virtual_beam_has_independent_canonical_delay_set() -> None:
    response = prepare_d6_shared_rx_multibeam_response(
        D6SharedRxMultibeamRequest(
            element_count=8,
            source_angle_deg=0.0,
            steering_angles_deg=(-30.0, 0.0, 30.0),
        )
    )

    port, nadir, starboard = response.virtual_beams
    assert port.steering_angle_deg == pytest.approx(-30.0)
    assert nadir.steering_angle_deg == pytest.approx(0.0)
    assert starboard.steering_angle_deg == pytest.approx(30.0)
    assert nadir.relative_compensation_delays_us == pytest.approx((0.0,) * 8, abs=1e-12)
    assert port.relative_compensation_delays_us != starboard.relative_compensation_delays_us
    assert port.steering_delay_gradient_us_per_element == pytest.approx(
        -starboard.steering_delay_gradient_us_per_element,
        abs=1e-12,
    )


def test_virtual_beam_matching_source_is_coherent_without_changing_shared_arrivals() -> None:
    response = prepare_d6_shared_rx_multibeam_response(
        D6SharedRxMultibeamRequest(
            element_count=8,
            source_angle_deg=20.0,
            steering_angles_deg=(0.0, 20.0),
        )
    )

    broadside, matched = response.virtual_beams
    assert matched.evaluated_array_factor_power == pytest.approx(1.0, abs=1e-12)
    assert matched.evaluated_physical_beam_power >= broadside.evaluated_physical_beam_power
    assert tuple(channel.index for channel in response.shared_channels) == tuple(range(8))


def test_multibeam_rejects_empty_duplicate_and_out_of_scan_steering_sets() -> None:
    with pytest.raises(ValueError, match="at least one"):
        D6SharedRxMultibeamRequest(steering_angles_deg=())
    with pytest.raises(ValueError, match="duplicates"):
        D6SharedRxMultibeamRequest(steering_angles_deg=(0.0, 0.0))
    with pytest.raises(ValueError, match="scan interval"):
        D6SharedRxMultibeamRequest(
            steering_angles_deg=(70.0,),
            scan_min_deg=-60.0,
            scan_max_deg=60.0,
        )

import pytest
from pydantic import ValidationError

from hydrosim.app.timing_api import D14TimingRequest, prepare_d14_timing_response


def test_d14_timing_preserves_ping_epochs_and_latency_shift() -> None:
    response = prepare_d14_timing_response(
        D14TimingRequest(
            trigger_time_s=10.0,
            tx_delay_ms=1.0,
            rx_start_delay_ms=2.0,
            rx_duration_ms=20.0,
            sensor_sample_time_s=9.995,
            sensor_latency_ms=8.0,
        )
    )

    assert response.trigger_time_s == pytest.approx(10.0)
    assert response.tx_time_s == pytest.approx(10.001)
    assert response.rx_start_time_s == pytest.approx(10.002)
    assert response.rx_end_time_s == pytest.approx(10.022)
    assert response.receive_duration_ms == pytest.approx(20.0)
    assert response.tx_to_rx_end_ms == pytest.approx(21.0)
    assert response.sensor_available_time_s == pytest.approx(10.003)
    assert response.metadata["unsupported"] == "temporal-to-spatial consequence"


def test_d14_timeline_is_chronologically_sorted() -> None:
    response = prepare_d14_timing_response(
        D14TimingRequest(
            trigger_time_s=1.0,
            tx_delay_ms=1.0,
            rx_start_delay_ms=2.0,
            rx_duration_ms=5.0,
            sensor_sample_time_s=0.999,
            sensor_latency_ms=10.0,
        )
    )

    event_times = [event.time_s for event in response.timeline]
    assert event_times == sorted(event_times)
    assert {event.kind for event in response.timeline} == {
        "trigger",
        "tx",
        "rx_start",
        "rx_end",
        "sensor_sample",
        "sensor_available",
    }


def test_d14_rejects_rx_start_before_tx() -> None:
    with pytest.raises(ValidationError, match="trigger_time <= tx_time <= rx_start_time <= rx_end_time"):
        prepare_d14_timing_response(
            D14TimingRequest(tx_delay_ms=5.0, rx_start_delay_ms=2.0)
        )


def test_d14_rejects_negative_latency() -> None:
    with pytest.raises(ValidationError):
        D14TimingRequest(sensor_latency_ms=-1.0)

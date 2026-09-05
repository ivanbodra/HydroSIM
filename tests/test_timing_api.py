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
    assert response.metadata["association_epoch"] == "sonar tx_time"


def test_d14_position_association_selects_latest_causally_available_sample() -> None:
    response = prepare_d14_timing_response(D14TimingRequest(
        trigger_time_s=0.0,
        tx_delay_ms=1000.0,
        rx_start_delay_ms=1000.0,
        sensor_sample_time_s=0.0,
        selected_streams=("position",),
        position_update_rate_hz=10.0,
        position_latency_ms=150.0,
        vessel_speed_mps=5.0,
    ))
    association = response.associations[0]
    assert association.available
    assert association.stream_id == "position"
    assert association.sample_time_s == pytest.approx(0.8)
    assert association.availability_time_s == pytest.approx(0.95)
    assert association.age_s == pytest.approx(0.2)
    assert association.along_track_timing_consequence_m == pytest.approx(-1.0)


def test_d14_position_and_attitude_associate_independently() -> None:
    response = prepare_d14_timing_response(D14TimingRequest(
        tx_delay_ms=1000.0,
        rx_start_delay_ms=1000.0,
        sensor_sample_time_s=0.0,
        position_update_rate_hz=2.0,
        attitude_update_rate_hz=10.0,
        position_latency_ms=100.0,
        attitude_latency_ms=50.0,
        vessel_speed_mps=4.0,
    ))
    position, attitude = response.associations
    assert position.sample_time_s == pytest.approx(0.5)
    assert attitude.sample_time_s == pytest.approx(0.9)
    assert position.age_s == pytest.approx(0.5)
    assert attitude.age_s == pytest.approx(0.1)
    assert attitude.along_track_timing_consequence_m is None


def test_d14_reports_unavailable_when_first_sample_has_not_arrived() -> None:
    response = prepare_d14_timing_response(D14TimingRequest(
        tx_delay_ms=10.0,
        rx_start_delay_ms=10.0,
        sensor_sample_time_s=1.0,
        selected_streams=("position",),
    ))
    assert not response.associations[0].available
    assert response.associations[0].sample_time_s is None


def test_d14_timeline_is_chronologically_sorted() -> None:
    response = prepare_d14_timing_response(D14TimingRequest(
        trigger_time_s=1.0, tx_delay_ms=1.0, rx_start_delay_ms=2.0,
        rx_duration_ms=5.0, sensor_sample_time_s=0.999, sensor_latency_ms=10.0,
    ))
    event_times = [event.time_s for event in response.timeline]
    assert event_times == sorted(event_times)
    assert {event.kind for event in response.timeline} == {
        "trigger", "tx", "rx_start", "rx_end", "sensor_sample", "sensor_available",
    }


def test_d14_rejects_rx_start_before_tx() -> None:
    with pytest.raises(ValidationError, match="trigger_time <= tx_time <= rx_start_time <= rx_end_time"):
        prepare_d14_timing_response(D14TimingRequest(tx_delay_ms=5.0, rx_start_delay_ms=2.0))


def test_d14_rejects_negative_latency() -> None:
    with pytest.raises(ValidationError):
        D14TimingRequest(sensor_latency_ms=-1.0)
    with pytest.raises(ValidationError):
        D14TimingRequest(position_latency_ms=-1.0)

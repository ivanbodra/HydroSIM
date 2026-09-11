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


def test_d14_fixed_clock_offset_changes_timestamp_not_physical_epochs() -> None:
    baseline = prepare_d14_timing_response(D14TimingRequest(
        trigger_time_s=10.0,
        tx_delay_ms=20.0,
        rx_start_delay_ms=20.0,
        sensor_sample_time_s=9.5,
        sensor_latency_ms=125.0,
        synchronization_mode="fixed_clock_offset",
        clock_offset_ms=0.0,
        apply_clock_correction=False,
    ))
    ahead = prepare_d14_timing_response(D14TimingRequest(
        trigger_time_s=10.0,
        tx_delay_ms=20.0,
        rx_start_delay_ms=20.0,
        sensor_sample_time_s=9.5,
        sensor_latency_ms=125.0,
        synchronization_mode="fixed_clock_offset",
        clock_offset_ms=250.0,
        apply_clock_correction=False,
    ))

    assert ahead.sensor_sample_time_s == pytest.approx(baseline.sensor_sample_time_s)
    assert ahead.sensor_available_time_s == pytest.approx(baseline.sensor_available_time_s)
    assert ahead.tx_time_s == pytest.approx(baseline.tx_time_s)
    assert ahead.clock_synchronization.sensor_reported_time_s == pytest.approx(9.75)
    assert ahead.clock_synchronization.clock_offset_s == pytest.approx(0.25)
    assert ahead.clock_synchronization.clock_epoch_error_s == pytest.approx(0.25)


def test_d14_known_clock_offset_correction_recovers_common_measurement_epoch() -> None:
    response = prepare_d14_timing_response(D14TimingRequest(
        sensor_sample_time_s=2.0,
        synchronization_mode="fixed_clock_offset",
        clock_offset_ms=-40.0,
        apply_clock_correction=True,
    ))
    clock = response.clock_synchronization

    assert clock.sensor_reported_time_s == pytest.approx(1.96)
    assert clock.corrected_common_time_s == pytest.approx(2.0)
    assert clock.interpreted_measurement_time_s == pytest.approx(2.0)
    assert clock.clock_epoch_error_s == pytest.approx(0.0, abs=1e-12)


def test_d14_latency_changes_availability_not_reported_timestamp() -> None:
    fast = prepare_d14_timing_response(D14TimingRequest(
        sensor_sample_time_s=1.0,
        sensor_latency_ms=10.0,
        synchronization_mode="fixed_clock_offset",
        clock_offset_ms=100.0,
    ))
    slow = prepare_d14_timing_response(D14TimingRequest(
        sensor_sample_time_s=1.0,
        sensor_latency_ms=210.0,
        synchronization_mode="fixed_clock_offset",
        clock_offset_ms=100.0,
    ))

    assert slow.clock_synchronization.sensor_reported_time_s == pytest.approx(
        fast.clock_synchronization.sensor_reported_time_s
    )
    assert slow.sensor_available_time_s - fast.sensor_available_time_s == pytest.approx(0.2)


def test_d14_ideal_common_time_rejects_nonzero_clock_offset() -> None:
    with pytest.raises(ValidationError, match="clock_offset_ms"):
        D14TimingRequest(synchronization_mode="ideal_common_time", clock_offset_ms=1.0)


def test_d14_rejects_rx_start_before_tx() -> None:
    with pytest.raises(ValidationError, match="trigger_time <= tx_time <= rx_start_time <= rx_end_time"):
        prepare_d14_timing_response(D14TimingRequest(tx_delay_ms=5.0, rx_start_delay_ms=2.0))


def test_d14_rejects_negative_latency() -> None:
    with pytest.raises(ValidationError):
        D14TimingRequest(sensor_latency_ms=-1.0)
    with pytest.raises(ValidationError):
        D14TimingRequest(position_latency_ms=-1.0)

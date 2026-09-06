import pytest

from hydrosim.integration import (
    ProtocolMessageAcceptance,
    PuInputProfile,
    SensorStreamProfile,
    evaluate_pu_sensor_compatibility,
)


def _serial_stream(**updates) -> SensorStreamProfile:
    values = dict(
        device_class="position_sensor",
        stream_id="GNSS-1",
        transport_kind="serial",
        port_id="COM1",
        baud_rate_baud=38400.0,
        protocol_id="marine_nav",
        message_id="position_fix",
        update_rate_hz=10.0,
        timestamp_source="gnss_utc",
    )
    values.update(updates)
    return SensorStreamProfile(**values)


def _pu_input(**updates) -> PuInputProfile:
    values = dict(
        input_id="PU-NAV-1",
        accepted_device_classes=("position_sensor",),
        accepted_transport_kinds=("serial",),
        accepted_serial_baud_rates=(38400.0, 115200.0),
        accepted_protocol_messages=(
            ProtocolMessageAcceptance(
                protocol_id="marine_nav",
                message_ids=("position_fix", "heading"),
            ),
        ),
        min_update_rate_hz=1.0,
        max_update_rate_hz=20.0,
        accepted_timestamp_sources=("gnss_utc",),
    )
    values.update(updates)
    return PuInputProfile(**values)


def test_serial_profile_is_compatible_when_all_declared_capabilities_match() -> None:
    result = evaluate_pu_sensor_compatibility(_serial_stream(), _pu_input())

    assert result.status == "compatible"
    assert result.reason_codes == ()
    assert result.nominal_update_period_s == pytest.approx(0.1)


def test_compatibility_reports_all_independent_mismatches_deterministically() -> None:
    stream = _serial_stream(
        device_class="attitude_sensor",
        baud_rate_baud=9600.0,
        protocol_id="unsupported_protocol",
        message_id="roll_pitch",
        update_rate_hz=50.0,
        timestamp_source="device_internal_clock",
    )

    result = evaluate_pu_sensor_compatibility(stream, _pu_input())

    assert result.status == "incompatible"
    assert result.reason_codes == (
        "device_class_mismatch",
        "serial_baud_mismatch",
        "protocol_mismatch",
        "update_rate_out_of_range",
        "time_source_mismatch",
    )


def test_message_mismatch_is_distinct_from_protocol_mismatch() -> None:
    result = evaluate_pu_sensor_compatibility(
        _serial_stream(message_id="unsupported_message"),
        _pu_input(),
    )

    assert result.reason_codes == ("message_mismatch",)


def test_network_stream_has_no_serial_baud_semantics() -> None:
    stream = SensorStreamProfile(
        device_class="echosounder",
        stream_id="MBES-1",
        transport_kind="network",
        network_transport="udp",
        network_endpoint="239.1.2.3:4001",
        protocol_id="generic_acoustic",
        message_id="detections",
        update_rate_hz=5.0,
        timestamp_source="pu_receive_time",
    )
    pu_input = PuInputProfile(
        input_id="PU-ACOUSTIC",
        accepted_device_classes=("echosounder",),
        accepted_transport_kinds=("network",),
        accepted_protocol_messages=(
            ProtocolMessageAcceptance(
                protocol_id="generic_acoustic",
                message_ids=("detections",),
            ),
        ),
        max_update_rate_hz=10.0,
        accepted_timestamp_sources=("pu_receive_time",),
    )

    assert evaluate_pu_sensor_compatibility(stream, pu_input).status == "compatible"

    invalid = stream.model_dump()
    invalid["baud_rate_baud"] = 38400.0
    with pytest.raises(ValueError, match="must not define serial baud"):
        SensorStreamProfile(**invalid)

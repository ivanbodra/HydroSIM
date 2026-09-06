"""Generic PED-D13 PU/sensor configuration compatibility model.

This module implements the vendor-neutral first-slice contract in
``docs/science/ped_d13_pu_sensor_integration_contract.md``. It evaluates declared
sensor-stream and PU-input capability profiles only; it does not simulate message
payloads, packet traffic, hardware interoperability, or timing/latency behavior.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DeviceClass = Literal[
    "position_sensor",
    "attitude_sensor",
    "sound_speed_sensor",
    "echosounder",
]
TransportKind = Literal["serial", "network"]
NetworkTransport = Literal["udp", "tcp"]
TimestampSource = Literal["device_internal_clock", "gnss_utc", "pu_receive_time"]
CompatibilityStatus = Literal["compatible", "incompatible"]
ReasonCode = Literal[
    "device_class_mismatch",
    "transport_mismatch",
    "serial_baud_mismatch",
    "protocol_mismatch",
    "message_mismatch",
    "update_rate_out_of_range",
    "time_source_mismatch",
    "missing_required_connection_parameter",
]


class SensorStreamProfile(BaseModel):
    """Configured logical sensor stream for the PED-D13 learner slice."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    device_class: DeviceClass
    stream_id: str = Field(min_length=1)
    transport_kind: TransportKind
    port_id: str | None = None
    baud_rate_baud: float | None = Field(default=None, gt=0.0)
    network_transport: NetworkTransport | None = None
    network_endpoint: str | None = None
    protocol_id: str = Field(min_length=1)
    message_id: str = Field(min_length=1)
    update_rate_hz: float = Field(gt=0.0)
    timestamp_source: TimestampSource

    @model_validator(mode="after")
    def validate_transport_fields(self) -> "SensorStreamProfile":
        if self.transport_kind == "serial":
            if self.port_id is None or self.baud_rate_baud is None:
                raise ValueError("serial streams require port_id and baud_rate_baud")
            if self.network_transport is not None or self.network_endpoint is not None:
                raise ValueError("serial streams must not define network transport fields")
        else:
            if self.network_transport is None or self.network_endpoint is None:
                raise ValueError("network streams require network_transport and network_endpoint")
            if self.baud_rate_baud is not None:
                raise ValueError("network streams must not define serial baud")
        return self


class ProtocolMessageAcceptance(BaseModel):
    """Accepted messages for one protocol family."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    protocol_id: str = Field(min_length=1)
    message_ids: tuple[str, ...] = Field(min_length=1)


class PuInputProfile(BaseModel):
    """Configured PU input capability profile."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    input_id: str = Field(min_length=1)
    accepted_device_classes: tuple[DeviceClass, ...] = Field(min_length=1)
    accepted_transport_kinds: tuple[TransportKind, ...] = Field(min_length=1)
    accepted_serial_baud_rates: tuple[float, ...] = ()
    accepted_protocol_messages: tuple[ProtocolMessageAcceptance, ...] = Field(min_length=1)
    min_update_rate_hz: float | None = Field(default=None, gt=0.0)
    max_update_rate_hz: float | None = Field(default=None, gt=0.0)
    accepted_timestamp_sources: tuple[TimestampSource, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_rate_range(self) -> "PuInputProfile":
        if (
            self.min_update_rate_hz is not None
            and self.max_update_rate_hz is not None
            and self.max_update_rate_hz < self.min_update_rate_hz
        ):
            raise ValueError("max_update_rate_hz must be greater than or equal to min_update_rate_hz")
        if any(value <= 0.0 for value in self.accepted_serial_baud_rates):
            raise ValueError("accepted_serial_baud_rates must contain only positive values")
        return self


class PuSensorCompatibilityResult(BaseModel):
    """Derived compatibility status and deterministic failed-condition reasons."""

    model_config = ConfigDict(frozen=True)

    status: CompatibilityStatus
    reason_codes: tuple[ReasonCode, ...]
    nominal_update_period_s: float = Field(gt=0.0)


def evaluate_pu_sensor_compatibility(
    stream: SensorStreamProfile,
    pu_input: PuInputProfile,
) -> PuSensorCompatibilityResult:
    """Evaluate compatibility from declared profiles only."""

    reasons: list[ReasonCode] = []

    if stream.device_class not in pu_input.accepted_device_classes:
        reasons.append("device_class_mismatch")

    if stream.transport_kind not in pu_input.accepted_transport_kinds:
        reasons.append("transport_mismatch")

    if stream.transport_kind == "serial":
        if stream.port_id is None or stream.baud_rate_baud is None:
            reasons.append("missing_required_connection_parameter")
        elif (
            pu_input.accepted_serial_baud_rates
            and stream.baud_rate_baud not in pu_input.accepted_serial_baud_rates
        ):
            reasons.append("serial_baud_mismatch")
    else:
        if stream.network_transport is None or stream.network_endpoint is None:
            reasons.append("missing_required_connection_parameter")

    protocol_entry = next(
        (
            item
            for item in pu_input.accepted_protocol_messages
            if item.protocol_id == stream.protocol_id
        ),
        None,
    )
    if protocol_entry is None:
        reasons.append("protocol_mismatch")
    elif stream.message_id not in protocol_entry.message_ids:
        reasons.append("message_mismatch")

    if (
        pu_input.min_update_rate_hz is not None
        and stream.update_rate_hz < pu_input.min_update_rate_hz
    ) or (
        pu_input.max_update_rate_hz is not None
        and stream.update_rate_hz > pu_input.max_update_rate_hz
    ):
        reasons.append("update_rate_out_of_range")

    if stream.timestamp_source not in pu_input.accepted_timestamp_sources:
        reasons.append("time_source_mismatch")

    unique_reasons = tuple(dict.fromkeys(reasons))
    return PuSensorCompatibilityResult(
        status="compatible" if not unique_reasons else "incompatible",
        reason_codes=unique_reasons,
        nominal_update_period_s=1.0 / stream.update_rate_hz,
    )

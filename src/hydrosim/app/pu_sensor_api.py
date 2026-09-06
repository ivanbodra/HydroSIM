"""Application adapter for PED-D13 PU/sensor integration compatibility."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from hydrosim.integration import (
    PuInputProfile,
    PuSensorCompatibilityResult,
    SensorStreamProfile,
    evaluate_pu_sensor_compatibility,
)


class D13PuSensorRequest(BaseModel):
    """Configured learner-selected stream and PU input capability profiles."""

    model_config = ConfigDict(extra="forbid")

    stream: SensorStreamProfile
    pu_input: PuInputProfile


class D13ConnectionSummary(BaseModel):
    """Render-ready configuration summary; no runtime communication claim."""

    model_config = ConfigDict(frozen=True)

    stream_id: str
    pu_input_id: str
    device_class: str
    transport_kind: str
    connection: str
    protocol_id: str
    message_id: str
    update_rate_hz: float
    nominal_update_period_s: float
    timestamp_source: str


class D13PuSensorResponse(BaseModel):
    """Stable PED-D13 response for the production frontend."""

    model_config = ConfigDict(frozen=True)

    status: str
    reason_codes: tuple[str, ...]
    summary: D13ConnectionSummary
    metadata: dict[str, str]


def prepare_d13_pu_sensor_response(request: D13PuSensorRequest) -> D13PuSensorResponse:
    """Evaluate compatibility in Python and serialize a render-ready result."""

    result: PuSensorCompatibilityResult = evaluate_pu_sensor_compatibility(
        request.stream,
        request.pu_input,
    )
    if request.stream.transport_kind == "serial":
        connection = (
            f"{request.stream.port_id} @ {request.stream.baud_rate_baud:g} Bd"
            if request.stream.port_id is not None and request.stream.baud_rate_baud is not None
            else "serial configuration incomplete"
        )
    else:
        connection = (
            f"{request.stream.network_transport}:{request.stream.network_endpoint}"
            if request.stream.network_transport is not None
            and request.stream.network_endpoint is not None
            else "network configuration incomplete"
        )

    return D13PuSensorResponse(
        status=result.status,
        reason_codes=result.reason_codes,
        summary=D13ConnectionSummary(
            stream_id=request.stream.stream_id,
            pu_input_id=request.pu_input.input_id,
            device_class=request.stream.device_class,
            transport_kind=request.stream.transport_kind,
            connection=connection,
            protocol_id=request.stream.protocol_id,
            message_id=request.stream.message_id,
            update_rate_hz=request.stream.update_rate_hz,
            nominal_update_period_s=result.nominal_update_period_s,
            timestamp_source=request.stream.timestamp_source,
        ),
        metadata={
            "state_semantics": "Configured profiles; Derived compatibility and summary",
            "compatibility_boundary": (
                "configuration compatibility only; no packet delivery, latency, "
                "hardware interoperability, or observation generation"
            ),
        },
    )

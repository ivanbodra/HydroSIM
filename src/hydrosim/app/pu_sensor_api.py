"""Application adapter for PED-D13 PU/sensor integration compatibility."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from hydrosim.integration import (
    ProtocolMessageAcceptance,
    PuInputProfile,
    PuSensorCompatibilityResult,
    SensorStreamProfile,
    evaluate_pu_sensor_compatibility,
)

D13PedagogicalPuProfileId = Literal["PU-A"]


PEDAGOGICAL_PU_PROFILES: dict[str, PuInputProfile] = {
    "PU-A": PuInputProfile(
        input_id="PU-A",
        accepted_device_classes=("position_sensor", "attitude_sensor"),
        accepted_transport_kinds=("serial", "network"),
        accepted_serial_baud_rates=(9600.0, 38400.0, 115200.0),
        accepted_protocol_messages=(
            ProtocolMessageAcceptance(protocol_id="nav", message_ids=("position",)),
            ProtocolMessageAcceptance(protocol_id="motion", message_ids=("attitude",)),
        ),
        min_update_rate_hz=1.0,
        max_update_rate_hz=20.0,
        accepted_timestamp_sources=("gnss_utc", "pu_receive_time"),
    ),
}


class D13PuSensorRequest(BaseModel):
    """Configured learner-selected stream plus API-owned or explicit PU profile."""

    model_config = ConfigDict(extra="forbid")

    stream: SensorStreamProfile
    pu_input_id: D13PedagogicalPuProfileId | None = None
    pu_input: PuInputProfile | None = None

    @model_validator(mode="after")
    def _validate_profile_source(self) -> "D13PuSensorRequest":
        if (self.pu_input_id is None) == (self.pu_input is None):
            raise ValueError("provide exactly one of pu_input_id or pu_input")
        return self


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
    pu_input_profile: PuInputProfile
    metadata: dict[str, str]


def _resolve_pu_input(request: D13PuSensorRequest) -> PuInputProfile:
    if request.pu_input is not None:
        return request.pu_input
    if request.pu_input_id is None:  # guarded by request validation
        raise RuntimeError("PU profile source was not resolved")
    return PEDAGOGICAL_PU_PROFILES[request.pu_input_id]


def prepare_d13_pu_sensor_response(request: D13PuSensorRequest) -> D13PuSensorResponse:
    """Evaluate compatibility in Python and serialize a render-ready result."""

    pu_input = _resolve_pu_input(request)
    result: PuSensorCompatibilityResult = evaluate_pu_sensor_compatibility(
        request.stream,
        pu_input,
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
            pu_input_id=pu_input.input_id,
            device_class=request.stream.device_class,
            transport_kind=request.stream.transport_kind,
            connection=connection,
            protocol_id=request.stream.protocol_id,
            message_id=request.stream.message_id,
            update_rate_hz=request.stream.update_rate_hz,
            nominal_update_period_s=result.nominal_update_period_s,
            timestamp_source=request.stream.timestamp_source,
        ),
        pu_input_profile=pu_input,
        metadata={
            "profile_authority": "Python/API-owned pedagogical profile when pu_input_id is used",
            "state_semantics": "Configured profiles; Derived compatibility and summary",
            "compatibility_boundary": (
                "configuration compatibility only; no packet delivery, latency, "
                "hardware interoperability, or observation generation"
            ),
        },
    )

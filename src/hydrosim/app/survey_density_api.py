"""Application adapter for the independent PED-D17 along-track spacing slice.

Coverage/gap and across-track density consequences are intentionally excluded until
an authoritative scientific contract defines them (see #352). This module exposes
only the kinematic consequence of configured vessel speed and ping rate.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

KNOT_TO_MPS = 0.5144444444444445


class D17SurveyDensityRequest(BaseModel):
    """Learner-configured acquisition cadence and vessel speed."""

    model_config = ConfigDict(extra="forbid")

    ping_rate_hz: float = Field(gt=0.0)
    vessel_speed_knots: float = Field(ge=0.0)


class D17SurveyDensityResponse(BaseModel):
    """Render-ready quantities that do not require a coverage model."""

    model_config = ConfigDict(frozen=True)

    ping_rate_hz: float
    ping_period_s: float
    vessel_speed_knots: float
    vessel_speed_mps: float
    along_track_ping_spacing_m: float
    status: str
    unsupported_consequences: tuple[str, ...]
    metadata: dict[str, str]


def prepare_d17_survey_density_response(
    request: D17SurveyDensityRequest,
) -> D17SurveyDensityResponse:
    """Derive deterministic along-track ping spacing from cadence and speed."""

    ping_period_s = 1.0 / request.ping_rate_hz
    vessel_speed_mps = request.vessel_speed_knots * KNOT_TO_MPS
    spacing_m = vessel_speed_mps * ping_period_s

    return D17SurveyDensityResponse(
        ping_rate_hz=request.ping_rate_hz,
        ping_period_s=ping_period_s,
        vessel_speed_knots=request.vessel_speed_knots,
        vessel_speed_mps=vessel_speed_mps,
        along_track_ping_spacing_m=spacing_m,
        status="partial",
        unsupported_consequences=("coverage_gap", "across_track_density"),
        metadata={
            "state_semantics": "Configured ping rate/speed; Derived period/speed/along-track spacing",
            "assumption": "constant vessel speed and ping rate between consecutive transmit epochs",
            "scientific_boundary": "coverage/gap and across-track density await #352",
        },
    )

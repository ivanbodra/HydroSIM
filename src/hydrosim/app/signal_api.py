"""Application/API bridge for the React PED-D2 Signal lesson.

The bridge deliberately exposes application-ready values derived from the canonical
Python waveform model. The frontend must not reimplement waveform physics.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import (
    prepare_signal_explorer_display_trace,
    prepare_signal_explorer_snapshot,
)


class SignalRequest(BaseModel):
    """Frontend-owned controls expressed in physical units."""

    model_config = ConfigDict(extra="forbid")

    pulse_type: Literal["cw", "lfm"] = "lfm"
    center_frequency_khz: float = Field(default=200.0, gt=0.0)
    duration_ms: float = Field(default=1.0, gt=0.0)
    bandwidth_khz: float = Field(default=100.0, gt=0.0)
    chirp_direction: Literal["up", "down"] = "up"
    envelope_model: Literal["rectangular", "tukey"] = "rectangular"


class TraceSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    x: tuple[float, ...]
    y: tuple[float, ...]
    x_unit: str
    y_unit: str


class SignalResponse(BaseModel):
    """Small stable contract consumed by the pedagogical frontend."""

    model_config = ConfigDict(frozen=True)

    pulse_type: Literal["cw", "lfm"]
    waveform: TraceSeries
    instantaneous_frequency: TraceSeries
    matched_filter: TraceSeries
    metadata: dict[str, float | str]


def prepare_signal_response(request: SignalRequest) -> SignalResponse:
    """Convert frontend controls to canonical Python models and render-ready values."""

    common = dict(
        center_frequency_hz=request.center_frequency_khz * 1e3,
        duration_seconds=request.duration_ms * 1e-3,
        envelope_model=request.envelope_model,
    )
    if request.pulse_type == "cw":
        pulse = ContinuousWavePulse(**common)
    else:
        pulse = LinearFMPulse(
            **common,
            bandwidth_hz=request.bandwidth_khz * 1e3,
            chirp_direction=request.chirp_direction,
        )

    highest_hz = max(
        float(pulse.center_frequency_hz),
        float(getattr(pulse, "start_frequency_hz", pulse.center_frequency_hz)),
        float(getattr(pulse, "end_frequency_hz", pulse.center_frequency_hz)),
    )
    display_rate = max(2.5e6, 6.0 * highest_hz)
    display = prepare_signal_explorer_display_trace(pulse, sample_rate_hz=display_rate)

    bandwidth_hz = float(getattr(pulse, "bandwidth_hz", 0.0))
    processing_rate = max(400e3, 2.5 * bandwidth_hz)
    processing = prepare_signal_explorer_snapshot(pulse, sample_rate_hz=processing_rate)

    time_ms = tuple(value * 1e3 for value in display.time_seconds)
    return SignalResponse(
        pulse_type=request.pulse_type,
        waveform=TraceSeries(
            x=time_ms,
            y=display.passband_amplitude,
            x_unit="ms",
            y_unit="relative amplitude",
        ),
        instantaneous_frequency=TraceSeries(
            x=time_ms,
            y=tuple(value / 1e3 for value in display.instantaneous_frequency_hz),
            x_unit="ms",
            y_unit="kHz",
        ),
        matched_filter=TraceSeries(
            x=tuple(value * 1e6 for value in processing.autocorrelation.lag_seconds),
            y=processing.autocorrelation.normalized_amplitude,
            x_unit="us",
            y_unit="normalized amplitude",
        ),
        metadata={
            "center_frequency_khz": request.center_frequency_khz,
            "duration_ms": request.duration_ms,
            "bandwidth_khz": request.bandwidth_khz if request.pulse_type == "lfm" else 0.0,
            "chirp_direction": request.chirp_direction if request.pulse_type == "lfm" else "none",
            "envelope_model": request.envelope_model,
            "waveform_representation": display.representation,
            "processing_representation": processing.representation,
        },
    )


def create_fastapi_app():
    """Create the optional local HTTP adapter used by Vite/React development."""

    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError as exc:  # pragma: no cover - exercised only without web extra
        raise RuntimeError(
            "Install HydroSIM with the 'web' extra to run the React bridge: pip install -e '.[web]'"
        ) from exc

    app = FastAPI(title="HydroSIM Pedagogical API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["POST", "GET"],
        allow_headers=["content-type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/pedagogical/signal", response_model=SignalResponse)
    def signal(request: SignalRequest) -> SignalResponse:
        return prepare_signal_response(request)

    return app


app = None
try:  # Let uvicorn import this module when the optional web dependencies exist.
    app = create_fastapi_app()
except RuntimeError:
    pass

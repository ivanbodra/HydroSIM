"""Application/API bridge for React PED-D1/PED-D2/PED-D3/PED-D4 pedagogical lessons.

The bridge exposes render-ready values derived from canonical Python models. The
frontend remains presentation-only and must not reimplement scientific equations.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.acquisition.wave_kinematics import (
    AcousticWaveKinematics,
    monostatic_two_way_range_offset,
)
from hydrosim.app.propagation_api import (
    D4PropagationRequest,
    D4PropagationResponse,
    prepare_d4_propagation_response,
)
from hydrosim.app.sonar_equation_api import (
    D3SonarEquationRequest,
    D3SonarEquationResponse,
    prepare_d3_sonar_equation_response,
)
from hydrosim.visualization import (
    prepare_signal_explorer_display_trace,
    prepare_signal_explorer_snapshot,
)


class SignalRequest(BaseModel):
    """Frontend-owned PED-D2 controls expressed in physical units."""

    model_config = ConfigDict(extra="forbid")

    pulse_type: Literal["cw", "lfm"] = "lfm"
    center_frequency_khz: float = Field(default=200.0, gt=0.0)
    duration_ms: float = Field(default=1.0, gt=0.0)
    bandwidth_khz: float = Field(default=100.0, gt=0.0)
    chirp_direction: Literal["up", "down"] = "up"
    envelope_model: Literal["rectangular", "tukey"] = "rectangular"


class WaveKinematicsRequest(BaseModel):
    """Frontend-owned PED-D1 Configured quantities and minimal view controls."""

    model_config = ConfigDict(extra="forbid")

    frequency_khz: float = Field(default=200.0, gt=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    normalized_amplitude: float = Field(default=1.0, ge=0.0)
    initial_phase_rad: float = 0.0
    sample_count: int = Field(default=256, ge=32, le=4096)
    display_cycles: float = Field(default=2.0, gt=0.0, le=10.0)
    snapshot_time_fraction_of_period: float = Field(default=0.0, ge=-10.0, le=10.0)
    range_lag_us: float | None = None


class TraceSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    x: tuple[float, ...]
    y: tuple[float, ...]
    x_unit: str
    y_unit: str


class SignalResponse(BaseModel):
    """Small stable PED-D2 contract consumed by the pedagogical frontend."""

    model_config = ConfigDict(frozen=True)

    pulse_type: Literal["cw", "lfm"]
    waveform: TraceSeries
    instantaneous_frequency: TraceSeries
    matched_filter: TraceSeries
    metadata: dict[str, float | str]


class WaveKinematicsResponse(BaseModel):
    """Render-ready PED-D1 Derived quantities from canonical wave kinematics."""

    model_config = ConfigDict(frozen=True)

    period_seconds: float
    wavelength_m: float
    temporal_waveform: TraceSeries
    spatial_waveform: TraceSeries
    range_offset_m: float | None
    metadata: dict[str, float | str]


def _uniform_samples(*, start: float, stop: float, count: int) -> tuple[float, ...]:
    if count == 1:
        return (start,)
    step = (stop - start) / float(count - 1)
    return tuple(start + index * step for index in range(count))


def prepare_wave_kinematics_response(request: WaveKinematicsRequest) -> WaveKinematicsResponse:
    """Convert PED-D1 controls to canonical kinematics and render-ready traces."""

    model = AcousticWaveKinematics(
        frequency_hz=request.frequency_khz * 1e3,
        sound_speed_mps=request.sound_speed_mps,
        normalized_amplitude=request.normalized_amplitude,
        initial_phase_rad=request.initial_phase_rad,
    )

    time_seconds = _uniform_samples(
        start=0.0,
        stop=request.display_cycles * model.period_seconds,
        count=request.sample_count,
    )
    snapshot_time = request.snapshot_time_fraction_of_period * model.period_seconds
    distance_m = _uniform_samples(
        start=0.0,
        stop=request.display_cycles * model.wavelength_m,
        count=request.sample_count,
    )

    temporal_amplitude = tuple(
        model.normalized_field(x_m=0.0, time_seconds=value) for value in time_seconds
    )
    spatial_amplitude = tuple(
        model.normalized_field(x_m=value, time_seconds=snapshot_time) for value in distance_m
    )

    range_offset_m = None
    if request.range_lag_us is not None:
        range_offset_m = monostatic_two_way_range_offset(
            lag_seconds=request.range_lag_us * 1e-6,
            sound_speed_mps=request.sound_speed_mps,
        )

    return WaveKinematicsResponse(
        period_seconds=model.period_seconds,
        wavelength_m=model.wavelength_m,
        temporal_waveform=TraceSeries(
            x=tuple(value * 1e3 for value in time_seconds),
            y=temporal_amplitude,
            x_unit="ms",
            y_unit="normalized amplitude",
        ),
        spatial_waveform=TraceSeries(
            x=distance_m,
            y=spatial_amplitude,
            x_unit="m",
            y_unit="normalized amplitude",
        ),
        range_offset_m=range_offset_m,
        metadata={
            "frequency_khz": request.frequency_khz,
            "sound_speed_mps": request.sound_speed_mps,
            "normalized_amplitude": request.normalized_amplitude,
            "initial_phase_rad": request.initial_phase_rad,
            "snapshot_time_fraction_of_period": request.snapshot_time_fraction_of_period,
            "field_representation": "normalized_1d_harmonic_plane_wave",
            "propagation_direction": "+x",
            "state_semantics": "Configured inputs; Derived outputs",
        },
    )


def prepare_signal_response(request: SignalRequest) -> SignalResponse:
    """Convert PED-D2 controls to canonical Python models and render-ready values."""

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
        from fastapi import FastAPI, HTTPException
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

    @app.post("/api/v1/pedagogical/wave-kinematics", response_model=WaveKinematicsResponse)
    def wave_kinematics(request: WaveKinematicsRequest) -> WaveKinematicsResponse:
        return prepare_wave_kinematics_response(request)

    @app.post("/api/v1/pedagogical/signal", response_model=SignalResponse)
    def signal(request: SignalRequest) -> SignalResponse:
        return prepare_signal_response(request)

    @app.post("/api/v1/pedagogical/sonar-equation", response_model=D3SonarEquationResponse)
    def sonar_equation(request: D3SonarEquationRequest) -> D3SonarEquationResponse:
        return prepare_d3_sonar_equation_response(request)

    @app.post("/api/v1/pedagogical/propagation", response_model=D4PropagationResponse)
    def propagation(request: D4PropagationRequest) -> D4PropagationResponse:
        try:
            return prepare_d4_propagation_response(request)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = None
try:  # Let uvicorn import this module when the optional web dependencies exist.
    app = create_fastapi_app()
except RuntimeError:
    pass

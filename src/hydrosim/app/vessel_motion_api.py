"""Application adapter for the PED-D12 vessel-motion learner slice.

The adapter converts learner-facing units to HydroSIM's canonical motion models and
serializes sampled Truth poses. It intentionally does not infer beam, sensor, or
sounding consequences that are not provided by the Scientific Core.
"""

from __future__ import annotations

from math import degrees, radians

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.geometry import Vector3
from hydrosim.motion.models import HarmonicSignal, StraightLineTrajectory, VesselMotionModel
from hydrosim.timing import SimulationTime


class D12AngularHarmonicRequest(BaseModel):
    """Configured angular harmonic expressed in learner-facing degrees."""

    model_config = ConfigDict(extra="forbid")

    amplitude_deg: float = 0.0
    period_seconds: float = Field(default=5.0, gt=0.0)
    phase_deg: float = 0.0


class D12HeaveHarmonicRequest(BaseModel):
    """Configured positive-Up heave harmonic."""

    model_config = ConfigDict(extra="forbid")

    amplitude_m: float = 0.0
    period_seconds: float = Field(default=5.0, gt=0.0)
    phase_deg: float = 0.0


class D12VesselMotionRequest(BaseModel):
    """Learner-configurable subset supported by the canonical motion core."""

    model_config = ConfigDict(extra="forbid")

    heading_deg: float = 0.0
    speed_mps: float = Field(default=0.0, ge=0.0)
    start_north_m: float = 0.0
    start_east_m: float = 0.0
    start_down_m: float = 0.0
    duration_seconds: float = Field(default=10.0, gt=0.0)
    sample_count: int = Field(default=101, ge=2, le=4096)
    roll: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    pitch: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    yaw_deviation: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    heave: D12HeaveHarmonicRequest = D12HeaveHarmonicRequest()


class D12VesselMotionSample(BaseModel):
    model_config = ConfigDict(frozen=True)

    time_seconds: float
    north_m: float
    east_m: float
    down_m: float
    roll_deg: float
    pitch_deg: float
    heading_deg: float
    yaw_deviation_deg: float
    heave_up_m: float


class D12VesselMotionResponse(BaseModel):
    """Render-ready sampled Truth poses from the canonical motion model."""

    model_config = ConfigDict(frozen=True)

    samples: tuple[D12VesselMotionSample, ...]
    metadata: dict[str, str]


def _angular_signal(request: D12AngularHarmonicRequest) -> HarmonicSignal:
    return HarmonicSignal(
        amplitude=radians(request.amplitude_deg),
        period_seconds=request.period_seconds,
        phase_rad=radians(request.phase_deg),
    )


def _heave_signal(request: D12HeaveHarmonicRequest) -> HarmonicSignal:
    return HarmonicSignal(
        amplitude=request.amplitude_m,
        period_seconds=request.period_seconds,
        phase_rad=radians(request.phase_deg),
    )


def prepare_d12_vessel_motion_response(
    request: D12VesselMotionRequest,
) -> D12VesselMotionResponse:
    """Sample canonical trajectory + vessel motion at uniform simulation times."""

    heading_rad = radians(request.heading_deg)
    model = VesselMotionModel(
        trajectory=StraightLineTrajectory(
            start_time=SimulationTime(seconds=0.0),
            start_position=Vector3(
                x=request.start_north_m,
                y=request.start_east_m,
                z=request.start_down_m,
            ),
            speed_mps=request.speed_mps,
            heading_rad=heading_rad,
            frame="N",
        ),
        roll=_angular_signal(request.roll),
        pitch=_angular_signal(request.pitch),
        yaw_deviation=_angular_signal(request.yaw_deviation),
        heave=_heave_signal(request.heave),
    )

    step = request.duration_seconds / float(request.sample_count - 1)
    samples: list[D12VesselMotionSample] = []
    for index in range(request.sample_count):
        time_seconds = index * step
        time = SimulationTime(seconds=time_seconds)
        pose = model.pose_at(time)
        yaw_deviation_rad = float(pose.attitude.yaw) - heading_rad
        heave_up_m = request.start_down_m - float(pose.position.z)
        samples.append(
            D12VesselMotionSample(
                time_seconds=time_seconds,
                north_m=float(pose.position.x),
                east_m=float(pose.position.y),
                down_m=float(pose.position.z),
                roll_deg=degrees(float(pose.attitude.roll)),
                pitch_deg=degrees(float(pose.attitude.pitch)),
                heading_deg=degrees(float(pose.attitude.yaw)),
                yaw_deviation_deg=degrees(yaw_deviation_rad),
                heave_up_m=heave_up_m,
            )
        )

    return D12VesselMotionResponse(
        samples=tuple(samples),
        metadata={
            "frame": "N (North-East-Down)",
            "heading_convention": "degrees clockwise from North",
            "heave_convention": "positive Up; subtracted from navigation Down coordinate",
            "state_semantics": "Configured inputs; Truth/Derived sampled outputs",
            "fidelity": "canonical deterministic trajectory and harmonic vessel motion only",
            "unsupported": "installation geometry, beam displacement, sounding consequences",
        },
    )

"""PED-D7 adapter for beamwidth-defined TX/RX directional responses."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.acquisition.beam_spacing import make_equiangular_beam_plan
from hydrosim.acquisition.beamwidth_pattern import beamwidth_gaussian_response


class D7DirectionalResponseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transmit_across_track_beamwidth_deg: float = Field(default=2.0, gt=0.0, lt=179.0)
    receive_across_track_beamwidth_deg: float = Field(default=1.0, gt=0.0, lt=179.0)
    mbes_beam_count: int = Field(default=9, ge=2, le=1024)
    minimum_angle_deg: float = Field(default=-60.0, gt=-89.0, lt=89.0)
    maximum_angle_deg: float = Field(default=60.0, gt=-89.0, lt=89.0)
    selected_beam_index: int = Field(default=4, ge=0)
    angular_sample_count: int = Field(default=241, ge=3, le=2001)


class D7DirectionalSeries(BaseModel):
    model_config = ConfigDict(frozen=True)

    angle_deg: tuple[float, ...]
    normalized_field_amplitude: tuple[float, ...]
    normalized_power: tuple[float, ...]


class D7DirectionalResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    selected_beam_index: int
    selected_receive_steering_deg: float
    transmit_steering_deg: float
    tx: D7DirectionalSeries
    rx: D7DirectionalSeries
    two_way: D7DirectionalSeries
    metadata: dict[str, str]


def _series(angles: tuple[float, ...], *, steering: float, hpbw: float) -> D7DirectionalSeries:
    samples = tuple(
        beamwidth_gaussian_response(angle_deg=a, steering_deg=steering, hpbw_deg=hpbw)
        for a in angles
    )
    return D7DirectionalSeries(
        angle_deg=angles,
        normalized_field_amplitude=tuple(float(s.normalized_field_amplitude) for s in samples),
        normalized_power=tuple(float(s.normalized_power) for s in samples),
    )


def prepare_d7_directional_response(request: D7DirectionalResponseRequest) -> D7DirectionalResponse:
    """Build render-ready selected TX/RX/two-way response from the scientific proxy."""
    if request.maximum_angle_deg <= request.minimum_angle_deg:
        raise ValueError("maximum_angle_deg must exceed minimum_angle_deg")
    plan = make_equiangular_beam_plan(
        minimum_angle_rad=__import__("math").radians(request.minimum_angle_deg),
        maximum_angle_rad=__import__("math").radians(request.maximum_angle_deg),
        beam_count=request.mbes_beam_count,
    )
    if request.selected_beam_index >= len(plan.across_track_angles_rad):
        raise ValueError("selected_beam_index must identify an MBES receive beam")
    selected_deg = __import__("math").degrees(plan.across_track_angles_rad[request.selected_beam_index])
    step = (request.maximum_angle_deg - request.minimum_angle_deg) / (request.angular_sample_count - 1)
    angles = tuple(request.minimum_angle_deg + i * step for i in range(request.angular_sample_count))
    tx = _series(angles, steering=0.0, hpbw=request.transmit_across_track_beamwidth_deg)
    rx = _series(angles, steering=selected_deg, hpbw=request.receive_across_track_beamwidth_deg)
    two_field = tuple(a * b for a, b in zip(tx.normalized_field_amplitude, rx.normalized_field_amplitude, strict=True))
    two_power = tuple(a * b for a, b in zip(tx.normalized_power, rx.normalized_power, strict=True))
    return D7DirectionalResponse(
        selected_beam_index=request.selected_beam_index,
        selected_receive_steering_deg=selected_deg,
        transmit_steering_deg=0.0,
        tx=tx,
        rx=rx,
        two_way=D7DirectionalSeries(angle_deg=angles, normalized_field_amplitude=two_field, normalized_power=two_power),
        metadata={
            "pattern_source": "beamwidth_gaussian_proxy",
            "angle_frame": "sensor across-track; positive Port (-Y), negative Starboard (+Y)",
            "power_convention": "normalized power; two-way P = P_tx * P_rx",
            "field_convention": "nonnegative normalized field amplitude; two-way B = B_tx * B_rx",
            "physical_array_inference": "none",
            "state_semantics": "Configured beamwidth/selection; Derived directional response",
        },
    )

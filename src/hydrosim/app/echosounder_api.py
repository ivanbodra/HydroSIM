"""Application adapter for PED-D8 SBES versus MBES geometry.

This module validates learner controls and serializes canonical Scientific Core
outputs. Beam spacing, layered propagation, and footprint equations remain in
``hydrosim.acquisition``.
"""

from __future__ import annotations

from math import copysign, degrees, radians
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.acquisition.beam_spacing import (
    BeamSteeringPlan,
    make_equiangular_beam_plan,
    make_equidistant_beam_plan,
)
from hydrosim.acquisition.footprint import (
    FlatSeafloorFootprintModel,
    estimate_flat_seafloor_footprint,
)
from hydrosim.acquisition.layered_propagation import (
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_to_depth,
)


class D8SoundSpeedLayerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top_depth_m: float = Field(ge=0.0)
    bottom_depth_m: float = Field(gt=0.0)
    sound_speed_mps: float = Field(gt=0.0)


class D8EchosounderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selected_system: Literal["sbes", "mbes"] = "mbes"
    vertical_separation_m: float = Field(default=100.0, gt=0.0)
    start_depth_m: float = Field(default=0.0, ge=0.0)
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    sound_speed_layers: tuple[D8SoundSpeedLayerRequest, ...] | None = None
    pulse_duration_ms: float = Field(default=0.2, gt=0.0)
    transmit_along_track_beamwidth_deg: float = Field(default=2.0, gt=0.0, lt=179.0)
    receive_across_track_beamwidth_deg: float = Field(default=1.0, gt=0.0, lt=179.0)
    mbes_beam_count: int = Field(default=9, ge=2, le=1024)
    minimum_angle_deg: float = Field(default=-60.0, gt=-89.0, lt=89.0)
    maximum_angle_deg: float = Field(default=60.0, gt=-89.0, lt=89.0)
    spacing_method: Literal["equiangular", "equidistant"] = "equiangular"

    @model_validator(mode="after")
    def _validate_sector(self) -> "D8EchosounderRequest":
        if self.maximum_angle_deg <= self.minimum_angle_deg:
            raise ValueError("maximum_angle_deg must exceed minimum_angle_deg")
        return self


class D8FootprintResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    beam_limited_along_track_width_m: float
    beam_limited_across_track_width_m: float
    pulse_limited_across_track_width_m: float | None
    effective_across_track_width_m: float
    effective_area_m2: float
    across_track_limiting_mechanism: str


class D8BeamResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    steering_angle_rad: float
    steering_angle_deg: float
    endpoint_across_track_m: float
    incidence_angle_from_normal_deg: float
    footprint: D8FootprintResult


class D8SystemResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    system: Literal["sbes", "mbes"]
    spacing_method: Literal["equiangular", "equidistant"] | None
    beams: tuple[D8BeamResult, ...]
    adjacent_across_track_spacings_m: tuple[float, ...]
    geometric_beam_center_swath_width_m: float
    target_across_track_positions_m: tuple[float, ...] | None


class D8EchosounderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    selected_system: Literal["sbes", "mbes"]
    target_depth_m: float
    sbes: D8SystemResult
    mbes: D8SystemResult
    metadata: dict[str, str | float | int]


def _build_profile(request: D8EchosounderRequest) -> LayeredSoundSpeedProfile:
    target_depth = request.start_depth_m + request.vertical_separation_m
    if request.sound_speed_layers is None:
        return LayeredSoundSpeedProfile(
            layers=(
                SoundSpeedLayer(
                    top_depth_m=request.start_depth_m,
                    bottom_depth_m=target_depth,
                    sound_speed_mps=request.sound_speed_mps,
                ),
            )
        )
    return LayeredSoundSpeedProfile(
        layers=tuple(
            SoundSpeedLayer(
                top_depth_m=layer.top_depth_m,
                bottom_depth_m=layer.bottom_depth_m,
                sound_speed_mps=layer.sound_speed_mps,
            )
            for layer in request.sound_speed_layers
        )
    )


def _trace_endpoint_and_incidence(
    *,
    profile: LayeredSoundSpeedProfile,
    angle_rad: float,
    target_depth_m: float,
    start_depth_m: float,
) -> tuple[float, float]:
    path = trace_layered_ray_to_depth(
        profile=profile,
        launch_angle_from_vertical_rad=abs(angle_rad),
        target_depth_m=target_depth_m,
        start_depth_m=start_depth_m,
    )
    endpoint = (
        copysign(float(path.horizontal_distance_m), angle_rad) if angle_rad != 0.0 else 0.0
    )
    incidence = float(path.segments[-1].angle_from_vertical_rad)
    return endpoint, incidence


def _footprint(
    request: D8EchosounderRequest, *, incidence_angle_rad: float
) -> D8FootprintResult:
    model = FlatSeafloorFootprintModel(
        transmit_along_track_beamwidth_rad=radians(request.transmit_along_track_beamwidth_deg),
        receive_across_track_beamwidth_rad=radians(request.receive_across_track_beamwidth_deg),
    )
    result = estimate_flat_seafloor_footprint(
        model=model,
        vertical_separation_m=request.vertical_separation_m,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=abs(incidence_angle_rad),
        pulse_duration_seconds=request.pulse_duration_ms * 1e-3,
        sound_speed_mps=request.sound_speed_mps,
    )
    return D8FootprintResult(
        beam_limited_along_track_width_m=float(result.beam_limited_along_track_width_m),
        beam_limited_across_track_width_m=float(result.beam_limited_across_track_width_m),
        pulse_limited_across_track_width_m=(
            None
            if result.pulse_limited_across_track_width_m is None
            else float(result.pulse_limited_across_track_width_m)
        ),
        effective_across_track_width_m=float(result.effective_across_track_width_m),
        effective_area_m2=float(result.effective_area_m2),
        across_track_limiting_mechanism=result.across_track_limiting_mechanism,
    )


def _beam_result(
    request: D8EchosounderRequest,
    *,
    profile: LayeredSoundSpeedProfile,
    target_depth_m: float,
    angle_rad: float,
) -> D8BeamResult:
    endpoint, incidence = _trace_endpoint_and_incidence(
        profile=profile,
        angle_rad=angle_rad,
        target_depth_m=target_depth_m,
        start_depth_m=request.start_depth_m,
    )
    return D8BeamResult(
        steering_angle_rad=angle_rad,
        steering_angle_deg=degrees(angle_rad),
        endpoint_across_track_m=endpoint,
        incidence_angle_from_normal_deg=degrees(incidence),
        footprint=_footprint(request, incidence_angle_rad=incidence),
    )


def _mbes_plan(
    request: D8EchosounderRequest,
    *,
    profile: LayeredSoundSpeedProfile,
    target_depth_m: float,
) -> BeamSteeringPlan:
    common = dict(
        minimum_angle_rad=radians(request.minimum_angle_deg),
        maximum_angle_rad=radians(request.maximum_angle_deg),
        beam_count=request.mbes_beam_count,
    )
    if request.spacing_method == "equiangular":
        return make_equiangular_beam_plan(**common)
    return make_equidistant_beam_plan(
        profile=profile,
        target_depth_m=target_depth_m,
        start_depth_m=request.start_depth_m,
        **common,
    )


def _system_result(
    *,
    system: Literal["sbes", "mbes"],
    spacing_method: Literal["equiangular", "equidistant"] | None,
    beams: tuple[D8BeamResult, ...],
    target_positions: tuple[float, ...] | None,
) -> D8SystemResult:
    endpoints = tuple(beam.endpoint_across_track_m for beam in beams)
    adjacent = tuple(b - a for a, b in zip(endpoints, endpoints[1:], strict=False))
    swath = 0.0 if len(endpoints) == 1 else max(endpoints) - min(endpoints)
    return D8SystemResult(
        system=system,
        spacing_method=spacing_method,
        beams=beams,
        adjacent_across_track_spacings_m=adjacent,
        geometric_beam_center_swath_width_m=swath,
        target_across_track_positions_m=target_positions,
    )


def prepare_d8_echosounder_response(request: D8EchosounderRequest) -> D8EchosounderResponse:
    """Build synchronized SBES/MBES geometry from canonical Core calls."""

    profile = _build_profile(request)
    target_depth = request.start_depth_m + request.vertical_separation_m
    profile.layer_at_depth(request.start_depth_m)
    profile.layer_at_depth(target_depth)

    sbes_beam = _beam_result(
        request,
        profile=profile,
        target_depth_m=target_depth,
        angle_rad=0.0,
    )
    sbes = _system_result(
        system="sbes",
        spacing_method=None,
        beams=(sbes_beam,),
        target_positions=None,
    )

    plan = _mbes_plan(request, profile=profile, target_depth_m=target_depth)
    mbes_beams = tuple(
        _beam_result(
            request,
            profile=profile,
            target_depth_m=target_depth,
            angle_rad=float(angle),
        )
        for angle in plan.across_track_angles_rad
    )
    targets = (
        None
        if plan.target_across_track_positions_m is None
        else tuple(float(value) for value in plan.target_across_track_positions_m)
    )
    mbes = _system_result(
        system="mbes",
        spacing_method=plan.spacing_method,
        beams=mbes_beams,
        target_positions=targets,
    )

    return D8EchosounderResponse(
        selected_system=request.selected_system,
        target_depth_m=target_depth,
        sbes=sbes,
        mbes=mbes,
        metadata={
            "depth_unit": "m",
            "distance_unit": "m",
            "angle_unit": "deg and rad",
            "pulse_duration_unit": "ms",
            "positive_across_track": "Port (-Y)",
            "negative_across_track": "Starboard (+Y)",
            "swath_definition": "max beam-centre endpoint - min beam-centre endpoint",
            "footprint_model": "canonical flat-seafloor half-power/pulse rectangular approximation",
            "state_semantics": "Configured inputs; Derived outputs",
            "validity": "horizontal flat seafloor; deterministic one-ping geometry",
            "mbes_beam_count": request.mbes_beam_count,
        },
    )

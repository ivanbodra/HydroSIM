"""Pedagogical scalar uncertainty mapping for PED-D18.

This module implements only the controlled analytical mapping defined in
``docs/science/ped_d18_scientific_contract.md`` and delegates covariance
propagation to the canonical uncertainty Core.
"""

from __future__ import annotations

from math import cos, sin, sqrt

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.integration.uncertainty import (
    InputSemanticState,
    UncertainInputSet,
    propagate_uncertainty,
)


class D18ScalarUncertaintyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slant_range_m: float = Field(default=30.0, gt=0.0)
    across_track_angle_rad: float = 0.0
    sound_speed_mps: float = Field(default=1500.0, gt=0.0)
    vessel_speed_mps: float = 0.0

    u_position_horizontal_m: float = Field(default=0.0, ge=0.0)
    u_attitude_roll_rad: float = Field(default=0.0, ge=0.0)
    u_range_m: float = Field(default=0.0, ge=0.0)
    u_sound_speed_mps: float = Field(default=0.0, ge=0.0)
    u_offset_across_m: float = Field(default=0.0, ge=0.0)
    u_timing_s: float = Field(default=0.0, ge=0.0)
    u_water_level_m: float = Field(default=0.0, ge=0.0)
    coverage_factor: float | None = Field(default=None, gt=0.0)


class D18VarianceContribution(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_id: str
    along_variance_m2: float
    across_variance_m2: float
    down_variance_m2: float


class D18ScalarUncertaintyResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    frame: str
    state: str
    method: str
    twtt_seconds: float
    component_ids: tuple[str, str, str]
    standard_uncertainty_m: tuple[float, float, float]
    covariance_m2: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    thu_m: float
    tvu_m: float
    combined_3d_standard_uncertainty_m: float
    expanded_uncertainty_m: tuple[float, float, float] | None
    coverage_factor: float | None
    variance_contributions: tuple[D18VarianceContribution, ...]
    metadata: dict[str, str | float]


def _diagonal(values: tuple[float, ...]) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(value * value if row == column else 0.0 for column, value in enumerate(values))
        for row, _ in enumerate(values)
    )


def prepare_d18_scalar_uncertainty_response(
    request: D18ScalarUncertaintyRequest,
) -> D18ScalarUncertaintyResponse:
    r = request.slant_range_m
    beta = request.across_track_angle_rad
    c = request.sound_speed_mps
    v = request.vessel_speed_mps
    twtt = 2.0 * r / c

    input_ids = (
        "p_h_along",
        "p_h_across",
        "roll",
        "range",
        "sound_speed",
        "offset_across",
        "timing",
        "water_level",
    )
    input_units = ("m", "m", "rad", "m", "m/s", "m", "s", "m")
    standard_inputs = (
        request.u_position_horizontal_m,
        request.u_position_horizontal_m,
        request.u_attitude_roll_rad,
        request.u_range_m,
        request.u_sound_speed_mps,
        request.u_offset_across_m,
        request.u_timing_s,
        request.u_water_level_m,
    )
    covariance = _diagonal(standard_inputs)

    s = sin(beta)
    k = cos(beta)
    half_twtt = 0.5 * twtt
    jacobian = (
        (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, v, 0.0),
        (0.0, 1.0, -r * k, -s, -half_twtt * s, 1.0, 0.0, 0.0),
        (0.0, 0.0, -r * s, k, half_twtt * k, 0.0, 0.0, 1.0),
    )

    inputs = UncertainInputSet(
        values=(0.0,) * 8,
        component_ids=input_ids,
        units=input_units,
        frame="local-along-across-down",
        covariance=covariance,
        component_states=(InputSemanticState.CONFIGURED,) * 8,
    )
    propagated = propagate_uncertainty(
        inputs,
        jacobian,
        result_component_ids=("along", "across", "down"),
        units=("m", "m", "m"),
        frame="local-along-across-down",
        coverage_factor=request.coverage_factor,
    )

    standard = tuple(float(value) for value in propagated.standard_uncertainty)
    covariance_out = tuple(
        tuple(float(value) for value in row) for row in propagated.covariance
    )

    contributions: list[D18VarianceContribution] = []
    for index, input_id in enumerate(input_ids):
        variance = standard_inputs[index] ** 2
        contributions.append(
            D18VarianceContribution(
                input_id=input_id,
                along_variance_m2=(jacobian[0][index] ** 2) * variance,
                across_variance_m2=(jacobian[1][index] ** 2) * variance,
                down_variance_m2=(jacobian[2][index] ** 2) * variance,
            )
        )

    expanded = None
    if propagated.expanded_uncertainty is not None:
        expanded = tuple(float(value) for value in propagated.expanded_uncertainty)

    return D18ScalarUncertaintyResponse(
        frame=propagated.frame,
        state=propagated.state.value,
        method=propagated.method,
        twtt_seconds=twtt,
        component_ids=("along", "across", "down"),
        standard_uncertainty_m=(standard[0], standard[1], standard[2]),
        covariance_m2=(covariance_out[0], covariance_out[1], covariance_out[2]),
        thu_m=sqrt(standard[0] ** 2 + standard[1] ** 2),
        tvu_m=standard[2],
        combined_3d_standard_uncertainty_m=sqrt(sum(value * value for value in standard)),
        expanded_uncertainty_m=expanded,
        coverage_factor=propagated.coverage_factor,
        variance_contributions=tuple(contributions),
        metadata={
            "input_state": "Configured",
            "output_state": "Derived",
            "angle_sign": "Port positive; Starboard negative",
            "vertical_axis": "+down",
            "model_scope": "controlled homogeneous first-order PED-D18 slice",
        },
    )

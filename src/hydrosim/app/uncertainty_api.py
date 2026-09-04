"""Application adapter for the PED-D18 uncertainty learner experience.

This module performs request validation and serialization only. Covariance
propagation, truth-error sign, verification residuals, semantic states, and
coverage handling remain owned by :mod:`hydrosim.integration.uncertainty`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hydrosim.integration.uncertainty import (
    InputSemanticState,
    UncertainInputSet,
    compute_truth_error,
    compute_verification_residual,
    propagate_uncertainty,
)


class D18UncertaintyRequest(BaseModel):
    """Configured first-slice inputs for pedagogical uncertainty propagation."""

    model_config = ConfigDict(extra="forbid")

    values: tuple[float, ...]
    component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    covariance: tuple[tuple[float, ...], ...]
    component_states: tuple[Literal["Observed", "Configured", "Estimated"], ...]
    jacobian: tuple[tuple[float, ...], ...]
    result_component_ids: tuple[str, ...]
    result_units: tuple[str, ...]
    result_frame: str
    coverage_factor: float | None = Field(default=None, gt=0.0)
    coverage_probability: float | None = Field(default=None, gt=0.0, le=1.0)
    derived_value: tuple[float, ...] | None = None
    truth_value: tuple[float, ...] | None = None
    truth_component_ids: tuple[str, ...] | None = None
    truth_units: tuple[str, ...] | None = None
    truth_frame: str | None = None
    verification_value_a: tuple[float, ...] | None = None
    verification_value_b: tuple[float, ...] | None = None
    verification_association_a: str | None = None
    verification_association_b: str | None = None
    verification_component_ids: tuple[str, ...] | None = None
    verification_units: tuple[str, ...] | None = None
    verification_frame: str | None = None

    @model_validator(mode="after")
    def optional_pairs_must_be_complete(self) -> "D18UncertaintyRequest":
        truth_values = (self.derived_value, self.truth_value)
        if any(value is not None for value in truth_values):
            required = (
                self.derived_value,
                self.truth_value,
                self.truth_component_ids,
                self.truth_units,
                self.truth_frame,
            )
            if any(value is None for value in required):
                raise ValueError("truth-error inputs must be supplied as a complete set")

        verification_values = (self.verification_value_a, self.verification_value_b)
        if any(value is not None for value in verification_values):
            required = (
                self.verification_value_a,
                self.verification_value_b,
                self.verification_association_a,
                self.verification_association_b,
                self.verification_component_ids,
                self.verification_units,
                self.verification_frame,
            )
            if any(value is None for value in required):
                raise ValueError("verification-residual inputs must be supplied as a complete set")
        return self


class D18TruthErrorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    derived_value: tuple[float, ...]
    truth_value: tuple[float, ...]
    error_vector: tuple[float, ...]
    component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    state: str
    sign_convention: str = "Derived - Truth"


class D18VerificationResidualResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    value_a: tuple[float, ...]
    value_b: tuple[float, ...]
    residual: tuple[float, ...]
    association_a: str
    association_b: str
    component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    state: str
    sign_convention: str = "A - B"


class D18UncertaintyResponse(BaseModel):
    """Render-ready view of the canonical versioned uncertainty contract."""

    model_config = ConfigDict(frozen=True)

    schema_version: str
    method: str
    input_component_ids: tuple[str, ...]
    input_units: tuple[str, ...]
    input_frame: str
    input_states: tuple[str, ...]
    input_covariance: tuple[tuple[float, ...], ...]
    result_component_ids: tuple[str, ...]
    result_units: tuple[str, ...]
    result_frame: str
    propagated_covariance: tuple[tuple[float, ...], ...]
    standard_uncertainty: tuple[float, ...]
    coverage_factor: float | None
    coverage_probability: float | None
    expanded_uncertainty: tuple[float, ...] | None
    state: str
    truth_error: D18TruthErrorResponse | None = None
    verification_residual: D18VerificationResidualResponse | None = None


def _matrix_tuple(values) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(float(value) for value in row) for row in values)


def _vector_tuple(values) -> tuple[float, ...]:
    return tuple(float(value) for value in values)


def prepare_d18_uncertainty_response(request: D18UncertaintyRequest) -> D18UncertaintyResponse:
    inputs = UncertainInputSet(
        values=request.values,
        component_ids=request.component_ids,
        units=request.units,
        frame=request.frame,
        covariance=request.covariance,
        component_states=tuple(InputSemanticState(state) for state in request.component_states),
    )
    propagated = propagate_uncertainty(
        inputs,
        request.jacobian,
        result_component_ids=request.result_component_ids,
        units=request.result_units,
        frame=request.result_frame,
        coverage_factor=request.coverage_factor,
        coverage_probability=request.coverage_probability,
    )

    truth_error = None
    if request.derived_value is not None:
        result = compute_truth_error(
            request.derived_value,
            request.truth_value,
            component_ids=request.truth_component_ids,
            units=request.truth_units,
            frame=request.truth_frame,
        )
        truth_error = D18TruthErrorResponse(
            derived_value=_vector_tuple(result.derived_value),
            truth_value=_vector_tuple(result.truth_value),
            error_vector=_vector_tuple(result.truth_error_vector),
            component_ids=result.component_ids,
            units=result.units,
            frame=result.frame,
            state=result.state.value,
        )

    verification = None
    if request.verification_value_a is not None:
        result = compute_verification_residual(
            request.verification_value_a,
            request.verification_value_b,
            association_a=request.verification_association_a,
            association_b=request.verification_association_b,
            component_ids=request.verification_component_ids,
            units=request.verification_units,
            frame=request.verification_frame,
        )
        verification = D18VerificationResidualResponse(
            value_a=_vector_tuple(result.value_a),
            value_b=_vector_tuple(result.value_b),
            residual=_vector_tuple(result.verification_residual),
            association_a=result.association_a,
            association_b=result.association_b,
            component_ids=result.component_ids,
            units=result.units,
            frame=result.frame,
            state=result.state.value,
        )

    return D18UncertaintyResponse(
        schema_version=propagated.schema_version,
        method=propagated.method,
        input_component_ids=inputs.component_ids,
        input_units=inputs.units,
        input_frame=inputs.frame,
        input_states=tuple(state.value for state in inputs.component_states),
        input_covariance=_matrix_tuple(inputs.covariance),
        result_component_ids=propagated.result_component_ids,
        result_units=propagated.units,
        result_frame=propagated.frame,
        propagated_covariance=_matrix_tuple(propagated.covariance),
        standard_uncertainty=_vector_tuple(propagated.standard_uncertainty),
        coverage_factor=propagated.coverage_factor,
        coverage_probability=propagated.coverage_probability,
        expanded_uncertainty=(
            None if propagated.expanded_uncertainty is None else _vector_tuple(propagated.expanded_uncertainty)
        ),
        state=propagated.state.value,
        truth_error=truth_error,
        verification_residual=verification,
    )

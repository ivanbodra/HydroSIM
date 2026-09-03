"""Versioned uncertainty, truth-error, and verification-residual contracts.

This module implements the minimum scientific API defined by
``docs/science/uncertainty_error_verification_contract.md``.  It deliberately
keeps a-priori uncertainty, simulation-truth error, and a-posteriori
verification residuals as separate types and operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence
import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray


SCHEMA_VERSION = "0.1"
_FLOAT = np.float64


class InputSemanticState(str, Enum):
    """Allowed semantic states for uncertain input quantities."""

    OBSERVED = "Observed"
    CONFIGURED = "Configured"
    ESTIMATED = "Estimated"


class DerivedSemanticState(str, Enum):
    """Semantic state used by results computed by this module."""

    DERIVED = "Derived"


def _vector(values: ArrayLike, *, name: str) -> NDArray[np.float64]:
    vector = np.asarray(values, dtype=_FLOAT)
    if vector.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional vector")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def _matrix(values: ArrayLike, *, name: str) -> NDArray[np.float64]:
    matrix = np.asarray(values, dtype=_FLOAT)
    if matrix.ndim != 2:
        raise ValueError(f"{name} must be a two-dimensional matrix")
    if not np.all(np.isfinite(matrix)):
        raise ValueError(f"{name} must contain only finite values")
    return matrix


def _validate_covariance(
    covariance: ArrayLike,
    *,
    dimension: int,
    name: str,
    atol: float = 1e-12,
) -> NDArray[np.float64]:
    matrix = _matrix(covariance, name=name)
    if matrix.shape != (dimension, dimension):
        raise ValueError(f"{name} must have shape ({dimension}, {dimension})")
    if np.any(np.diag(matrix) < -atol):
        raise ValueError(f"{name} diagonal variances must be non-negative")
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=atol):
        raise ValueError(f"{name} must be symmetric")
    eigenvalues = np.linalg.eigvalsh(matrix)
    scale = max(1.0, float(np.max(np.abs(matrix))))
    if float(np.min(eigenvalues)) < -atol * scale:
        raise ValueError(f"{name} must be positive semidefinite")
    return matrix


def _metadata_lengths(
    component_ids: Sequence[str], units: Sequence[str], *, dimension: int
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    ids = tuple(component_ids)
    unit_tuple = tuple(units)
    if len(ids) != dimension:
        raise ValueError("component_ids length must match vector dimension")
    if len(unit_tuple) != dimension:
        raise ValueError("units length must match vector dimension")
    if len(set(ids)) != len(ids):
        raise ValueError("component_ids must be unique and ordered")
    return ids, unit_tuple


@dataclass
class UncertainInputSet:
    """Ordered uncertain inputs and their full covariance matrix, schema v0.1."""

    values: ArrayLike
    component_ids: Sequence[str]
    units: Sequence[str]
    frame: str
    covariance: ArrayLike
    component_states: Sequence[InputSemanticState | str]
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def __post_init__(self) -> None:
        self.values = _vector(self.values, name="values")
        self.component_ids, self.units = _metadata_lengths(
            self.component_ids, self.units, dimension=self.values.size
        )
        if not self.frame:
            raise ValueError("frame must be declared")
        self.covariance = _validate_covariance(
            self.covariance,
            dimension=self.values.size,
            name="covariance",
        )
        states = tuple(InputSemanticState(state) for state in self.component_states)
        if len(states) != self.values.size:
            raise ValueError("component_states length must match vector dimension")
        self.component_states = states

    @property
    def state(self) -> InputSemanticState | tuple[InputSemanticState, ...]:
        """Return a single state for homogeneous inputs, otherwise per-component states."""

        if all(state == self.component_states[0] for state in self.component_states):
            return self.component_states[0]
        return self.component_states


@dataclass
class PropagatedUncertainty:
    """Linearized output covariance and standard uncertainties, schema v0.1."""

    result_component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    covariance: NDArray[np.float64]
    standard_uncertainty: NDArray[np.float64]
    coverage_factor: float | None = None
    coverage_probability: float | None = None
    expanded_uncertainty: NDArray[np.float64] | None = None
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    method: str = field(default="linearized_jacobian", init=False)
    state: DerivedSemanticState = field(default=DerivedSemanticState.DERIVED, init=False)


@dataclass
class TruthErrorVector:
    """Canonical simulation truth error, defined strictly as Derived minus Truth."""

    derived_value: NDArray[np.float64]
    truth_value: NDArray[np.float64]
    truth_error_vector: NDArray[np.float64]
    component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    state: DerivedSemanticState = field(default=DerivedSemanticState.DERIVED, init=False)

    @property
    def error_vector(self) -> NDArray[np.float64]:
        """Deprecated compatibility alias preserving the canonical sign exactly."""

        warnings.warn(
            "error_vector is ambiguous; use truth_error_vector",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.truth_error_vector


@dataclass
class VerificationResidual:
    """Ordered A-minus-B verification residual, distinct from truth error."""

    value_a: NDArray[np.float64]
    value_b: NDArray[np.float64]
    verification_residual: NDArray[np.float64]
    association_a: str
    association_b: str
    component_ids: tuple[str, ...]
    units: tuple[str, ...]
    frame: str
    covariance: NDArray[np.float64] | None = None
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
    state: DerivedSemanticState = field(default=DerivedSemanticState.DERIVED, init=False)


def propagate_uncertainty(
    inputs: UncertainInputSet,
    jacobian: ArrayLike,
    *,
    result_component_ids: Sequence[str],
    units: Sequence[str],
    frame: str,
    coverage_factor: float | None = None,
    coverage_probability: float | None = None,
) -> PropagatedUncertainty:
    """Propagate covariance with the local first-order relation ``J Sigma_x J^T``.

    The caller owns the scientific validity of the supplied Jacobian at the
    stated nominal/configured point.  This function does not imply that the
    linearized covariance is exact outside that local validity boundary.
    """

    jac = _matrix(jacobian, name="jacobian")
    if jac.shape[1] != inputs.values.size:
        raise ValueError("jacobian input dimension must match uncertain inputs")
    output_dimension = jac.shape[0]
    ids, output_units = _metadata_lengths(
        result_component_ids, units, dimension=output_dimension
    )
    if not frame:
        raise ValueError("frame must be declared")

    sigma_y = jac @ inputs.covariance @ jac.T
    sigma_y = 0.5 * (sigma_y + sigma_y.T)
    sigma_y = _validate_covariance(
        sigma_y,
        dimension=output_dimension,
        name="propagated covariance",
    )
    standard = np.sqrt(np.clip(np.diag(sigma_y), 0.0, None))

    if coverage_factor is not None and coverage_factor <= 0.0:
        raise ValueError("coverage_factor must be positive")
    if coverage_probability is not None and not 0.0 < coverage_probability <= 1.0:
        raise ValueError("coverage_probability must be in (0, 1]")
    expanded = None if coverage_factor is None else coverage_factor * standard

    return PropagatedUncertainty(
        result_component_ids=ids,
        units=output_units,
        frame=frame,
        covariance=sigma_y,
        standard_uncertainty=standard,
        coverage_factor=coverage_factor,
        coverage_probability=coverage_probability,
        expanded_uncertainty=expanded,
    )


def compute_truth_error(
    derived_value: ArrayLike,
    truth_value: ArrayLike,
    *,
    component_ids: Sequence[str],
    units: Sequence[str],
    frame: str,
) -> TruthErrorVector:
    """Return the canonical ``Derived - Truth`` simulation error vector."""

    derived = _vector(derived_value, name="derived_value")
    truth = _vector(truth_value, name="truth_value")
    if derived.shape != truth.shape:
        raise ValueError("derived_value and truth_value must have the same shape")
    ids, unit_tuple = _metadata_lengths(component_ids, units, dimension=derived.size)
    if not frame:
        raise ValueError("frame must be declared")
    return TruthErrorVector(
        derived_value=derived,
        truth_value=truth,
        truth_error_vector=derived - truth,
        component_ids=ids,
        units=unit_tuple,
        frame=frame,
    )


def compute_verification_residual(
    value_a: ArrayLike,
    value_b: ArrayLike,
    *,
    association_a: str,
    association_b: str,
    component_ids: Sequence[str],
    units: Sequence[str],
    frame: str,
    covariance_a: ArrayLike | None = None,
    covariance_b: ArrayLike | None = None,
    cross_covariance_ab: ArrayLike | None = None,
) -> VerificationResidual:
    """Return ordered ``A - B`` residual and, when supplied, its covariance.

    If covariance is requested both individual covariances are required.  An
    omitted cross-covariance means no cross-covariance information is available
    and is therefore treated as zero; callers with known common-mode covariance
    must provide it explicitly.
    """

    a = _vector(value_a, name="value_a")
    b = _vector(value_b, name="value_b")
    if a.shape != b.shape:
        raise ValueError("value_a and value_b must have the same shape")
    dimension = a.size
    ids, unit_tuple = _metadata_lengths(component_ids, units, dimension=dimension)
    if not association_a or not association_b:
        raise ValueError("both residual associations must be declared")
    if not frame:
        raise ValueError("frame must be declared")

    residual_covariance = None
    covariance_requested = any(
        item is not None for item in (covariance_a, covariance_b, cross_covariance_ab)
    )
    if covariance_requested:
        if covariance_a is None or covariance_b is None:
            raise ValueError("covariance_a and covariance_b are both required")
        sigma_a = _validate_covariance(
            covariance_a, dimension=dimension, name="covariance_a"
        )
        sigma_b = _validate_covariance(
            covariance_b, dimension=dimension, name="covariance_b"
        )
        if cross_covariance_ab is None:
            sigma_ab = np.zeros((dimension, dimension), dtype=_FLOAT)
        else:
            sigma_ab = _matrix(cross_covariance_ab, name="cross_covariance_ab")
            if sigma_ab.shape != (dimension, dimension):
                raise ValueError(
                    f"cross_covariance_ab must have shape ({dimension}, {dimension})"
                )
        residual_covariance = sigma_a + sigma_b - sigma_ab - sigma_ab.T
        residual_covariance = 0.5 * (
            residual_covariance + residual_covariance.T
        )
        residual_covariance = _validate_covariance(
            residual_covariance,
            dimension=dimension,
            name="verification residual covariance",
        )

    return VerificationResidual(
        value_a=a,
        value_b=b,
        verification_residual=a - b,
        association_a=association_a,
        association_b=association_b,
        component_ids=ids,
        units=unit_tuple,
        frame=frame,
        covariance=residual_covariance,
    )

import numpy as np
import pytest

from hydrosim.integration import (
    DerivedSemanticState,
    InputSemanticState,
    TruthErrorVector,
    UncertainInputSet,
    VerificationResidual,
    compute_truth_error,
    compute_verification_residual,
    propagate_uncertainty,
)


def _inputs(values, covariance, component_ids=None):
    dimension = len(values)
    return UncertainInputSet(
        values=values,
        component_ids=component_ids or tuple(f"x{i}" for i in range(dimension)),
        units=("m",) * dimension,
        frame="local_ned",
        covariance=covariance,
        component_states=(InputSemanticState.CONFIGURED,) * dimension,
    )


def test_identity_covariance_propagation():
    sigma_x = np.array([[4.0, 1.2], [1.2, 9.0]])
    inputs = _inputs([10.0, 20.0], sigma_x)

    result = propagate_uncertainty(
        inputs,
        np.eye(2),
        result_component_ids=("north", "east"),
        units=("m", "m"),
        frame="local_ned",
    )

    np.testing.assert_allclose(result.covariance, sigma_x)
    np.testing.assert_allclose(result.standard_uncertainty, [2.0, 3.0])
    assert result.method == "linearized_jacobian"
    assert result.state is DerivedSemanticState.DERIVED
    assert result.schema_version == "0.1"


def test_scalar_linear_covariance_propagation():
    inputs = _inputs([5.0], [[0.25]], component_ids=("range",))

    result = propagate_uncertainty(
        inputs,
        [[3.0]],
        result_component_ids=("scaled_range",),
        units=("m",),
        frame="local_ned",
    )

    assert result.covariance[0, 0] == pytest.approx(2.25)
    assert result.standard_uncertainty[0] == pytest.approx(1.5)


def test_correlated_sum_retains_covariance_contribution():
    sigma_x = np.array([[4.0, 1.5], [1.5, 9.0]])
    inputs = _inputs([0.0, 0.0], sigma_x)

    result = propagate_uncertainty(
        inputs,
        [[1.0, 1.0]],
        result_component_ids=("sum",),
        units=("m",),
        frame="local_ned",
    )

    assert result.covariance[0, 0] == pytest.approx(16.0)
    assert result.covariance[0, 0] != pytest.approx(13.0)


def test_correlated_difference_can_cancel_common_mode_uncertainty():
    sigma = 4.0
    result = compute_verification_residual(
        [12.0],
        [11.5],
        association_a="main-line",
        association_b="cross-line",
        component_ids=("depth",),
        units=("m",),
        frame="chart_datum_depth",
        covariance_a=[[sigma]],
        covariance_b=[[sigma]],
        cross_covariance_ab=[[sigma]],
    )

    assert result.verification_residual[0] == pytest.approx(0.5)
    assert result.covariance is not None
    assert result.covariance[0, 0] == pytest.approx(0.0)


def test_truth_error_uses_derived_minus_truth_sign():
    result = compute_truth_error(
        [11.0, 18.0, 33.0],
        [10.0, 20.0, 30.0],
        component_ids=("north", "east", "down"),
        units=("m", "m", "m"),
        frame="local_ned",
    )

    np.testing.assert_allclose(result.truth_error_vector, [1.0, -2.0, 3.0])
    assert isinstance(result, TruthErrorVector)
    assert result.state is DerivedSemanticState.DERIVED
    with pytest.warns(DeprecationWarning):
        np.testing.assert_allclose(result.error_vector, result.truth_error_vector)


def test_verification_residual_preserves_operand_order():
    ab = compute_verification_residual(
        [12.0],
        [11.5],
        association_a="A",
        association_b="B",
        component_ids=("depth",),
        units=("m",),
        frame="chart_datum_depth",
    )
    ba = compute_verification_residual(
        [11.5],
        [12.0],
        association_a="B",
        association_b="A",
        component_ids=("depth",),
        units=("m",),
        frame="chart_datum_depth",
    )

    assert ab.verification_residual[0] == pytest.approx(0.5)
    assert ba.verification_residual[0] == pytest.approx(-0.5)
    assert ab.association_a == "A"
    assert ab.association_b == "B"


def test_uncertainty_truth_error_and_residual_are_distinct_api_types():
    inputs = UncertainInputSet(
        values=[1.0, 2.0],
        component_ids=("along_track", "across_track"),
        units=("m", "m"),
        frame="vessel_local",
        covariance=[[1.0, 0.25], [0.25, 2.0]],
        component_states=("Observed", "Estimated"),
    )
    propagated = propagate_uncertainty(
        inputs,
        np.eye(2),
        result_component_ids=("along_track", "across_track"),
        units=("m", "m"),
        frame="vessel_local",
    )
    truth_error = compute_truth_error(
        [1.1, 1.9],
        [1.0, 2.0],
        component_ids=("along_track", "across_track"),
        units=("m", "m"),
        frame="vessel_local",
    )
    residual = compute_verification_residual(
        [1.1, 1.9],
        [1.05, 2.0],
        association_a="line-A",
        association_b="line-B",
        component_ids=("along_track", "across_track"),
        units=("m", "m"),
        frame="vessel_local",
    )

    assert propagated.__class__ is not TruthErrorVector
    assert isinstance(residual, VerificationResidual)
    assert not hasattr(propagated, "truth_error_vector")
    assert not hasattr(truth_error, "verification_residual")
    assert not hasattr(residual, "standard_uncertainty")
    assert inputs.state == (
        InputSemanticState.OBSERVED,
        InputSemanticState.ESTIMATED,
    )


def test_covariance_validation_rejects_non_psd_matrix():
    with pytest.raises(ValueError, match="positive semidefinite"):
        _inputs([0.0, 0.0], [[1.0, 2.0], [2.0, 1.0]])

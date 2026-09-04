import math

import pytest

from hydrosim.app.uncertainty_api import D18UncertaintyRequest, prepare_d18_uncertainty_response


def _request(**updates) -> D18UncertaintyRequest:
    values = {
        "values": (10.0, 20.0),
        "component_ids": ("x", "z"),
        "units": ("m", "m"),
        "frame": "NED",
        "covariance": ((4.0, 1.0), (1.0, 9.0)),
        "component_states": ("Configured", "Observed"),
        "jacobian": ((1.0, 1.0),),
        "result_component_ids": ("sum",),
        "result_units": ("m",),
        "result_frame": "NED",
        "coverage_factor": 2.0,
        "coverage_probability": 0.95,
    }
    values.update(updates)
    return D18UncertaintyRequest(**values)


def test_d18_uses_canonical_covariance_propagation_and_coverage():
    response = prepare_d18_uncertainty_response(_request())

    # [1, 1] Sigma [1, 1]^T = 4 + 1 + 1 + 9 = 15.
    assert response.propagated_covariance[0] == pytest.approx((15.0,))
    assert response.standard_uncertainty == pytest.approx((math.sqrt(15.0),))
    assert response.expanded_uncertainty == pytest.approx((2.0 * math.sqrt(15.0),))
    assert response.method == "linearized_jacobian"
    assert response.state == "Derived"
    assert response.input_states == ("Configured", "Observed")


def test_d18_preserves_truth_error_and_verification_sign_conventions():
    response = prepare_d18_uncertainty_response(
        _request(
            derived_value=(12.0, 17.0),
            truth_value=(10.0, 20.0),
            truth_component_ids=("x", "z"),
            truth_units=("m", "m"),
            truth_frame="NED",
            verification_value_a=(5.0, 8.0),
            verification_value_b=(3.0, 10.0),
            verification_association_a="line-a",
            verification_association_b="line-b",
            verification_component_ids=("x", "z"),
            verification_units=("m", "m"),
            verification_frame="NED",
        )
    )

    assert response.truth_error is not None
    assert response.truth_error.error_vector == pytest.approx((2.0, -3.0))
    assert response.truth_error.sign_convention == "Derived - Truth"
    assert response.truth_error.state == "Derived"

    assert response.verification_residual is not None
    assert response.verification_residual.residual == pytest.approx((2.0, -2.0))
    assert response.verification_residual.sign_convention == "A - B"
    assert response.verification_residual.association_a == "line-a"
    assert response.verification_residual.association_b == "line-b"


def test_d18_rejects_incomplete_optional_truth_error_contract():
    with pytest.raises(ValueError, match="truth-error inputs"):
        _request(derived_value=(1.0, 2.0))


def test_d18_rejects_invalid_covariance_through_canonical_model():
    with pytest.raises(ValueError, match="symmetric"):
        prepare_d18_uncertainty_response(
            _request(covariance=((1.0, 2.0), (0.0, 1.0)))
        )

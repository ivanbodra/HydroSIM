from math import sin

import pytest

from hydrosim.app.propagation_api import (
    D4LayerInput,
    D4PropagationRequest,
    prepare_d4_propagation_response,
)


def _two_layer_profile(lower_speed_mps: float = 1520.0):
    return (
        D4LayerInput(top_depth_m=0.0, bottom_depth_m=10.0, sound_speed_mps=1480.0),
        D4LayerInput(top_depth_m=10.0, bottom_depth_m=40.0, sound_speed_mps=lower_speed_mps),
    )


def test_d4_response_preserves_snell_and_segment_totals():
    response = prepare_d4_propagation_response(
        D4PropagationRequest(
            launch_angle_deg=30.0,
            target_depth_m=30.0,
            reference_profile=_two_layer_profile(),
        )
    )

    ray = response.reference_ray
    assert len(ray.segments) == 2
    assert ray.segments[1].angle_from_vertical_deg != pytest.approx(
        ray.segments[0].angle_from_vertical_deg
    )
    parameters = [
        sin(segment.angle_from_vertical_deg * 3.141592653589793 / 180.0)
        / segment.sound_speed_mps
        for segment in ray.segments
    ]
    assert parameters[0] == pytest.approx(parameters[1], rel=1e-12)
    assert sum(segment.path_length_m for segment in ray.segments) == pytest.approx(
        ray.path_length_m
    )
    assert sum(segment.travel_time_ms for segment in ray.segments) == pytest.approx(
        ray.travel_time_ms
    )
    assert ray.polyline_depth_m == pytest.approx((0.0, 10.0, 30.0))
    assert response.metadata["model"] == "hydrosim.propagation.layered_snell_piecewise_constant"


def test_d4_constant_c_anchor_has_same_angle_in_each_layer():
    profile = (
        D4LayerInput(top_depth_m=0.0, bottom_depth_m=10.0, sound_speed_mps=1500.0),
        D4LayerInput(top_depth_m=10.0, bottom_depth_m=40.0, sound_speed_mps=1500.0),
    )
    response = prepare_d4_propagation_response(
        D4PropagationRequest(
            launch_angle_deg=35.0,
            target_depth_m=30.0,
            reference_profile=profile,
        )
    )

    angles = [segment.angle_from_vertical_deg for segment in response.reference_ray.segments]
    assert angles == pytest.approx((35.0, 35.0))


def test_d4_incorrect_profile_reconstructs_same_travel_time_and_reports_endpoint_error():
    response = prepare_d4_propagation_response(
        D4PropagationRequest(
            launch_angle_deg=45.0,
            target_depth_m=30.0,
            reference_profile=_two_layer_profile(1520.0),
            processing_profile=_two_layer_profile(1490.0),
        )
    )

    comparison = response.comparison
    assert comparison is not None
    assert comparison.processing_ray.travel_time_ms == pytest.approx(
        response.reference_ray.travel_time_ms
    )
    assert comparison.travel_time_difference_ms == pytest.approx(0.0, abs=1e-9)
    assert abs(comparison.depth_error_m) > 0.0
    assert comparison.state_semantics.startswith("Derived simulation-truth error")
    assert response.processing_profile is not None
    assert response.processing_profile.state == "Configured processing profile"


def test_d4_rejects_target_beyond_finite_profile_instead_of_extrapolating():
    with pytest.raises(ValueError, match="outside sound-speed profile"):
        prepare_d4_propagation_response(
            D4PropagationRequest(
                launch_angle_deg=20.0,
                target_depth_m=60.0,
                reference_profile=_two_layer_profile(),
            )
        )

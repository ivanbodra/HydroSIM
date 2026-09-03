import pytest

from hydrosim.app.refraction_api import (
    D4ProfileLayer,
    D4RefractionRequest,
    prepare_d4_refraction_response,
)


def _layer(top: float, bottom: float, c: float) -> D4ProfileLayer:
    return D4ProfileLayer(top_depth_m=top, bottom_depth_m=bottom, sound_speed_mps=c)


def test_constant_speed_profile_preserves_straight_ray_and_units() -> None:
    response = prepare_d4_refraction_response(
        D4RefractionRequest(
            launch_angle_deg_from_vertical=30.0,
            target_depth_m=60.0,
            reference_profile=(_layer(0.0, 100.0, 1500.0),),
        )
    )

    ray = response.reference_ray
    assert len(ray.segments) == 1
    assert ray.segments[0].angle_from_vertical_deg == pytest.approx(30.0)
    assert ray.horizontal_distance_m == pytest.approx(34.64101615137754)
    assert ray.path_length_m == pytest.approx(69.2820323027551)
    assert ray.travel_time_seconds == pytest.approx(ray.path_length_m / 1500.0)
    assert response.metadata["distance_unit"] == "m"
    assert response.metadata["angle_ui_unit"] == "deg from downward vertical"
    assert response.metadata["ray_outputs_state"] == "Derived"


def test_two_layer_response_preserves_core_ray_parameter_and_segment_totals() -> None:
    response = prepare_d4_refraction_response(
        D4RefractionRequest(
            launch_angle_deg_from_vertical=30.0,
            target_depth_m=100.0,
            reference_profile=(
                _layer(0.0, 40.0, 1500.0),
                _layer(40.0, 120.0, 1540.0),
            ),
        )
    )

    ray = response.reference_ray
    assert len(ray.segments) == 2
    assert ray.segments[1].angle_from_vertical_deg > ray.segments[0].angle_from_vertical_deg
    assert all(
        segment.ray_parameter_seconds_per_m == pytest.approx(ray.ray_parameter_seconds_per_m)
        for segment in ray.segments
    )
    assert sum(segment.path_length_m for segment in ray.segments) == pytest.approx(
        ray.path_length_m
    )
    assert sum(segment.travel_time_seconds for segment in ray.segments) == pytest.approx(
        ray.travel_time_seconds
    )


def test_identical_processing_profile_closes_on_reference_ray() -> None:
    profile = (
        _layer(0.0, 30.0, 1475.0),
        _layer(30.0, 80.0, 1500.0),
        _layer(80.0, 150.0, 1530.0),
    )
    response = prepare_d4_refraction_response(
        D4RefractionRequest(
            launch_angle_deg_from_vertical=31.5,
            target_depth_m=112.5,
            reference_profile=profile,
            processing_profile=profile,
        )
    )

    comparison = response.profile_comparison
    assert comparison is not None
    assert comparison.depth_endpoint_error_m == pytest.approx(0.0, abs=1e-9)
    assert comparison.horizontal_endpoint_error_m == pytest.approx(0.0, abs=1e-9)
    assert comparison.path_length_difference_m == pytest.approx(0.0, abs=1e-9)
    assert comparison.travel_time_difference_seconds == pytest.approx(0.0, abs=1e-12)


def test_incorrect_processing_profile_exposes_derived_endpoint_error() -> None:
    response = prepare_d4_refraction_response(
        D4RefractionRequest(
            launch_angle_deg_from_vertical=25.0,
            target_depth_m=100.0,
            reference_profile=(
                _layer(0.0, 50.0, 1480.0),
                _layer(50.0, 150.0, 1520.0),
            ),
            processing_profile=(
                _layer(0.0, 50.0, 1500.0),
                _layer(50.0, 150.0, 1500.0),
            ),
        )
    )

    comparison = response.profile_comparison
    assert comparison is not None
    assert comparison.processing.travel_time_seconds == pytest.approx(
        comparison.reference.travel_time_seconds
    )
    assert abs(comparison.depth_endpoint_error_m) > 1e-6
    assert abs(comparison.horizontal_endpoint_error_m) > 1e-6
    assert response.metadata["processing_profile_state"] == "Configured"


def test_profile_domain_is_not_silently_extrapolated() -> None:
    with pytest.raises(ValueError, match="outside sound-speed profile"):
        prepare_d4_refraction_response(
            D4RefractionRequest(
                target_depth_m=120.0,
                reference_profile=(_layer(0.0, 100.0, 1500.0),),
            )
        )


def test_critical_condition_is_propagated_explicitly() -> None:
    with pytest.raises(ValueError, match="critical"):
        prepare_d4_refraction_response(
            D4RefractionRequest(
                launch_angle_deg_from_vertical=45.0,
                target_depth_m=20.0,
                reference_profile=(
                    _layer(0.0, 10.0, 1000.0),
                    _layer(10.0, 20.0, 2000.0),
                ),
            )
        )

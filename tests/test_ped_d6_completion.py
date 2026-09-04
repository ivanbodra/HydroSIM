import pytest

from hydrosim.acquisition.aperture_weights import deterministic_aperture_weights
from hydrosim.app.array_api import D6ArrayRequest, D6MillsCrossRequest, prepare_d6_array_response


def test_hann_weights_are_symmetric_non_negative_and_zero_at_endpoints() -> None:
    weights = deterministic_aperture_weights(8, "hann")

    assert weights[0] == 0j
    assert weights[-1] == 0j
    assert all(weight.imag == 0.0 and weight.real >= 0.0 for weight in weights)
    assert tuple(weight.real for weight in weights) == pytest.approx(
        tuple(weight.real for weight in reversed(weights))
    )


def test_single_element_hann_reduces_to_unit_weight() -> None:
    assert deterministic_aperture_weights(1, "hann") == (1.0 + 0.0j,)


def test_d6_hann_weights_feed_existing_pattern_path() -> None:
    response = prepare_d6_array_response(
        D6ArrayRequest(
            element_count=8,
            element_spacing_m=0.00375,
            element_face_m=0.003,
            weighting="hann",
        )
    )

    assert response.aperture_weights[0] == pytest.approx(0.0)
    assert response.aperture_weights[-1] == pytest.approx(0.0)
    assert response.peak_normalized_power == pytest.approx(1.0)
    assert response.metadata["weights"] == "hann"


def test_d6_rectangular_geometry_is_serialized_from_transducer_array() -> None:
    response = prepare_d6_array_response(
        D6ArrayRequest(
            element_count=3,
            element_spacing_m=0.004,
            longitudinal_element_count=2,
            longitudinal_element_spacing_m=0.006,
            element_face_m=0.002,
        )
    )

    assert len(response.element_positions_array_frame_m) == 6
    assert response.physical_aperture_longitudinal_m == pytest.approx(0.008)
    assert response.physical_aperture_transverse_m == pytest.approx(0.010)
    assert len(response.aperture_weights) == 6


def test_d6_rejects_hann_for_rectangular_array_until_2d_taper_is_defined() -> None:
    with pytest.raises(ValueError, match="active 1-D"):
        D6ArrayRequest(
            longitudinal_element_count=2,
            longitudinal_element_spacing_m=0.005,
            weighting="hann",
        )


def test_d6_mills_cross_exposes_orthogonal_construction_geometry_only() -> None:
    response = prepare_d6_array_response(
        D6ArrayRequest(
            mills_cross=D6MillsCrossRequest(
                transmit_count=4,
                receive_count=6,
                transmit_spacing_m=0.005,
                receive_spacing_m=0.004,
                transmit_element_face_m=0.002,
                receive_element_face_m=0.002,
            )
        )
    )

    assert response.mills_cross is not None
    tx = response.mills_cross.transmit_axis_sensor_frame
    rx = response.mills_cross.receive_axis_sensor_frame
    assert sum(a * b for a, b in zip(tx, rx, strict=True)) == pytest.approx(0.0, abs=1e-12)
    assert len(response.mills_cross.transmit_element_positions_sensor_frame_m) == 4
    assert len(response.mills_cross.receive_element_positions_sensor_frame_m) == 6

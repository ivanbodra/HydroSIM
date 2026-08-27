from math import pi

import pytest
from pydantic import ValidationError

from hydrosim.geometry.arrays import TransducerArray
from hydrosim.geometry.models import Attitude, Vector3


def test_1d_centred_array_positions_odd_count() -> None:
    array = TransducerArray(
        name="rx",
        role="rx",
        n_x=3,
        n_y=1,
        d_x=0.5,
        d_y=0.0,
        element_longitudinal_size=0.2,
        element_transverse_size=0.1,
    )

    positions = [element.position for element in array.elements()]
    assert positions == [
        Vector3(x=-0.5, y=0.0, z=0.0),
        Vector3(x=0.0, y=0.0, z=0.0),
        Vector3(x=0.5, y=0.0, z=0.0),
    ]


def test_1d_centred_array_positions_even_count() -> None:
    array = TransducerArray(
        name="tx",
        role="tx",
        n_x=4,
        n_y=1,
        d_x=0.25,
        d_y=0.0,
        element_longitudinal_size=0.1,
        element_transverse_size=0.1,
    )

    xs = [element.position.x for element in array.elements()]
    assert xs == pytest.approx([-0.375, -0.125, 0.125, 0.375])
    assert sum(xs) == pytest.approx(0.0)


def test_rectangular_2d_centred_positions() -> None:
    array = TransducerArray(
        name="planar",
        n_x=2,
        n_y=3,
        d_x=1.0,
        d_y=0.5,
        element_longitudinal_size=0.2,
        element_transverse_size=0.2,
    )

    positions = {(e.position.x, e.position.y, e.position.z) for e in array.elements()}
    assert positions == {
        (-0.5, -0.5, 0.0),
        (-0.5, 0.0, 0.0),
        (-0.5, 0.5, 0.0),
        (0.5, -0.5, 0.0),
        (0.5, 0.0, 0.0),
        (0.5, 0.5, 0.0),
    }
    assert array.element_count == 6


def test_aperture_extents_include_element_size() -> None:
    array = TransducerArray(
        name="array",
        n_x=4,
        n_y=3,
        d_x=0.3,
        d_y=0.2,
        element_longitudinal_size=0.1,
        element_transverse_size=0.08,
    )

    assert array.aperture_longitudinal == pytest.approx(1.0)
    assert array.aperture_transverse == pytest.approx(0.48)


def test_single_element_axis_allows_zero_spacing() -> None:
    array = TransducerArray(
        name="linear",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.2,
        element_longitudinal_size=0.1,
        element_transverse_size=0.1,
    )

    assert array.aperture_longitudinal == pytest.approx(0.1)
    assert array.element_count == 4


def test_multiple_elements_require_positive_spacing() -> None:
    with pytest.raises(ValidationError):
        TransducerArray(
            name="bad-x",
            n_x=2,
            n_y=1,
            d_x=0.0,
            d_y=0.0,
            element_longitudinal_size=0.1,
            element_transverse_size=0.1,
        )

    with pytest.raises(ValidationError):
        TransducerArray(
            name="bad-y",
            n_x=1,
            n_y=2,
            d_x=0.0,
            d_y=0.0,
            element_longitudinal_size=0.1,
            element_transverse_size=0.1,
        )


def test_invalid_counts_and_dimensions_are_rejected() -> None:
    with pytest.raises(ValidationError):
        TransducerArray(
            name="bad-count",
            n_x=0,
            n_y=1,
            d_x=0.0,
            d_y=0.0,
            element_longitudinal_size=0.1,
            element_transverse_size=0.1,
        )

    with pytest.raises(ValidationError):
        TransducerArray(
            name="bad-size",
            n_x=1,
            n_y=1,
            d_x=0.0,
            d_y=0.0,
            element_longitudinal_size=-0.1,
            element_transverse_size=0.1,
        )


def test_array_orientation_rotates_positions_into_sensor_frame() -> None:
    array = TransducerArray(
        name="rotated",
        n_x=2,
        n_y=1,
        d_x=2.0,
        d_y=0.0,
        element_longitudinal_size=0.1,
        element_transverse_size=0.1,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=pi / 2),
    )

    positions = array.element_positions_sensor_frame()
    assert positions[0].is_close(Vector3(x=0.0, y=-1.0, z=0.0), atol=1e-12)
    assert positions[1].is_close(Vector3(x=0.0, y=1.0, z=0.0), atol=1e-12)


def test_tx_and_rx_arrays_are_independent_physical_objects() -> None:
    tx = TransducerArray(
        name="tx-array",
        role="tx",
        n_x=8,
        n_y=1,
        d_x=0.1,
        d_y=0.0,
        element_longitudinal_size=0.08,
        element_transverse_size=0.05,
    )
    rx = TransducerArray(
        name="rx-array",
        role="rx",
        n_x=1,
        n_y=16,
        d_x=0.0,
        d_y=0.05,
        element_longitudinal_size=0.05,
        element_transverse_size=0.04,
    )

    assert tx.role == "tx"
    assert rx.role == "rx"
    assert tx.element_count == 8
    assert rx.element_count == 16
    assert tx.aperture_longitudinal != rx.aperture_longitudinal
    assert tx.aperture_transverse != rx.aperture_transverse

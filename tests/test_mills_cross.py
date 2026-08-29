from math import isclose, pi, sin, cos

import pytest
from pydantic import ValidationError

from hydrosim.acquisition import two_way_beam_pattern_sensor_frame
from hydrosim.geometry import (
    Attitude,
    MillsCrossConfiguration,
    TransducerArray,
    Vector3,
    make_reference_mills_cross,
)


def _array(
    *,
    name: str,
    role: str,
    n_x: int,
    n_y: int,
    d_x: float,
    d_y: float,
    yaw: float = 0.0,
) -> TransducerArray:
    return TransducerArray(
        name=name,
        role=role,
        n_x=n_x,
        n_y=n_y,
        d_x=d_x,
        d_y=d_y,
        element_longitudinal_size=1e-6,
        element_transverse_size=1e-6,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=yaw),
    )


def test_reference_mills_cross_has_longitudinal_tx_and_transverse_rx_axes():
    config = make_reference_mills_cross(
        transmit_count=8,
        receive_count=16,
        transmit_spacing=0.005,
        receive_spacing=0.005,
        transmit_element_longitudinal_size=0.004,
        transmit_element_transverse_size=0.004,
        receive_element_longitudinal_size=0.004,
        receive_element_transverse_size=0.004,
    )

    tx_axis = config.transmit_axis_sensor_frame
    rx_axis = config.receive_axis_sensor_frame
    assert isclose(tx_axis.x, 1.0, abs_tol=1e-12)
    assert isclose(tx_axis.y, 0.0, abs_tol=1e-12)
    assert isclose(rx_axis.x, 0.0, abs_tol=1e-12)
    assert isclose(rx_axis.y, 1.0, abs_tol=1e-12)


def test_mills_cross_accepts_orthogonality_created_by_array_orientation():
    tx = _array(name="tx", role="tx", n_x=1, n_y=8, d_x=0.0, d_y=0.005)
    rx = _array(
        name="rx",
        role="rx",
        n_x=1,
        n_y=8,
        d_x=0.0,
        d_y=0.005,
        yaw=pi / 2.0,
    )

    config = MillsCrossConfiguration(transmit_array=tx, receive_array=rx)

    dot = (
        config.transmit_axis_sensor_frame.x * config.receive_axis_sensor_frame.x
        + config.transmit_axis_sensor_frame.y * config.receive_axis_sensor_frame.y
        + config.transmit_axis_sensor_frame.z * config.receive_axis_sensor_frame.z
    )
    assert isclose(dot, 0.0, abs_tol=1e-12)


def test_mills_cross_rejects_parallel_apertures():
    tx = _array(name="tx", role="tx", n_x=1, n_y=8, d_x=0.0, d_y=0.005)
    rx = _array(name="rx", role="rx", n_x=1, n_y=8, d_x=0.0, d_y=0.005)

    with pytest.raises(ValidationError, match="must be orthogonal"):
        MillsCrossConfiguration(transmit_array=tx, receive_array=rx)


def test_reference_mills_cross_two_way_response_separates_tx_and_rx_dimensions():
    wavelength = 0.01
    config = make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
    )
    angle = pi / 12.0
    across_track_direction_sensor = Vector3(x=0.0, y=-sin(angle), z=cos(angle))
    broadside = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern_sensor_frame(
        transmit_array=config.transmit_array,
        receive_array=config.receive_array,
        direction_sensor_frame=across_track_direction_sensor,
        transmit_steering_direction_sensor_frame=broadside,
        receive_steering_direction_sensor_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(response.transmit_response.normalized_amplitude, 1.0, rel_tol=1e-8)
    assert response.receive_response.normalized_amplitude < 1.0
    assert response.normalized_amplitude < 1.0

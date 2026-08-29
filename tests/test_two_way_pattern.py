from math import isclose, pi, sqrt

from hydrosim.acquisition.beam_pattern import across_track_direction
from hydrosim.acquisition.two_way_pattern import (
    two_way_beam_pattern,
    two_way_beam_pattern_sensor_frame,
)
from hydrosim.geometry import Attitude, TransducerArray, Vector3


def _linear_array(
    *,
    name: str,
    count: int,
    spacing: float,
    element_size: float = 1e-6,
    orientation: Attitude | None = None,
) -> TransducerArray:
    return TransducerArray(
        name=name,
        n_x=1,
        n_y=count,
        d_x=0.0,
        d_y=spacing,
        element_longitudinal_size=element_size,
        element_transverse_size=element_size,
        orientation=orientation or Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def test_matched_tx_and_rx_have_unity_two_way_response():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=4, spacing=wavelength / 2.0)
    rx = _linear_array(name="rx", count=8, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=broadside,
        receive_direction_array_frame=broadside,
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(response.normalized_amplitude, 1.0, abs_tol=1e-12)
    assert isclose(response.normalized_power, 1.0, abs_tol=1e-12)


def test_two_way_amplitude_is_product_of_independent_one_way_amplitudes():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=1, spacing=0.0)
    rx = _linear_array(name="rx", count=2, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)
    source = across_track_direction(pi / 6.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=source,
        receive_direction_array_frame=source,
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    expected_rx = sqrt(2.0) / 2.0
    assert isclose(response.transmit_response.normalized_amplitude, 1.0, rel_tol=1e-8)
    assert isclose(response.receive_response.normalized_amplitude, expected_rx, rel_tol=1e-8)
    assert isclose(response.normalized_amplitude, expected_rx, rel_tol=1e-8)
    assert isclose(
        response.normalized_power,
        response.normalized_amplitude * response.normalized_amplitude,
        abs_tol=1e-15,
    )


def test_tx_and_rx_directions_are_independent_local_frame_representations():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=2, spacing=wavelength / 2.0)
    rx = _linear_array(name="rx", count=2, spacing=wavelength / 2.0)
    broadside = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=Vector3(x=0.0, y=-0.5, z=sqrt(3.0) / 2.0),
        receive_direction_array_frame=Vector3(x=0.0, y=0.0, z=1.0),
        transmit_steering_direction_array_frame=broadside,
        receive_steering_direction_array_frame=broadside,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert response.transmit_response.normalized_amplitude < 1.0
    assert isclose(response.receive_response.normalized_amplitude, 1.0, abs_tol=1e-12)
    assert response.normalized_amplitude < 1.0


def test_array_orientation_round_trip_preserves_direction():
    array = _linear_array(
        name="rotated",
        count=2,
        spacing=0.005,
        orientation=Attitude(roll=0.1, pitch=-0.2, yaw=0.3),
    )
    original = Vector3(x=0.2, y=-0.4, z=0.8)

    sensor = array.direction_to_sensor_frame(original)
    recovered = array.direction_from_sensor_frame(sensor)

    assert isclose(recovered.x, original.x, abs_tol=1e-12)
    assert isclose(recovered.y, original.y, abs_tol=1e-12)
    assert isclose(recovered.z, original.z, abs_tol=1e-12)


def test_orthogonal_tx_rx_arrays_receive_distinct_local_components():
    wavelength = 0.01
    tx = _linear_array(name="tx", count=4, spacing=wavelength / 2.0)
    rx = _linear_array(
        name="rx",
        count=4,
        spacing=wavelength / 2.0,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=pi / 2.0),
    )
    component = 1.0 / sqrt(2.0)
    physical_direction = Vector3(x=0.0, y=component, z=component)
    broadside_sensor = Vector3(x=0.0, y=0.0, z=1.0)

    response = two_way_beam_pattern_sensor_frame(
        transmit_array=tx,
        receive_array=rx,
        direction_sensor_frame=physical_direction,
        transmit_steering_direction_sensor_frame=broadside_sensor,
        receive_steering_direction_sensor_frame=broadside_sensor,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    tx_local = response.transmit_direction_array_frame
    rx_local = response.receive_direction_array_frame
    assert isclose(tx_local.x, 0.0, abs_tol=1e-12)
    assert isclose(tx_local.y, component, abs_tol=1e-12)
    assert isclose(rx_local.x, component, abs_tol=1e-12)
    assert isclose(rx_local.y, 0.0, abs_tol=1e-12)
    assert isclose(tx_local.z, component, abs_tol=1e-12)
    assert isclose(rx_local.z, component, abs_tol=1e-12)


def test_sensor_frame_api_matches_manual_local_transforms():
    wavelength = 0.01
    tx = _linear_array(
        name="tx",
        count=3,
        spacing=wavelength / 2.0,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.2),
    )
    rx = _linear_array(
        name="rx",
        count=5,
        spacing=wavelength / 2.0,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=-0.4),
    )
    direction_sensor = Vector3(x=0.1, y=-0.3, z=0.95)
    steering_sensor = Vector3(x=0.0, y=0.0, z=1.0)

    automatic = two_way_beam_pattern_sensor_frame(
        transmit_array=tx,
        receive_array=rx,
        direction_sensor_frame=direction_sensor,
        transmit_steering_direction_sensor_frame=steering_sensor,
        receive_steering_direction_sensor_frame=steering_sensor,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    manual = two_way_beam_pattern(
        transmit_array=tx,
        receive_array=rx,
        transmit_direction_array_frame=tx.direction_from_sensor_frame(direction_sensor),
        receive_direction_array_frame=rx.direction_from_sensor_frame(direction_sensor),
        transmit_steering_direction_array_frame=tx.direction_from_sensor_frame(steering_sensor),
        receive_steering_direction_array_frame=rx.direction_from_sensor_frame(steering_sensor),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(automatic.field_real, manual.field_real, abs_tol=1e-12)
    assert isclose(automatic.field_imag, manual.field_imag, abs_tol=1e-12)
    assert isclose(automatic.normalized_power, manual.normalized_power, abs_tol=1e-12)

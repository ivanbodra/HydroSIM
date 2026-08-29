from math import isclose, radians, sqrt

from hydrosim.acquisition import (
    ArrayElementTruthArrival,
    ArrayTruthReception,
    NarrowbandReceiveTone,
    coherent_receive_sum,
    ideal_receive_steering,
)
from hydrosim.geometry import Attitude, TransducerArray, Vector3
from hydrosim.timing import SimulationTime


def _array() -> TransducerArray:
    # At 150 kHz and c=1500 m/s, wavelength is 0.01 m, so d_y=lambda/2.
    return TransducerArray(
        name="rx_test",
        role="rx",
        n_x=1,
        n_y=5,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def _two_element_half_wavelength_array() -> TransducerArray:
    return TransducerArray(
        name="rx_two",
        role="rx",
        n_x=1,
        n_y=2,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def _synthetic_reception(angle_rad: float, array: TransducerArray | None = None) -> ArrayTruthReception:
    array = array or _array()
    truth_law = ideal_receive_steering(
        receive_array=array,
        across_track_angle_rad=angle_rad,
        sound_speed_mps=1500.0,
    )
    centre = 1.0
    arrivals = []
    for element, delay in zip(array.elements(), truth_law.element_delays, strict=True):
        dt = float(delay.predicted_arrival_offset_seconds)
        arrivals.append(
            ArrayElementTruthArrival(
                index_x=element.index_x,
                index_y=element.index_y,
                element_position_array_frame=element.position,
                arrival_position_navigation=element.position,
                inbound_range_m=100.0,
                arrival_time=SimulationTime(seconds=centre + dt),
                relative_to_array_center_seconds=dt,
                iterations=1,
            )
        )
    return ArrayTruthReception(
        beam_index=3,
        array_name=array.name,
        center_return_time=SimulationTime(seconds=centre),
        direction_to_bottom_navigation=truth_law.direction_to_source_array_frame,
        direction_to_bottom_array_frame=truth_law.direction_to_source_array_frame,
        element_arrivals=tuple(arrivals),
    )


def test_matched_steering_aligns_all_element_phases():
    array = _array()
    angle = radians(30.0)
    result = coherent_receive_sum(
        reception=_synthetic_reception(angle),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=angle,
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )

    assert isclose(result.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(result.coherent_power_normalized, 1.0, abs_tol=1e-12)
    assert all(isclose(p.residual_phase_rad, 0.0, abs_tol=1e-12) for p in result.element_phasors)


def test_wrong_steering_reduces_coherent_sum():
    array = _array()
    result = coherent_receive_sum(
        reception=_synthetic_reception(radians(30.0)),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )

    assert result.normalized_magnitude < 0.5
    assert result.coherent_power_normalized < 0.25


def test_frequency_changes_phase_sensitivity_for_same_timing_error():
    array = _array()
    reception = _synthetic_reception(radians(20.0))
    steering = ideal_receive_steering(
        receive_array=array,
        across_track_angle_rad=0.0,
        sound_speed_mps=1500.0,
    )

    low = coherent_receive_sum(
        reception=reception,
        steering=steering,
        tone=NarrowbandReceiveTone(frequency_hz=50_000.0),
    )
    high = coherent_receive_sum(
        reception=reception,
        steering=steering,
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )

    assert low.normalized_magnitude > high.normalized_magnitude


def test_two_element_half_wavelength_broadside_response_matches_closed_form():
    """Independent check: two elements, d=lambda/2, source at +30 deg, steer 0.

    The inter-element residual phase is pi*sin(30 deg)=pi/2. For two equal
    phasors separated by phase Delta, normalized magnitude is |cos(Delta/2)|,
    hence sqrt(2)/2. This value is derived independently of HydroSIM's delay law.
    """

    array = _two_element_half_wavelength_array()
    result = coherent_receive_sum(
        reception=_synthetic_reception(radians(30.0), array),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=0.0,
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )

    assert isclose(result.normalized_magnitude, sqrt(2.0) / 2.0, abs_tol=1e-12)
    assert isclose(result.coherent_power_normalized, 0.5, abs_tol=1e-12)


def test_two_element_half_wavelength_opposite_steering_cancels():
    """Independent check: +30 deg source steered to -30 deg gives Delta=pi."""

    array = _two_element_half_wavelength_array()
    result = coherent_receive_sum(
        reception=_synthetic_reception(radians(30.0), array),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=radians(-30.0),
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )

    assert isclose(result.normalized_magnitude, 0.0, abs_tol=1e-12)
    assert isclose(result.coherent_power_normalized, 0.0, abs_tol=1e-12)

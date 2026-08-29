from math import isclose, pi, radians, sqrt

from hydrosim.acquisition import (
    ArrayElementTruthArrival,
    ArrayTruthReception,
    NarrowbandReceiveTone,
    SplitApertureDefinition,
    coherent_receive_sum,
    ideal_receive_steering,
    split_aperture_phase_centers,
    split_coherent_receive_sum,
)
from hydrosim.geometry import Attitude, TransducerArray
from hydrosim.timing import SimulationTime


def _array() -> TransducerArray:
    return TransducerArray(
        name="rx_split",
        role="rx",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def _reception(source_angle_rad: float) -> ArrayTruthReception:
    array = _array()
    truth = ideal_receive_steering(
        receive_array=array,
        across_track_angle_rad=source_angle_rad,
        sound_speed_mps=1500.0,
    )
    arrivals = []
    for element, delay in zip(array.elements(), truth.element_delays, strict=True):
        dt = float(delay.predicted_arrival_offset_seconds)
        arrivals.append(
            ArrayElementTruthArrival(
                index_x=element.index_x,
                index_y=element.index_y,
                element_position_array_frame=element.position,
                arrival_position_navigation=element.position,
                inbound_range_m=100.0,
                arrival_time=SimulationTime(seconds=1.0 + dt),
                relative_to_array_center_seconds=dt,
                iterations=1,
            )
        )
    return ArrayTruthReception(
        beam_index=2,
        array_name=array.name,
        center_return_time=SimulationTime(seconds=1.0),
        direction_to_bottom_navigation=truth.direction_to_source_array_frame,
        direction_to_bottom_array_frame=truth.direction_to_source_array_frame,
        element_arrivals=tuple(arrivals),
    )


def _coherent(source_angle_rad: float, steering_angle_rad: float):
    array = _array()
    return coherent_receive_sum(
        reception=_reception(source_angle_rad),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=steering_angle_rad,
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )


def test_phase_centres_match_four_element_geometry() -> None:
    result = split_aperture_phase_centers(receive_array=_array())

    assert result.negative_element_count == 2
    assert result.positive_element_count == 2
    assert isclose(result.negative_center_array_frame.y, -0.005, abs_tol=1e-12)
    assert isclose(result.positive_center_array_frame.y, 0.005, abs_tol=1e-12)
    assert isclose(result.negative_to_positive_baseline_array_frame.y, 0.01, abs_tol=1e-12)
    assert isclose(result.baseline_length_m, 0.01, abs_tol=1e-12)


def test_matched_steering_gives_equal_in_phase_subapertures() -> None:
    array = _array()
    coherent = _coherent(radians(25.0), radians(25.0))
    result = split_coherent_receive_sum(receive_array=array, coherent_sum=coherent)

    assert result.negative.element_count == 2
    assert result.positive.element_count == 2
    assert isclose(result.negative.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(result.positive.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(result.differential_phase_rad, 0.0, abs_tol=1e-12)


def test_split_phase_records_source_steering_mismatch() -> None:
    """Four lambda/2-spaced elements: +30 deg source, broadside steering.

    The two half-aperture phase centres are separated by 0.01 m = one wavelength.
    At sin(30 deg)=0.5 their differential phase magnitude is pi. Each two-element
    half has an internal phase separation pi/2 and normalized magnitude sqrt(2)/2.
    """

    array = _array()
    coherent = _coherent(radians(30.0), 0.0)
    result = split_coherent_receive_sum(receive_array=array, coherent_sum=coherent)

    assert isclose(result.negative.normalized_magnitude, sqrt(2.0) / 2.0, abs_tol=1e-12)
    assert isclose(result.positive.normalized_magnitude, sqrt(2.0) / 2.0, abs_tol=1e-12)
    assert isclose(abs(result.differential_phase_rad), pi, abs_tol=1e-12)


def test_center_element_policy_is_explicit_for_odd_arrays() -> None:
    odd = TransducerArray(
        name="rx_odd",
        role="rx",
        n_x=1,
        n_y=3,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
    )
    truth = ideal_receive_steering(receive_array=odd, across_track_angle_rad=0.0, sound_speed_mps=1500.0)
    arrivals = tuple(
        ArrayElementTruthArrival(
            index_x=e.index_x,
            index_y=e.index_y,
            element_position_array_frame=e.position,
            arrival_position_navigation=e.position,
            inbound_range_m=10.0,
            arrival_time=SimulationTime(seconds=1.0),
            relative_to_array_center_seconds=0.0,
            iterations=1,
        )
        for e in odd.elements()
    )
    reception = ArrayTruthReception(
        beam_index=0,
        array_name=odd.name,
        center_return_time=SimulationTime(seconds=1.0),
        direction_to_bottom_navigation=truth.direction_to_source_array_frame,
        direction_to_bottom_array_frame=truth.direction_to_source_array_frame,
        element_arrivals=arrivals,
    )
    coherent = coherent_receive_sum(
        reception=reception,
        steering=truth,
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )
    result = split_coherent_receive_sum(
        receive_array=odd,
        coherent_sum=coherent,
        definition=SplitApertureDefinition(center_element_policy="both"),
    )

    assert result.negative.element_count == 2
    assert result.positive.element_count == 2

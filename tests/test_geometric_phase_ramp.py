from math import isclose, radians

import pytest

from hydrosim.acquisition import (
    ArrayElementTruthArrival,
    ArrayTruthReception,
    ContinuousWavePulse,
    NarrowbandReceiveTone,
    RefractedPatternIllumination,
    RefractedProjectedPatternCell,
    SplitApertureDefinition,
    build_geometric_phase_ramp,
    coherent_receive_sum,
    ideal_receive_steering,
    ideal_split_aperture_differential_phase,
    sensor_angular_direction,
    split_coherent_receive_sum,
)
from hydrosim.geometry import Attitude, TransducerArray
from hydrosim.timing import SimulationTime


def _array() -> TransducerArray:
    return TransducerArray(
        name="rx_phase_ramp",
        role="rx",
        n_x=1,
        n_y=4,
        d_x=0.0,
        d_y=0.005,
        element_longitudinal_size=0.004,
        element_transverse_size=0.004,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )


def _synthetic_reception(source_angle_rad: float) -> ArrayTruthReception:
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
        beam_index=0,
        array_name=array.name,
        center_return_time=SimulationTime(seconds=1.0),
        direction_to_bottom_navigation=truth.direction_to_source_array_frame,
        direction_to_bottom_array_frame=truth.direction_to_source_array_frame,
        element_arrivals=tuple(arrivals),
    )


def _cell(ai: int, ci: int, along: float, across: float, time_s: float) -> RefractedProjectedPatternCell:
    return RefractedProjectedPatternCell(
        along_track_index=ai,
        across_track_index=ci,
        along_track_angle_rad=along,
        across_track_angle_rad=across,
        normalized_power=1.0,
        relative_power_to_peak=1.0,
        forward_center_m=float(ai),
        port_center_m=float(ci),
        horizontal_distance_m=1.0,
        acoustic_path_length_m=100.0,
        one_way_travel_time_seconds=time_s,
        incidence_angle_from_normal_rad=abs(across),
        projected_area_m2=1.0,
        equivalent_area_contribution_m2=1.0,
    )


def _illumination() -> RefractedPatternIllumination:
    angles = (-0.02, 0.02)
    cells = []
    for ai, along in enumerate(angles):
        for ci, across in enumerate(angles):
            # Earlier arrival on the negative-across side, later on the positive.
            time_s = 0.100 + 0.001 * ci
            cells.append(_cell(ai, ci, along, across, time_s))
    return RefractedPatternIllumination(
        configuration_name="synthetic",
        start_depth_m=0.0,
        target_depth_m=100.0,
        peak_power=1.0,
        sampled_grid_area_m2=4.0,
        equivalent_insonified_area_m2=4.0,
        cells=tuple(cells),
    )


def test_centroid_baseline_phase_matches_explicit_split_sum() -> None:
    array = _array()
    source_angle = radians(12.0)
    steering_angle = radians(4.0)
    coherent = coherent_receive_sum(
        reception=_synthetic_reception(source_angle),
        steering=ideal_receive_steering(
            receive_array=array,
            across_track_angle_rad=steering_angle,
            sound_speed_mps=1500.0,
        ),
        tone=NarrowbandReceiveTone(frequency_hz=150_000.0),
    )
    split = split_coherent_receive_sum(receive_array=array, coherent_sum=coherent)
    geometric = ideal_split_aperture_differential_phase(
        receive_array=array,
        definition=SplitApertureDefinition(),
        source_direction_sensor_frame=sensor_angular_direction(0.0, source_angle),
        steering_direction_sensor_frame=sensor_angular_direction(0.0, steering_angle),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    assert isclose(geometric, split.differential_phase_rad, abs_tol=1e-12)


def test_phase_ramp_records_spatial_and_twtt_resolution() -> None:
    ramp = build_geometric_phase_ramp(
        illumination=_illumination(),
        receive_array=_array(),
        definition=SplitApertureDefinition(),
        pulse=ContinuousWavePulse(center_frequency_hz=150_000.0, duration_seconds=0.004),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        steering_along_track_angle_rad=0.0,
        steering_across_track_angle_rad=0.0,
        start_reference_one_way_travel_time_seconds=0.099,
        sample_count=9,
        sample_rate_hz=2000.0,
    )
    assert ramp.along_track_resolution.nominal_spacing == pytest.approx(0.04)
    assert ramp.across_track_resolution.nominal_spacing == pytest.approx(0.04)
    assert ramp.temporal_resolution.name == "twtt"
    assert ramp.temporal_resolution.nominal_spacing == pytest.approx(1.0 / 2000.0)
    assert len(ramp.samples) == 9
    assert any(sample.equivalent_weighted_area_m2 > 0.0 for sample in ramp.samples)
    assert all(0.0 <= sample.circular_resultant_magnitude <= 1.0 for sample in ramp.samples)

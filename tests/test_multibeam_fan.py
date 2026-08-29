from math import isclose

from hydrosim.acquisition import simulate_mills_cross_multibeam_fan
from hydrosim.geometry import make_reference_mills_cross


def _configuration():
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=8,
        receive_count=16,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="fan_test",
    )


def test_multibeam_fan_spans_starboard_to_port_with_one_physical_rx_array():
    fan = simulate_mills_cross_multibeam_fan(
        configuration=_configuration(),
        start_across_track_angle_rad=-0.30,
        end_across_track_angle_rad=0.30,
        beam_count=7,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert len(fan.beams) == 7
    assert isclose(fan.beams[0].receive_steering_across_track_angle_rad, -0.30)
    assert isclose(fan.beams[-1].receive_steering_across_track_angle_rad, 0.30)
    assert fan.beams[0].steering_direction_sensor_frame.y > 0.0  # Starboard
    assert fan.beams[-1].steering_direction_sensor_frame.y < 0.0  # Port


def test_each_sampled_source_is_strongest_in_its_matching_receive_beam():
    fan = simulate_mills_cross_multibeam_fan(
        configuration=_configuration(),
        start_across_track_angle_rad=-0.30,
        end_across_track_angle_rad=0.30,
        beam_count=7,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert fan.strongest_beam_index_by_source == tuple(range(7))
    assert len(fan.response_matrix) == 49


def test_receive_beam_is_unity_on_its_own_steering_direction():
    fan = simulate_mills_cross_multibeam_fan(
        configuration=_configuration(),
        start_across_track_angle_rad=-0.20,
        end_across_track_angle_rad=0.20,
        beam_count=5,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    for beam in fan.beams:
        assert isclose(beam.receive_amplitude_at_beam_center, 1.0, abs_tol=1e-12)
        assert isclose(
            beam.two_way_amplitude_at_beam_center,
            beam.transmit_amplitude_at_beam_center * beam.receive_amplitude_at_beam_center,
            abs_tol=1e-12,
        )


def test_response_matrix_resolves_center_beam_more_strongly_than_edge_beams():
    fan = simulate_mills_cross_multibeam_fan(
        configuration=_configuration(),
        start_across_track_angle_rad=-0.30,
        end_across_track_angle_rad=0.30,
        beam_count=7,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    center_source = [sample for sample in fan.response_matrix if sample.source_index == 3]
    by_beam = {sample.beam_index: sample.normalized_power for sample in center_source}

    assert by_beam[3] > by_beam[0]
    assert by_beam[3] > by_beam[6]
    assert isclose(by_beam[0], by_beam[6], rel_tol=1e-12, abs_tol=1e-12)

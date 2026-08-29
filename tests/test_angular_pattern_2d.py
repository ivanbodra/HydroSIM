from math import isclose, pi, sqrt

from hydrosim.acquisition import (
    scan_mills_cross_two_way_pattern_2d,
    sensor_angular_direction,
)
from hydrosim.geometry import make_reference_mills_cross


def _reference_configuration():
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="test_mills_cross",
    )


def test_sensor_angular_direction_matches_hydrosim_sign_conventions():
    forward = sensor_angular_direction(pi / 6.0, 0.0)
    port = sensor_angular_direction(0.0, pi / 6.0)

    assert forward.x > 0.0
    assert isclose(forward.y, 0.0, abs_tol=1e-12)
    assert port.y < 0.0
    assert isclose(port.x, 0.0, abs_tol=1e-12)
    assert isclose(
        sqrt(forward.x**2 + forward.y**2 + forward.z**2),
        1.0,
        abs_tol=1e-12,
    )


def test_reference_mills_cross_two_way_pattern_peaks_at_broadside():
    scan = scan_mills_cross_two_way_pattern_2d(
        configuration=_reference_configuration(),
        along_track_start_angle_rad=-0.2,
        along_track_end_angle_rad=0.2,
        along_track_sample_count=9,
        across_track_start_angle_rad=-0.2,
        across_track_end_angle_rad=0.2,
        across_track_sample_count=9,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(scan.peak_along_track_angle_rad, 0.0, abs_tol=1e-12)
    assert isclose(scan.peak_across_track_angle_rad, 0.0, abs_tol=1e-12)
    assert isclose(scan.peak_power, 1.0, abs_tol=1e-12)
    assert len(scan.samples) == 81


def test_mills_cross_localizes_two_way_response_in_both_principal_planes():
    configuration = _reference_configuration()
    angle = 0.15
    scan = scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-angle,
        along_track_end_angle_rad=angle,
        along_track_sample_count=3,
        across_track_start_angle_rad=-angle,
        across_track_end_angle_rad=angle,
        across_track_sample_count=3,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    center = next(
        sample
        for sample in scan.samples
        if isclose(sample.along_track_angle_rad, 0.0, abs_tol=1e-12)
        and isclose(sample.across_track_angle_rad, 0.0, abs_tol=1e-12)
    )
    along_only = next(
        sample
        for sample in scan.samples
        if isclose(sample.along_track_angle_rad, angle, abs_tol=1e-12)
        and isclose(sample.across_track_angle_rad, 0.0, abs_tol=1e-12)
    )
    across_only = next(
        sample
        for sample in scan.samples
        if isclose(sample.along_track_angle_rad, 0.0, abs_tol=1e-12)
        and isclose(sample.across_track_angle_rad, angle, abs_tol=1e-12)
    )
    diagonal = next(
        sample
        for sample in scan.samples
        if isclose(sample.along_track_angle_rad, angle, abs_tol=1e-12)
        and isclose(sample.across_track_angle_rad, angle, abs_tol=1e-12)
    )

    assert isclose(center.normalized_power, 1.0, abs_tol=1e-12)
    assert along_only.transmit_amplitude < center.transmit_amplitude
    assert across_only.receive_amplitude < center.receive_amplitude
    assert along_only.normalized_power < center.normalized_power
    assert across_only.normalized_power < center.normalized_power
    assert diagonal.normalized_power < along_only.normalized_power
    assert diagonal.normalized_power < across_only.normalized_power

from math import isclose, pi, radians

from hydrosim.acquisition.beam_pattern import (
    across_track_direction,
    one_way_beam_pattern,
    scan_across_track_beam_pattern,
)
from hydrosim.geometry import TransducerArray


FREQUENCY_HZ = 150_000.0
SOUND_SPEED_MPS = 1500.0
WAVELENGTH_M = SOUND_SPEED_MPS / FREQUENCY_HZ


def _transverse_array(*, n_y: int, spacing_m: float, element_size_m: float) -> TransducerArray:
    return TransducerArray(
        name="rx",
        role="rx",
        n_x=1,
        n_y=n_y,
        d_x=0.0,
        d_y=spacing_m,
        element_longitudinal_size=0.001,
        element_transverse_size=element_size_m,
    )


def test_boresight_one_way_pattern_is_unity_for_uniform_array():
    array = _transverse_array(
        n_y=8,
        spacing_m=WAVELENGTH_M / 2.0,
        element_size_m=WAVELENGTH_M / 4.0,
    )
    direction = across_track_direction(0.0)
    response = one_way_beam_pattern(
        array=array,
        source_direction_array_frame=direction,
        steering_direction_array_frame=direction,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )

    assert isclose(response.element_factor.amplitude, 1.0, abs_tol=1e-15)
    assert isclose(response.array_factor.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(response.normalized_amplitude, 1.0, abs_tol=1e-12)
    assert isclose(response.normalized_power, 1.0, abs_tol=1e-12)


def test_element_factor_can_suppress_an_array_factor_grating_lobe():
    # With d=lambda, a two-element broadside array has an AF grating lobe at 90 deg.
    # A transverse rectangular element of width lambda has its first element-factor
    # null at that same direction, so the physical one-way pattern is zero there.
    array = _transverse_array(
        n_y=2,
        spacing_m=WAVELENGTH_M,
        element_size_m=WAVELENGTH_M,
    )
    response = one_way_beam_pattern(
        array=array,
        source_direction_array_frame=across_track_direction(pi / 2.0),
        steering_direction_array_frame=across_track_direction(0.0),
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )

    assert isclose(response.array_factor.normalized_magnitude, 1.0, abs_tol=1e-12)
    assert isclose(response.element_factor.amplitude, 0.0, abs_tol=1e-12)
    assert isclose(response.normalized_power, 0.0, abs_tol=1e-12)


def test_half_wavelength_eight_element_array_has_expected_half_power_beamwidth():
    # For an 8-element uniform broadside ULA with d=lambda/2 and a small element,
    # the one-way half-power beamwidth is about 12.8 deg. The test uses a dense
    # angular scan and a bounded analytical expectation rather than implementation
    # internals.
    array = _transverse_array(
        n_y=8,
        spacing_m=WAVELENGTH_M / 2.0,
        element_size_m=WAVELENGTH_M / 20.0,
    )
    scan = scan_across_track_beam_pattern(
        array=array,
        steering_angle_rad=0.0,
        start_angle_rad=radians(-30.0),
        end_angle_rad=radians(30.0),
        sample_count=1201,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )

    assert isclose(scan.peak_angle_rad, 0.0, abs_tol=radians(0.051))
    assert scan.half_power_beamwidth_rad is not None
    beamwidth_deg = float(scan.half_power_beamwidth_rad) * 180.0 / pi
    assert 12.5 < beamwidth_deg < 13.1


def test_steered_pattern_peak_tracks_requested_across_track_angle():
    array = _transverse_array(
        n_y=8,
        spacing_m=WAVELENGTH_M / 2.0,
        element_size_m=WAVELENGTH_M / 20.0,
    )
    scan = scan_across_track_beam_pattern(
        array=array,
        steering_angle_rad=radians(20.0),
        start_angle_rad=radians(-10.0),
        end_angle_rad=radians(50.0),
        sample_count=601,
        frequency_hz=FREQUENCY_HZ,
        sound_speed_mps=SOUND_SPEED_MPS,
    )

    assert isclose(scan.peak_angle_rad, radians(20.0), abs_tol=radians(0.11))

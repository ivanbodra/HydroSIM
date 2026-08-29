import pytest

from hydrosim.acquisition import (
    derive_mills_cross_footprint_beamwidths,
    estimate_mills_cross_pattern_footprint,
)
from hydrosim.geometry import make_reference_mills_cross


def _configuration(count: int):
    wavelength = 0.01
    return make_reference_mills_cross(
        transmit_count=count,
        receive_count=count,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name=f"mills_cross_{count}",
    )


def test_reference_mills_cross_derives_symmetric_principal_plane_widths() -> None:
    widths = derive_mills_cross_footprint_beamwidths(
        configuration=_configuration(16),
        transmit_steering_along_track_angle_rad=0.0,
        receive_steering_across_track_angle_rad=0.0,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        scan_half_span_rad=0.25,
        sample_count=1001,
    )

    assert widths.transmit_along_track.peak_angle_rad == pytest.approx(0.0, abs=1e-12)
    assert widths.receive_across_track.peak_angle_rad == pytest.approx(0.0, abs=1e-12)
    assert widths.transmit_along_track.half_power_beamwidth_rad == pytest.approx(
        widths.receive_across_track.half_power_beamwidth_rad,
        rel=2e-3,
    )
    assert float(widths.footprint_model.transmit_along_track_beamwidth_rad) == pytest.approx(
        float(widths.transmit_along_track.half_power_beamwidth_rad)
    )


def test_larger_aperture_produces_narrower_pattern_derived_footprint() -> None:
    small = estimate_mills_cross_pattern_footprint(
        configuration=_configuration(8),
        transmit_steering_along_track_angle_rad=0.0,
        receive_steering_across_track_angle_rad=0.15,
        vertical_separation_m=40.0,
        pulse_duration_seconds=0.001,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        sample_count=1001,
    )
    large = estimate_mills_cross_pattern_footprint(
        configuration=_configuration(32),
        transmit_steering_along_track_angle_rad=0.0,
        receive_steering_across_track_angle_rad=0.15,
        vertical_separation_m=40.0,
        pulse_duration_seconds=0.001,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        sample_count=1001,
    )

    assert large.beamwidths.transmit_along_track.half_power_beamwidth_rad < (
        small.beamwidths.transmit_along_track.half_power_beamwidth_rad
    )
    assert large.beamwidths.receive_across_track.half_power_beamwidth_rad < (
        small.beamwidths.receive_across_track.half_power_beamwidth_rad
    )
    assert large.footprint.effective_area_m2 < small.footprint.effective_area_m2


def test_steered_receive_peak_tracks_requested_across_track_angle() -> None:
    requested = 0.12
    widths = derive_mills_cross_footprint_beamwidths(
        configuration=_configuration(16),
        transmit_steering_along_track_angle_rad=-0.05,
        receive_steering_across_track_angle_rad=requested,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
        scan_half_span_rad=0.2,
        sample_count=1001,
    )

    assert widths.transmit_along_track.peak_angle_rad == pytest.approx(-0.05, abs=5e-4)
    assert widths.receive_across_track.peak_angle_rad == pytest.approx(requested, abs=5e-4)

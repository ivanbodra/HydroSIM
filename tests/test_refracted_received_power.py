import pytest

from hydrosim.acquisition import (
    AngularScatteringStrengthSample,
    AngularScatteringStrengthTable,
    LayeredSoundSpeedProfile,
    LinearFMPulse,
    PropagationLossModel,
    SoundSpeedLayer,
    integrate_refracted_matched_filter_seafloor_backscatter,
    integrate_refracted_propagation_weighted_return,
    project_angular_pattern_through_layered_profile,
    scan_mills_cross_two_way_pattern_2d,
)
from hydrosim.geometry import make_reference_mills_cross


def _illumination(samples: int = 31):
    wavelength = 0.01
    configuration = make_reference_mills_cross(
        transmit_count=8,
        receive_count=8,
        transmit_spacing=wavelength / 2.0,
        receive_spacing=wavelength / 2.0,
        transmit_element_longitudinal_size=1e-6,
        transmit_element_transverse_size=1e-6,
        receive_element_longitudinal_size=1e-6,
        receive_element_transverse_size=1e-6,
        name="refracted_received_power_test",
    )
    scan = scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-0.12,
        along_track_end_angle_rad=0.12,
        along_track_sample_count=samples,
        across_track_start_angle_rad=-0.12,
        across_track_end_angle_rad=0.12,
        across_track_sample_count=samples,
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )
    profile = LayeredSoundSpeedProfile(layers=(
        SoundSpeedLayer(top_depth_m=0.0, bottom_depth_m=25.0, sound_speed_mps=1500.0),
        SoundSpeedLayer(top_depth_m=25.0, bottom_depth_m=50.0, sound_speed_mps=1530.0),
    ))
    return project_angular_pattern_through_layered_profile(
        scan=scan,
        profile=profile,
        target_depth_m=50.0,
    )


def _table():
    return AngularScatteringStrengthTable(samples=(
        AngularScatteringStrengthSample(
            incidence_angle_from_normal_rad=0.0,
            scattering_strength_db_per_m2=-30.0,
        ),
        AngularScatteringStrengthSample(
            incidence_angle_from_normal_rad=0.5,
            scattering_strength_db_per_m2=-30.0,
        ),
    ))


def _pulse():
    return LinearFMPulse(
        center_frequency_hz=150_000.0,
        bandwidth_hz=80_000.0,
        duration_seconds=0.001,
    )


def _reference_time(illumination) -> float:
    center = min(
        illumination.cells,
        key=lambda cell: abs(float(cell.along_track_angle_rad))
        + abs(float(cell.across_track_angle_rad)),
    )
    return float(center.one_way_travel_time_seconds)


def test_propagation_weighting_reduces_relative_return_below_bottom_only_strength() -> None:
    illumination = _illumination()
    reference_time = _reference_time(illumination)
    bottom_only = integrate_refracted_matched_filter_seafloor_backscatter(
        illumination=illumination,
        scattering_table=_table(),
        pulse=_pulse(),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=400_000.0,
    )
    received = integrate_refracted_propagation_weighted_return(
        illumination=illumination,
        scattering_table=_table(),
        pulse=_pulse(),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=400_000.0,
        propagation_loss_model=PropagationLossModel(absorption_db_per_km=0.0),
    )

    assert received.received_power_relative_db < bottom_only.integrated_backscatter_strength_db
    assert received.minimum_two_way_transmission_loss_db > 0.0
    assert received.received_power_ratio > 0.0
    assert received.received_amplitude_ratio**2 == pytest.approx(received.received_power_ratio)


def test_absorption_further_reduces_refracted_received_return() -> None:
    illumination = _illumination()
    reference_time = _reference_time(illumination)
    no_absorption = integrate_refracted_propagation_weighted_return(
        illumination=illumination,
        scattering_table=_table(),
        pulse=_pulse(),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=400_000.0,
        propagation_loss_model=PropagationLossModel(absorption_db_per_km=0.0),
    )
    with_absorption = integrate_refracted_propagation_weighted_return(
        illumination=illumination,
        scattering_table=_table(),
        pulse=_pulse(),
        reference_one_way_travel_time_seconds=reference_time,
        sample_rate_hz=400_000.0,
        propagation_loss_model=PropagationLossModel(absorption_db_per_km=40.0),
    )

    assert with_absorption.received_power_relative_db < no_absorption.received_power_relative_db
    assert with_absorption.minimum_two_way_transmission_loss_db > no_absorption.minimum_two_way_transmission_loss_db
    assert with_absorption.maximum_two_way_transmission_loss_db > no_absorption.maximum_two_way_transmission_loss_db


def test_longer_refracted_paths_have_larger_two_way_loss() -> None:
    illumination = _illumination(samples=41)
    result = integrate_refracted_propagation_weighted_return(
        illumination=illumination,
        scattering_table=_table(),
        pulse=_pulse(),
        reference_one_way_travel_time_seconds=_reference_time(illumination),
        sample_rate_hz=400_000.0,
        propagation_loss_model=PropagationLossModel(absorption_db_per_km=10.0),
    )

    assert result.maximum_one_way_path_length_m > result.minimum_one_way_path_length_m
    assert result.maximum_two_way_transmission_loss_db > result.minimum_two_way_transmission_loss_db

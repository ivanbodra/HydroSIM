from math import isclose

from hydrosim.visualization import BeamExplorerControls, prepare_beam_explorer_snapshot


def test_beam_explorer_snapshot_uses_frequency_for_wavelength_and_spacing_ratio():
    snapshot = prepare_beam_explorer_snapshot(
        BeamExplorerControls(
            frequency_hz=150_000.0,
            sound_speed_mps=1500.0,
            element_spacing_m=0.005,
            angular_sample_count=121,
        )
    )

    assert isclose(snapshot.wavelength_m, 0.01, abs_tol=1e-12)
    assert isclose(snapshot.spacing_over_wavelength, 0.5, abs_tol=1e-12)
    assert snapshot.along_track_half_power_beamwidth_rad > 0.0
    assert snapshot.across_track_half_power_beamwidth_rad > 0.0
    assert snapshot.nadir_footprint.effective_area_m2 > 0.0


def test_beam_explorer_retains_full_two_dimensional_modeled_response():
    snapshot = prepare_beam_explorer_snapshot(BeamExplorerControls(angular_sample_count=31))

    scan = snapshot.response_scan
    assert len(scan.along_track_angles_rad) == 31
    assert len(scan.across_track_angles_rad) == 31
    assert len(scan.samples) == 31 * 31
    assert scan is snapshot.along_track_scan
    assert scan is snapshot.across_track_scan
    center = 15 * 31 + 15
    assert isclose(float(scan.samples[center].normalized_power), 1.0, rel_tol=1e-12)
    assert any(0.0 < float(sample.normalized_power) < 0.5 for sample in scan.samples)


def test_beam_explorer_aperture_narrows_beam_and_footprint():
    small = prepare_beam_explorer_snapshot(BeamExplorerControls(elements_per_arm=8))
    large = prepare_beam_explorer_snapshot(BeamExplorerControls(elements_per_arm=16))

    assert large.element_center_span_m > small.element_center_span_m
    assert large.along_track_half_power_beamwidth_rad < small.along_track_half_power_beamwidth_rad
    assert large.nadir_footprint.effective_area_m2 < small.nadir_footprint.effective_area_m2


def test_beam_explorer_footprint_scales_with_depth_for_same_beam():
    shallow = prepare_beam_explorer_snapshot(BeamExplorerControls(seafloor_depth_m=20.0))
    deep = prepare_beam_explorer_snapshot(BeamExplorerControls(seafloor_depth_m=40.0))

    assert isclose(
        deep.nadir_footprint.beam_limited_along_track_width_m,
        2.0 * shallow.nadir_footprint.beam_limited_along_track_width_m,
        rel_tol=1e-12,
    )
    assert isclose(
        deep.nadir_footprint.effective_area_m2,
        4.0 * shallow.nadir_footprint.effective_area_m2,
        rel_tol=1e-12,
    )


def test_beam_explorer_rejects_even_angular_grid():
    controls = BeamExplorerControls(angular_sample_count=10)

    try:
        prepare_beam_explorer_snapshot(controls)
    except ValueError as exc:
        assert "odd integer" in str(exc)
    else:
        raise AssertionError("expected ValueError for an even angular grid")

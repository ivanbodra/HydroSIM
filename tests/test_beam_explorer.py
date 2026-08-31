from math import isclose

from hydrosim.visualization import BeamExplorerControls, prepare_beam_explorer_snapshot


def test_beam_explorer_snapshot_uses_frequency_for_wavelength_and_spacing_ratio():
    snapshot = prepare_beam_explorer_snapshot(
        BeamExplorerControls(
            frequency_hz=150_000.0,
            sound_speed_mps=1500.0,
            element_spacing_m=0.005,
            angular_sample_count= nine := 9,
        )
    )

    assert nine == 9
    assert isclose(snapshot.wavelength_m, 0.01, abs_tol=1e-12)
    assert isclose(snapshot.spacing_over_wavelength, 0.5, abs_tol=1e-12)
    assert len(snapshot.scan.samples) == 81


def test_beam_explorer_aperture_span_grows_with_element_count():
    small = prepare_beam_explorer_snapshot(
        BeamExplorerControls(elements_per_arm=8, angular_sample_count=5)
    )
    large = prepare_beam_explorer_snapshot(
        BeamExplorerControls(elements_per_arm=16, angular_sample_count=5)
    )

    assert large.element_center_span_m > small.element_center_span_m


def test_beam_explorer_rejects_even_angular_grid():
    controls = BeamExplorerControls(angular_sample_count=10)

    try:
        prepare_beam_explorer_snapshot(controls)
    except ValueError as exc:
        assert "odd integer" in str(exc)
    else:
        raise AssertionError("expected ValueError for an even angular grid")

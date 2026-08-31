from math import isclose

from hydrosim.visualization import (
    PropagationExplorerControls,
    prepare_propagation_explorer_snapshot,
)


def test_zero_processing_bias_closes_controlled_propagation_experiment():
    snapshot = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(processing_lower_layer_bias_mps=0.0)
    )

    assert len(snapshot.beams) == 9
    assert max(float(beam.sounding_error_norm_m) for beam in snapshot.beams) < 1e-8


def test_processing_bias_changes_reconstruction_but_not_truth_rays():
    reference = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(processing_lower_layer_bias_mps=0.0)
    )
    biased = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(processing_lower_layer_bias_mps=15.0)
    )

    for reference_beam, biased_beam in zip(reference.beams, biased.beams, strict=True):
        assert isclose(
            float(reference_beam.truth_bottom_point.y),
            float(biased_beam.truth_bottom_point.y),
            abs_tol=1e-10,
        )
        assert isclose(
            float(reference_beam.true_twtt_seconds),
            float(biased_beam.true_twtt_seconds),
            abs_tol=1e-12,
        )

    assert max(float(beam.sounding_error_norm_m) for beam in biased.beams) > 0.01


def test_processing_profile_support_is_explicit_and_truth_remains_bounded_to_bottom():
    snapshot = prepare_propagation_explorer_snapshot()

    assert float(snapshot.true_profile.layers[-1].bottom_depth_m) == 60.0
    assert float(snapshot.processing_profile.layers[-1].bottom_depth_m) == 11_000.0
    assert (
        float(snapshot.processing_profile.layers[-1].sound_speed_mps)
        == float(snapshot.processing_profile.layers[-2].sound_speed_mps)
    )


def test_propagation_explorer_preserves_symmetric_signed_fan():
    snapshot = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(maximum_beam_angle_deg=50.0, beam_count=5)
    )
    angles = [float(beam.configured_across_track_angle_rad) for beam in snapshot.beams]

    assert angles[0] < 0.0
    assert angles[2] == 0.0
    assert angles[-1] > 0.0
    assert isclose(abs(angles[0]), abs(angles[-1]), abs_tol=1e-12)

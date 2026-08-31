import pytest

from hydrosim.visualization import (
    PropagationExplorerControls,
    draw_layered_svp_explorer_snapshot,
    plot_layered_svp_explorer_snapshot,
    prepare_propagation_explorer_snapshot,
)

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")


def test_propagation_renderer_builds_three_causal_panels():
    import matplotlib.pyplot as plt

    snapshot = prepare_propagation_explorer_snapshot()
    figure, axes = plot_layered_svp_explorer_snapshot(snapshot)

    assert len(axes) == 3
    assert axes[0].get_title() == "Sound-speed profiles"
    assert axes[1].get_title() == "Truth rays and reconstructed swath"
    assert axes[2].get_title() == "Beamwise sounding error"
    plt.close(figure)


def test_propagation_renderer_redraws_existing_axes_for_processing_bias():
    import matplotlib.pyplot as plt

    figure, axes = plot_layered_svp_explorer_snapshot(
        prepare_propagation_explorer_snapshot()
    )
    identities = tuple(id(axis) for axis in axes)
    biased = prepare_propagation_explorer_snapshot(
        PropagationExplorerControls(processing_lower_layer_bias_mps=12.0)
    )
    draw_layered_svp_explorer_snapshot(biased, axes)

    assert tuple(id(axis) for axis in axes) == identities
    assert "lower-layer bias=+12.0 m/s" in figure._suptitle.get_text()
    plt.close(figure)

import pytest

from hydrosim.visualization import (
    BeamExplorerControls,
    draw_beam_explorer_snapshot,
    plot_beam_explorer_snapshot,
    prepare_beam_explorer_snapshot,
)

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")


def _snapshot(frequency_hz=150_000.0, elements=8):
    return prepare_beam_explorer_snapshot(
        BeamExplorerControls(
            frequency_hz=frequency_hz,
            elements_per_arm=elements,
            angular_sample_count=121,
        )
    )


def test_beam_renderer_builds_pattern_and_footprint_panels():
    import matplotlib.pyplot as plt

    figure, axes = plot_beam_explorer_snapshot(_snapshot())
    assert len(axes) == 3
    assert axes[0].get_title() == "Along-track principal plane"
    assert axes[1].get_title() == "Across-track principal plane"
    assert axes[2].get_title() == "Nadir -3 dB footprint at 30 m"
    assert "beamwidth → footprint" in figure._suptitle.get_text()
    plt.close(figure)


def test_beam_renderer_redraws_existing_axes():
    import matplotlib.pyplot as plt

    figure, axes = plot_beam_explorer_snapshot(_snapshot())
    identities = tuple(id(axis) for axis in axes)
    draw_beam_explorer_snapshot(_snapshot(300_000.0, 12), axes)
    assert tuple(id(axis) for axis in axes) == identities
    assert "300 kHz" in figure._suptitle.get_text()
    assert "footprint" in axes[2].get_title()
    plt.close(figure)

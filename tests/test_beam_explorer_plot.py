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
            angular_sample_count=61,
        )
    )


def test_beam_renderer_builds_pattern_and_continuous_response_panels():
    import matplotlib.pyplot as plt

    figure, axes = plot_beam_explorer_snapshot(_snapshot())
    assert len(axes) == 3
    assert axes[0].get_title() == "Along-track principal plane"
    assert axes[1].get_title() == "Across-track principal plane"
    assert axes[2].get_title() == "Modeled seafloor response at 30 m"
    assert "beamwidth → footprint" in figure._suptitle.get_text()
    assert len(axes[2].collections) >= 2
    assert len(axes[2].lines) == 2
    plt.close(figure)


def test_beam_renderer_response_is_not_a_hard_rectangle_outline():
    import matplotlib.pyplot as plt

    figure, axes = plot_beam_explorer_snapshot(_snapshot())
    footprint_axis = axes[2]

    assert all(len(line.get_xdata()) != 5 for line in footprint_axis.lines)
    assert footprint_axis.collections
    plt.close(figure)


def test_beam_renderer_redraws_existing_axes():
    import matplotlib.pyplot as plt

    figure, axes = plot_beam_explorer_snapshot(_snapshot())
    identities = tuple(id(axis) for axis in axes)
    draw_beam_explorer_snapshot(_snapshot(300_000.0, 12), axes)
    assert tuple(id(axis) for axis in axes) == identities
    assert "300 kHz" in figure._suptitle.get_text()
    assert "response" in axes[2].get_title()
    plt.close(figure)

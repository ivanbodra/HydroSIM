import pytest

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import (
    draw_signal_explorer_comparison,
    plot_signal_explorer_comparison,
    prepare_signal_explorer_snapshot,
)

pytest.importorskip("matplotlib")


def _comparison(center_frequency_hz: float, bandwidth_hz: float, duration_seconds: float):
    sample_rate_hz = max(80_000.0, 1.25 * bandwidth_hz)
    cw = prepare_signal_explorer_snapshot(
        ContinuousWavePulse(
            center_frequency_hz=center_frequency_hz,
            duration_seconds=duration_seconds,
        ),
        sample_rate_hz=sample_rate_hz,
    )
    lfm = prepare_signal_explorer_snapshot(
        LinearFMPulse(
            center_frequency_hz=center_frequency_hz,
            bandwidth_hz=bandwidth_hz,
            duration_seconds=duration_seconds,
        ),
        sample_rate_hz=sample_rate_hz,
    )
    return cw, lfm


def test_signal_renderer_builds_three_cw_vs_chirp_panels() -> None:
    cw, lfm = _comparison(100_000.0, 20_000.0, 1e-3)

    figure, axes = plot_signal_explorer_comparison(cw, lfm)
    try:
        assert len(axes) == 3
        assert axes[0].get_title() == "Transmitted waveform: complex baseband"
        assert axes[1].get_title() == "Phase evolution"
        assert axes[2].get_title() == "Pulse-compression response"
        assert len(axes[0].lines) == 3  # zero reference + CW + LFM
        assert len(axes[1].lines) == 2
        assert len(axes[2].lines) == 3  # zero-lag reference + CW + LFM
        assert "CW versus chirp" in figure._suptitle.get_text()
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)


def test_signal_renderer_accepts_input_order_reversed() -> None:
    cw, lfm = _comparison(70_000.0, 12_000.0, 5e-4)

    figure, axes = plot_signal_explorer_comparison(lfm, cw)
    try:
        labels = [line.get_label() for line in axes[2].lines]
        assert "CW" in labels
        assert "LFM chirp" in labels
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)


def test_signal_renderer_rejects_pair_without_cw_and_lfm() -> None:
    first = prepare_signal_explorer_snapshot(
        ContinuousWavePulse(center_frequency_hz=100_000.0, duration_seconds=1e-3),
        sample_rate_hz=40_000.0,
    )
    second = prepare_signal_explorer_snapshot(
        ContinuousWavePulse(center_frequency_hz=200_000.0, duration_seconds=1e-3),
        sample_rate_hz=40_000.0,
    )

    with pytest.raises(ValueError, match="one CW pulse and one LFM pulse"):
        plot_signal_explorer_comparison(first, second)


def test_signal_draw_redraws_in_place_without_accumulating_lines() -> None:
    first_cw, first_lfm = _comparison(100_000.0, 20_000.0, 1e-3)
    second_cw, second_lfm = _comparison(300_000.0, 60_000.0, 2e-3)

    figure, axes = plot_signal_explorer_comparison(first_cw, first_lfm)
    try:
        original_axis_ids = tuple(id(axis) for axis in axes)
        draw_signal_explorer_comparison(second_cw, second_lfm, axes)

        assert tuple(id(axis) for axis in axes) == original_axis_ids
        assert len(axes[0].lines) == 3
        assert len(axes[1].lines) == 2
        assert len(axes[2].lines) == 3
        assert "300 kHz" in figure._suptitle.get_text()
        assert "60 kHz bandwidth" in figure._suptitle.get_text()
    finally:
        import matplotlib.pyplot as plt

        plt.close(figure)


def test_signal_draw_requires_three_axes() -> None:
    cw, lfm = _comparison(100_000.0, 20_000.0, 1e-3)

    with pytest.raises(ValueError, match="exactly three axes"):
        draw_signal_explorer_comparison(cw, lfm, ())

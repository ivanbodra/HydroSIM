import pytest

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse
from hydrosim.visualization import (
    plot_signal_explorer_comparison,
    prepare_signal_explorer_snapshot,
)

pytest.importorskip("matplotlib")


def test_signal_renderer_builds_three_cw_vs_chirp_panels() -> None:
    sample_rate_hz = 80_000.0
    duration_seconds = 1e-3
    cw = prepare_signal_explorer_snapshot(
        ContinuousWavePulse(center_frequency_hz=100_000.0, duration_seconds=duration_seconds),
        sample_rate_hz=sample_rate_hz,
    )
    lfm = prepare_signal_explorer_snapshot(
        LinearFMPulse(
            center_frequency_hz=100_000.0,
            bandwidth_hz=20_000.0,
            duration_seconds=duration_seconds,
        ),
        sample_rate_hz=sample_rate_hz,
    )

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
    cw = prepare_signal_explorer_snapshot(
        ContinuousWavePulse(center_frequency_hz=70_000.0, duration_seconds=5e-4),
        sample_rate_hz=60_000.0,
    )
    lfm = prepare_signal_explorer_snapshot(
        LinearFMPulse(
            center_frequency_hz=70_000.0,
            bandwidth_hz=12_000.0,
            duration_seconds=5e-4,
        ),
        sample_rate_hz=60_000.0,
    )

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

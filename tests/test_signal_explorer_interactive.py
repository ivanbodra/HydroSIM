import pytest

from hydrosim.visualization import (
    SignalExplorerControls,
    launch_signal_explorer_interactive,
    prepare_signal_explorer_comparison,
)

pytest.importorskip("matplotlib")


def test_comparison_controls_build_cw_and_lfm_snapshots() -> None:
    controls = SignalExplorerControls(
        center_frequency_hz=300_000.0,
        duration_seconds=1e-3,
        lfm_bandwidth_hz=100_000.0,
        sample_rate_hz=400_000.0,
    )
    cw, lfm = prepare_signal_explorer_comparison(controls)

    assert cw.pulse.center_frequency_hz == pytest.approx(300_000.0)
    assert lfm.pulse.center_frequency_hz == pytest.approx(300_000.0)
    assert lfm.pulse.bandwidth_hz == pytest.approx(100_000.0)
    assert cw.sample_rate_hz == pytest.approx(400_000.0)
    assert lfm.sample_rate_hz == pytest.approx(400_000.0)


def test_controls_reject_lfm_sampling_below_baseband_nyquist() -> None:
    controls = SignalExplorerControls(lfm_bandwidth_hz=200_000.0, sample_rate_hz=150_000.0)
    with pytest.raises(ValueError, match="Nyquist"):
        prepare_signal_explorer_comparison(controls)


def test_interactive_shell_exposes_three_sliders() -> None:
    import matplotlib.pyplot as plt

    figure, axes = launch_signal_explorer_interactive()
    try:
        assert len(axes) == 3
        controls = figure.hydrosim_signal_explorer_controls
        assert set(controls) == {"frequency", "duration", "bandwidth"}
        controls["bandwidth"].set_val(150.0)
        assert axes[2].get_title() == "Pulse-compression response"
    finally:
        plt.close(figure)

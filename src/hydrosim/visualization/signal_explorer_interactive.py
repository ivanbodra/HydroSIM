"""Interactive Matplotlib shell for the HydroSIM Didactic Signal Explorer.

This module adds presentation controls only. Every control change rebuilds the
rendered state through :func:`prepare_signal_explorer_snapshot`; waveform and
matched-filter physics remain in the Scientific Core.
"""

from __future__ import annotations

from dataclasses import dataclass

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse

from .signal_explorer import prepare_signal_explorer_snapshot
from .signal_explorer_plot import (
    draw_signal_explorer_comparison,
    plot_signal_explorer_comparison,
)


@dataclass(frozen=True)
class SignalExplorerControls:
    """Small control state for the first interactive signal lesson."""

    center_frequency_hz: float = 300_000.0
    duration_seconds: float = 1e-3
    lfm_bandwidth_hz: float = 100_000.0
    sample_rate_hz: float = 400_000.0

    def validate(self) -> None:
        if self.center_frequency_hz <= 0.0:
            raise ValueError("center_frequency_hz must be positive")
        if self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if self.lfm_bandwidth_hz <= 0.0:
            raise ValueError("lfm_bandwidth_hz must be positive")
        if self.sample_rate_hz < self.lfm_bandwidth_hz:
            raise ValueError("sample_rate_hz must satisfy the LFM complex-baseband Nyquist condition")


def prepare_signal_explorer_comparison(controls: SignalExplorerControls):
    """Build the CW/LFM snapshots represented by one control state."""

    controls.validate()
    cw = ContinuousWavePulse(
        center_frequency_hz=controls.center_frequency_hz,
        duration_seconds=controls.duration_seconds,
    )
    lfm = LinearFMPulse(
        center_frequency_hz=controls.center_frequency_hz,
        bandwidth_hz=controls.lfm_bandwidth_hz,
        duration_seconds=controls.duration_seconds,
    )
    return (
        prepare_signal_explorer_snapshot(cw, sample_rate_hz=controls.sample_rate_hz),
        prepare_signal_explorer_snapshot(lfm, sample_rate_hz=controls.sample_rate_hz),
    )


def launch_signal_explorer_interactive(
    controls: SignalExplorerControls | None = None,
):
    """Launch the first interactive CW-versus-chirp lesson.

    Sliders control center frequency, pulse duration, and LFM bandwidth. The
    sample rate is kept automatically above the represented complex-baseband
    Nyquist limit. Center frequency is intentionally a waveform-definition
    control here: propagation/absorption consequences are not shown until a
    referenced frequency-dependent absorption model is connected.
    """

    try:
        from matplotlib.widgets import Slider
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "Matplotlib is required for launch_signal_explorer_interactive; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    state = controls or SignalExplorerControls()
    state.validate()

    cw, lfm = prepare_signal_explorer_comparison(state)
    figure, axes = plot_signal_explorer_comparison(cw, lfm)
    figure.subplots_adjust(bottom=0.30)

    frequency_ax = figure.add_axes((0.14, 0.18, 0.72, 0.03))
    duration_ax = figure.add_axes((0.14, 0.12, 0.72, 0.03))
    bandwidth_ax = figure.add_axes((0.14, 0.06, 0.72, 0.03))

    frequency_slider = Slider(
        frequency_ax,
        "Center frequency (kHz)",
        50.0,
        700.0,
        valinit=state.center_frequency_hz / 1e3,
    )
    duration_slider = Slider(
        duration_ax,
        "Pulse duration (ms)",
        0.1,
        5.0,
        valinit=state.duration_seconds * 1e3,
    )
    bandwidth_slider = Slider(
        bandwidth_ax,
        "LFM bandwidth (kHz)",
        10.0,
        300.0,
        valinit=state.lfm_bandwidth_hz / 1e3,
    )

    def _redraw(_value: float) -> None:
        bandwidth_hz = float(bandwidth_slider.val) * 1e3
        updated = SignalExplorerControls(
            center_frequency_hz=float(frequency_slider.val) * 1e3,
            duration_seconds=float(duration_slider.val) * 1e-3,
            lfm_bandwidth_hz=bandwidth_hz,
            sample_rate_hz=max(float(state.sample_rate_hz), 1.25 * bandwidth_hz),
        )
        new_cw, new_lfm = prepare_signal_explorer_comparison(updated)
        draw_signal_explorer_comparison(new_cw, new_lfm, axes)
        figure.canvas.draw_idle()

    for slider in (frequency_slider, duration_slider, bandwidth_slider):
        slider.on_changed(_redraw)

    # Keep widget references alive and make them accessible to tests/embedders.
    figure.hydrosim_signal_explorer_controls = {
        "frequency": frequency_slider,
        "duration": duration_slider,
        "bandwidth": bandwidth_slider,
    }
    return figure, axes

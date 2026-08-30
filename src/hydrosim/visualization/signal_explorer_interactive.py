"""Interactive Matplotlib shell for the HydroSIM Didactic Signal Explorer.

This module adds presentation controls only. Every control change rebuilds the
rendered state through :func:`prepare_signal_explorer_snapshot`; waveform and
matched-filter physics remain in the Scientific Core.
"""

from __future__ import annotations

from dataclasses import dataclass

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse

from .signal_explorer import prepare_signal_explorer_snapshot
from .signal_explorer_plot import plot_signal_explorer_comparison


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
        import matplotlib.pyplot as plt
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

        for axis in axes:
            axis.clear()

        # Reuse the same scientific snapshots but redraw in-place so the widgets
        # remain attached to this figure.
        from .signal_explorer_plot import _time_scale
        import numpy as np

        duration_max = max(
            float(new_cw.pulse.duration_seconds), float(new_lfm.pulse.duration_seconds)
        )
        scale, unit = _time_scale(duration_max)
        waveform_axis, phase_axis, matched_axis = axes
        for snapshot, label in ((new_cw, "CW"), (new_lfm, "LFM chirp")):
            time = np.asarray(snapshot.time_seconds, dtype=float) * scale
            waveform_axis.plot(time, snapshot.baseband_real, label=label)
            phase_axis.plot(time, snapshot.unwrapped_baseband_phase_rad, label=label)
            lag = np.asarray(snapshot.autocorrelation.lag_seconds, dtype=float) * scale
            matched_axis.plot(lag, snapshot.autocorrelation.normalized_amplitude, label=label)

        waveform_axis.axhline(0.0, linewidth=0.8)
        waveform_axis.set(
            xlabel=f"Pulse time ({unit})",
            ylabel="In-phase baseband component",
            title="Transmitted waveform: complex baseband",
        )
        phase_axis.set(
            xlabel=f"Pulse time ({unit})",
            ylabel="Unwrapped phase (rad)",
            title="Phase evolution",
        )
        matched_axis.axvline(0.0, linewidth=0.8)
        matched_axis.set(
            xlabel=f"Matched-filter lag ({unit})",
            ylabel="Normalized amplitude",
            title="Pulse-compression response",
        )
        matched_axis.set_ylim(bottom=0.0)
        for axis in axes:
            axis.legend()
        figure.suptitle(
            "HydroSIM Didactic Explorer — CW versus chirp\n"
            f"center {updated.center_frequency_hz / 1e3:g} kHz | "
            f"LFM bandwidth {updated.lfm_bandwidth_hz / 1e3:g} kHz"
        )
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

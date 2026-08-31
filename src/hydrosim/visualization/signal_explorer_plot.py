"""Concrete renderer for the HydroSIM Didactic Signal Explorer.

The renderer compares one finite-duration CW pulse with one LFM/chirp pulse using
an existing :class:`SignalExplorerSnapshot` for each waveform. It introduces no
new waveform or matched-filter physics. The same draw function is shared by the
standalone Matplotlib renderer and application shells so presentation code does
not duplicate scientific-state interpretation.

The three panels expose the same scientific state from different didactic views:

- in-phase complex-baseband component versus time;
- unwrapped complex-baseband phase versus time;
- normalized matched-filter/autocorrelation amplitude versus lag.

Matplotlib remains an optional visualization dependency.
"""

from __future__ import annotations

import numpy as np

from hydrosim.acquisition import ContinuousWavePulse, LinearFMPulse

from .signal_explorer import SignalExplorerSnapshot


def _time_scale(seconds: float) -> tuple[float, str]:
    """Choose a readable display scale without changing scientific values."""

    magnitude = abs(float(seconds))
    if magnitude < 1e-3:
        return 1e6, "µs"
    if magnitude < 1.0:
        return 1e3, "ms"
    return 1.0, "s"


def _require_cw_lfm_pair(
    first: SignalExplorerSnapshot,
    second: SignalExplorerSnapshot,
) -> tuple[SignalExplorerSnapshot, SignalExplorerSnapshot]:
    snapshots = (first, second)
    cw = next((item for item in snapshots if isinstance(item.pulse, ContinuousWavePulse)), None)
    lfm = next((item for item in snapshots if isinstance(item.pulse, LinearFMPulse)), None)
    if cw is None or lfm is None:
        raise ValueError("Signal Explorer comparison requires one CW pulse and one LFM pulse")
    return cw, lfm


def draw_signal_explorer_comparison(
    first: SignalExplorerSnapshot,
    second: SignalExplorerSnapshot,
    axes,
    *,
    clear: bool = True,
):
    """Draw a CW-versus-LFM comparison into three existing Matplotlib axes."""

    if len(axes) != 3:
        raise ValueError("Signal Explorer rendering requires exactly three axes")

    cw, lfm = _require_cw_lfm_pair(first, second)
    waveform_axis, phase_axis, matched_axis = axes
    if clear:
        for axis in axes:
            axis.clear()

    duration_max = max(float(cw.pulse.duration_seconds), float(lfm.pulse.duration_seconds))
    scale, unit = _time_scale(duration_max)

    for snapshot, label in ((cw, "CW"), (lfm, "LFM chirp")):
        time = np.asarray(snapshot.time_seconds, dtype=float) * scale
        real = np.asarray(snapshot.baseband_real, dtype=float)
        phase = np.asarray(snapshot.unwrapped_baseband_phase_rad, dtype=float)
        waveform_axis.plot(time, real, label=label)
        phase_axis.plot(time, phase, label=label)

        lag = np.asarray(snapshot.autocorrelation.lag_seconds, dtype=float) * scale
        matched = np.asarray(snapshot.autocorrelation.normalized_amplitude, dtype=float)
        matched_axis.plot(lag, matched, label=label)

    waveform_axis.axhline(0.0, linewidth=0.8)
    waveform_axis.set_xlabel(f"Pulse time ({unit})")
    waveform_axis.set_ylabel("In-phase baseband")
    waveform_axis.set_title("Transmitted waveform")
    waveform_axis.legend(loc="upper right")
    waveform_axis.grid(alpha=0.18)

    phase_axis.set_xlabel(f"Pulse time ({unit})")
    phase_axis.set_ylabel("Phase (rad)")
    phase_axis.set_title("Phase evolution")
    phase_axis.legend(loc="upper left")
    phase_axis.grid(alpha=0.18)

    matched_axis.axvline(0.0, linewidth=0.8)
    matched_axis.set_xlabel(f"Matched-filter lag ({unit})")
    matched_axis.set_ylabel("Normalized amplitude")
    matched_axis.set_title("Pulse-compression response")
    matched_axis.set_ylim(bottom=0.0)
    matched_axis.legend(loc="upper right")
    matched_axis.grid(alpha=0.18)

    waveform_axis.figure.subplots_adjust(left=0.08, right=0.985, bottom=0.10, top=0.95)
    return axes


def plot_signal_explorer_comparison(
    first: SignalExplorerSnapshot,
    second: SignalExplorerSnapshot,
):
    """Create a standalone CW-versus-chirp comparison figure."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "Matplotlib is required for plot_signal_explorer_comparison; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    figure = plt.figure(figsize=(12.8, 7.0))
    grid = figure.add_gridspec(2, 2, height_ratios=(1.05, 1.0), hspace=0.34, wspace=0.26)
    axes = (
        figure.add_subplot(grid[0, :]),
        figure.add_subplot(grid[1, 0]),
        figure.add_subplot(grid[1, 1]),
    )
    draw_signal_explorer_comparison(first, second, axes, clear=False)
    return figure, axes

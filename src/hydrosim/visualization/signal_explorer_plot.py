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
    """Draw a CW-versus-LFM comparison into three existing Matplotlib axes.

    This is the stable renderer boundary used by interactive/application shells.
    It only interprets already-computed snapshot state; it does not calculate
    waveform, sampling, matched-filter, propagation, or attenuation physics.
    """

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
    waveform_axis.set_ylabel("In-phase baseband component")
    waveform_axis.set_title("Transmitted waveform: complex baseband")
    waveform_axis.legend()

    phase_axis.set_xlabel(f"Pulse time ({unit})")
    phase_axis.set_ylabel("Unwrapped phase (rad)")
    phase_axis.set_title("Phase evolution")
    phase_axis.legend()

    matched_axis.axvline(0.0, linewidth=0.8)
    matched_axis.set_xlabel(f"Matched-filter lag ({unit})")
    matched_axis.set_ylabel("Normalized amplitude")
    matched_axis.set_title("Pulse-compression response")
    matched_axis.set_ylim(bottom=0.0)
    matched_axis.legend()

    cw_frequency_khz = float(cw.pulse.center_frequency_hz) / 1e3
    lfm_center_khz = float(lfm.pulse.center_frequency_hz) / 1e3
    lfm_bandwidth_khz = float(lfm.pulse.bandwidth_hz) / 1e3
    waveform_axis.figure.suptitle(
        "HydroSIM Didactic Explorer — CW versus chirp\n"
        f"CW: {cw_frequency_khz:g} kHz | "
        f"LFM: {lfm_center_khz:g} kHz center, {lfm_bandwidth_khz:g} kHz bandwidth"
    )
    return axes


def plot_signal_explorer_comparison(
    first: SignalExplorerSnapshot,
    second: SignalExplorerSnapshot,
):
    """Create a standalone three-panel CW-versus-chirp comparison figure."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "Matplotlib is required for plot_signal_explorer_comparison; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    figure = plt.figure(figsize=(13.5, 4.8))
    grid = figure.add_gridspec(1, 3, wspace=0.32)
    axes = (
        figure.add_subplot(grid[0, 0]),
        figure.add_subplot(grid[0, 1]),
        figure.add_subplot(grid[0, 2]),
    )
    draw_signal_explorer_comparison(first, second, axes, clear=False)
    return figure, axes

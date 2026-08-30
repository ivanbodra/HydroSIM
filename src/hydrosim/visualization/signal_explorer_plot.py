"""First concrete renderer for the HydroSIM Didactic Signal Explorer.

The renderer compares one finite-duration CW pulse with one LFM/chirp pulse using
an existing :class:`SignalExplorerSnapshot` for each waveform. It introduces no
new waveform or matched-filter physics. The three panels intentionally expose the
same scientific state from different didactic viewpoints:

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


def plot_signal_explorer_comparison(
    first: SignalExplorerSnapshot,
    second: SignalExplorerSnapshot,
):
    """Render the first CW-versus-chirp Didactic Explorer comparison.

    The caller may provide the snapshots in either order. Each waveform keeps its
    own sample rate and duration. Time and lag axes use a common display unit chosen
    from the largest physical duration represented in the pair.
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "Matplotlib is required for plot_signal_explorer_comparison; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    cw, lfm = _require_cw_lfm_pair(first, second)
    duration_max = max(float(cw.pulse.duration_seconds), float(lfm.pulse.duration_seconds))
    scale, unit = _time_scale(duration_max)

    figure = plt.figure(figsize=(13.5, 4.8))
    grid = figure.add_gridspec(1, 3, wspace=0.32)
    waveform_axis = figure.add_subplot(grid[0, 0])
    phase_axis = figure.add_subplot(grid[0, 1])
    matched_axis = figure.add_subplot(grid[0, 2])

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
    figure.suptitle(
        "HydroSIM Didactic Explorer — CW versus chirp\n"
        f"CW: {cw_frequency_khz:g} kHz | "
        f"LFM: {lfm_center_khz:g} kHz center, {lfm_bandwidth_khz:g} kHz bandwidth"
    )
    return figure, (waveform_axis, phase_axis, matched_axis)

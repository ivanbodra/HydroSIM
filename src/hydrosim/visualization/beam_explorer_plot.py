"""Renderer for the HydroSIM Beam Explorer lesson.

The renderer consumes an existing BeamExplorerSnapshot and introduces no new
beam-pattern or footprint physics.
"""

from __future__ import annotations

from math import degrees

import numpy as np

from .beam_explorer import BeamExplorerSnapshot


def _power_db(amplitude: np.ndarray, floor_db: float = -40.0) -> np.ndarray:
    power = np.asarray(amplitude, dtype=float) ** 2
    return 10.0 * np.log10(np.maximum(power, 10.0 ** (floor_db / 10.0)))


def _principal_plane_samples(scan, *, varying_axis: str):
    n_along = len(scan.along_track_angles_rad)
    n_across = len(scan.across_track_angles_rad)
    if varying_axis == "along":
        center_across = n_across // 2
        return (
            [scan.samples[i * n_across + center_across] for i in range(n_along)],
            np.array([degrees(float(v)) for v in scan.along_track_angles_rad]),
        )
    if varying_axis == "across":
        center_along = n_along // 2
        return (
            [scan.samples[center_along * n_across + j] for j in range(n_across)],
            np.array([degrees(float(v)) for v in scan.across_track_angles_rad]),
        )
    raise ValueError("varying_axis must be 'along' or 'across'")


def draw_beam_explorer_snapshot(snapshot: BeamExplorerSnapshot, axes) -> None:
    """Draw principal-plane responses and the derived nadir -3 dB footprint."""

    along_axis, across_axis, footprint_axis = axes
    for axis in axes:
        axis.clear()

    along_samples, along_deg = _principal_plane_samples(snapshot.along_track_scan, varying_axis="along")
    across_samples, across_deg = _principal_plane_samples(snapshot.across_track_scan, varying_axis="across")

    for samples, angle, axis, title in (
        (along_samples, along_deg, along_axis, "Along-track principal plane"),
        (across_samples, across_deg, across_axis, "Across-track principal plane"),
    ):
        tx = _power_db(np.array([float(s.transmit_amplitude) for s in samples]))
        rx = _power_db(np.array([float(s.receive_amplitude) for s in samples]))
        two_way = _power_db(np.array([float(s.normalized_amplitude) for s in samples]))
        axis.plot(angle, tx, label="TX")
        axis.plot(angle, rx, label="RX")
        axis.plot(angle, two_way, label="TX × RX")
        axis.axhline(-3.0, linewidth=0.8, linestyle="--")
        axis.axvline(0.0, linewidth=0.8)
        axis.set_ylim(-40.0, 1.0)
        axis.set_xlabel("Angle (deg)")
        axis.set_ylabel("Normalized power (dB)")
        axis.set_title(title)
        axis.legend()

    fp = snapshot.nadir_footprint
    along = float(fp.beam_limited_along_track_width_m)
    across = float(fp.effective_across_track_width_m)
    rectangle = np.array(
        [[-along / 2, -across / 2], [along / 2, -across / 2], [along / 2, across / 2], [-along / 2, across / 2], [-along / 2, -across / 2]]
    )
    footprint_axis.plot(rectangle[:, 0], rectangle[:, 1], linewidth=2.0)
    footprint_axis.axhline(0.0, linewidth=0.6)
    footprint_axis.axvline(0.0, linewidth=0.6)
    margin = 1.35 * max(along, across)
    footprint_axis.set_xlim(-margin / 2, margin / 2)
    footprint_axis.set_ylim(-margin / 2, margin / 2)
    footprint_axis.set_aspect("equal", adjustable="box")
    footprint_axis.set_xlabel("Along-track (m)")
    footprint_axis.set_ylabel("Across-track (m)")
    footprint_axis.set_title(f"Nadir -3 dB footprint at {snapshot.controls.seafloor_depth_m:g} m")
    footprint_axis.text(
        0.5,
        0.04,
        f"{along:.2f} m × {across:.2f} m\narea ≈ {float(fp.effective_area_m2):.2f} m²",
        transform=footprint_axis.transAxes,
        ha="center",
        va="bottom",
    )

    frequency_khz = snapshot.controls.frequency_hz / 1e3
    wavelength_mm = snapshot.wavelength_m * 1e3
    along_bw = degrees(snapshot.along_track_half_power_beamwidth_rad)
    across_bw = degrees(snapshot.across_track_half_power_beamwidth_rad)
    axes[0].figure.suptitle(
        "HydroSIM Didactic Explorer — frequency × aperture → beamwidth → footprint\n"
        f"{frequency_khz:g} kHz | λ={wavelength_mm:.2f} mm | d/λ={snapshot.spacing_over_wavelength:.2f} | "
        f"-3 dB: {along_bw:.2f}° × {across_bw:.2f}°"
    )


def plot_beam_explorer_snapshot(snapshot: BeamExplorerSnapshot):
    """Create the complete first Beam Explorer figure."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Matplotlib is required for plot_beam_explorer_snapshot; install the visualization extra"
        ) from exc

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.8))
    draw_beam_explorer_snapshot(snapshot, axes)
    figure.subplots_adjust(wspace=0.32, top=0.80)
    return figure, axes

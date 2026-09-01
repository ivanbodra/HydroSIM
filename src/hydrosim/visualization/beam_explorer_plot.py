"""Renderer for the HydroSIM Beam Explorer lesson.

The renderer consumes an existing BeamExplorerSnapshot and introduces no new
beam-pattern or footprint physics. The seafloor panel projects the modeled 2D
TX × RX angular response onto a flat seafloor at the configured depth.
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
    peak_along_index = min(
        range(n_along),
        key=lambda index: abs(
            float(scan.along_track_angles_rad[index]) - float(scan.peak_along_track_angle_rad)
        ),
    )
    peak_across_index = min(
        range(n_across),
        key=lambda index: abs(
            float(scan.across_track_angles_rad[index]) - float(scan.peak_across_track_angle_rad)
        ),
    )
    if varying_axis == "along":
        return (
            [scan.samples[i * n_across + peak_across_index] for i in range(n_along)],
            np.array([degrees(float(v)) for v in scan.along_track_angles_rad]),
        )
    if varying_axis == "across":
        return (
            [scan.samples[peak_along_index * n_across + j] for j in range(n_across)],
            np.array([degrees(float(v)) for v in scan.across_track_angles_rad]),
        )
    raise ValueError("varying_axis must be 'along' or 'across'")


def _project_response_to_flat_seafloor(snapshot: BeamExplorerSnapshot):
    """Return along/across coordinates and modeled normalized power in dB."""

    scan = snapshot.response_scan
    depth = float(snapshot.controls.seafloor_depth_m)
    along = depth * np.tan(np.asarray(scan.along_track_angles_rad, dtype=float))
    across = -depth * np.tan(np.asarray(scan.across_track_angles_rad, dtype=float))
    power = np.asarray([float(sample.normalized_power) for sample in scan.samples], dtype=float)
    power = power.reshape((len(along), len(across)))
    peak = float(np.max(power))
    if peak <= 0.0:
        raise ValueError("Beam Explorer response scan has no positive power")
    power_db = 10.0 * np.log10(np.maximum(power / peak, 1e-4))
    return along, across, power_db


def draw_beam_explorer_snapshot(snapshot: BeamExplorerSnapshot, axes) -> None:
    """Draw principal-plane responses and the modeled seafloor response."""

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

    along_m, across_m, power_db = _project_response_to_flat_seafloor(snapshot)
    footprint_axis.pcolormesh(
        along_m,
        across_m,
        power_db.T,
        shading="auto",
        vmin=-40.0,
        vmax=0.0,
    )
    footprint_axis.contour(
        along_m,
        across_m,
        power_db.T,
        levels=[-3.0],
        linewidths=1.5,
    )
    footprint_axis.axhline(0.0, linewidth=0.6)
    footprint_axis.axvline(0.0, linewidth=0.6)

    fp = snapshot.nadir_footprint
    along_width = float(fp.beam_limited_along_track_width_m)
    across_width = float(fp.effective_across_track_width_m)
    margin = 2.5 * max(along_width, across_width)
    projected_center = -float(snapshot.steered_across_track_center_offset_m)
    footprint_axis.set_xlim(-margin, margin)
    footprint_axis.set_ylim(projected_center - margin, projected_center + margin)
    footprint_axis.set_aspect("equal", adjustable="box")
    footprint_axis.set_xlabel("Along-track (m)")
    footprint_axis.set_ylabel("Across-track (m)")
    footprint_axis.set_title(f"Modeled seafloor response at {snapshot.controls.seafloor_depth_m:g} m")
    footprint_axis.text(
        0.5,
        0.04,
        f"-3 dB ≈ {along_width:.2f} m × {across_width:.2f} m\n"
        f"steering={snapshot.controls.across_track_steering_angle_deg:+.0f}°",
        transform=footprint_axis.transAxes,
        ha="center",
        va="bottom",
    )

    frequency_khz = snapshot.controls.frequency_hz / 1e3
    wavelength_mm = snapshot.wavelength_m * 1e3
    along_bw = degrees(snapshot.along_track_half_power_beamwidth_rad)
    across_bw = degrees(snapshot.across_track_half_power_beamwidth_rad)
    axes[0].figure.suptitle(
        "HydroSIM Didactic Explorer — frequency × aperture × steering → beam pattern → footprint\n"
        f"{frequency_khz:g} kHz | λ={wavelength_mm:.2f} mm | d/λ={snapshot.spacing_over_wavelength:.2f} | "
        f"steering={snapshot.controls.across_track_steering_angle_deg:+.0f}° | "
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

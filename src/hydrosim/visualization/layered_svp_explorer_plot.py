"""Renderer for the layered-SVP Didactic Explorer.

The renderer consumes an existing :class:`LayeredSvpExplorerSnapshot`. It does not
perform acquisition or propagation calculations and therefore introduces no new
scientific model. Matplotlib remains an optional visualization dependency.
"""

from __future__ import annotations

from math import degrees

import numpy as np

from .layered_svp_explorer import LayeredSvpExplorerSnapshot


def _profile_step_coordinates(
    profile,
    *,
    start_depth_m: float,
    maximum_depth_m: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    speeds: list[float] = []
    depths: list[float] = []
    for layer in profile.layers:
        top = max(float(layer.top_depth_m), start_depth_m)
        bottom = float(layer.bottom_depth_m)
        if maximum_depth_m is not None:
            if top >= maximum_depth_m:
                break
            bottom = min(bottom, maximum_depth_m)
        if bottom <= start_depth_m:
            continue
        speeds.extend((float(layer.sound_speed_mps), float(layer.sound_speed_mps)))
        depths.extend((top, bottom))
    return np.asarray(speeds), np.asarray(depths)


def _truth_ray_plot_coordinates(beam, *, sensor_y: float, sensor_z: float) -> tuple[list[float], list[float]]:
    """Convert layered path increments to signed N-frame plotting coordinates."""

    bottom_delta_y = float(beam.truth_bottom_point.y) - sensor_y
    if abs(bottom_delta_y) <= 1e-15:
        horizontal_sign = 0.0
    else:
        horizontal_sign = 1.0 if bottom_delta_y > 0.0 else -1.0

    path_start_depth = float(beam.truth_ray_path.start_depth_m)
    y_coordinates = [sensor_y]
    z_coordinates = [sensor_z]
    cumulative_horizontal = 0.0
    for segment in beam.truth_ray_path.segments:
        cumulative_horizontal += float(segment.horizontal_distance_m)
        y_coordinates.append(sensor_y + horizontal_sign * cumulative_horizontal)
        z_coordinates.append(sensor_z + float(segment.end_depth_m) - path_start_depth)
    return y_coordinates, z_coordinates


def draw_layered_svp_explorer_snapshot(snapshot: LayeredSvpExplorerSnapshot, axes) -> None:
    """Redraw an existing three-axis layered-SVP figure in place."""

    profile_axis, swath_axis, error_axis = axes
    for axis in axes:
        axis.clear()

    display_depth = float(snapshot.terrain_depth_m)
    true_c, true_z = _profile_step_coordinates(
        snapshot.true_profile,
        start_depth_m=float(snapshot.profile_start_depth_m),
        maximum_depth_m=display_depth,
    )
    proc_c, proc_z = _profile_step_coordinates(
        snapshot.processing_profile,
        start_depth_m=float(snapshot.profile_start_depth_m),
        maximum_depth_m=display_depth,
    )
    profile_axis.plot(true_c, true_z, label="Truth SVP")
    profile_axis.plot(proc_c, proc_z, linestyle="--", label="Processing SVP")
    profile_axis.set_xlabel("Sound speed (m/s)")
    profile_axis.set_ylabel("Depth, +down (m)")
    profile_axis.set_title("Sound-speed profiles")
    profile_axis.invert_yaxis()
    profile_axis.legend()

    sensor_y = float(snapshot.sensor_pose.position.y)
    sensor_z = float(snapshot.sensor_pose.position.z)
    swath_axis.scatter((sensor_y,), (sensor_z,), marker="v", label="Transducer")
    swath_axis.axhline(float(snapshot.terrain_depth_m), linewidth=1.0, label="Truth bottom")

    truth_y: list[float] = []
    truth_z: list[float] = []
    reconstructed_y: list[float] = []
    reconstructed_z: list[float] = []
    angles_deg: list[float] = []
    vertical_errors: list[float] = []
    across_errors: list[float] = []

    for beam in snapshot.beams:
        ray_y, ray_z = _truth_ray_plot_coordinates(beam, sensor_y=sensor_y, sensor_z=sensor_z)
        swath_axis.plot(ray_y, ray_z, linewidth=0.9, alpha=0.7)
        truth_y.append(float(beam.truth_bottom_point.y))
        truth_z.append(float(beam.truth_bottom_point.z))
        reconstructed_y.append(float(beam.reconstructed_bottom_point.y))
        reconstructed_z.append(float(beam.reconstructed_bottom_point.z))
        angles_deg.append(degrees(float(beam.configured_across_track_angle_rad)))
        vertical_errors.append(float(beam.vertical_error_m))
        across_errors.append(float(beam.across_track_error_m))

    swath_axis.scatter(truth_y, truth_z, marker="o", label="Truth intersections")
    swath_axis.scatter(reconstructed_y, reconstructed_z, marker="x", label="Reconstructed soundings")
    swath_axis.set_xlabel("Across-track y (m): +starboard")
    swath_axis.set_ylabel("Depth z, +down (m)")
    swath_axis.set_title("Truth rays and reconstructed swath")
    swath_axis.invert_yaxis()
    swath_axis.legend()

    error_axis.axhline(0.0, linewidth=0.8)
    error_axis.plot(angles_deg, vertical_errors, marker="o", label="Vertical error")
    error_axis.plot(angles_deg, across_errors, marker="x", label="Across-track error")
    error_axis.set_xlabel("Configured across-track angle (deg)")
    error_axis.set_ylabel("Calculated - Truth error (m)")
    error_axis.set_title("Beamwise sounding error")
    error_axis.legend()

    max_error = max((float(beam.sounding_error_norm_m) for beam in snapshot.beams), default=0.0)
    profile_bias = (
        float(snapshot.processing_profile.layers[-1].sound_speed_mps)
        - float(snapshot.true_profile.layers[-1].sound_speed_mps)
    )
    profile_axis.figure.suptitle(
        "HydroSIM Didactic Explorer — processing SVP mismatch\n"
        f"lower-layer bias={profile_bias:+.1f} m/s | max sounding error={max_error:.3f} m"
    )


def plot_layered_svp_explorer_snapshot(snapshot: LayeredSvpExplorerSnapshot):
    """Create the layered-SVP figure and render its first snapshot."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Matplotlib is required for plot_layered_svp_explorer_snapshot; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    figure = plt.figure(figsize=(14.0, 5.2))
    grid = figure.add_gridspec(1, 3, width_ratios=(0.8, 1.8, 1.1), wspace=0.32)
    axes = (
        figure.add_subplot(grid[0, 0]),
        figure.add_subplot(grid[0, 1]),
        figure.add_subplot(grid[0, 2]),
    )
    draw_layered_svp_explorer_snapshot(snapshot, axes)
    return figure, axes

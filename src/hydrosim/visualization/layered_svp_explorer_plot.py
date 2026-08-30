"""First concrete renderer for the layered-SVP Didactic Explorer.

This module renders an existing :class:`LayeredSvpExplorerSnapshot`. It does not
perform acquisition or propagation calculations and therefore introduces no new
scientific model. Matplotlib remains an optional visualization dependency.
"""

from __future__ import annotations

from math import degrees

import numpy as np

from .layered_svp_explorer import LayeredSvpExplorerSnapshot


def _profile_step_coordinates(profile, *, start_depth_m: float) -> tuple[np.ndarray, np.ndarray]:
    speeds: list[float] = []
    depths: list[float] = []
    for layer in profile.layers:
        top = max(float(layer.top_depth_m), start_depth_m)
        bottom = float(layer.bottom_depth_m)
        if bottom <= start_depth_m:
            continue
        speeds.extend((float(layer.sound_speed_mps), float(layer.sound_speed_mps)))
        depths.extend((top, bottom))
    return np.asarray(speeds), np.asarray(depths)


def _truth_ray_plot_coordinates(beam, *, sensor_y: float, sensor_z: float) -> tuple[list[float], list[float]]:
    """Convert layered path increments to N-frame cross-track plotting coordinates.

    ``LayeredRayPath`` stores positive horizontal distance magnitudes because the
    propagation model is a principal-plane ray tracer. The signed N-frame side is
    already represented by the experiment's Truth bottom point, so visualization
    recovers that sign without introducing a second beam-angle convention.
    """

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
        z_coordinates.append(
            sensor_z + float(segment.end_depth_m) - path_start_depth
        )

    return y_coordinates, z_coordinates


def plot_layered_svp_explorer_snapshot(snapshot: LayeredSvpExplorerSnapshot):
    """Render SVPs, cross-track geometry, and beamwise error in one figure."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional environment
        raise ImportError(
            "Matplotlib is required for plot_layered_svp_explorer_snapshot; "
            "install HydroSIM with the 'visualization' extra"
        ) from exc

    figure = plt.figure(figsize=(14.0, 5.2))
    grid = figure.add_gridspec(1, 3, width_ratios=(0.8, 1.8, 1.1), wspace=0.32)
    profile_axis = figure.add_subplot(grid[0, 0])
    swath_axis = figure.add_subplot(grid[0, 1])
    error_axis = figure.add_subplot(grid[0, 2])

    true_c, true_z = _profile_step_coordinates(
        snapshot.true_profile, start_depth_m=float(snapshot.profile_start_depth_m)
    )
    proc_c, proc_z = _profile_step_coordinates(
        snapshot.processing_profile, start_depth_m=float(snapshot.profile_start_depth_m)
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
        ray_y, ray_z = _truth_ray_plot_coordinates(
            beam,
            sensor_y=sensor_y,
            sensor_z=sensor_z,
        )
        swath_axis.plot(ray_y, ray_z, linewidth=0.9, alpha=0.7)
        truth_y.append(float(beam.truth_bottom_point.y))
        truth_z.append(float(beam.truth_bottom_point.z))
        reconstructed_y.append(float(beam.reconstructed_bottom_point.y))
        reconstructed_z.append(float(beam.reconstructed_bottom_point.z))
        angles_deg.append(degrees(float(beam.configured_across_track_angle_rad)))
        vertical_errors.append(float(beam.vertical_error_m))
        across_errors.append(float(beam.across_track_error_m))

    swath_axis.scatter(truth_y, truth_z, marker="o", label="Truth intersections")
    swath_axis.scatter(
        reconstructed_y,
        reconstructed_z,
        marker="x",
        label="Reconstructed soundings",
    )
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

    figure.suptitle("HydroSIM Didactic Explorer — layered SVP sounding")
    return figure, (profile_axis, swath_axis, error_axis)

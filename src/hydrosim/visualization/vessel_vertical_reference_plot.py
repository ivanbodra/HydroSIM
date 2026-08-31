"""Didactic renderer for static vessel sensor and vertical-reference geometry."""

from __future__ import annotations

from typing import Any

from hydrosim.app.vessel_vertical_reference import VesselVerticalReferenceSnapshot


def draw_vessel_vertical_reference_snapshot(
    snapshot: VesselVerticalReferenceSnapshot,
    axes: tuple[Any, Any],
) -> None:
    """Draw vessel-frame geometry and hydrographic water level as separate views."""

    vessel_ax, datum_ax = axes
    vessel_ax.clear()
    datum_ax.clear()

    vrp = snapshot.vessel_vrp_pose.position
    sensors = (
        ("GNSS", snapshot.gnss_position, "^"),
        ("IMU", snapshot.imu_position, "s"),
        ("Transducer", snapshot.transducer_position, "v"),
    )

    xs = [float(vrp.x)] + [float(position.x) for _, position, _ in sensors]
    zs = [float(vrp.z)] + [float(position.z) for _, position, _ in sensors]
    max_abs_x = max(4.0, max(abs(value - float(vrp.x)) for value in xs) + 1.5)
    z_min = min(zs + [float(vrp.z) + snapshot.waterline_z_from_vrp_m]) - 1.2
    z_max = max(zs + [float(vrp.z) + snapshot.waterline_z_from_vrp_m]) + 1.2

    vessel_ax.axhspan(
        float(vrp.z) + snapshot.waterline_z_from_vrp_m,
        z_max,
        alpha=0.08,
        label="below configured waterline",
    )
    vessel_ax.axhline(
        float(vrp.z) + snapshot.waterline_z_from_vrp_m,
        linewidth=1.5,
        label="Configured waterline",
    )
    vessel_ax.scatter([vrp.x], [vrp.z], s=70, marker="o", zorder=4)
    vessel_ax.annotate("VRP", (vrp.x, vrp.z), xytext=(7, -12), textcoords="offset points")

    for label, position, marker in sensors:
        vessel_ax.plot(
            [vrp.x, position.x],
            [vrp.z, position.z],
            linewidth=1.1,
            alpha=0.65,
        )
        vessel_ax.scatter([position.x], [position.z], s=60, marker=marker, zorder=4)
        vessel_ax.annotate(
            label,
            (position.x, position.z),
            xytext=(7, 6),
            textcoords="offset points",
        )

    vessel_ax.set_xlim(float(vrp.x) - max_abs_x, float(vrp.x) + max_abs_x)
    vessel_ax.set_ylim(z_max, z_min)
    vessel_ax.set_aspect("equal", adjustable="box")
    vessel_ax.set_xlabel("Body X from VRP [m]")
    vessel_ax.set_ylabel("Body Z [m]  (positive down)")
    vessel_ax.set_title("Vessel/body frame")
    vessel_ax.grid(alpha=0.18)

    level = float(snapshot.water_level_m_relative_to_datum)
    span = max(1.0, abs(level) + 0.5)
    datum_ax.axhline(0.0, linewidth=1.2)
    datum_ax.axhline(level, linewidth=2.0)
    datum_ax.annotate(
        "Hydrographic datum",
        (0.5, 0.0),
        xytext=(0, -18),
        textcoords="offset points",
        ha="center",
    )
    datum_ax.annotate(
        f"Water level = {level:+.2f} m",
        (0.5, level),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center",
    )
    datum_ax.set_xlim(0.0, 1.0)
    datum_ax.set_ylim(-span, span)
    datum_ax.set_xticks([])
    datum_ax.set_ylabel("Level relative to datum [m]")
    datum_ax.set_title("Separate hydrographic reference")
    datum_ax.grid(axis="y", alpha=0.18)
    datum_ax.text(
        0.5,
        0.06,
        "No datum ↔ VRP relation inferred",
        transform=datum_ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
    )


def plot_vessel_vertical_reference_snapshot(
    snapshot: VesselVerticalReferenceSnapshot,
) -> tuple[Any, tuple[Any, Any]]:
    """Create the two-panel Vessel lesson figure."""

    import matplotlib.pyplot as plt

    figure, axes_array = plt.subplots(
        1,
        2,
        figsize=(11.2, 6.4),
        gridspec_kw={"width_ratios": (2.2, 1.0), "wspace": 0.28},
    )
    axes = (axes_array[0], axes_array[1])
    draw_vessel_vertical_reference_snapshot(snapshot, axes)
    figure.tight_layout()
    return figure, axes

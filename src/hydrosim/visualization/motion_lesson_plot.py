"""Presentation renderer for the deterministic Motion learning slice."""

from __future__ import annotations

from typing import Any

from hydrosim.app.motion_lesson import MotionLessonSnapshot


def _components(vector: Any) -> tuple[float, float, float]:
    return float(vector.x), float(vector.y), float(vector.z)


def draw_motion_lesson_snapshot(snapshot: MotionLessonSnapshot, ax: Any) -> None:
    """Draw vessel axes, transducer position, and beam direction from a prepared snapshot."""

    ax.clear()

    vrp = _components(snapshot.vrp_position_n_m)
    transducer = _components(snapshot.transducer_position_n_m)
    forward = _components(snapshot.body_forward_axis_n)
    starboard = _components(snapshot.body_starboard_axis_n)
    down = _components(snapshot.body_down_axis_n)
    beam = _components(snapshot.beam_direction_n)

    ax.scatter(*vrp, s=55, label="VRP")
    ax.scatter(*transducer, s=55, marker="v", label="Transducer")
    ax.plot(
        [vrp[0], transducer[0]],
        [vrp[1], transducer[1]],
        [vrp[2], transducer[2]],
        linewidth=1.5,
    )

    axis_scale = 1.5
    for vector, label in (
        (forward, "Body X / forward"),
        (starboard, "Body Y / starboard"),
        (down, "Body Z / down"),
    ):
        ax.quiver(
            vrp[0],
            vrp[1],
            vrp[2],
            vector[0],
            vector[1],
            vector[2],
            length=axis_scale,
            normalize=True,
            label=label,
        )

    ax.quiver(
        transducer[0],
        transducer[1],
        transducer[2],
        beam[0],
        beam[1],
        beam[2],
        length=2.2,
        normalize=True,
        linewidth=2.0,
        label="Beam direction",
    )

    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-3.0, 3.0)
    ax.set_zlim(3.0, -3.0)
    ax.set_xlabel("Navigation X [m]")
    ax.set_ylabel("Navigation Y [m]")
    ax.set_zlabel("Navigation Z [m] (positive down)")
    ax.set_title("Instantaneous vessel / transducer / beam consequence")
    ax.view_init(elev=24, azim=-55)
    ax.legend(loc="upper left", fontsize=8)
    ax.figure.tight_layout()


def plot_motion_lesson_snapshot(snapshot: MotionLessonSnapshot) -> tuple[Any, Any]:
    """Create a Matplotlib figure for a prepared Motion lesson snapshot."""

    from matplotlib.figure import Figure

    figure = Figure(figsize=(8.5, 6.0), constrained_layout=True)
    ax = figure.add_subplot(111, projection="3d")
    draw_motion_lesson_snapshot(snapshot, ax)
    return figure, ax

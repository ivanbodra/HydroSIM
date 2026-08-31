"""Capture the real HydroSIM Didactic Explorer Qt window to a PNG file.

This helper is intended for CI/headless documentation capture. It launches the
actual PySide6 application, optionally selects a lesson, grabs the real top-level
window, writes a PNG, and then exits the Qt event loop.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from hydrosim.app.didactic_explorer import launch_didactic_explorer


_LESSON_ROWS = {"Signal": 0, "Beam": 1, "Propagation": 2, "Vessel": 3, "Motion": 4}


def capture(output: Path, delay_ms: int = 1200, lesson: str | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])

    def save_and_quit() -> None:
        window = getattr(app, "hydrosim_didactic_explorer_window", None)
        if window is None:
            app.quit()
            raise RuntimeError("Didactic Explorer window was not created")

        if lesson is not None:
            navigation = getattr(window, "hydrosim_navigation", None)
            if navigation is None:
                app.quit()
                raise RuntimeError("Didactic Explorer navigation was not exposed")
            navigation.setCurrentRow(_LESSON_ROWS[lesson])
            app.processEvents()

        window.repaint()
        app.processEvents()
        pixmap = window.grab()
        if not pixmap.save(str(output), "PNG"):
            app.quit()
            raise RuntimeError(f"Could not save screenshot to {output}")
        app.quit()

    QTimer.singleShot(delay_ms, save_and_quit)
    launch_didactic_explorer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/didactic_explorer_actual.png"),
    )
    parser.add_argument("--delay-ms", type=int, default=1200)
    parser.add_argument("--lesson", choices=tuple(_LESSON_ROWS), default=None)
    args = parser.parse_args()
    capture(args.output, args.delay_ms, args.lesson)

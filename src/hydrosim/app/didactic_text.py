"""Localized presentation copy facade for the HydroSIM Didactic Explorer.

This module contains no scientific semantics. It only maps lesson-oriented names to
the canonical application localization layer.
"""

from __future__ import annotations

from hydrosim.app.localization import Localizer


def text(key: str, language: str = "en") -> str:
    """Return localized Didactic Explorer text for ``key``."""

    return Localizer(language).text(key)


SIGNAL_TEXT_KEYS = {
    "heading": "signal.title",
    "question": "signal.question_focus",
    "boundary": "signal.scientific_boundary",
    "try_it": "common.try_it",
    "instruction": "signal.instruction",
    "duration": "signal.pulse_duration",
    "bandwidth": "signal.lfm_bandwidth",
    "reset": "common.reset",
    "what_to_look_for": "common.what_to_look_for",
    "observation": "signal.observation",
    "not_shown": "signal.not_shown",
    "scientific_boundary_label": "common.scientific_boundary",
    "quantitative": "common.quantitative",
}

"""Localized presentation copy for the HydroSIM Didactic Explorer.

This module contains presentation-only strings. Canonical scientific identifiers,
configuration keys, and model names remain in English elsewhere in the project.
"""

from __future__ import annotations

from hydrosim.app.localization import translate


def text(key: str, language: str = "en") -> str:
    """Return localized Didactic Explorer text for ``key``."""

    return translate(key, language)


SIGNAL_TEXT_KEYS = {
    "heading": "signal.heading",
    "question": "signal.learning_question",
    "boundary": "signal.scientific_boundary",
    "try_it": "common.try_it",
    "instruction": "signal.instruction",
    "duration": "signal.pulse_duration",
    "bandwidth": "signal.lfm_bandwidth",
    "reset": "common.reset_lesson",
    "what_to_look_for": "common.what_to_look_for",
    "observation": "signal.observation",
    "not_shown": "signal.not_shown",
    "scientific_boundary_label": "common.scientific_boundary",
    "quantitative": "common.quantitative",
}

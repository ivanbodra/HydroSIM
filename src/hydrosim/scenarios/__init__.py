"""Pedagogical HydroSIM scenarios."""

from .pitch_calibration import (
    PitchCalibrationResult,
    PitchCalibrationScenarioConfig,
    PitchProfile,
    estimate_pitch_correction,
    pitch_profile_mismatch_rms,
    run_pitch_calibration_scenario,
)
from .roll_offset import (
    RollOffsetResult,
    RollOffsetScenarioConfig,
    RollOffsetSummary,
    load_roll_offset_scenario,
    run_roll_offset_scenario,
)

__all__ = [
    "PitchCalibrationResult",
    "PitchCalibrationScenarioConfig",
    "PitchProfile",
    "RollOffsetResult",
    "RollOffsetScenarioConfig",
    "RollOffsetSummary",
    "estimate_pitch_correction",
    "load_roll_offset_scenario",
    "pitch_profile_mismatch_rms",
    "run_pitch_calibration_scenario",
    "run_roll_offset_scenario",
]

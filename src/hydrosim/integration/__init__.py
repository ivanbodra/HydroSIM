"""Reference models for hydrographic sensor integration errors.

The modules in this package are scientific reference implementations. They are
kept separate from UI code and from future optimization/calibration routines so
that equations, conventions, and validation cases remain independently testable.
"""

from .risc_maingot import (
    AdjustedMotionState,
    apply_maingot_motion_errors,
    configured_lever_arm_from_maingot_error,
    hydrosim_lever_arm_error_from_maingot,
    hydrosim_sss_error_from_maingot,
    maingot_latency_adjusted,
    maingot_surface_sound_speed,
    maingot_surface_sound_speed_steering_angle,
)
from .uncertainty import (
    DerivedSemanticState,
    InputSemanticState,
    PropagatedUncertainty,
    TruthErrorVector,
    UncertainInputSet,
    VerificationResidual,
    compute_truth_error,
    compute_verification_residual,
    propagate_uncertainty,
)

__all__ = [
    "AdjustedMotionState",
    "DerivedSemanticState",
    "InputSemanticState",
    "PropagatedUncertainty",
    "TruthErrorVector",
    "UncertainInputSet",
    "VerificationResidual",
    "apply_maingot_motion_errors",
    "compute_truth_error",
    "compute_verification_residual",
    "configured_lever_arm_from_maingot_error",
    "hydrosim_lever_arm_error_from_maingot",
    "hydrosim_sss_error_from_maingot",
    "maingot_latency_adjusted",
    "maingot_surface_sound_speed",
    "maingot_surface_sound_speed_steering_angle",
    "propagate_uncertainty",
]

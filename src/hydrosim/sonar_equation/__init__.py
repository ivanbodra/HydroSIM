"""Didactic sonar-equation terms kept separate from acquisition physics."""

from .absorption import AinslieMcColmEnvironment, ainslie_mccolm_absorption_db_per_km
from .backscatter import (
    AreaBackscatterInput,
    AreaBackscatterResult,
    area_backscatter_term,
)
from .d3_adapter import D3SonarEquationInput, D3SonarEquationResult, evaluate_d3_sonar_equation

__all__ = [name for name in globals() if not name.startswith("_")]

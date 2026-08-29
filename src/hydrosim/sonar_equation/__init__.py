"""Didactic sonar-equation terms kept separate from acquisition physics."""

from .backscatter import (
    AreaBackscatterInput,
    AreaBackscatterResult,
    area_backscatter_term,
)

__all__ = [name for name in globals() if not name.startswith("_")]

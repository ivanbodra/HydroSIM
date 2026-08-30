"""Visualization helpers for HydroSIM.

Visualization remains downstream of the scientific model. Importing this package
does not require optional plotting dependencies; plotting libraries are imported
only inside renderer functions.
"""

from .layered_svp_explorer import (
    LayeredSvpExplorerBeam,
    LayeredSvpExplorerSnapshot,
    prepare_layered_svp_explorer_snapshot,
)
from .layered_svp_explorer_plot import plot_layered_svp_explorer_snapshot
from .mills_cross_pattern import (
    MillsCrossPatternPanels,
    plot_mills_cross_pattern_panels,
    prepare_mills_cross_pattern_panels,
)
from .signal_explorer import SignalExplorerSnapshot, prepare_signal_explorer_snapshot
from .signal_explorer_plot import plot_signal_explorer_comparison

__all__ = [
    "LayeredSvpExplorerBeam",
    "LayeredSvpExplorerSnapshot",
    "MillsCrossPatternPanels",
    "SignalExplorerSnapshot",
    "plot_layered_svp_explorer_snapshot",
    "plot_mills_cross_pattern_panels",
    "plot_signal_explorer_comparison",
    "prepare_layered_svp_explorer_snapshot",
    "prepare_mills_cross_pattern_panels",
    "prepare_signal_explorer_snapshot",
]

"""Visualization helpers for HydroSIM.

Visualization remains downstream of the scientific model. Importing this package
does not require optional plotting dependencies; plotting libraries are imported
only inside renderer functions.
"""

from .beam_explorer import (
    BeamExplorerControls,
    BeamExplorerSnapshot,
    prepare_beam_explorer_snapshot,
)
from .beam_explorer_plot import draw_beam_explorer_snapshot, plot_beam_explorer_snapshot
from .layered_svp_explorer import (
    LayeredSvpExplorerBeam,
    LayeredSvpExplorerSnapshot,
    prepare_layered_svp_explorer_snapshot,
)
from .layered_svp_explorer_plot import (
    draw_layered_svp_explorer_snapshot,
    plot_layered_svp_explorer_snapshot,
)
from .mills_cross_pattern import (
    MillsCrossPatternPanels,
    plot_mills_cross_pattern_panels,
    prepare_mills_cross_pattern_panels,
)
from .propagation_explorer import (
    PropagationExplorerControls,
    prepare_propagation_explorer_snapshot,
)
from .signal_explorer import (
    SignalExplorerDisplayTrace,
    SignalExplorerSnapshot,
    prepare_signal_explorer_display_trace,
    prepare_signal_explorer_snapshot,
)
from .signal_explorer_interactive import (
    SignalExplorerControls,
    launch_signal_explorer_interactive,
    prepare_signal_explorer_comparison,
)
from .signal_explorer_plot import (
    draw_signal_explorer_comparison,
    plot_signal_explorer_comparison,
)

__all__ = [
    "BeamExplorerControls",
    "BeamExplorerSnapshot",
    "LayeredSvpExplorerBeam",
    "LayeredSvpExplorerSnapshot",
    "MillsCrossPatternPanels",
    "PropagationExplorerControls",
    "SignalExplorerControls",
    "SignalExplorerDisplayTrace",
    "SignalExplorerSnapshot",
    "draw_beam_explorer_snapshot",
    "draw_layered_svp_explorer_snapshot",
    "draw_signal_explorer_comparison",
    "launch_signal_explorer_interactive",
    "plot_beam_explorer_snapshot",
    "plot_layered_svp_explorer_snapshot",
    "plot_mills_cross_pattern_panels",
    "plot_signal_explorer_comparison",
    "prepare_beam_explorer_snapshot",
    "prepare_layered_svp_explorer_snapshot",
    "prepare_mills_cross_pattern_panels",
    "prepare_propagation_explorer_snapshot",
    "prepare_signal_explorer_comparison",
    "prepare_signal_explorer_display_trace",
    "prepare_signal_explorer_snapshot",
]

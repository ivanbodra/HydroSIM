"""HydroSIM application layer.

The application layer coordinates navigation, controls, and visualization while
keeping scientific calculations in the Scientific Core and visualization
composition modules.
"""

from .didactic_explorer import launch_didactic_explorer

__all__ = ["launch_didactic_explorer"]

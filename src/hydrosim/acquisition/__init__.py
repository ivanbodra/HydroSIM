"""Dynamic acoustic acquisition infrastructure."""

from .generation import generate_acquisition_sequence
from .models import AcquisitionPing, AcquisitionSequence, PingSchedule
from .reception import (
    ArrayElementTruthArrival,
    ArrayTruthReception,
    simulate_truth_array_reception,
)
from .returns import (
    BeamTruthReturn,
    ConstantSoundSpeedPropagation,
    simulate_truth_beam_return,
)

__all__ = [
    "AcquisitionPing",
    "AcquisitionSequence",
    "ArrayElementTruthArrival",
    "ArrayTruthReception",
    "BeamTruthReturn",
    "ConstantSoundSpeedPropagation",
    "PingSchedule",
    "generate_acquisition_sequence",
    "simulate_truth_array_reception",
    "simulate_truth_beam_return",
]

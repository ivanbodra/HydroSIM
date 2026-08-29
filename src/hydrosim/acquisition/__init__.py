"""Dynamic acoustic acquisition infrastructure."""

from .array_factor import ArrayFactorElementContribution, ArrayFactorResponse, array_factor
from .beamforming import (
    ReceiveElementSteeringDelay,
    ReceiveSteeringEvaluation,
    ReceiveSteeringHypothesis,
    evaluate_receive_steering,
    ideal_receive_steering,
)
from .element_factor import RectangularElementFactor, rectangular_element_factor
from .element_signals import (
    CoherentReceiveSum,
    NarrowbandReceiveTone,
    ReceiveElementPhasor,
    coherent_receive_sum,
)
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
    "ArrayFactorElementContribution",
    "ArrayFactorResponse",
    "ArrayTruthReception",
    "BeamTruthReturn",
    "CoherentReceiveSum",
    "ConstantSoundSpeedPropagation",
    "NarrowbandReceiveTone",
    "PingSchedule",
    "ReceiveElementPhasor",
    "ReceiveElementSteeringDelay",
    "ReceiveSteeringEvaluation",
    "ReceiveSteeringHypothesis",
    "RectangularElementFactor",
    "array_factor",
    "coherent_receive_sum",
    "evaluate_receive_steering",
    "generate_acquisition_sequence",
    "ideal_receive_steering",
    "rectangular_element_factor",
    "simulate_truth_array_reception",
    "simulate_truth_beam_return",
]

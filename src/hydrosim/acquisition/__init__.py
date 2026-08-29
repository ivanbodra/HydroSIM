"""Dynamic acoustic acquisition infrastructure."""

from .angular_pattern_2d import (
    AngularPattern2DSample,
    AngularPattern2DScan,
    scan_mills_cross_two_way_pattern_2d,
    sensor_angular_direction,
)
from .array_factor import ArrayFactorElementContribution, ArrayFactorResponse, array_factor
from .beam_pattern import (
    AcrossTrackBeamPatternSample,
    AcrossTrackBeamPatternScan,
    OneWayBeamPatternResponse,
    across_track_direction,
    one_way_beam_pattern,
    scan_across_track_beam_pattern,
)
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
from .multibeam_fan import (
    MillsCrossMultibeamFan,
    MultibeamFanBeam,
    MultibeamFanMatrixSample,
    simulate_mills_cross_multibeam_fan,
)
from .receive_beam_bank import (
    ReceiveBeamBankResponse,
    ReceiveBeamResponse,
    evaluate_mills_cross_receive_beam_bank,
)
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
from .two_way_pattern import (
    TwoWayBeamPatternResponse,
    two_way_beam_pattern,
    two_way_beam_pattern_sensor_frame,
)

__all__ = [
    "AcquisitionPing",
    "AcquisitionSequence",
    "AcrossTrackBeamPatternSample",
    "AcrossTrackBeamPatternScan",
    "AngularPattern2DSample",
    "AngularPattern2DScan",
    "ArrayElementTruthArrival",
    "ArrayFactorElementContribution",
    "ArrayFactorResponse",
    "ArrayTruthReception",
    "BeamTruthReturn",
    "CoherentReceiveSum",
    "ConstantSoundSpeedPropagation",
    "MillsCrossMultibeamFan",
    "MultibeamFanBeam",
    "MultibeamFanMatrixSample",
    "NarrowbandReceiveTone",
    "OneWayBeamPatternResponse",
    "PingSchedule",
    "ReceiveBeamBankResponse",
    "ReceiveBeamResponse",
    "ReceiveElementPhasor",
    "ReceiveElementSteeringDelay",
    "ReceiveSteeringEvaluation",
    "ReceiveSteeringHypothesis",
    "RectangularElementFactor",
    "TwoWayBeamPatternResponse",
    "across_track_direction",
    "array_factor",
    "coherent_receive_sum",
    "evaluate_mills_cross_receive_beam_bank",
    "evaluate_receive_steering",
    "generate_acquisition_sequence",
    "ideal_receive_steering",
    "one_way_beam_pattern",
    "rectangular_element_factor",
    "scan_across_track_beam_pattern",
    "scan_mills_cross_two_way_pattern_2d",
    "sensor_angular_direction",
    "simulate_mills_cross_multibeam_fan",
    "simulate_truth_array_reception",
    "simulate_truth_beam_return",
    "two_way_beam_pattern",
    "two_way_beam_pattern_sensor_frame",
]

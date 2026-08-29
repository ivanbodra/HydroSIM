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
from .layered_propagation import (
    LayeredRayPath,
    LayeredRaySegment,
    LayeredSoundSpeedProfile,
    SoundSpeedLayer,
    trace_layered_ray_to_depth,
)
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
from .sector_signal_chain import (
    SectorSignalChainPing,
    SectorSignalChainResult,
    SectorWaveformAssignment,
    SectorWaveformPlan,
    simulate_sector_waveform_propagation_ping,
)
from .transmission_loss import (
    OneWayTransmissionLoss,
    PropagationLossModel,
    ReciprocalTransmissionLoss,
    one_way_transmission_loss,
    reciprocal_transmission_loss,
)
from .transmit_sectors import TransmitSector, TransmitSectorSet, make_uniform_transmit_sectors
from .two_way_pattern import (
    TwoWayBeamPatternResponse,
    two_way_beam_pattern,
    two_way_beam_pattern_sensor_frame,
)
from .waveform import (
    ContinuousWavePulse,
    LinearFMPulse,
    MatchedFilterSummary,
    matched_filter,
    sample_cw_baseband,
    sample_lfm_baseband,
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
    "ContinuousWavePulse",
    "LayeredRayPath",
    "LayeredRaySegment",
    "LayeredSoundSpeedProfile",
    "LinearFMPulse",
    "MatchedFilterSummary",
    "MillsCrossMultibeamFan",
    "MultibeamFanBeam",
    "MultibeamFanMatrixSample",
    "NarrowbandReceiveTone",
    "OneWayBeamPatternResponse",
    "OneWayTransmissionLoss",
    "PingSchedule",
    "PropagationLossModel",
    "ReceiveBeamBankResponse",
    "ReceiveBeamResponse",
    "ReceiveElementPhasor",
    "ReceiveElementSteeringDelay",
    "ReceiveSteeringEvaluation",
    "ReceiveSteeringHypothesis",
    "ReciprocalTransmissionLoss",
    "RectangularElementFactor",
    "SectorSignalChainPing",
    "SectorSignalChainResult",
    "SectorWaveformAssignment",
    "SectorWaveformPlan",
    "SoundSpeedLayer",
    "TransmitSector",
    "TransmitSectorSet",
    "TwoWayBeamPatternResponse",
    "across_track_direction",
    "array_factor",
    "coherent_receive_sum",
    "evaluate_mills_cross_receive_beam_bank",
    "evaluate_receive_steering",
    "generate_acquisition_sequence",
    "ideal_receive_steering",
    "make_uniform_transmit_sectors",
    "matched_filter",
    "one_way_beam_pattern",
    "one_way_transmission_loss",
    "reciprocal_transmission_loss",
    "rectangular_element_factor",
    "sample_cw_baseband",
    "sample_lfm_baseband",
    "scan_across_track_beam_pattern",
    "scan_mills_cross_two_way_pattern_2d",
    "sensor_angular_direction",
    "simulate_mills_cross_multibeam_fan",
    "simulate_sector_waveform_propagation_ping",
    "simulate_truth_array_reception",
    "simulate_truth_beam_return",
    "trace_layered_ray_to_depth",
    "two_way_beam_pattern",
    "two_way_beam_pattern_sensor_frame",
]

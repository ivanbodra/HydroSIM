"""Dynamic acoustic acquisition infrastructure."""

from .angular_pattern_2d import (
    AngularPattern2DSample,
    AngularPattern2DScan,
    scan_mills_cross_two_way_pattern_2d,
    sensor_angular_direction,
)
from .angular_scattering import (
    AngularMatchedFilterScatteringIntegration,
    AngularScatteringIntegration,
    AngularScatteringStrengthSample,
    AngularScatteringStrengthTable,
    angular_matched_filter_scattering_bottom_response,
    angular_scattering_bottom_response,
    integrate_angular_matched_filter_seafloor_backscatter,
    integrate_angular_seafloor_backscatter,
    scattering_strength_at_incidence,
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
from .bottom_interaction import (
    BottomInteractionResponse,
    PointTargetStrength,
    SeafloorAreaBackscatter,
    SeafloorAreaSemantics,
    evaluate_bottom_interaction,
    evaluate_point_target_strength,
    evaluate_seafloor_area_backscatter,
)
from .element_factor import RectangularElementFactor, rectangular_element_factor
from .element_signals import (
    CoherentReceiveSum,
    NarrowbandReceiveTone,
    ReceiveElementPhasor,
    coherent_receive_sum,
)
from .footprint import (
    FlatSeafloorFootprintModel,
    InsonifiedFootprint,
    estimate_flat_seafloor_footprint,
    seafloor_backscatter_from_footprint,
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
from .pattern_beamwidth import (
    MillsCrossFootprintBeamwidths,
    PatternDerivedFootprint,
    PrincipalPlaneBeamwidth,
    derive_mills_cross_footprint_beamwidths,
    derive_principal_plane_beamwidth,
    estimate_mills_cross_pattern_footprint,
)
from .pattern_footprint_2d import (
    MatchedFilterWeightedEquivalentArea,
    ProjectedPatternCell,
    ProjectedPatternIllumination,
    PulseGatedEquivalentArea,
    gate_projected_pattern_by_rectangular_pulse,
    project_angular_pattern_to_flat_seafloor,
    seafloor_backscatter_from_matched_filter_weighted_pattern,
    seafloor_backscatter_from_projected_pattern,
    seafloor_backscatter_from_pulse_gated_pattern,
    weight_projected_pattern_by_matched_filter,
)
from .refracted_pattern_footprint import (
    RefractedPatternIllumination,
    RefractedProjectedPatternCell,
    project_angular_pattern_through_layered_profile,
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
from .returns import BeamTruthReturn, ConstantSoundSpeedPropagation, simulate_truth_beam_return
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
from .two_way_pattern import TwoWayBeamPatternResponse, two_way_beam_pattern, two_way_beam_pattern_sensor_frame
from .waveform import (
    ContinuousWavePulse,
    LinearFMPulse,
    MatchedFilterSummary,
    WaveformAutocorrelation,
    matched_filter,
    sample_cw_baseband,
    sample_lfm_baseband,
    sample_waveform_baseband,
    waveform_autocorrelation,
)

__all__ = [name for name in globals() if not name.startswith("_")]

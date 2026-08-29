"""Integrated reference chain from TX sectors to matched-filtered RX beams.

This module connects HydroSIM capabilities while keeping their scientific
semantics explicit:

    TX sector -> waveform -> layered propagation -> propagation amplitude loss
              -> ideal point return -> receive-beam bank -> matched filter

The first integration remains a stationary reciprocal reference. Each sector is
traced along its steering direction to a requested depth in a horizontally
stratified ocean, and the return is assumed to follow the same path back to a
co-located receiver.

When a ``PropagationLossModel`` is supplied, the ideal point return is scaled by
spherical spreading plus an explicitly supplied absorption coefficient. Bottom
scattering, target strength, source level, noise, electronics and detection remain
separate capabilities. If no propagation-loss model is supplied, unit return
amplitude is retained for backward-compatible geometry/timing experiments.
"""

from __future__ import annotations

from math import acos
from typing import Sequence

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from hydrosim.geometry import MillsCrossConfiguration

from .layered_propagation import LayeredRayPath, LayeredSoundSpeedProfile, trace_layered_ray_to_depth
from .receive_beam_bank import evaluate_mills_cross_receive_beam_bank
from .transmission_loss import (
    PropagationLossModel,
    ReciprocalTransmissionLoss,
    reciprocal_transmission_loss,
)
from .transmit_sectors import TransmitSectorSet
from .waveform import (
    ContinuousWavePulse,
    LinearFMPulse,
    MatchedFilterSummary,
    matched_filter,
    sample_cw_baseband,
    sample_lfm_baseband,
)

WaveformPulse = ContinuousWavePulse | LinearFMPulse


class SectorWaveformAssignment(BaseModel):
    """Waveform assigned to one transmit-sector index."""

    model_config = ConfigDict(frozen=True)

    sector_index: int = Field(ge=0)
    pulse: WaveformPulse


class SectorSignalChainResult(BaseModel):
    """Integrated deterministic result for one transmit sector."""

    model_config = ConfigDict(frozen=True)

    sector_index: int = Field(ge=0)
    sector_name: str = Field(min_length=1)
    steering_along_track_angle_rad: FiniteFloat
    steering_across_track_angle_rad: FiniteFloat
    center_frequency_hz: FiniteFloat = Field(gt=0.0)
    tx_delay_seconds: FiniteFloat = Field(ge=0.0)
    propagation_path: LayeredRayPath
    one_way_travel_time_seconds: FiniteFloat = Field(ge=0.0)
    reciprocal_twtt_seconds: FiniteFloat = Field(ge=0.0)
    propagation_loss: ReciprocalTransmissionLoss | None = None
    ideal_point_return_amplitude: FiniteFloat = Field(gt=0.0)
    echo_arrival_offset_seconds: FiniteFloat = Field(ge=0.0)
    echo_delay_samples: int = Field(ge=0)
    strongest_receive_beam_index: int = Field(ge=0)
    strongest_receive_beam_power: FiniteFloat = Field(ge=0.0)
    matched_filter: MatchedFilterSummary
    timing_quantization_error_seconds: FiniteFloat


class SectorSignalChainPing(BaseModel):
    """Integrated reference results for all TX sectors in one ping."""

    model_config = ConfigDict(frozen=True)

    sector_set_name: str = Field(min_length=1)
    target_depth_m: FiniteFloat = Field(gt=0.0)
    transducer_depth_m: FiniteFloat = Field(ge=0.0)
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    receive_steering_across_track_angles_rad: tuple[FiniteFloat, ...]
    sectors: tuple[SectorSignalChainResult, ...]


class SectorWaveformPlan(BaseModel):
    """Complete one-to-one waveform assignment for a transmit-sector set."""

    model_config = ConfigDict(frozen=True)

    assignments: tuple[SectorWaveformAssignment, ...]

    @model_validator(mode="after")
    def _unique_sector_indices(self) -> "SectorWaveformPlan":
        indices = [assignment.sector_index for assignment in self.assignments]
        if len(indices) != len(set(indices)):
            raise ValueError("waveform assignments must use unique sector indices")
        return self

    def pulse_for_sector(self, sector_index: int) -> WaveformPulse:
        for assignment in self.assignments:
            if assignment.sector_index == sector_index:
                return assignment.pulse
        raise ValueError(f"no waveform assigned to sector {sector_index}")


def _sample_pulse(pulse: WaveformPulse, *, sample_rate_hz: float) -> np.ndarray:
    if isinstance(pulse, ContinuousWavePulse):
        return sample_cw_baseband(pulse, sample_rate_hz=sample_rate_hz)
    return sample_lfm_baseband(pulse, sample_rate_hz=sample_rate_hz)


def simulate_sector_waveform_propagation_ping(
    *,
    configuration: MillsCrossConfiguration,
    sector_set: TransmitSectorSet,
    waveform_plan: SectorWaveformPlan,
    profile: LayeredSoundSpeedProfile,
    target_depth_m: float,
    receive_steering_across_track_angles_rad: Sequence[float],
    sample_rate_hz: float,
    transducer_depth_m: float = 0.0,
    propagation_loss_model: PropagationLossModel | None = None,
) -> SectorSignalChainPing:
    """Run the integrated sector/waveform/refraction/RX/MF reference chain.

    The bottom interaction remains an ideal point return at the endpoint of each
    sector's refracted path. Reciprocity is assumed for the inbound path, hence
    TWTT = 2*T_one_way. If ``propagation_loss_model`` is present, the returned
    pressure-like analytic waveform is multiplied by the reciprocal propagation
    amplitude ratio from spherical spreading plus absorption.

    Sector delay is relative to the ping TX reference and is included in the
    synthesized echo arrival. Matched-filter timing is sample-quantized and the
    quantization error is exposed explicitly.
    """

    if sample_rate_hz <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if not receive_steering_across_track_angles_rad:
        raise ValueError("receive steering angle list must not be empty")

    sector_indices = {sector.sector_index for sector in sector_set.sectors}
    assignment_indices = {item.sector_index for item in waveform_plan.assignments}
    if assignment_indices != sector_indices:
        raise ValueError("waveform plan must assign exactly one pulse to every transmit sector")

    results: list[SectorSignalChainResult] = []
    for sector in sector_set.sectors:
        pulse = waveform_plan.pulse_for_sector(sector.sector_index)
        direction = sector.steering_direction_sensor_frame
        launch_angle = acos(max(-1.0, min(1.0, float(direction.z))))
        path = trace_layered_ray_to_depth(
            profile=profile,
            launch_angle_from_vertical_rad=launch_angle,
            target_depth_m=target_depth_m,
            start_depth_m=transducer_depth_m,
        )
        one_way_time = float(path.travel_time_seconds)
        twtt = 2.0 * one_way_time
        arrival_offset = float(sector.tx_delay_seconds) + twtt

        propagation_loss = None
        echo_amplitude = 1.0
        if propagation_loss_model is not None:
            propagation_loss = reciprocal_transmission_loss(
                one_way_path_length_m=float(path.path_length_m),
                model=propagation_loss_model,
            )
            echo_amplitude = float(propagation_loss.two_way_amplitude_ratio)

        reference = _sample_pulse(pulse, sample_rate_hz=sample_rate_hz)
        echo_delay_samples = int(round(arrival_offset * float(sample_rate_hz)))
        received = np.zeros(echo_delay_samples + reference.size + 1, dtype=np.complex128)
        received[echo_delay_samples : echo_delay_samples + reference.size] = (
            echo_amplitude * reference
        )
        _, mf_summary = matched_filter(
            received,
            reference,
            sample_rate_hz=sample_rate_hz,
        )

        bank = evaluate_mills_cross_receive_beam_bank(
            configuration=configuration,
            source_along_track_angle_rad=float(sector.steering_along_track_angle_rad),
            source_across_track_angle_rad=float(sector.steering_across_track_angle_rad),
            receive_steering_across_track_angles_rad=receive_steering_across_track_angles_rad,
            transmit_steering_along_track_angle_rad=float(sector.steering_along_track_angle_rad),
            transmit_steering_across_track_angle_rad=float(sector.steering_across_track_angle_rad),
            receive_steering_along_track_angle_rad=float(sector.steering_along_track_angle_rad),
            frequency_hz=float(pulse.center_frequency_hz),
            sound_speed_mps=float(profile.layer_at_depth(transducer_depth_m).sound_speed_mps),
        )

        measured_offset = float(mf_summary.peak_lag_seconds)
        results.append(
            SectorSignalChainResult(
                sector_index=sector.sector_index,
                sector_name=sector.name,
                steering_along_track_angle_rad=sector.steering_along_track_angle_rad,
                steering_across_track_angle_rad=sector.steering_across_track_angle_rad,
                center_frequency_hz=pulse.center_frequency_hz,
                tx_delay_seconds=sector.tx_delay_seconds,
                propagation_path=path,
                one_way_travel_time_seconds=one_way_time,
                reciprocal_twtt_seconds=twtt,
                propagation_loss=propagation_loss,
                ideal_point_return_amplitude=echo_amplitude,
                echo_arrival_offset_seconds=arrival_offset,
                echo_delay_samples=echo_delay_samples,
                strongest_receive_beam_index=bank.strongest_beam_index,
                strongest_receive_beam_power=bank.strongest_beam_power,
                matched_filter=mf_summary,
                timing_quantization_error_seconds=measured_offset - arrival_offset,
            )
        )

    return SectorSignalChainPing(
        sector_set_name=sector_set.name,
        target_depth_m=target_depth_m,
        transducer_depth_m=transducer_depth_m,
        sample_rate_hz=sample_rate_hz,
        receive_steering_across_track_angles_rad=tuple(
            float(angle) for angle in receive_steering_across_track_angles_rad
        ),
        sectors=tuple(results),
    )

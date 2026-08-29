"""Element-level narrowband receive phase model for HydroSIM.

This module is the first signal-domain layer downstream of Truth element arrivals.
It intentionally models only a monochromatic narrowband component with equal unit
amplitude at every receive element. Element directivity, sensitivity, bandwidth,
noise, waveform envelope, attenuation, scattering amplitude, and electronics are
separate future capabilities.

For a tone frequency f and an element timing offset dt relative to the array centre,
the received phase offset is

    phi = -2*pi*f*dt

under the convention s(t) = exp(i*2*pi*f*t): an earlier arrival has positive phase
at the centre reference epoch. A steering compensation delay tau contributes

    phi_steer = -2*pi*f*tau

because delaying a signal by tau rotates its phasor by -2*pi*f*tau.
"""

from __future__ import annotations

from cmath import exp
from math import pi

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .beamforming import ReceiveSteeringHypothesis
from .reception import ArrayTruthReception


class NarrowbandReceiveTone(BaseModel):
    """One monochromatic receive component used for idealized beamforming."""

    model_config = ConfigDict(frozen=True)

    frequency_hz: FiniteFloat = Field(gt=0.0)


class ReceiveElementPhasor(BaseModel):
    """Narrowband phase state for one physical receive-array element."""

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    truth_arrival_offset_seconds: FiniteFloat
    steering_compensation_delay_seconds: FiniteFloat
    truth_phase_rad: FiniteFloat
    steering_phase_rad: FiniteFloat
    residual_phase_rad: FiniteFloat
    real: FiniteFloat
    imag: FiniteFloat


class CoherentReceiveSum(BaseModel):
    """Equal-weight coherent sum across receive elements."""

    model_config = ConfigDict(frozen=True)

    beam_index: int = Field(ge=0)
    array_name: str = Field(min_length=1)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    element_phasors: tuple[ReceiveElementPhasor, ...]
    coherent_real: FiniteFloat
    coherent_imag: FiniteFloat
    coherent_magnitude: FiniteFloat = Field(ge=0.0)
    normalized_magnitude: FiniteFloat = Field(ge=0.0, le=1.000000000001)
    coherent_power_normalized: FiniteFloat = Field(ge=0.0, le=1.000000000002)


def coherent_receive_sum(
    *,
    reception: ArrayTruthReception,
    steering: ReceiveSteeringHypothesis,
    tone: NarrowbandReceiveTone,
) -> CoherentReceiveSum:
    """Apply ideal steering delays to Truth element arrivals and sum phasors.

    Each element is assigned unit amplitude. The result therefore isolates phase
    coherence caused by geometry, frequency, and steering. Perfect timing alignment
    yields normalized magnitude 1.0. This is not yet a physical received-level or
    sonar-equation calculation.
    """

    if reception.array_name != steering.array_name:
        raise ValueError("reception and steering must reference the same array")
    if len(reception.element_arrivals) != len(steering.element_delays):
        raise ValueError("reception and steering element counts differ")

    frequency = float(tone.frequency_hz)
    phasors: list[ReceiveElementPhasor] = []
    total = 0j

    for arrival, delay in zip(
        reception.element_arrivals, steering.element_delays, strict=True
    ):
        if (arrival.index_x, arrival.index_y) != (delay.index_x, delay.index_y):
            raise ValueError("reception and steering element ordering differs")

        dt_truth = float(arrival.relative_to_array_center_seconds)
        tau = float(delay.compensation_delay_seconds)
        truth_phase = -2.0 * pi * frequency * dt_truth
        steering_phase = -2.0 * pi * frequency * tau
        residual_phase = truth_phase + steering_phase
        value = exp(1j * residual_phase)
        total += value

        phasors.append(
            ReceiveElementPhasor(
                index_x=arrival.index_x,
                index_y=arrival.index_y,
                truth_arrival_offset_seconds=dt_truth,
                steering_compensation_delay_seconds=tau,
                truth_phase_rad=truth_phase,
                steering_phase_rad=steering_phase,
                residual_phase_rad=residual_phase,
                real=value.real,
                imag=value.imag,
            )
        )

    count = len(phasors)
    magnitude = abs(total)
    normalized = magnitude / count if count else 0.0

    return CoherentReceiveSum(
        beam_index=reception.beam_index,
        array_name=reception.array_name,
        frequency_hz=frequency,
        element_phasors=tuple(phasors),
        coherent_real=total.real,
        coherent_imag=total.imag,
        coherent_magnitude=magnitude,
        normalized_magnitude=normalized,
        coherent_power_normalized=normalized * normalized,
    )

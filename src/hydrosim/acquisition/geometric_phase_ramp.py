"""Discretization-aware geometric split-aperture phase-ramp demonstration.

This module deliberately does not synthesize physical seafloor backscatter.  It
uses the already sampled TX×RX footprint only as a non-negative geometric/time
weight over arrival directions and computes the circular mean of the ideal
split-aperture differential phase expected from those directions.

For one direction ``u`` and receive steering direction ``u_s``, with the baseline
``b = r_positive - r_negative`` between geometric subaperture centroids, HydroSIM's
array-factor sign convention gives

    dphi = -k (u - u_s) . b,

where ``k = 2*pi*f/c``.  The minus sign follows directly from
``arg(z_negative * conj(z_positive))``.

At one temporal sample ``t`` the continuous directional/area average is realized
numerically as a circular weighted sum over footprint cells,

    C(t) ~= sum_i w_i(t) exp(j dphi_i),
    dphi_bar(t) = arg(C(t)),

with

    w_i(t) = (P_i/P_peak) W_t(2(T_i - T_ref)) dA_i.

This is a reference geometry/processing demonstration, not received acoustic
pressure, echo level, bottom reflectivity, or a vendor bottom-detection algorithm.
Spatial and temporal resolution are returned explicitly so convergence can be
assessed before interpreting the phase ramp.
"""

from __future__ import annotations

from cmath import exp, phase
from math import pi, sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import TransducerArray, Vector3

from .angular_pattern_2d import sensor_angular_direction
from .footprint_contribution import _autocorrelation_power_at_lag
from .numerical_resolution import ResolutionAxis
from .refracted_pattern_footprint import RefractedPatternIllumination
from .split_aperture import SplitApertureDefinition, split_aperture_phase_centers
from .waveform import WaveformPulse, waveform_autocorrelation


class GeometricPhaseRampSample(BaseModel):
    """One temporal sample of the weighted geometric differential phase."""

    model_config = ConfigDict(frozen=True)

    sample_index: int = Field(ge=0)
    reference_one_way_travel_time_seconds: FiniteFloat = Field(gt=0.0)
    differential_phase_rad: FiniteFloat
    circular_resultant_magnitude: FiniteFloat = Field(ge=0.0, le=1.000000000001)
    equivalent_weighted_area_m2: FiniteFloat = Field(ge=0.0)
    contributing_cell_count: int = Field(ge=0)


class GeometricPhaseRamp(BaseModel):
    """Time series plus explicit spatial/temporal numerical resolution metadata."""

    model_config = ConfigDict(frozen=True)

    array_name: str = Field(min_length=1)
    frequency_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    steering_along_track_angle_rad: FiniteFloat
    steering_across_track_angle_rad: FiniteFloat
    along_track_resolution: ResolutionAxis
    across_track_resolution: ResolutionAxis
    temporal_resolution: ResolutionAxis
    samples: tuple[GeometricPhaseRampSample, ...]


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def ideal_split_aperture_differential_phase(
    *,
    receive_array: TransducerArray,
    definition: SplitApertureDefinition,
    source_direction_sensor_frame: Vector3,
    steering_direction_sensor_frame: Vector3,
    frequency_hz: float,
    sound_speed_mps: float,
) -> float:
    """Return ideal centroid-baseline differential phase for one direction."""

    frequency = float(frequency_hz)
    c = float(sound_speed_mps)
    if frequency <= 0.0 or c <= 0.0:
        raise ValueError("frequency_hz and sound_speed_mps must be positive")
    centers = split_aperture_phase_centers(receive_array=receive_array, definition=definition)
    source = receive_array.direction_from_sensor_frame(source_direction_sensor_frame)
    steering = receive_array.direction_from_sensor_frame(steering_direction_sensor_frame)
    delta = Vector3(
        x=float(source.x) - float(steering.x),
        y=float(source.y) - float(steering.y),
        z=float(source.z) - float(steering.z),
    )
    k = 2.0 * pi * frequency / c
    return -k * _dot(delta, centers.negative_to_positive_baseline_array_frame)


def build_geometric_phase_ramp(
    *,
    illumination: RefractedPatternIllumination,
    receive_array: TransducerArray,
    definition: SplitApertureDefinition,
    pulse: WaveformPulse,
    frequency_hz: float,
    sound_speed_mps: float,
    steering_along_track_angle_rad: float,
    steering_across_track_angle_rad: float,
    start_reference_one_way_travel_time_seconds: float,
    sample_count: int,
    sample_rate_hz: float,
) -> GeometricPhaseRamp:
    """Build a sampled geometric phase ramp from a refracted footprint.

    The temporal grid samples *one-way reference time*.  Because matched-filter
    weighting is evaluated in two-way lag, adjacent reference samples are spaced
    by ``1/(2*sample_rate_hz)`` so the implied TWTT grid spacing is ``1/fs``.
    """

    fs = float(sample_rate_hz)
    if fs <= 0.0:
        raise ValueError("sample_rate_hz must be positive")
    if sample_count < 2:
        raise ValueError("sample_count must be at least two")
    start = float(start_reference_one_way_travel_time_seconds)
    if start <= 0.0:
        raise ValueError("start reference travel time must be positive")

    along_values = sorted({float(cell.along_track_angle_rad) for cell in illumination.cells})
    across_values = sorted({float(cell.across_track_angle_rad) for cell in illumination.cells})
    if len(along_values) < 2 or len(across_values) < 2:
        raise ValueError("phase-ramp footprint requires at least two angular samples per axis")
    da = min(b - a for a, b in zip(along_values, along_values[1:], strict=True))
    dc = min(b - a for a, b in zip(across_values, across_values[1:], strict=True))

    autocorrelation = waveform_autocorrelation(pulse, sample_rate_hz=fs)
    steering = sensor_angular_direction(
        steering_along_track_angle_rad,
        steering_across_track_angle_rad,
    )

    cell_phases: list[float] = []
    for cell in illumination.cells:
        direction = sensor_angular_direction(
            float(cell.along_track_angle_rad),
            float(cell.across_track_angle_rad),
        )
        cell_phases.append(
            ideal_split_aperture_differential_phase(
                receive_array=receive_array,
                definition=definition,
                source_direction_sensor_frame=direction,
                steering_direction_sensor_frame=steering,
                frequency_hz=frequency_hz,
                sound_speed_mps=sound_speed_mps,
            )
        )

    dt_one_way = 0.5 / fs
    samples: list[GeometricPhaseRampSample] = []
    for sample_index in range(sample_count):
        reference_time = start + sample_index * dt_one_way
        circular_sum = 0j
        total_weight = 0.0
        contributing = 0
        for cell, cell_phase in zip(illumination.cells, cell_phases, strict=True):
            temporal = _autocorrelation_power_at_lag(
                autocorrelation,
                2.0 * (float(cell.one_way_travel_time_seconds) - reference_time),
            )
            weight = (
                float(cell.relative_power_to_peak)
                * temporal
                * float(cell.projected_area_m2)
            )
            if weight <= 0.0:
                continue
            contributing += 1
            total_weight += weight
            circular_sum += weight * exp(1j * cell_phase)

        if total_weight > 0.0:
            mean_phase = phase(circular_sum)
            resultant = abs(circular_sum) / total_weight
            if 1.0 < resultant < 1.0 + 1e-12:
                resultant = 1.0
        else:
            mean_phase = 0.0
            resultant = 0.0

        samples.append(
            GeometricPhaseRampSample(
                sample_index=sample_index,
                reference_one_way_travel_time_seconds=reference_time,
                differential_phase_rad=mean_phase,
                circular_resultant_magnitude=resultant,
                equivalent_weighted_area_m2=total_weight,
                contributing_cell_count=contributing,
            )
        )

    return GeometricPhaseRamp(
        array_name=receive_array.name,
        frequency_hz=frequency_hz,
        sound_speed_mps=sound_speed_mps,
        steering_along_track_angle_rad=steering_along_track_angle_rad,
        steering_across_track_angle_rad=steering_across_track_angle_rad,
        along_track_resolution=ResolutionAxis(
            name="along_track_angle",
            unit="rad",
            semantics="continuous_sampled",
            sample_count=len(along_values),
            nominal_spacing=da,
        ),
        across_track_resolution=ResolutionAxis(
            name="across_track_angle",
            unit="rad",
            semantics="continuous_sampled",
            sample_count=len(across_values),
            nominal_spacing=dc,
        ),
        temporal_resolution=ResolutionAxis(
            name="twtt",
            unit="s",
            semantics="continuous_sampled",
            sample_count=sample_count,
            nominal_spacing=1.0 / fs,
        ),
        samples=tuple(samples),
    )

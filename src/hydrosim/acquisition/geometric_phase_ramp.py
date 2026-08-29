"""Discretization-aware geometric split-aperture phase-ramp demonstration.

This module deliberately does not synthesize physical seafloor backscatter. It
uses the already sampled TX×RX footprint only as a non-negative geometric/time
weight over arrival directions and computes the circular mean of the ideal
split-aperture differential phase expected from those directions.

For one direction ``u`` and receive steering direction ``u_s``, with the baseline
``b = r_positive - r_negative`` between geometric subaperture centroids, HydroSIM's
array-factor sign convention gives

    dphi = -k (u - u_s) . b,

where ``k = 2*pi*f/c``. The minus sign follows directly from
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
from math import atan2, cos, pi, sin

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


class PhaseRampConvergenceDiagnostic(BaseModel):
    """Difference between coarse and refined phase-ramp realizations.

    Phase is circular, so sample differences are wrapped to ``[-pi, pi]`` before
    the maximum and RMS metrics are calculated. Samples for which either
    realization has zero weighted area are excluded because phase is undefined
    there in the physical interpretation.
    """

    model_config = ConfigDict(frozen=True)

    compared_sample_count: int = Field(ge=1)
    max_absolute_circular_phase_change_rad: FiniteFloat = Field(ge=0.0)
    rms_circular_phase_change_rad: FiniteFloat = Field(ge=0.0)
    max_absolute_resultant_change: FiniteFloat = Field(ge=0.0)
    phase_tolerance_rad: FiniteFloat = Field(ge=0.0)
    resultant_tolerance: FiniteFloat = Field(ge=0.0)
    converged: bool


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def _circular_difference(a: float, b: float) -> float:
    """Return the signed shortest angular difference ``a-b`` in radians."""

    return atan2(sin(float(a) - float(b)), cos(float(a) - float(b)))


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

    The temporal grid samples *one-way reference time*. Because matched-filter
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
    da = min(b - a for a, b in zip(along_values, along_values[1:], strict=False))
    dc = min(b - a for a, b in zip(across_values, across_values[1:], strict=False))

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


def compare_geometric_phase_ramp_refinement(
    *,
    coarse: GeometricPhaseRamp,
    fine: GeometricPhaseRamp,
    phase_tolerance_rad: float,
    resultant_tolerance: float,
) -> PhaseRampConvergenceDiagnostic:
    """Compare phase ramps only at common physical epochs under refinement.

    The refined realization may improve spatial resolution, temporal resolution,
    or both, but it must not be coarser on any of the three recorded axes. Common
    epochs are matched by one-way reference travel time rather than by sample
    index. This avoids comparing different physical times when temporal sampling
    changes.
    """

    phase_tol = float(phase_tolerance_rad)
    resultant_tol = float(resultant_tolerance)
    if phase_tol < 0.0 or resultant_tol < 0.0:
        raise ValueError("convergence tolerances must be non-negative")

    scalar_pairs = (
        (coarse.frequency_hz, fine.frequency_hz, "frequency_hz"),
        (coarse.sound_speed_mps, fine.sound_speed_mps, "sound_speed_mps"),
        (coarse.steering_along_track_angle_rad, fine.steering_along_track_angle_rad, "along-track steering"),
        (coarse.steering_across_track_angle_rad, fine.steering_across_track_angle_rad, "across-track steering"),
    )
    if coarse.array_name != fine.array_name:
        raise ValueError("phase-ramp refinements must use the same receive array")
    for coarse_value, fine_value, name in scalar_pairs:
        if abs(float(coarse_value) - float(fine_value)) > 1e-12:
            raise ValueError(f"phase-ramp refinements must use the same {name}")

    coarse_axes = (
        coarse.along_track_resolution,
        coarse.across_track_resolution,
        coarse.temporal_resolution,
    )
    fine_axes = (
        fine.along_track_resolution,
        fine.across_track_resolution,
        fine.temporal_resolution,
    )
    refined_any = False
    for coarse_axis, fine_axis in zip(coarse_axes, fine_axes, strict=True):
        if float(fine_axis.nominal_spacing) > float(coarse_axis.nominal_spacing) + 1e-15:
            raise ValueError("fine phase ramp must not be coarser on any resolution axis")
        if float(fine_axis.nominal_spacing) < float(coarse_axis.nominal_spacing) - 1e-15:
            refined_any = True
    if not refined_any:
        raise ValueError("fine phase ramp must refine at least one resolution axis")

    fine_by_time = {
        round(float(sample.reference_one_way_travel_time_seconds), 12): sample
        for sample in fine.samples
    }
    phase_changes: list[float] = []
    resultant_changes: list[float] = []
    for coarse_sample in coarse.samples:
        key = round(float(coarse_sample.reference_one_way_travel_time_seconds), 12)
        fine_sample = fine_by_time.get(key)
        if fine_sample is None:
            continue
        if (
            float(coarse_sample.equivalent_weighted_area_m2) <= 0.0
            or float(fine_sample.equivalent_weighted_area_m2) <= 0.0
        ):
            continue
        phase_changes.append(
            abs(
                _circular_difference(
                    float(fine_sample.differential_phase_rad),
                    float(coarse_sample.differential_phase_rad),
                )
            )
        )
        resultant_changes.append(
            abs(
                float(fine_sample.circular_resultant_magnitude)
                - float(coarse_sample.circular_resultant_magnitude)
            )
        )

    if not phase_changes:
        raise ValueError("phase-ramp refinements have no common weighted temporal samples")

    max_phase = max(phase_changes)
    rms_phase = (sum(value * value for value in phase_changes) / len(phase_changes)) ** 0.5
    max_resultant = max(resultant_changes)
    return PhaseRampConvergenceDiagnostic(
        compared_sample_count=len(phase_changes),
        max_absolute_circular_phase_change_rad=max_phase,
        rms_circular_phase_change_rad=rms_phase,
        max_absolute_resultant_change=max_resultant,
        phase_tolerance_rad=phase_tol,
        resultant_tolerance=resultant_tol,
        converged=max_phase <= phase_tol and max_resultant <= resultant_tol,
    )

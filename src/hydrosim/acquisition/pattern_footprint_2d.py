"""Project a sampled 2D Mills-Cross pattern onto a flat seafloor.

A -3 dB contour is a beam descriptor, not a physical boundary of insonification.
HydroSIM therefore retains the full sampled TX×RX power distribution and derives
power-equivalent scattering areas from explicit spatial and temporal weighting.

Spatial weighting:

    A_eq = integral (P / P_peak) dA

Temporal weighting may be either a simple rectangular-pulse range shell or the
normalized matched-filter power response |R_ss(dt)|^2 / |R_ss(0)|^2. The latter
keeps CW and LFM pulse compression distinct and is the preferred deterministic
reference for an incoherent area-scattering power model.

For a horizontal seafloor the local incidence angle is retained independently for
every projected cell. With vertical separation h and slant range R,

    theta_i = acos(h / R_i),

measured from the local seafloor normal. This prepares the spatial integration for
explicit user-supplied S_b(theta) models without hiding an empirical angular law
inside the footprint calculation.
"""

from __future__ import annotations

from bisect import bisect_left
from math import acos, sqrt, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_pattern_2d import AngularPattern2DScan
from .bottom_interaction import SeafloorAreaBackscatter
from .waveform import WaveformAutocorrelation, WaveformPulse, waveform_autocorrelation


class ProjectedPatternCell(BaseModel):
    """One angular grid cell projected onto a horizontal seafloor plane."""

    model_config = ConfigDict(frozen=True)

    along_track_index: int = Field(ge=0)
    across_track_index: int = Field(ge=0)
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    normalized_power: FiniteFloat = Field(ge=0.0)
    relative_power_to_peak: FiniteFloat = Field(ge=0.0)
    forward_center_m: FiniteFloat
    port_center_m: FiniteFloat
    slant_range_m: FiniteFloat = Field(gt=0.0)
    incidence_angle_from_normal_rad: FiniteFloat = Field(ge=0.0)
    projected_area_m2: FiniteFloat = Field(gt=0.0)
    equivalent_area_contribution_m2: FiniteFloat = Field(ge=0.0)
    inside_half_power_contour: bool


class ProjectedPatternIllumination(BaseModel):
    """Full sampled pattern projection plus descriptive and equivalent areas."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    vertical_separation_m: FiniteFloat = Field(gt=0.0)
    peak_power: FiniteFloat = Field(gt=0.0)
    sampled_grid_area_m2: FiniteFloat = Field(gt=0.0)
    equivalent_insonified_area_m2: FiniteFloat = Field(gt=0.0)
    half_power_area_m2: FiniteFloat = Field(ge=0.0)
    half_power_cell_count: int = Field(ge=0)
    total_cell_count: int = Field(gt=0)
    half_power_forward_min_m: FiniteFloat | None = None
    half_power_forward_max_m: FiniteFloat | None = None
    half_power_port_min_m: FiniteFloat | None = None
    half_power_port_max_m: FiniteFloat | None = None
    cells: tuple[ProjectedPatternCell, ...]


class PulseGatedEquivalentArea(BaseModel):
    """Pattern-weighted area within a rectangular-pulse one-way range shell."""

    model_config = ConfigDict(frozen=True)

    center_one_way_range_m: FiniteFloat = Field(gt=0.0)
    pulse_duration_seconds: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    range_shell_width_m: FiniteFloat = Field(gt=0.0)
    minimum_one_way_range_m: FiniteFloat = Field(gt=0.0)
    maximum_one_way_range_m: FiniteFloat = Field(gt=0.0)
    contributing_cell_count: int = Field(ge=0)
    equivalent_insonified_area_m2: FiniteFloat = Field(ge=0.0)


class MatchedFilterWeightedEquivalentArea(BaseModel):
    """Pattern-times-matched-filter power-equivalent scattering area."""

    model_config = ConfigDict(frozen=True)

    center_one_way_range_m: FiniteFloat = Field(gt=0.0)
    sample_rate_hz: FiniteFloat = Field(gt=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    contributing_cell_count: int = Field(ge=0)
    equivalent_insonified_area_m2: FiniteFloat = Field(ge=0.0)
    autocorrelation: WaveformAutocorrelation


def _cell_edges(values: tuple[FiniteFloat, ...]) -> tuple[float, ...]:
    coordinates = tuple(float(value) for value in values)
    if len(coordinates) < 2:
        raise ValueError("pattern axis requires at least two samples")
    edges = [coordinates[0] - 0.5 * (coordinates[1] - coordinates[0])]
    for left, right in zip(coordinates, coordinates[1:], strict=False):
        edges.append(0.5 * (left + right))
    edges.append(coordinates[-1] + 0.5 * (coordinates[-1] - coordinates[-2]))
    return tuple(edges)


def project_angular_pattern_to_flat_seafloor(
    *, scan: AngularPattern2DScan, vertical_separation_m: float
) -> ProjectedPatternIllumination:
    """Project the full sampled 2D TX×RX power distribution onto a flat bottom."""

    h = float(vertical_separation_m)
    if h <= 0.0:
        raise ValueError("vertical_separation_m must be positive")
    along_count = len(scan.along_track_angles_rad)
    across_count = len(scan.across_track_angles_rad)
    if len(scan.samples) != along_count * across_count:
        raise ValueError("AngularPattern2DScan sample layout is inconsistent with its axes")
    peak_power = float(scan.peak_power)
    if peak_power <= 0.0:
        raise ValueError("AngularPattern2DScan peak_power must be positive")

    along_edges = _cell_edges(scan.along_track_angles_rad)
    across_edges = _cell_edges(scan.across_track_angles_rad)
    cells: list[ProjectedPatternCell] = []
    grid_area = equivalent_area = half_power_area = 0.0
    half_power_forward: list[float] = []
    half_power_port: list[float] = []

    for ai, along in enumerate(scan.along_track_angles_rad):
        x0, x1 = h * tan(along_edges[ai]), h * tan(along_edges[ai + 1])
        dx = abs(x1 - x0)
        for ci, across in enumerate(scan.across_track_angles_rad):
            y0, y1 = h * tan(across_edges[ci]), h * tan(across_edges[ci + 1])
            area = dx * abs(y1 - y0)
            sample = scan.samples[ai * across_count + ci]
            power = float(sample.normalized_power)
            relative = power / peak_power
            contribution = relative * area
            inside = relative >= 0.5
            forward = h * tan(float(along))
            port = h * tan(float(across))
            slant = sqrt(h * h + forward**2 + port**2)
            incidence = acos(h / slant)
            grid_area += area
            equivalent_area += contribution
            if inside:
                half_power_area += area
                half_power_forward.extend((min(x0, x1), max(x0, x1)))
                half_power_port.extend((min(y0, y1), max(y0, y1)))
            cells.append(ProjectedPatternCell(
                along_track_index=ai, across_track_index=ci,
                along_track_angle_rad=along, across_track_angle_rad=across,
                normalized_power=power, relative_power_to_peak=relative,
                forward_center_m=forward, port_center_m=port, slant_range_m=slant,
                incidence_angle_from_normal_rad=incidence,
                projected_area_m2=area, equivalent_area_contribution_m2=contribution,
                inside_half_power_contour=inside,
            ))

    return ProjectedPatternIllumination(
        configuration_name=scan.configuration_name, vertical_separation_m=h,
        peak_power=peak_power, sampled_grid_area_m2=grid_area,
        equivalent_insonified_area_m2=equivalent_area,
        half_power_area_m2=half_power_area,
        half_power_cell_count=sum(c.inside_half_power_contour for c in cells),
        total_cell_count=len(cells),
        half_power_forward_min_m=min(half_power_forward) if half_power_forward else None,
        half_power_forward_max_m=max(half_power_forward) if half_power_forward else None,
        half_power_port_min_m=min(half_power_port) if half_power_port else None,
        half_power_port_max_m=max(half_power_port) if half_power_port else None,
        cells=tuple(cells),
    )


def gate_projected_pattern_by_rectangular_pulse(
    *, illumination: ProjectedPatternIllumination, center_one_way_range_m: float,
    pulse_duration_seconds: float, sound_speed_mps: float,
) -> PulseGatedEquivalentArea:
    """Apply a simple rectangular-pulse one-way range shell."""

    center, tau, c = float(center_one_way_range_m), float(pulse_duration_seconds), float(sound_speed_mps)
    if center <= 0.0 or tau <= 0.0 or c <= 0.0:
        raise ValueError("range, pulse duration and sound speed must be positive")
    width = c * tau / 2.0
    minimum, maximum = center - width / 2.0, center + width / 2.0
    if minimum <= 0.0:
        raise ValueError("pulse range shell must remain at positive one-way range")
    contributing = [c0 for c0 in illumination.cells if minimum <= float(c0.slant_range_m) <= maximum]
    return PulseGatedEquivalentArea(
        center_one_way_range_m=center, pulse_duration_seconds=tau, sound_speed_mps=c,
        range_shell_width_m=width, minimum_one_way_range_m=minimum,
        maximum_one_way_range_m=maximum, contributing_cell_count=len(contributing),
        equivalent_insonified_area_m2=sum(float(c0.equivalent_area_contribution_m2) for c0 in contributing),
    )


def _interpolate_autocorrelation_power(ac: WaveformAutocorrelation, lag_seconds: float) -> float:
    lags = tuple(float(v) for v in ac.lag_seconds)
    powers = tuple(float(v) for v in ac.normalized_power)
    lag = float(lag_seconds)
    if lag < lags[0] or lag > lags[-1]:
        return 0.0
    index = bisect_left(lags, lag)
    if index == 0:
        return powers[0]
    if index == len(lags):
        return powers[-1]
    l0, l1 = lags[index - 1], lags[index]
    p0, p1 = powers[index - 1], powers[index]
    if l1 == l0:
        return p0
    return p0 + (lag - l0) * (p1 - p0) / (l1 - l0)


def weight_projected_pattern_by_matched_filter(
    *, illumination: ProjectedPatternIllumination, pulse: WaveformPulse,
    center_one_way_range_m: float, sample_rate_hz: float, sound_speed_mps: float,
) -> MatchedFilterWeightedEquivalentArea:
    """Weight every projected cell by the matched-filter power response.

    A cell at one-way range R differs from the reference range R0 by a two-way
    delay ``dt = 2 (R - R0) / c``. For the current incoherent area-scattering
    power abstraction its contribution is weighted by normalized
    ``|R_ss(dt)|^2``. Cells outside the finite autocorrelation support contribute
    zero. This is not a coherent rough-surface scattering simulation.
    """

    center, fs, c = float(center_one_way_range_m), float(sample_rate_hz), float(sound_speed_mps)
    if center <= 0.0 or fs <= 0.0 or c <= 0.0:
        raise ValueError("range, sample rate and sound speed must be positive")
    ac = waveform_autocorrelation(pulse, sample_rate_hz=fs)
    area = 0.0
    count = 0
    for cell in illumination.cells:
        delay = 2.0 * (float(cell.slant_range_m) - center) / c
        temporal_power = _interpolate_autocorrelation_power(ac, delay)
        if temporal_power > 0.0:
            count += 1
            area += float(cell.equivalent_area_contribution_m2) * temporal_power
    return MatchedFilterWeightedEquivalentArea(
        center_one_way_range_m=center, sample_rate_hz=fs, sound_speed_mps=c,
        contributing_cell_count=count, equivalent_insonified_area_m2=area,
        autocorrelation=ac,
    )


def seafloor_backscatter_from_projected_pattern(*, scattering_strength_db_per_m2: float,
    illumination: ProjectedPatternIllumination, incidence_angle_from_normal_rad: float) -> SeafloorAreaBackscatter:
    area = float(illumination.equivalent_insonified_area_m2)
    if area <= 0.0:
        raise ValueError("projected pattern has zero equivalent insonified area")
    return SeafloorAreaBackscatter(scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=area, incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
        area_semantics="equivalent_pattern_weighted")


def seafloor_backscatter_from_pulse_gated_pattern(*, scattering_strength_db_per_m2: float,
    gated_area: PulseGatedEquivalentArea, incidence_angle_from_normal_rad: float) -> SeafloorAreaBackscatter:
    area = float(gated_area.equivalent_insonified_area_m2)
    if area <= 0.0:
        raise ValueError("pulse-gated pattern has zero equivalent insonified area")
    return SeafloorAreaBackscatter(scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=area, incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
        area_semantics="equivalent_pattern_and_pulse_weighted")


def seafloor_backscatter_from_matched_filter_weighted_pattern(*, scattering_strength_db_per_m2: float,
    weighted_area: MatchedFilterWeightedEquivalentArea, incidence_angle_from_normal_rad: float) -> SeafloorAreaBackscatter:
    """Build area backscatter from pattern-times-matched-filter equivalent area."""

    area = float(weighted_area.equivalent_insonified_area_m2)
    if area <= 0.0:
        raise ValueError("matched-filter weighted pattern has zero equivalent insonified area")
    return SeafloorAreaBackscatter(scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=area, incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
        area_semantics="equivalent_pattern_and_matched_filter_weighted")

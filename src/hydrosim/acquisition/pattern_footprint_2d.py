"""Project a sampled 2D Mills-Cross pattern onto a flat seafloor.

A -3 dB contour is a beam descriptor, not a physical boundary of insonification.
Outside that contour the seafloor generally continues to receive acoustic energy,
including from the rest of the main lobe and sidelobes. HydroSIM therefore keeps
the full sampled TX×RX power distribution and separates three concepts:

* projected grid area: the geometric area covered by the sampled angular domain;
* half-power area: a descriptive area inside P >= 0.5 P_peak;
* equivalent insonified area: the power-weighted integral

      A_eq = integral (P / P_peak) dA

  approximated over the projected angular grid.

``A_eq`` is the area that, if uniformly weighted at the sampled peak power, would
produce the same integrated power as the distributed sampled pattern. Its value
necessarily depends on the angular scan extent: sidelobes outside the sampled
window are not included.

The module also provides a first explicit rectangular-pulse range gate. For a
pulse of duration tau, the contributing one-way range shell has width c*tau/2.
The current sampled gate includes cells by centre range; fractional range-cell
clipping and matched-filter autocorrelation weighting are later refinements.
"""

from __future__ import annotations

from math import sqrt, tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_pattern_2d import AngularPattern2DScan
from .bottom_interaction import SeafloorAreaBackscatter


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
    *,
    scan: AngularPattern2DScan,
    vertical_separation_m: float,
) -> ProjectedPatternIllumination:
    """Project the full sampled 2D TX×RX power distribution onto a flat bottom.

    No threshold is used to define insonification. The half-power contour remains
    available only as a descriptive statistic. Equivalent area is the sum of
    ``(P/P_peak) * dA`` over every sampled grid cell.
    """

    h = float(vertical_separation_m)
    if h <= 0.0:
        raise ValueError("vertical_separation_m must be positive")

    along_count = len(scan.along_track_angles_rad)
    across_count = len(scan.across_track_angles_rad)
    expected = along_count * across_count
    if len(scan.samples) != expected:
        raise ValueError("AngularPattern2DScan sample layout is inconsistent with its axes")

    peak_power = float(scan.peak_power)
    if peak_power <= 0.0:
        raise ValueError("AngularPattern2DScan peak_power must be positive")

    along_edges = _cell_edges(scan.along_track_angles_rad)
    across_edges = _cell_edges(scan.across_track_angles_rad)

    cells: list[ProjectedPatternCell] = []
    grid_area = 0.0
    equivalent_area = 0.0
    half_power_area = 0.0
    half_power_forward: list[float] = []
    half_power_port: list[float] = []

    for along_index, along in enumerate(scan.along_track_angles_rad):
        x0 = h * tan(along_edges[along_index])
        x1 = h * tan(along_edges[along_index + 1])
        dx = abs(x1 - x0)
        for across_index, across in enumerate(scan.across_track_angles_rad):
            y0 = h * tan(across_edges[across_index])
            y1 = h * tan(across_edges[across_index + 1])
            dy = abs(y1 - y0)
            area = dx * dy
            flat_index = along_index * across_count + across_index
            sample = scan.samples[flat_index]
            power = float(sample.normalized_power)
            relative_power = power / peak_power
            equivalent_contribution = relative_power * area
            inside_half_power = relative_power >= 0.5
            forward_center = h * tan(float(along))
            port_center = h * tan(float(across))
            slant_range = sqrt(h * h + forward_center**2 + port_center**2)

            grid_area += area
            equivalent_area += equivalent_contribution
            if inside_half_power:
                half_power_area += area
                half_power_forward.extend((min(x0, x1), max(x0, x1)))
                half_power_port.extend((min(y0, y1), max(y0, y1)))

            cells.append(
                ProjectedPatternCell(
                    along_track_index=along_index,
                    across_track_index=across_index,
                    along_track_angle_rad=along,
                    across_track_angle_rad=across,
                    normalized_power=power,
                    relative_power_to_peak=relative_power,
                    forward_center_m=forward_center,
                    port_center_m=port_center,
                    slant_range_m=slant_range,
                    projected_area_m2=area,
                    equivalent_area_contribution_m2=equivalent_contribution,
                    inside_half_power_contour=inside_half_power,
                )
            )

    return ProjectedPatternIllumination(
        configuration_name=scan.configuration_name,
        vertical_separation_m=h,
        peak_power=peak_power,
        sampled_grid_area_m2=grid_area,
        equivalent_insonified_area_m2=equivalent_area,
        half_power_area_m2=half_power_area,
        half_power_cell_count=sum(cell.inside_half_power_contour for cell in cells),
        total_cell_count=len(cells),
        half_power_forward_min_m=min(half_power_forward) if half_power_forward else None,
        half_power_forward_max_m=max(half_power_forward) if half_power_forward else None,
        half_power_port_min_m=min(half_power_port) if half_power_port else None,
        half_power_port_max_m=max(half_power_port) if half_power_port else None,
        cells=tuple(cells),
    )


def gate_projected_pattern_by_rectangular_pulse(
    *,
    illumination: ProjectedPatternIllumination,
    center_one_way_range_m: float,
    pulse_duration_seconds: float,
    sound_speed_mps: float,
) -> PulseGatedEquivalentArea:
    """Apply a first rectangular-pulse range shell to pattern-weighted cells.

    A transmitted pulse of duration ``tau`` occupies a one-way range thickness
    ``c*tau/2`` in the received echo. ``center_one_way_range_m`` defines the centre
    of that shell, so the half-width is ``c*tau/4``.
    """

    center = float(center_one_way_range_m)
    tau = float(pulse_duration_seconds)
    c = float(sound_speed_mps)
    if center <= 0.0:
        raise ValueError("center_one_way_range_m must be positive")
    if tau <= 0.0:
        raise ValueError("pulse_duration_seconds must be positive")
    if c <= 0.0:
        raise ValueError("sound_speed_mps must be positive")

    width = c * tau / 2.0
    half_width = width / 2.0
    minimum = center - half_width
    maximum = center + half_width
    if minimum <= 0.0:
        raise ValueError("pulse range shell must remain at positive one-way range")

    contributing = [
        cell
        for cell in illumination.cells
        if minimum <= float(cell.slant_range_m) <= maximum
    ]
    equivalent_area = sum(
        float(cell.equivalent_area_contribution_m2) for cell in contributing
    )
    return PulseGatedEquivalentArea(
        center_one_way_range_m=center,
        pulse_duration_seconds=tau,
        sound_speed_mps=c,
        range_shell_width_m=width,
        minimum_one_way_range_m=minimum,
        maximum_one_way_range_m=maximum,
        contributing_cell_count=len(contributing),
        equivalent_insonified_area_m2=equivalent_area,
    )


def seafloor_backscatter_from_projected_pattern(
    *,
    scattering_strength_db_per_m2: float,
    illumination: ProjectedPatternIllumination,
    incidence_angle_from_normal_rad: float,
) -> SeafloorAreaBackscatter:
    """Build area backscatter from the full pattern-weighted equivalent area."""

    area = float(illumination.equivalent_insonified_area_m2)
    if area <= 0.0:
        raise ValueError("projected pattern has zero equivalent insonified area")
    return SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=area,
        incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
        area_semantics="equivalent_pattern_weighted",
    )


def seafloor_backscatter_from_pulse_gated_pattern(
    *,
    scattering_strength_db_per_m2: float,
    gated_area: PulseGatedEquivalentArea,
    incidence_angle_from_normal_rad: float,
) -> SeafloorAreaBackscatter:
    """Build area backscatter from pattern-times-rectangular-pulse equivalent area."""

    area = float(gated_area.equivalent_insonified_area_m2)
    if area <= 0.0:
        raise ValueError("pulse-gated pattern has zero equivalent insonified area")
    return SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=area,
        incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
        area_semantics="equivalent_pattern_and_pulse_weighted",
    )

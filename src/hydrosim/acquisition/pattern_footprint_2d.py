"""Project a sampled 2D Mills-Cross beam pattern directly onto a flat seafloor.

This module removes the rectangular -3 dB beamwidth approximation from one
footprint pathway. It uses the existing ``AngularPattern2DScan`` as the scientific
source and projects angular grid cells onto a horizontal plane at vertical
separation ``h``.

HydroSIM's angular coordinates are slope angles, so intersection with z=h is exact
for the local flat-plane reference:

    x_forward = h tan(alpha_along)
    y_port    = h tan(alpha_across)

The footprint is a thresholded raster approximation to the projected 2D response.
For the default half-power contour, a cell contributes area when its centre sample
satisfies

    P >= 0.5 P_peak.

Cell area is computed from projected angular-bin edges, not from a nominal
beamwidth rectangle. This allows non-rectangular, asymmetric and combined-steering
patterns to produce correspondingly different footprints. It remains a sampled
far-field / flat-bottom approximation; terrain projection and fractional contour
cell clipping are later refinements.
"""

from __future__ import annotations

from math import tan

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .angular_pattern_2d import AngularPattern2DScan
from .bottom_interaction import SeafloorAreaBackscatter


class ProjectedPatternCell(BaseModel):
    """One angular grid cell projected onto the horizontal seafloor plane."""

    model_config = ConfigDict(frozen=True)

    along_track_index: int = Field(ge=0)
    across_track_index: int = Field(ge=0)
    along_track_angle_rad: FiniteFloat
    across_track_angle_rad: FiniteFloat
    normalized_power: FiniteFloat = Field(ge=0.0)
    forward_center_m: FiniteFloat
    port_center_m: FiniteFloat
    projected_area_m2: FiniteFloat = Field(gt=0.0)
    included: bool


class ProjectedPatternFootprint(BaseModel):
    """Thresholded direct projection of a sampled two-way beam pattern."""

    model_config = ConfigDict(frozen=True)

    configuration_name: str = Field(min_length=1)
    vertical_separation_m: FiniteFloat = Field(gt=0.0)
    threshold_fraction_of_peak: FiniteFloat = Field(gt=0.0, le=1.0)
    threshold_power: FiniteFloat = Field(ge=0.0)
    included_cell_count: int = Field(ge=0)
    total_cell_count: int = Field(gt=0)
    effective_area_m2: FiniteFloat = Field(ge=0.0)
    forward_min_m: FiniteFloat | None = None
    forward_max_m: FiniteFloat | None = None
    port_min_m: FiniteFloat | None = None
    port_max_m: FiniteFloat | None = None
    cells: tuple[ProjectedPatternCell, ...]


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
    threshold_fraction_of_peak: float = 0.5,
) -> ProjectedPatternFootprint:
    """Project thresholded 2D pattern cells onto a horizontal seafloor.

    ``threshold_fraction_of_peak=0.5`` corresponds to the two-way half-power
    footprint of the sampled pattern. Grid cells are treated as piecewise constant
    at their centre value. The returned cell list preserves enough information for
    didactic visualization and later fractional-cell contour refinement.
    """

    h = float(vertical_separation_m)
    fraction = float(threshold_fraction_of_peak)
    if h <= 0.0:
        raise ValueError("vertical_separation_m must be positive")
    if not 0.0 < fraction <= 1.0:
        raise ValueError("threshold_fraction_of_peak must satisfy 0 < value <= 1")

    along_count = len(scan.along_track_angles_rad)
    across_count = len(scan.across_track_angles_rad)
    expected = along_count * across_count
    if len(scan.samples) != expected:
        raise ValueError("AngularPattern2DScan sample layout is inconsistent with its axes")

    along_edges = _cell_edges(scan.along_track_angles_rad)
    across_edges = _cell_edges(scan.across_track_angles_rad)
    threshold = fraction * float(scan.peak_power)

    cells: list[ProjectedPatternCell] = []
    included_area = 0.0
    included_forward: list[float] = []
    included_port: list[float] = []

    for along_index, along in enumerate(scan.along_track_angles_rad):
        x0 = h * tan(along_edges[along_index])
        x1 = h * tan(along_edges[along_index + 1])
        dx = abs(x1 - x0)
        for across_index, across in enumerate(scan.across_track_angles_rad):
            y0 = h * tan(across_edges[across_index])
            y1 = h * tan(across_edges[across_index + 1])
            dy = abs(y1 - y0)
            flat_index = along_index * across_count + across_index
            sample = scan.samples[flat_index]
            power = float(sample.normalized_power)
            included = power >= threshold
            area = dx * dy
            forward_center = h * tan(float(along))
            port_center = h * tan(float(across))
            if included:
                included_area += area
                included_forward.extend((min(x0, x1), max(x0, x1)))
                included_port.extend((min(y0, y1), max(y0, y1)))
            cells.append(
                ProjectedPatternCell(
                    along_track_index=along_index,
                    across_track_index=across_index,
                    along_track_angle_rad=along,
                    across_track_angle_rad=across,
                    normalized_power=power,
                    forward_center_m=forward_center,
                    port_center_m=port_center,
                    projected_area_m2=area,
                    included=included,
                )
            )

    return ProjectedPatternFootprint(
        configuration_name=scan.configuration_name,
        vertical_separation_m=h,
        threshold_fraction_of_peak=fraction,
        threshold_power=threshold,
        included_cell_count=sum(cell.included for cell in cells),
        total_cell_count=len(cells),
        effective_area_m2=included_area,
        forward_min_m=min(included_forward) if included_forward else None,
        forward_max_m=max(included_forward) if included_forward else None,
        port_min_m=min(included_port) if included_port else None,
        port_max_m=max(included_port) if included_port else None,
        cells=tuple(cells),
    )


def seafloor_backscatter_from_projected_pattern(
    *,
    scattering_strength_db_per_m2: float,
    footprint: ProjectedPatternFootprint,
    incidence_angle_from_normal_rad: float,
) -> SeafloorAreaBackscatter:
    """Build the area-backscatter model from the direct 2D-pattern footprint."""

    if float(footprint.effective_area_m2) <= 0.0:
        raise ValueError("projected pattern footprint has zero included area")
    return SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=scattering_strength_db_per_m2,
        insonified_area_m2=footprint.effective_area_m2,
        incidence_angle_from_normal_rad=incidence_angle_from_normal_rad,
    )

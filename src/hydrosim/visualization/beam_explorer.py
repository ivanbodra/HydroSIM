"""Composition layer for the first HydroSIM Beam Explorer lesson.

No new acoustic physics is introduced here. The snapshot is assembled from the
existing Mills-Cross geometry and two-way angular-pattern model. Because the
first lesson displays only the two principal planes, it evaluates two thin scans
rather than computing an unused dense 2-D field on every interactive update.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

from hydrosim.acquisition import AngularPattern2DScan, scan_mills_cross_two_way_pattern_2d
from hydrosim.geometry import make_reference_mills_cross


@dataclass(frozen=True)
class BeamExplorerControls:
    """Small control state for the first beam-pattern lesson."""

    frequency_hz: float = 150_000.0
    elements_per_arm: int = 16
    sound_speed_mps: float = 1500.0
    element_spacing_m: float = 0.005
    element_size_m: float = 0.004
    angular_extent_deg: float = 60.0
    angular_sample_count: int = 121

    def validate(self) -> None:
        if self.frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be positive")
        if self.elements_per_arm < 2:
            raise ValueError("elements_per_arm must be >= 2")
        if self.sound_speed_mps <= 0.0:
            raise ValueError("sound_speed_mps must be positive")
        if self.element_spacing_m <= 0.0:
            raise ValueError("element_spacing_m must be positive")
        if self.element_size_m <= 0.0:
            raise ValueError("element_size_m must be positive")
        if not 0.0 < self.angular_extent_deg < 90.0:
            raise ValueError("angular_extent_deg must lie between 0 and 90 degrees")
        if self.angular_sample_count < 3 or self.angular_sample_count % 2 == 0:
            raise ValueError("angular_sample_count must be an odd integer >= 3")


@dataclass(frozen=True)
class BeamExplorerSnapshot:
    """Render-ready state for a symmetric reference Mills-Cross lesson."""

    controls: BeamExplorerControls
    along_track_scan: AngularPattern2DScan
    across_track_scan: AngularPattern2DScan
    wavelength_m: float
    spacing_over_wavelength: float
    element_center_span_m: float


def prepare_beam_explorer_snapshot(
    controls: BeamExplorerControls | None = None,
) -> BeamExplorerSnapshot:
    """Build one beam-pattern lesson snapshot from existing scientific models."""

    state = controls or BeamExplorerControls()
    state.validate()
    configuration = make_reference_mills_cross(
        transmit_count=state.elements_per_arm,
        receive_count=state.elements_per_arm,
        transmit_spacing=state.element_spacing_m,
        receive_spacing=state.element_spacing_m,
        transmit_element_longitudinal_size=state.element_size_m,
        transmit_element_transverse_size=state.element_size_m,
        receive_element_longitudinal_size=state.element_size_m,
        receive_element_transverse_size=state.element_size_m,
        name="didactic_reference_mills_cross",
    )
    extent = state.angular_extent_deg * pi / 180.0
    common = dict(
        configuration=configuration,
        frequency_hz=state.frequency_hz,
        sound_speed_mps=state.sound_speed_mps,
    )
    along_track_scan = scan_mills_cross_two_way_pattern_2d(
        along_track_start_angle_rad=-extent,
        along_track_end_angle_rad=extent,
        along_track_sample_count=state.angular_sample_count,
        across_track_start_angle_rad=-extent,
        across_track_end_angle_rad=extent,
        across_track_sample_count=3,
        **common,
    )
    across_track_scan = scan_mills_cross_two_way_pattern_2d(
        along_track_start_angle_rad=-extent,
        along_track_end_angle_rad=extent,
        along_track_sample_count=3,
        across_track_start_angle_rad=-extent,
        across_track_end_angle_rad=extent,
        across_track_sample_count=state.angular_sample_count,
        **common,
    )
    wavelength = state.sound_speed_mps / state.frequency_hz
    return BeamExplorerSnapshot(
        controls=state,
        along_track_scan=along_track_scan,
        across_track_scan=across_track_scan,
        wavelength_m=wavelength,
        spacing_over_wavelength=state.element_spacing_m / wavelength,
        element_center_span_m=(state.elements_per_arm - 1) * state.element_spacing_m,
    )

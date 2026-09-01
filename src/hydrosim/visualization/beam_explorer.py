"""Composition layer for the HydroSIM Beam Explorer lesson.

No new acoustic physics is introduced here. The snapshot is assembled from the
existing Mills-Cross two-way angular-pattern and flat-seafloor footprint models.
A single two-dimensional angular response is retained so the renderer can show
both principal-plane cuts and the modeled continuous seafloor response.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, tan

from hydrosim.acquisition import (
    AngularPattern2DScan,
    scan_mills_cross_two_way_pattern_2d,
    sensor_angular_direction,
)
from hydrosim.acquisition.footprint import (
    FlatSeafloorFootprintModel,
    InsonifiedFootprint,
    estimate_flat_seafloor_footprint,
)
from hydrosim.geometry import Vector3, make_reference_mills_cross


@dataclass(frozen=True)
class BeamExplorerControls:
    """Small control state for the first complete beam-pattern lesson.

    ``across_track_steering_angle_deg`` follows the canonical HydroSIM sensor-frame
    convention: zero is the sensor +Z normal, positive angles point Port (-Y), and
    negative angles point Starboard (+Y).
    """

    frequency_hz: float = 150_000.0
    elements_per_arm: int = 16
    sound_speed_mps: float = 1500.0
    element_spacing_m: float = 0.005
    element_size_m: float = 0.004
    seafloor_depth_m: float = 30.0
    pulse_duration_seconds: float = 1e-3
    angular_extent_deg: float = 60.0
    angular_sample_count: int = 121
    across_track_steering_angle_deg: float = 0.0

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
        if self.seafloor_depth_m <= 0.0:
            raise ValueError("seafloor_depth_m must be positive")
        if self.pulse_duration_seconds <= 0.0:
            raise ValueError("pulse_duration_seconds must be positive")
        if not 0.0 < self.angular_extent_deg < 90.0:
            raise ValueError("angular_extent_deg must lie between 0 and 90 degrees")
        if abs(self.across_track_steering_angle_deg) >= self.angular_extent_deg:
            raise ValueError("across_track_steering_angle_deg must lie inside the angular scan extent")
        if self.angular_sample_count < 3 or self.angular_sample_count % 2 == 0:
            raise ValueError("angular_sample_count must be an odd integer >= 3")


@dataclass(frozen=True)
class BeamExplorerSnapshot:
    """Render-ready state for the reference Mills-Cross beam lesson."""

    controls: BeamExplorerControls
    response_scan: AngularPattern2DScan
    along_track_scan: AngularPattern2DScan
    across_track_scan: AngularPattern2DScan
    wavelength_m: float
    spacing_over_wavelength: float
    element_center_span_m: float
    along_track_half_power_beamwidth_rad: float
    across_track_half_power_beamwidth_rad: float
    nadir_footprint: InsonifiedFootprint
    across_track_steering_angle_rad: float
    steering_direction_sensor_frame: Vector3
    steered_across_track_center_offset_m: float

    @property
    def along_track_beamwidth_deg(self) -> float:
        """Compatibility readout for application code predating the radian field rename."""

        return self.along_track_half_power_beamwidth_rad * 180.0 / pi

    @property
    def footprint(self) -> InsonifiedFootprint:
        """Compatibility alias for the explicitly named nadir footprint."""

        return self.nadir_footprint


def _principal_samples(scan: AngularPattern2DScan, *, axis: str):
    n_along = len(scan.along_track_angles_rad)
    n_across = len(scan.across_track_angles_rad)
    peak_along_index = min(
        range(n_along),
        key=lambda index: abs(
            float(scan.along_track_angles_rad[index]) - float(scan.peak_along_track_angle_rad)
        ),
    )
    peak_across_index = min(
        range(n_across),
        key=lambda index: abs(
            float(scan.across_track_angles_rad[index]) - float(scan.peak_across_track_angle_rad)
        ),
    )
    if axis == "along":
        j = peak_across_index
        return (
            [float(scan.along_track_angles_rad[i]) for i in range(n_along)],
            [float(scan.samples[i * n_across + j].normalized_amplitude) ** 2 for i in range(n_along)],
        )
    if axis == "across":
        i = peak_along_index
        return (
            [float(scan.across_track_angles_rad[j]) for j in range(n_across)],
            [float(scan.samples[i * n_across + j].normalized_amplitude) ** 2 for j in range(n_across)],
        )
    raise ValueError("axis must be 'along' or 'across'")


def _half_power_beamwidth(scan: AngularPattern2DScan, *, axis: str) -> float:
    """Derive the local -3 dB width from the existing normalized two-way scan."""

    angles, power = _principal_samples(scan, axis=axis)
    peak_index = max(range(len(power)), key=power.__getitem__)
    target = 0.5 * power[peak_index]

    def crossing(i0: int, i1: int) -> float:
        a0, a1 = angles[i0], angles[i1]
        p0, p1 = power[i0], power[i1]
        if p1 == p0:
            return 0.5 * (a0 + a1)
        return a0 + (target - p0) * (a1 - a0) / (p1 - p0)

    left = None
    for i in range(peak_index, 0, -1):
        if power[i] >= target and power[i - 1] < target:
            left = crossing(i - 1, i)
            break
    right = None
    for i in range(peak_index, len(power) - 1):
        if power[i] >= target and power[i + 1] < target:
            right = crossing(i, i + 1)
            break
    if left is None or right is None:
        raise ValueError("half-power crossings are outside the Beam Explorer scan")
    return right - left


def prepare_beam_explorer_snapshot(
    controls: BeamExplorerControls | None = None,
) -> BeamExplorerSnapshot:
    """Build the modeled 2D response, -3 dB widths, steering state, and nadir footprint."""

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
    steering_rad = state.across_track_steering_angle_deg * pi / 180.0
    response_scan = scan_mills_cross_two_way_pattern_2d(
        configuration=configuration,
        along_track_start_angle_rad=-extent,
        along_track_end_angle_rad=extent,
        along_track_sample_count=state.angular_sample_count,
        across_track_start_angle_rad=-extent,
        across_track_end_angle_rad=extent,
        across_track_sample_count=state.angular_sample_count,
        transmit_steering_across_track_angle_rad=steering_rad,
        receive_steering_across_track_angle_rad=steering_rad,
        frequency_hz=state.frequency_hz,
        sound_speed_mps=state.sound_speed_mps,
    )
    wavelength = state.sound_speed_mps / state.frequency_hz
    along_width = _half_power_beamwidth(response_scan, axis="along")
    across_width = _half_power_beamwidth(response_scan, axis="across")
    footprint = estimate_flat_seafloor_footprint(
        model=FlatSeafloorFootprintModel(
            transmit_along_track_beamwidth_rad=along_width,
            receive_across_track_beamwidth_rad=across_width,
        ),
        vertical_separation_m=state.seafloor_depth_m,
        transmit_along_track_center_angle_rad=0.0,
        incidence_angle_from_normal_rad=0.0,
        pulse_duration_seconds=state.pulse_duration_seconds,
        sound_speed_mps=state.sound_speed_mps,
    )
    return BeamExplorerSnapshot(
        controls=state,
        response_scan=response_scan,
        along_track_scan=response_scan,
        across_track_scan=response_scan,
        wavelength_m=wavelength,
        spacing_over_wavelength=state.element_spacing_m / wavelength,
        element_center_span_m=(state.elements_per_arm - 1) * state.element_spacing_m,
        along_track_half_power_beamwidth_rad=along_width,
        across_track_half_power_beamwidth_rad=across_width,
        nadir_footprint=footprint,
        across_track_steering_angle_rad=steering_rad,
        steering_direction_sensor_frame=sensor_angular_direction(0.0, steering_rad),
        steered_across_track_center_offset_m=state.seafloor_depth_m * tan(steering_rad),
    )

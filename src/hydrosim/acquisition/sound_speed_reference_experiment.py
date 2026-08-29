"""End-to-end reference experiment for sound speed at the transducer.

This deliberately narrow experiment closes one complete causal chain without
mixing simulation Truth into sonar reconstruction:

    true local c
      -> sound-speed sensor
      -> c used by sonar
      -> TX steering law
      -> physical TX direction in Truth
      -> flat-bottom interaction and TWTT
      -> physical RX wavefront
      -> RX angle estimate under c used
      -> sonar constant-c reconstruction
      -> calculated-minus-Truth sounding error.

The experiment is stationary, monostatic, homogeneous, principal-plane, and uses a
flat bottom. Those restrictions are explicit so it can serve as a scientific
reference before motion, refraction, bistatic geometry, and finite footprints are
added.
"""

from __future__ import annotations

from math import sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose, Vector3
from hydrosim.geometry.rotations import rotate_vector, rotation_matrix_from_rpy

from .angular_pattern_2d import sensor_angular_direction
from .sound_speed_at_transducer import (
    PrincipalPlaneReceiveAngleEstimate,
    PrincipalPlaneSteeringTruthComparison,
    compare_principal_plane_steering_with_truth,
    estimate_principal_plane_receive_angle,
)
from .sound_speed_processing import SoundSpeedAtTransducerUse, use_measured_sound_speed_at_transducer
from .sound_speed_sensor import (
    SoundSpeedAtTransducerMeasurement,
    SoundSpeedSensorAtTransducer,
    measure_sound_speed_at_transducer,
)
from .sounding_observation import DetectedAcousticObservation
from .sounding_reconstruction import ConstantSoundSpeedSounding, reconstruct_constant_sound_speed_sounding


class SoundSpeedAtTransducerReferenceExperiment(BaseModel):
    """Closed reference chain and final calculated-minus-Truth sounding error."""

    model_config = ConfigDict(frozen=True)

    true_local_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    configured_across_track_angle_rad: FiniteFloat
    sensor_measurement: SoundSpeedAtTransducerMeasurement
    sound_speed_used_by_sonar: SoundSpeedAtTransducerUse
    transmit_truth: PrincipalPlaneSteeringTruthComparison
    truth_bottom_point: Vector3
    true_one_way_range_m: FiniteFloat = Field(gt=0.0)
    true_twtt_seconds: FiniteFloat = Field(gt=0.0)
    receive_angle_estimate: PrincipalPlaneReceiveAngleEstimate
    observation: DetectedAcousticObservation
    calculated_sounding: ConstantSoundSpeedSounding
    sounding_error: Vector3
    sounding_error_norm_m: FiniteFloat = Field(ge=0.0)
    experiment_assumption: str = "stationary_monostatic_homogeneous_principal_plane_flat_bottom"


def run_sound_speed_at_transducer_reference_experiment(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angle_rad: float,
    true_local_sound_speed_mps: float,
    sensor: SoundSpeedSensorAtTransducer = SoundSpeedSensorAtTransducer(),
) -> SoundSpeedAtTransducerReferenceExperiment:
    """Run the first closed HydroSIM sound-speed-at-transducer error experiment."""

    true_c = float(true_local_sound_speed_mps)
    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=true_c,
        sensor=sensor,
    )
    used = use_measured_sound_speed_at_transducer(measurement)
    configured_angle = float(configured_across_track_angle_rad)

    transmit_truth = compare_principal_plane_steering_with_truth(
        configured_angle_rad=configured_angle,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
        true_local_sound_speed_mps=true_c,
    )

    physical_direction_sensor = sensor_angular_direction(
        0.0,
        float(transmit_truth.physical_angle_rad),
    )
    rotation = rotation_matrix_from_rpy(sensor_pose.attitude)
    physical_direction_destination = rotate_vector(rotation, physical_direction_sensor)
    intersection = terrain.intersect_ray(sensor_pose.position, physical_direction_destination)
    if not intersection.valid or intersection.point is None or intersection.slant_range is None:
        raise ValueError("physical transmit ray does not intersect the flat terrain")

    truth_point = intersection.point
    true_range = float(intersection.slant_range)
    true_twtt = 2.0 * true_range / true_c

    receive_estimate = estimate_principal_plane_receive_angle(
        physical_arrival_angle_rad=float(transmit_truth.physical_angle_rad),
        true_local_sound_speed_mps=true_c,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
    )
    observation = DetectedAcousticObservation(
        parent_beam_index=0,
        detection_method="phase_zero_crossing",
        twtt_seconds=true_twtt,
        detected_across_track_angle_rad=float(receive_estimate.estimated_angle_rad),
        quality=1.0,
    )
    calculated = reconstruct_constant_sound_speed_sounding(
        observation,
        sensor_pose=sensor_pose,
        along_track_angle_rad=0.0,
        sound_speed_mps=float(used.sound_speed_mps),
    )

    error = Vector3(
        x=float(calculated.point.x) - float(truth_point.x),
        y=float(calculated.point.y) - float(truth_point.y),
        z=float(calculated.point.z) - float(truth_point.z),
    )
    error_norm = sqrt(float(error.x) ** 2 + float(error.y) ** 2 + float(error.z) ** 2)

    return SoundSpeedAtTransducerReferenceExperiment(
        true_local_sound_speed_mps=true_c,
        configured_across_track_angle_rad=configured_angle,
        sensor_measurement=measurement,
        sound_speed_used_by_sonar=used,
        transmit_truth=transmit_truth,
        truth_bottom_point=truth_point,
        true_one_way_range_m=true_range,
        true_twtt_seconds=true_twtt,
        receive_angle_estimate=receive_estimate,
        observation=observation,
        calculated_sounding=calculated,
        sounding_error=error,
        sounding_error_norm_m=error_norm,
    )

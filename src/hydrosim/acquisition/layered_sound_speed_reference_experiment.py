"""End-to-end layered sound-speed reference experiment.

This experiment keeps simulation Truth and sonar processing separate while adding
refraction to the earlier homogeneous sound-speed-at-transducer reference case.

Truth side:
    true processing-independent profile
      -> true local sound speed at transducer depth
      -> sensor measurement
      -> c used by sonar
      -> TX delay-law consequence in Truth
      -> refracted ray through the true profile
      -> reciprocal TWTT and physical return angle.

Processing side:
    physical receive wavefront
      -> angle estimated under c used by sonar
      -> tangential slowness carried into the configured processing profile
      -> TWTT-driven refracted reconstruction
      -> calculated-minus-Truth sounding error.

IMPORTANT SCOPE
---------------
The sensor ``bias_mps`` in this reference currently perturbs the array steering/
angle-estimation sound speed only. It does *not* modify the processing sound-speed
profile and therefore must not be interpreted as a complete model of a fixed sensor
offset in a real MBES. Some systems use the sound speed measured at transducer depth
as the first value of the ray-bending profile; modelling that coupling requires a
profile representation that can distinguish a transducer-depth boundary value from a
finite-thickness water-column layer. HydroSIM's present piecewise-constant layers do
not make that distinction without introducing an artificial layer thickness.

Consequently, exact cancellation of a steering-only perturbation in the aligned,
stationary reciprocal reference is a deliberately narrow numerical/scientific
closure result, not a claim that sound-speed-at-transducer errors generally cancel.
Tilted arrays, vessel attitude, multi-sector geometry, sensor/profile coupling, and
water-column errors are outside this reference and can break that cancellation.

The reference is intentionally stationary, monostatic, principal-plane, reciprocal,
and horizontally layered. The sensor frame must be aligned with the profile/NED
frame so this experiment isolates sound-speed effects rather than attitude errors.
"""

from __future__ import annotations

from math import copysign, sqrt

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose, Vector3

from .layered_propagation import LayeredRayPath, LayeredSoundSpeedProfile, trace_layered_ray_to_depth
from .layered_sound_speed_processing import (
    LayeredSoundSpeedAtTransducerSounding,
    reconstruct_layered_sound_speed_sounding_from_sonar_state,
)
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


class LayeredSoundSpeedReferenceExperiment(BaseModel):
    """Closed Truth-versus-processing comparison for the narrow reference regime."""

    model_config = ConfigDict(frozen=True)

    true_profile: LayeredSoundSpeedProfile
    processing_profile: LayeredSoundSpeedProfile
    profile_start_depth_m: FiniteFloat = Field(ge=0.0)
    true_target_depth_m: FiniteFloat = Field(gt=0.0)
    true_local_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    configured_across_track_angle_rad: FiniteFloat
    sensor_measurement: SoundSpeedAtTransducerMeasurement
    sound_speed_used_by_sonar: SoundSpeedAtTransducerUse
    transmit_truth: PrincipalPlaneSteeringTruthComparison
    true_ray_path: LayeredRayPath
    truth_bottom_point: Vector3
    true_twtt_seconds: FiniteFloat = Field(gt=0.0)
    receive_angle_estimate: PrincipalPlaneReceiveAngleEstimate
    observation: DetectedAcousticObservation
    calculated_sounding: LayeredSoundSpeedAtTransducerSounding
    sounding_error: Vector3
    sounding_error_norm_m: FiniteFloat = Field(ge=0.0)
    sound_speed_error_scope: str = "steering_only_sensor_measurement_perturbation"
    experiment_assumption: str = (
        "stationary_monostatic_reciprocal_principal_plane_horizontal_layers_aligned_flat_array_flat_bottom"
    )


def _require_profile_aligned_pose(sensor_pose: Pose) -> None:
    attitude = sensor_pose.attitude
    if any(abs(float(value)) > 1e-12 for value in (attitude.roll, attitude.pitch, attitude.yaw)):
        raise ValueError("reference experiment requires sensor attitude aligned with profile frame")


def run_layered_sound_speed_reference_experiment(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angle_rad: float,
    true_profile: LayeredSoundSpeedProfile,
    processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    sensor: SoundSpeedSensorAtTransducer = SoundSpeedSensorAtTransducer(),
) -> LayeredSoundSpeedReferenceExperiment:
    """Run the narrow layered Truth-versus-processing reference experiment.

    The local true sound speed is obtained from ``true_profile`` at the transducer
    profile depth. The sonar never receives that Truth value directly; it receives
    only the sensor observation and the resulting ``SoundSpeedAtTransducerUse``.

    ``sensor.bias_mps`` changes array steering/angle-estimation state only in this
    reference. It intentionally does not rewrite ``processing_profile``.
    """

    _require_profile_aligned_pose(sensor_pose)
    start_depth = float(profile_start_depth_m)
    if start_depth < 0.0:
        raise ValueError("profile_start_depth_m must be non-negative")

    vertical_separation = float(terrain.depth) - float(sensor_pose.position.z)
    if vertical_separation <= 0.0:
        raise ValueError("flat terrain must lie below the sensor in +Z/down")
    target_depth = start_depth + vertical_separation

    true_local_c = float(true_profile.layer_at_depth(start_depth).sound_speed_mps)
    true_profile.layer_at_depth(target_depth)
    processing_profile.layer_at_depth(start_depth)

    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=true_local_c,
        sensor=sensor,
    )
    used = use_measured_sound_speed_at_transducer(measurement)
    configured_angle = float(configured_across_track_angle_rad)

    transmit_truth = compare_principal_plane_steering_with_truth(
        configured_angle_rad=configured_angle,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
        true_local_sound_speed_mps=true_local_c,
    )
    physical_angle = float(transmit_truth.physical_angle_rad)
    true_path = trace_layered_ray_to_depth(
        profile=true_profile,
        launch_angle_from_vertical_rad=abs(physical_angle),
        target_depth_m=target_depth,
        start_depth_m=start_depth,
    )

    if abs(physical_angle) <= 1e-15:
        signed_horizontal = 0.0
    else:
        signed_horizontal = -copysign(float(true_path.horizontal_distance_m), physical_angle)

    truth_point = Vector3(
        x=float(sensor_pose.position.x),
        y=float(sensor_pose.position.y) + signed_horizontal,
        z=float(terrain.depth),
    )
    true_twtt = 2.0 * float(true_path.travel_time_seconds)

    receive_estimate = estimate_principal_plane_receive_angle(
        physical_arrival_angle_rad=physical_angle,
        true_local_sound_speed_mps=true_local_c,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
    )
    observation = DetectedAcousticObservation(
        parent_beam_index=0,
        detection_method="phase_zero_crossing",
        twtt_seconds=true_twtt,
        detected_across_track_angle_rad=float(receive_estimate.estimated_angle_rad),
        quality=1.0,
    )
    calculated = reconstruct_layered_sound_speed_sounding_from_sonar_state(
        observation,
        sensor_pose=sensor_pose,
        along_track_angle_rad=0.0,
        profile=processing_profile,
        profile_start_depth_m=start_depth,
        sound_speed_at_transducer=used,
    )

    calculated_point = calculated.sounding.point
    error = Vector3(
        x=float(calculated_point.x) - float(truth_point.x),
        y=float(calculated_point.y) - float(truth_point.y),
        z=float(calculated_point.z) - float(truth_point.z),
    )
    error_norm = sqrt(float(error.x) ** 2 + float(error.y) ** 2 + float(error.z) ** 2)

    return LayeredSoundSpeedReferenceExperiment(
        true_profile=true_profile,
        processing_profile=processing_profile,
        profile_start_depth_m=start_depth,
        true_target_depth_m=target_depth,
        true_local_sound_speed_mps=true_local_c,
        configured_across_track_angle_rad=configured_angle,
        sensor_measurement=measurement,
        sound_speed_used_by_sonar=used,
        transmit_truth=transmit_truth,
        true_ray_path=true_path,
        truth_bottom_point=truth_point,
        true_twtt_seconds=true_twtt,
        receive_angle_estimate=receive_estimate,
        observation=observation,
        calculated_sounding=calculated,
        sounding_error=error,
        sounding_error_norm_m=error_norm,
    )

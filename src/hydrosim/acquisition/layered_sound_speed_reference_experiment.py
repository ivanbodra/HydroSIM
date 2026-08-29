"""End-to-end layered sound-speed reference experiment.

This experiment keeps simulation Truth and sonar processing separate while adding
refraction to the earlier homogeneous sound-speed-at-transducer reference case.

Truth side:
    true processing-independent profile
      -> true local sound speed at transducer depth
      -> sensor measurement
      -> c used by sonar
      -> TX delay-law consequence in the array principal plane
      -> rotation from the tilted array frame into the profile frame
      -> refracted ray through the true profile
      -> reciprocal TWTT and physical return angle.

Processing side:
    physical receive wavefront
      -> angle estimated under c used by sonar in the array principal plane
      -> rotation into the profile frame
      -> explicit zero-thickness transducer-depth boundary
      -> tangential slowness carried into the configured processing profile
      -> TWTT-driven refracted reconstruction
      -> calculated-minus-Truth sounding error.

IMPORTANT SCOPE
---------------
``sensor.bias_mps`` perturbs the sound speed used for TX steering and RX angle
mapping and, on the processing side, the explicit zero-thickness profile boundary.
It does *not* rewrite any finite-thickness layer of ``processing_profile``. This
models the common conceptual separation between the array-face value and the
water-column profile without inventing a finite layer of sensor-biased water.

``principal_plane_array_tilt_rad`` is a controlled 2-D orientation parameter. It
rotates the array principal-plane angular coordinate relative to the horizontal-layer
profile frame before ray tracing and after receive-angle estimation. Positive tilt
is defined in the same signed direction as positive across-track beam angle. This is
an intentionally reduced principal-plane experiment, not a complete representation
of a Mills-cross installation or vessel attitude.

At zero tilt, exact cancellation of a transducer-value perturbation in the aligned,
stationary reciprocal reference is a deliberately narrow numerical/scientific
closure result, not a claim that sound-speed-at-transducer errors generally cancel.
Non-zero array tilt is the first controlled symmetry break: because the sound-speed
mapping is performed in array coordinates while Snell propagation is referenced to
the horizontal profile frame, rotation and sound-speed scaling do not generally
commute.

The reference is intentionally stationary, monostatic, principal-plane, reciprocal,
and horizontally layered. Vessel/sensor attitude must remain aligned with the
profile/NED frame so the experiment isolates array tilt and sound-speed effects from
platform-attitude errors. Scientific basis and source traceability are documented in
``docs/science/sound_speed_at_transducer.md``.
"""

from __future__ import annotations

from math import copysign, pi, sqrt

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
    """Closed Truth-versus-processing comparison for the controlled reference regime."""

    model_config = ConfigDict(frozen=True)

    true_profile: LayeredSoundSpeedProfile
    processing_profile: LayeredSoundSpeedProfile
    profile_start_depth_m: FiniteFloat = Field(ge=0.0)
    true_target_depth_m: FiniteFloat = Field(gt=0.0)
    true_local_sound_speed_mps: FiniteFloat = Field(gt=0.0)
    configured_across_track_angle_rad: FiniteFloat
    principal_plane_array_tilt_rad: FiniteFloat = 0.0
    sensor_measurement: SoundSpeedAtTransducerMeasurement
    sound_speed_used_by_sonar: SoundSpeedAtTransducerUse
    transmit_truth: PrincipalPlaneSteeringTruthComparison
    physical_launch_angle_profile_frame_rad: FiniteFloat
    true_ray_path: LayeredRayPath
    truth_bottom_point: Vector3
    true_twtt_seconds: FiniteFloat = Field(gt=0.0)
    receive_angle_estimate: PrincipalPlaneReceiveAngleEstimate
    estimated_receive_angle_profile_frame_rad: FiniteFloat
    observation: DetectedAcousticObservation
    calculated_sounding: LayeredSoundSpeedAtTransducerSounding
    sounding_error: Vector3
    sounding_error_norm_m: FiniteFloat = Field(ge=0.0)
    sound_speed_error_scope: str = "array_and_zero_thickness_boundary_sensor_perturbation"
    experiment_assumption: str = (
        "stationary_monostatic_reciprocal_principal_plane_horizontal_layers_"
        "aligned_platform_explicit_array_tilt_flat_bottom"
    )


class LayeredSoundSpeedErrorIsolationMatrix(BaseModel):
    """Four controlled runs separating transducer-value and water-column errors.

    ``reference`` has an ideal transducer sensor and the correct processing profile.
    ``transducer_only`` applies the requested sensor bias while retaining the correct
    finite-thickness profile. ``profile_only`` uses an ideal sensor with the supplied
    perturbed processing profile. ``combined`` applies both perturbations.

    All four cases use the same explicit principal-plane array tilt, so tilt is a
    controlled geometry coordinate rather than an additional error source.
    """

    model_config = ConfigDict(frozen=True)

    transducer_sensor_bias_mps: FiniteFloat
    principal_plane_array_tilt_rad: FiniteFloat = 0.0
    reference: LayeredSoundSpeedReferenceExperiment
    transducer_only: LayeredSoundSpeedReferenceExperiment
    profile_only: LayeredSoundSpeedReferenceExperiment
    combined: LayeredSoundSpeedReferenceExperiment


def _require_profile_aligned_pose(sensor_pose: Pose) -> None:
    attitude = sensor_pose.attitude
    if any(abs(float(value)) > 1e-12 for value in (attitude.roll, attitude.pitch, attitude.yaw)):
        raise ValueError("reference experiment requires sensor attitude aligned with profile frame")


def _require_downward_principal_plane_angle(angle_rad: float, *, name: str) -> float:
    angle = float(angle_rad)
    if not (-0.5 * pi < angle < 0.5 * pi):
        raise ValueError(f"{name} must satisfy -pi/2 < angle < pi/2")
    return angle


def run_layered_sound_speed_reference_experiment(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angle_rad: float,
    true_profile: LayeredSoundSpeedProfile,
    processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    sensor: SoundSpeedSensorAtTransducer = SoundSpeedSensorAtTransducer(),
    principal_plane_array_tilt_rad: float = 0.0,
) -> LayeredSoundSpeedReferenceExperiment:
    """Run the controlled layered Truth-versus-processing reference experiment.

    The configured beam angle is measured in the array principal-plane frame. The
    optional array tilt rotates that frame relative to the horizontal profile frame.
    TX sound-speed steering and RX sound-speed angle estimation are performed before
    this frame rotation, matching their array-coordinate semantics.

    ``sensor.bias_mps`` changes the array steering/angle-estimation state and the
    zero-thickness processing boundary. It intentionally does not rewrite
    ``processing_profile`` finite-thickness layers.
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
    array_tilt = _require_downward_principal_plane_angle(
        principal_plane_array_tilt_rad,
        name="principal_plane_array_tilt_rad",
    )

    transmit_truth = compare_principal_plane_steering_with_truth(
        configured_angle_rad=configured_angle,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
        true_local_sound_speed_mps=true_local_c,
    )
    physical_array_angle = float(transmit_truth.physical_angle_rad)
    physical_profile_angle = _require_downward_principal_plane_angle(
        array_tilt + physical_array_angle,
        name="physical launch angle in profile frame",
    )
    true_path = trace_layered_ray_to_depth(
        profile=true_profile,
        launch_angle_from_vertical_rad=abs(physical_profile_angle),
        target_depth_m=target_depth,
        start_depth_m=start_depth,
    )

    if abs(physical_profile_angle) <= 1e-15:
        signed_horizontal = 0.0
    else:
        signed_horizontal = -copysign(float(true_path.horizontal_distance_m), physical_profile_angle)

    truth_point = Vector3(
        x=float(sensor_pose.position.x),
        y=float(sensor_pose.position.y) + signed_horizontal,
        z=float(terrain.depth),
    )
    true_twtt = 2.0 * float(true_path.travel_time_seconds)

    # Reciprocal arrival is expressed in the array frame before RX angle mapping.
    receive_estimate = estimate_principal_plane_receive_angle(
        physical_arrival_angle_rad=physical_array_angle,
        true_local_sound_speed_mps=true_local_c,
        sound_speed_used_by_sonar_mps=float(used.sound_speed_mps),
    )
    estimated_profile_angle = _require_downward_principal_plane_angle(
        array_tilt + float(receive_estimate.estimated_angle_rad),
        name="estimated receive angle in profile frame",
    )
    observation = DetectedAcousticObservation(
        parent_beam_index=0,
        detection_method="phase_zero_crossing",
        twtt_seconds=true_twtt,
        detected_across_track_angle_rad=estimated_profile_angle,
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
        principal_plane_array_tilt_rad=array_tilt,
        sensor_measurement=measurement,
        sound_speed_used_by_sonar=used,
        transmit_truth=transmit_truth,
        physical_launch_angle_profile_frame_rad=physical_profile_angle,
        true_ray_path=true_path,
        truth_bottom_point=truth_point,
        true_twtt_seconds=true_twtt,
        receive_angle_estimate=receive_estimate,
        estimated_receive_angle_profile_frame_rad=estimated_profile_angle,
        observation=observation,
        calculated_sounding=calculated,
        sounding_error=error,
        sounding_error_norm_m=error_norm,
    )


def run_layered_sound_speed_error_isolation_matrix(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angle_rad: float,
    true_profile: LayeredSoundSpeedProfile,
    perturbed_processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
    transducer_sensor_bias_mps: float,
    principal_plane_array_tilt_rad: float = 0.0,
) -> LayeredSoundSpeedErrorIsolationMatrix:
    """Run controlled correct/incorrect transducer-value and profile combinations."""

    common = dict(
        sensor_pose=sensor_pose,
        terrain=terrain,
        configured_across_track_angle_rad=configured_across_track_angle_rad,
        true_profile=true_profile,
        profile_start_depth_m=profile_start_depth_m,
        principal_plane_array_tilt_rad=principal_plane_array_tilt_rad,
    )
    ideal_sensor = SoundSpeedSensorAtTransducer()
    biased_sensor = SoundSpeedSensorAtTransducer(bias_mps=float(transducer_sensor_bias_mps))

    reference = run_layered_sound_speed_reference_experiment(
        processing_profile=true_profile,
        sensor=ideal_sensor,
        **common,
    )
    transducer_only = run_layered_sound_speed_reference_experiment(
        processing_profile=true_profile,
        sensor=biased_sensor,
        **common,
    )
    profile_only = run_layered_sound_speed_reference_experiment(
        processing_profile=perturbed_processing_profile,
        sensor=ideal_sensor,
        **common,
    )
    combined = run_layered_sound_speed_reference_experiment(
        processing_profile=perturbed_processing_profile,
        sensor=biased_sensor,
        **common,
    )

    return LayeredSoundSpeedErrorIsolationMatrix(
        transducer_sensor_bias_mps=float(transducer_sensor_bias_mps),
        principal_plane_array_tilt_rad=float(principal_plane_array_tilt_rad),
        reference=reference,
        transducer_only=transducer_only,
        profile_only=profile_only,
        combined=combined,
    )

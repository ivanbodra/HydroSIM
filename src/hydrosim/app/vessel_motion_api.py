"""Application adapter for the PED-D12 vessel-motion learner slice.

The adapter converts learner-facing units to HydroSIM's canonical motion models and
serializes sampled Truth poses plus the Scientific Lead's reference beam/terrain
consequences. Beam generation, rigid rotations, and terrain intersection remain
owned by the canonical geometry Core.
"""

from __future__ import annotations

from math import degrees, hypot, radians
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hydrosim.geometry.arrays import TransducerArray
from hydrosim.geometry.beams import generate_ideal_fan_degrees
from hydrosim.geometry.models import Attitude, Vector3
from hydrosim.geometry.rotations import rotation_matrix_from_rpy
from hydrosim.geometry.terrain import FlatTerrain
from hydrosim.geometry.transforms import transform_vector
from hydrosim.motion.models import HarmonicSignal, StraightLineTrajectory, VesselMotionModel
from hydrosim.timing import SimulationTime


class D12AngularHarmonicRequest(BaseModel):
    """Configured angular harmonic expressed in learner-facing degrees."""

    model_config = ConfigDict(extra="forbid")

    amplitude_deg: float = 0.0
    period_seconds: float = Field(default=5.0, gt=0.0)
    phase_deg: float = 0.0


class D12HeaveHarmonicRequest(BaseModel):
    """Configured positive-Up heave harmonic."""

    model_config = ConfigDict(extra="forbid")

    amplitude_m: float = 0.0
    period_seconds: float = Field(default=5.0, gt=0.0)
    phase_deg: float = 0.0


class D12VesselMotionRequest(BaseModel):
    """Learner-configurable subset supported by the canonical motion core."""

    model_config = ConfigDict(extra="forbid")

    heading_deg: float = 0.0
    speed_mps: float = Field(default=0.0, ge=0.0)
    start_north_m: float = 0.0
    start_east_m: float = 0.0
    start_down_m: float = 0.0
    duration_seconds: float = Field(default=10.0, gt=0.0)
    sample_count: int = Field(default=101, ge=2, le=4096)
    terrain_depth_m: float = Field(default=30.0)
    half_swath_angle_deg: float = Field(default=60.0, gt=0.0, lt=90.0)
    roll: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    pitch: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    yaw_deviation: D12AngularHarmonicRequest = D12AngularHarmonicRequest()
    heave: D12HeaveHarmonicRequest = D12HeaveHarmonicRequest()


class D12Vector(BaseModel):
    model_config = ConfigDict(frozen=True)

    north_m: float
    east_m: float
    down_m: float


class D12BeamConsequence(BaseModel):
    """Reference/moved ideal beam geometry for one explicit beam identity."""

    model_config = ConfigDict(frozen=True)

    beam: Literal["port", "nadir", "starboard"]
    steering_angle_deg: float
    reference_direction: D12Vector
    moved_direction: D12Vector
    reference_intersection: D12Vector | None
    moved_intersection: D12Vector | None
    displacement: D12Vector | None


class D12SwathConsequence(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference_width_m: float | None
    moved_width_m: float | None
    width_change_m: float | None


class D12MotionConsequenceSample(BaseModel):
    model_config = ConfigDict(frozen=True)

    time_seconds: float
    beams: tuple[D12BeamConsequence, ...]
    swath: D12SwathConsequence


class D12VesselMotionSample(BaseModel):
    model_config = ConfigDict(frozen=True)

    time_seconds: float
    north_m: float
    east_m: float
    down_m: float
    roll_deg: float
    pitch_deg: float
    heading_deg: float
    yaw_deviation_deg: float
    heave_up_m: float


class D12VesselMotionResponse(BaseModel):
    """Render-ready sampled Truth poses and geometric motion consequences."""

    model_config = ConfigDict(frozen=True)

    samples: tuple[D12VesselMotionSample, ...]
    consequences: tuple[D12MotionConsequenceSample, ...]
    metadata: dict[str, str]


def _angular_signal(request: D12AngularHarmonicRequest) -> HarmonicSignal:
    return HarmonicSignal(
        amplitude=radians(request.amplitude_deg),
        period_seconds=request.period_seconds,
        phase_rad=radians(request.phase_deg),
    )


def _heave_signal(request: D12HeaveHarmonicRequest) -> HarmonicSignal:
    return HarmonicSignal(
        amplitude=request.amplitude_m,
        period_seconds=request.period_seconds,
        phase_rad=radians(request.phase_deg),
    )


def _zero_signal(period_seconds: float = 1.0) -> HarmonicSignal:
    return HarmonicSignal(amplitude=0.0, period_seconds=period_seconds, phase_rad=0.0)


def _render_vector(vector: Vector3) -> D12Vector:
    return D12Vector(north_m=float(vector.x), east_m=float(vector.y), down_m=float(vector.z))


def _difference(moved: Vector3, reference: Vector3) -> D12Vector:
    return D12Vector(
        north_m=float(moved.x - reference.x),
        east_m=float(moved.y - reference.y),
        down_m=float(moved.z - reference.z),
    )


def _swath_width(port: Vector3 | None, starboard: Vector3 | None) -> float | None:
    if port is None or starboard is None:
        return None
    return hypot(float(port.x - starboard.x), float(port.y - starboard.y))


def prepare_d12_vessel_motion_response(
    request: D12VesselMotionRequest,
) -> D12VesselMotionResponse:
    """Sample canonical motion and paired no-motion ideal beam consequences."""

    heading_rad = radians(request.heading_deg)
    trajectory = StraightLineTrajectory(
        start_time=SimulationTime(seconds=0.0),
        start_position=Vector3(
            x=request.start_north_m,
            y=request.start_east_m,
            z=request.start_down_m,
        ),
        speed_mps=request.speed_mps,
        heading_rad=heading_rad,
        frame="N",
    )
    model = VesselMotionModel(
        trajectory=trajectory,
        roll=_angular_signal(request.roll),
        pitch=_angular_signal(request.pitch),
        yaw_deviation=_angular_signal(request.yaw_deviation),
        heave=_heave_signal(request.heave),
    )
    reference_model = VesselMotionModel(
        trajectory=trajectory,
        roll=_zero_signal(),
        pitch=_zero_signal(),
        yaw_deviation=_zero_signal(),
        heave=_zero_signal(),
    )

    reference_array = TransducerArray(
        name="PED-D12 reference array",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.01,
        element_transverse_size=0.01,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )
    fan = generate_ideal_fan_degrees(
        reference_array,
        beam_count=3,
        total_swath_angle_degrees=2.0 * request.half_swath_angle_deg,
    )
    terrain = FlatTerrain(depth=request.terrain_depth_m)
    beam_names: tuple[Literal["port", "nadir", "starboard"], ...] = (
        "port",
        "nadir",
        "starboard",
    )

    step = request.duration_seconds / float(request.sample_count - 1)
    samples: list[D12VesselMotionSample] = []
    consequences: list[D12MotionConsequenceSample] = []
    for index in range(request.sample_count):
        time_seconds = index * step
        time = SimulationTime(seconds=time_seconds)
        pose = model.pose_at(time)
        reference_pose = reference_model.pose_at(time)
        yaw_deviation_rad = float(pose.attitude.yaw) - heading_rad
        heave_up_m = float(reference_pose.position.z - pose.position.z)
        samples.append(
            D12VesselMotionSample(
                time_seconds=time_seconds,
                north_m=float(pose.position.x),
                east_m=float(pose.position.y),
                down_m=float(pose.position.z),
                roll_deg=degrees(float(pose.attitude.roll)),
                pitch_deg=degrees(float(pose.attitude.pitch)),
                heading_deg=degrees(float(pose.attitude.yaw)),
                yaw_deviation_deg=degrees(yaw_deviation_rad),
                heave_up_m=heave_up_m,
            )
        )

        moved_rotation = rotation_matrix_from_rpy(pose.attitude)
        reference_rotation = rotation_matrix_from_rpy(reference_pose.attitude)
        beam_outputs: list[D12BeamConsequence] = []
        reference_points: dict[str, Vector3 | None] = {}
        moved_points: dict[str, Vector3 | None] = {}
        for name, beam in zip(beam_names, fan.beams, strict=True):
            moved_direction = transform_vector(beam.direction_sensor_frame, moved_rotation)
            reference_direction = transform_vector(beam.direction_sensor_frame, reference_rotation)
            moved_hit = terrain.intersect_ray(pose.position, moved_direction)
            reference_hit = terrain.intersect_ray(reference_pose.position, reference_direction)
            moved_point = moved_hit.point if moved_hit.valid else None
            reference_point = reference_hit.point if reference_hit.valid else None
            moved_points[name] = moved_point
            reference_points[name] = reference_point
            displacement = None
            if moved_point is not None and reference_point is not None:
                displacement = _difference(moved_point, reference_point)
            beam_outputs.append(
                D12BeamConsequence(
                    beam=name,
                    steering_angle_deg=degrees(float(beam.definition.across_track_angle)),
                    reference_direction=_render_vector(reference_direction),
                    moved_direction=_render_vector(moved_direction),
                    reference_intersection=(
                        _render_vector(reference_point) if reference_point is not None else None
                    ),
                    moved_intersection=_render_vector(moved_point) if moved_point is not None else None,
                    displacement=displacement,
                )
            )

        reference_width = _swath_width(reference_points["port"], reference_points["starboard"])
        moved_width = _swath_width(moved_points["port"], moved_points["starboard"])
        width_change = None
        if reference_width is not None and moved_width is not None:
            width_change = moved_width - reference_width
        consequences.append(
            D12MotionConsequenceSample(
                time_seconds=time_seconds,
                beams=tuple(beam_outputs),
                swath=D12SwathConsequence(
                    reference_width_m=reference_width,
                    moved_width_m=moved_width,
                    width_change_m=width_change,
                ),
            )
        )

    return D12VesselMotionResponse(
        samples=tuple(samples),
        consequences=tuple(consequences),
        metadata={
            "frame": "N (North-East-Down)",
            "heading_convention": "degrees clockwise from North",
            "heave_convention": "positive Up; subtracted from navigation Down coordinate",
            "beam_convention": "positive steering to Port; three-beam symmetric ideal fan",
            "terrain": "horizontal FlatTerrain at configured Down coordinate",
            "reference": "same nominal trajectory/heading with roll=pitch=yaw_deviation=heave=0",
            "state_semantics": "Configured Truth motion; Derived reference/moved geometry",
            "fidelity": "canonical rigid transforms, ideal beam centres, and plane intersection",
        },
    )

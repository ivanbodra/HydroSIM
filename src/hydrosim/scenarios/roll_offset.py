"""Pedagogical roll-alignment demonstration scenario.

This module loads the YAML scenario used by Issue #8 and executes the deterministic
geometric pipeline implemented in ``hydrosim.geometry``. The v0.1 demonstration
contains no stochastic error source yet; ``random_seed`` is nevertheless preserved
in the scenario/result contract so later noise models can remain reproducible.
"""

from __future__ import annotations

from math import sqrt
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, PositiveInt

from hydrosim.geometry import (
    Attitude,
    FlatTerrain,
    Pose,
    SoundingComparison,
    TransducerArray,
    Vector3,
    compare_true_and_configured_sounding,
    generate_ideal_fan_degrees,
)


class ScenarioIdentity(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    title: str = Field(min_length=1)


class TerrainConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    depth_m: FiniteFloat


class EnvironmentConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    terrain: TerrainConfig


class PlatformConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    speed_mps: FiniteFloat
    heading_deg: FiniteFloat


class SonarConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    number_of_beams: PositiveInt
    swath_angle_deg: FiniteFloat = Field(gt=0.0)


class AlignmentConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    roll_deg: FiniteFloat
    pitch_deg: FiniteFloat
    yaw_deg: FiniteFloat

    def as_attitude(self) -> Attitude:
        return Attitude.from_degrees(
            roll=float(self.roll_deg),
            pitch=float(self.pitch_deg),
            yaw=float(self.yaw_deg),
        )


class AlignmentStateConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    transducer_alignment: AlignmentConfig


class RollOffsetScenarioConfig(BaseModel):
    """Validated configuration for the first HydroSIM pedagogical scenario."""

    model_config = ConfigDict(frozen=True)

    scenario: ScenarioIdentity
    random_seed: int
    environment: EnvironmentConfig
    platform: PlatformConfig
    sonar: SonarConfig
    truth: AlignmentStateConfig
    configured: AlignmentStateConfig
    expected_learning_outcomes: tuple[str, ...] = ()


class RollOffsetSummary(BaseModel):
    """Across-swath residual statistics for the roll demonstration."""

    model_config = ConfigDict(frozen=True)

    beam_count: PositiveInt
    max_horizontal_error: FiniteFloat
    mean_horizontal_error: FiniteFloat
    rms_horizontal_error: FiniteFloat
    max_abs_vertical_error: FiniteFloat
    mean_vertical_error: FiniteFloat
    rms_vertical_error: FiniteFloat
    max_error_magnitude: FiniteFloat


class RollOffsetResult(BaseModel):
    """Complete deterministic result of the roll-offset scenario."""

    model_config = ConfigDict(frozen=True)

    scenario_id: str
    scenario_version: str
    random_seed: int
    soundings: tuple[SoundingComparison, ...]
    summary: RollOffsetSummary


def load_roll_offset_scenario(path: str | Path) -> RollOffsetScenarioConfig:
    """Load and validate a roll-offset scenario YAML file."""

    with Path(path).open("r", encoding="utf-8") as stream:
        payload = yaml.safe_load(stream)
    if not isinstance(payload, dict):
        raise ValueError("scenario YAML must contain a mapping at the root")
    return RollOffsetScenarioConfig.model_validate(payload)


def _summary(soundings: tuple[SoundingComparison, ...]) -> RollOffsetSummary:
    horizontal = [float(item.horizontal_error) for item in soundings]
    vertical = [float(item.vertical_error) for item in soundings]
    magnitude = [float(item.error_magnitude) for item in soundings]
    n = len(soundings)
    if n == 0:
        raise ValueError("scenario produced no soundings")

    return RollOffsetSummary(
        beam_count=n,
        max_horizontal_error=max(horizontal),
        mean_horizontal_error=sum(horizontal) / n,
        rms_horizontal_error=sqrt(sum(value * value for value in horizontal) / n),
        max_abs_vertical_error=max(abs(value) for value in vertical),
        mean_vertical_error=sum(vertical) / n,
        rms_vertical_error=sqrt(sum(value * value for value in vertical) / n),
        max_error_magnitude=max(magnitude),
    )


def run_roll_offset_scenario(config: RollOffsetScenarioConfig) -> RollOffsetResult:
    """Execute the deterministic flat-bottom roll-alignment demonstration."""

    if config.environment.terrain.type != "flat":
        raise ValueError("roll-offset v0.1 supports only flat terrain")
    if config.sonar.type != "ideal_multibeam":
        raise ValueError("roll-offset v0.1 supports only ideal_multibeam sonar")

    terrain = FlatTerrain(depth=float(config.environment.terrain.depth_m))
    vessel_pose = Pose(
        position=Vector3(x=0.0, y=0.0, z=0.0),
        attitude=Attitude.from_degrees(
            roll=0.0,
            pitch=0.0,
            yaw=float(config.platform.heading_deg),
        ),
        frame="N",
    )

    # Physical dimensions are intentionally neutral in v0.1: ideal fan steering is
    # independent of array aperture until beamforming/array-factor physics is added.
    array = TransducerArray(
        name="demo_rx",
        role="rx",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.01,
        element_transverse_size=0.01,
    )
    fan = generate_ideal_fan_degrees(
        array,
        beam_count=int(config.sonar.number_of_beams),
        total_swath_angle_degrees=float(config.sonar.swath_angle_deg),
        role="rx",
    )

    true_alignment = config.truth.transducer_alignment.as_attitude()
    configured_alignment = config.configured.transducer_alignment.as_attitude()
    lever_arm = Vector3(x=0.0, y=0.0, z=0.0)

    soundings = tuple(
        compare_true_and_configured_sounding(
            vessel_truth_pose=vessel_pose,
            lever_arm_vrp_to_sensor=lever_arm,
            true_sensor_alignment=true_alignment,
            configured_sensor_alignment=configured_alignment,
            beam=beam,
            terrain=terrain,
            sensor_frame="T",
        )
        for beam in fan.beams
    )

    return RollOffsetResult(
        scenario_id=config.scenario.id,
        scenario_version=config.scenario.version,
        random_seed=config.random_seed,
        soundings=soundings,
        summary=_summary(soundings),
    )

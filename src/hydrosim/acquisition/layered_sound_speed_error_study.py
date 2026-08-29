"""Parameterized orchestration for the layered sound-speed A/B/C/D matrix.

This module adds no new acoustic physics. It repeats the existing controlled matrix
across explicitly supplied across-track angles and transducer-sensor biases so later
asymmetry studies can compare cases without duplicating the four-case construction.
"""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, FiniteFloat

from hydrosim.geometry import FlatTerrain, Pose

from .layered_propagation import LayeredSoundSpeedProfile
from .layered_sound_speed_reference_experiment import (
    LayeredSoundSpeedErrorIsolationMatrix,
    run_layered_sound_speed_error_isolation_matrix,
)


class LayeredSoundSpeedErrorIsolationStudyCase(BaseModel):
    """One A/B/C/D matrix associated with explicit study coordinates."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angle_rad: FiniteFloat
    transducer_sensor_bias_mps: FiniteFloat
    matrix: LayeredSoundSpeedErrorIsolationMatrix


class LayeredSoundSpeedErrorIsolationStudy(BaseModel):
    """Deterministic Cartesian study of angle and transducer-sensor bias."""

    model_config = ConfigDict(frozen=True)

    configured_across_track_angles_rad: tuple[FiniteFloat, ...]
    transducer_sensor_biases_mps: tuple[FiniteFloat, ...]
    cases: tuple[LayeredSoundSpeedErrorIsolationStudyCase, ...]


def run_layered_sound_speed_error_isolation_study(
    *,
    sensor_pose: Pose,
    terrain: FlatTerrain,
    configured_across_track_angles_rad: Iterable[float],
    transducer_sensor_biases_mps: Iterable[float],
    true_profile: LayeredSoundSpeedProfile,
    perturbed_processing_profile: LayeredSoundSpeedProfile,
    profile_start_depth_m: float,
) -> LayeredSoundSpeedErrorIsolationStudy:
    """Repeat the existing A/B/C/D matrix over a Cartesian parameter grid.

    Angle is the outer loop and sensor bias is the inner loop. Inputs are materialized
    once to make iteration deterministic even when generators are supplied.
    """

    angles = tuple(float(value) for value in configured_across_track_angles_rad)
    biases = tuple(float(value) for value in transducer_sensor_biases_mps)
    if not angles:
        raise ValueError("configured_across_track_angles_rad must not be empty")
    if not biases:
        raise ValueError("transducer_sensor_biases_mps must not be empty")

    cases = []
    for angle in angles:
        for bias in biases:
            matrix = run_layered_sound_speed_error_isolation_matrix(
                sensor_pose=sensor_pose,
                terrain=terrain,
                configured_across_track_angle_rad=angle,
                true_profile=true_profile,
                perturbed_processing_profile=perturbed_processing_profile,
                profile_start_depth_m=profile_start_depth_m,
                transducer_sensor_bias_mps=bias,
            )
            cases.append(
                LayeredSoundSpeedErrorIsolationStudyCase(
                    configured_across_track_angle_rad=angle,
                    transducer_sensor_bias_mps=bias,
                    matrix=matrix,
                )
            )

    return LayeredSoundSpeedErrorIsolationStudy(
        configured_across_track_angles_rad=angles,
        transducer_sensor_biases_mps=biases,
        cases=tuple(cases),
    )

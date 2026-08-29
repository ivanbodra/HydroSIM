"""Detected acoustic observations downstream of bottom detection.

A bottom detector produces observables, not a georeferenced sounding point.  The
primary observable is two-way travel time (TWTT); a phase or beam detector may also
provide an arrival/steering angle.  Converting those observations into range or a
Cartesian sounding requires an explicit propagation/reconstruction model.

The constant-sound-speed helper in this module is intentionally narrow.  Under a
stationary reciprocal straight-ray model,

    one_way_range = c * TWTT / 2.

That conversion must not be used as a silent substitute for layered/refraction
reconstruction, where acoustic path length and horizontal/depth coordinates must be
obtained from the configured propagation model.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .bottom_detection import BottomDetection, DetectionMethod


class DetectedAcousticObservation(BaseModel):
    """Measurement-space result passed from detection to reconstruction."""

    model_config = ConfigDict(frozen=True)

    parent_beam_index: int | None = Field(default=None, ge=0)
    detection_index: int = Field(default=0, ge=0)
    detection_method: DetectionMethod
    twtt_seconds: FiniteFloat = Field(ge=0.0)
    detected_across_track_angle_rad: FiniteFloat | None = None
    quality: FiniteFloat | None = Field(default=None, ge=0.0, le=1.0)


class ConstantSoundSpeedRangeObservation(BaseModel):
    """Explicit straight-ray interpretation of a detected TWTT."""

    model_config = ConfigDict(frozen=True)

    observation: DetectedAcousticObservation
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    two_way_acoustic_path_length_m: FiniteFloat = Field(ge=0.0)
    reciprocal_one_way_range_m: FiniteFloat = Field(ge=0.0)
    propagation_assumption: str = "stationary_reciprocal_constant_sound_speed"


def acoustic_observation_from_detection(detection: BottomDetection) -> DetectedAcousticObservation:
    """Strip processing-specific detector details to the reconstruction observables."""

    return DetectedAcousticObservation(
        parent_beam_index=detection.parent_beam_index,
        detection_index=detection.detection_index,
        detection_method=detection.detection_method,
        twtt_seconds=detection.twtt_seconds,
        detected_across_track_angle_rad=detection.detected_across_track_angle_rad,
        quality=detection.quality,
    )


def interpret_observation_constant_sound_speed(
    observation: DetectedAcousticObservation,
    *,
    sound_speed_mps: float,
) -> ConstantSoundSpeedRangeObservation:
    """Interpret TWTT as reciprocal straight-ray range under explicit constant c.

    This helper is valid only for the named reference assumption.  It deliberately
    does not create a Cartesian point because across-track angle alone does not
    define the full 3-D ray when transmit along-track steering may be non-zero.
    """

    c = float(sound_speed_mps)
    if c <= 0.0:
        raise ValueError("sound_speed_mps must be positive")
    two_way_path = c * float(observation.twtt_seconds)
    return ConstantSoundSpeedRangeObservation(
        observation=observation,
        sound_speed_mps=c,
        two_way_acoustic_path_length_m=two_way_path,
        reciprocal_one_way_range_m=0.5 * two_way_path,
    )

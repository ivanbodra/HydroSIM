"""Processing representation of sound speed at the transducer/profile boundary.

Scientific basis and source traceability:
    docs/science/sound_speed_at_transducer.md

The value used by the sonar at the array and the finite-thickness water-column
profile are distinct states. Some real systems can insert the transducer sensor value
as the first profile value; HydroSIM must not emulate that by overwriting an entire
constant-c layer, because that would spread a point/boundary observation through a
finite depth interval.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat

from .sound_speed_processing import SoundSpeedAtTransducerUse

if TYPE_CHECKING:
    from .layered_propagation import LayeredSoundSpeedProfile


ProfileBoundarySource = Literal["processing_profile", "sound_speed_at_transducer"]


class SoundSpeedProfileBoundary(BaseModel):
    """Explicit sound speed at the ray-tracing start boundary."""

    model_config = ConfigDict(frozen=True)

    depth_m: FiniteFloat = Field(ge=0.0)
    sound_speed_mps: FiniteFloat = Field(gt=0.0)
    source: ProfileBoundarySource


def profile_boundary_from_profile(
    *, profile: LayeredSoundSpeedProfile, depth_m: float
) -> SoundSpeedProfileBoundary:
    """Use the configured profile value at the ray-tracing start depth."""

    depth = float(depth_m)
    c = float(profile.layer_at_depth(depth).sound_speed_mps)
    return SoundSpeedProfileBoundary(depth_m=depth, sound_speed_mps=c, source="processing_profile")


def profile_boundary_from_sound_speed_at_transducer(
    *, sound_speed_at_transducer: SoundSpeedAtTransducerUse, depth_m: float
) -> SoundSpeedProfileBoundary:
    """Use sonar processing state as a zero-thickness start-boundary value.

    This does not modify the first finite-thickness layer of the supplied water-column
    profile. It exists to model systems/workflows in which the transducer value is
    treated as the first ray-bending value while preserving HydroSIM's numerical
    distinction between a boundary sample and a layer.
    """

    return SoundSpeedProfileBoundary(
        depth_m=float(depth_m),
        sound_speed_mps=float(sound_speed_at_transducer.sound_speed_mps),
        source="sound_speed_at_transducer",
    )

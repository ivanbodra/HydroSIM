"""Ideal geometric beams and multibeam fan generation for HydroSIM.

This module is deliberately downstream of physical transducer-array geometry.
The v0.1 fan model uses explicit steering angles but does not yet derive beamwidth,
sidelobes, grating lobes, or steering limits from array factor / wavelength physics.

Across-track angle convention follows HydroSIM conventions: zero is the array-frame
+Z normal, positive angles steer toward Port (-Y), and negative angles steer toward
Starboard (+Y). With column vectors and active right-hand rotations, this is exactly
an active +X rotation applied to the +Z normal.
"""

from __future__ import annotations

from math import radians
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, PositiveInt

from .arrays import TransducerArray
from .models import Vector3
from .rotations import rotate_vector, rotation_matrix_from_rpy, rotation_x


class BeamDefinition(BaseModel):
    """One ideal beam steering definition.

    ``across_track_angle`` is stored in radians. Positive is Port; negative is
    Starboard. ``role`` keeps TX/RX semantics separable for later Mills Cross and
    physically derived beamforming models.
    """

    model_config = ConfigDict(frozen=True)

    index: int = Field(ge=0)
    across_track_angle: FiniteFloat
    role: Literal["tx", "rx"] = "rx"
    array_name: str = Field(min_length=1)


class BeamRay(BaseModel):
    """Ideal beam ray in array-local and containing sensor frames."""

    model_config = ConfigDict(frozen=True)

    definition: BeamDefinition
    origin_array_frame: Vector3 = Vector3(x=0.0, y=0.0, z=0.0)
    direction_array_frame: Vector3
    direction_sensor_frame: Vector3


class IdealFan(BaseModel):
    """Deterministic ideal equal-angle multibeam fan."""

    model_config = ConfigDict(frozen=True)

    array_name: str
    beam_count: PositiveInt
    total_swath_angle: FiniteFloat = Field(ge=0.0)
    spacing_strategy: Literal["equal_angle"] = "equal_angle"
    role: Literal["tx", "rx"] = "rx"
    beams: tuple[BeamRay, ...]

    @property
    def has_nadir_beam(self) -> bool:
        """Return True when the fan contains an explicit zero-angle beam."""

        return any(abs(float(beam.definition.across_track_angle)) <= 1e-15 for beam in self.beams)


def _equal_angle_values(beam_count: int, total_swath_angle: float) -> tuple[float, ...]:
    """Return symmetric steering angles spanning the requested total swath.

    For one beam, the only meaningful deterministic beam is nadir (0 rad).
    For odd beam counts > 1, nadir is explicitly present. For even beam counts,
    beams remain symmetric about nadir but no zero-angle beam exists.
    """

    if beam_count < 1:
        raise ValueError("beam_count must be >= 1")
    if total_swath_angle < 0.0:
        raise ValueError("total_swath_angle must be >= 0")

    if beam_count == 1:
        return (0.0,)

    half = 0.5 * float(total_swath_angle)
    step = float(total_swath_angle) / (beam_count - 1)
    return tuple(half - i * step for i in range(beam_count))


def generate_ideal_fan(
    array: TransducerArray,
    *,
    beam_count: int,
    total_swath_angle: float,
    spacing_strategy: Literal["equal_angle"] = "equal_angle",
    role: Literal["tx", "rx"] = "rx",
) -> IdealFan:
    """Generate a deterministic ideal fan referenced to a physical array.

    The array's physical geometry is carried as the upstream source model, while
    v0.1 steering angles are still idealized. Array dimensions and element spacing
    therefore do not alter the equal-angle fan yet. The fixed array orientation
    *does* rotate each ray from array-local coordinates into the sensor frame.
    """

    if spacing_strategy != "equal_angle":
        raise ValueError("only equal_angle spacing is implemented")

    angles = _equal_angle_values(beam_count, total_swath_angle)
    array_to_sensor = rotation_matrix_from_rpy(array.orientation)
    normal = Vector3(x=0.0, y=0.0, z=1.0)

    rays: list[BeamRay] = []
    for index, angle in enumerate(angles):
        direction_array = rotate_vector(rotation_x(angle), normal)
        direction_sensor = rotate_vector(array_to_sensor, direction_array)
        definition = BeamDefinition(
            index=index,
            across_track_angle=angle,
            role=role,
            array_name=array.name,
        )
        rays.append(
            BeamRay(
                definition=definition,
                direction_array_frame=direction_array,
                direction_sensor_frame=direction_sensor,
            )
        )

    return IdealFan(
        array_name=array.name,
        beam_count=beam_count,
        total_swath_angle=total_swath_angle,
        spacing_strategy=spacing_strategy,
        role=role,
        beams=tuple(rays),
    )


def generate_ideal_fan_degrees(
    array: TransducerArray,
    *,
    beam_count: int,
    total_swath_angle_degrees: float,
    spacing_strategy: Literal["equal_angle"] = "equal_angle",
    role: Literal["tx", "rx"] = "rx",
) -> IdealFan:
    """Convenience wrapper accepting total swath in degrees."""

    return generate_ideal_fan(
        array,
        beam_count=beam_count,
        total_swath_angle=radians(total_swath_angle_degrees),
        spacing_strategy=spacing_strategy,
        role=role,
    )

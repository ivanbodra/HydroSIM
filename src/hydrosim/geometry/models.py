"""Core typed geometry data models for HydroSIM.

The models in this module deliberately contain only Cartesian geometry semantics.
CRS, hydrographic vertical datum, water level, and other survey-product metadata
belong to higher-level models.
"""

from __future__ import annotations

from math import degrees, isclose, radians

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, field_validator


class Vector3(BaseModel):
    """A finite three-component Cartesian vector.

    Length-valued uses of ``Vector3`` are expressed in metres. The class itself
    does not carry a coordinate frame; the owning object supplies that semantic
    context.
    """

    model_config = ConfigDict(frozen=True)

    x: FiniteFloat
    y: FiniteFloat
    z: FiniteFloat

    def is_close(self, other: "Vector3", *, atol: float = 1e-9, rtol: float = 0.0) -> bool:
        """Return whether all components agree within the requested tolerance."""

        return (
            isclose(self.x, other.x, abs_tol=atol, rel_tol=rtol)
            and isclose(self.y, other.y, abs_tol=atol, rel_tol=rtol)
            and isclose(self.z, other.z, abs_tol=atol, rel_tol=rtol)
        )


class Attitude(BaseModel):
    """HydroSIM roll, pitch, and yaw attitude, stored internally in radians."""

    model_config = ConfigDict(frozen=True)

    roll: FiniteFloat
    pitch: FiniteFloat
    yaw: FiniteFloat

    @classmethod
    def from_degrees(cls, *, roll: float, pitch: float, yaw: float) -> "Attitude":
        """Construct an attitude from degree-valued inputs."""

        return cls(roll=radians(roll), pitch=radians(pitch), yaw=radians(yaw))

    def as_degrees(self) -> tuple[float, float, float]:
        """Return ``(roll, pitch, yaw)`` in degrees without changing storage."""

        return degrees(self.roll), degrees(self.pitch), degrees(self.yaw)

    def is_close(self, other: "Attitude", *, atol: float = 1e-12, rtol: float = 0.0) -> bool:
        """Return whether all attitude components agree within tolerance."""

        return (
            isclose(self.roll, other.roll, abs_tol=atol, rel_tol=rtol)
            and isclose(self.pitch, other.pitch, abs_tol=atol, rel_tol=rtol)
            and isclose(self.yaw, other.yaw, abs_tol=atol, rel_tol=rtol)
        )


class Pose(BaseModel):
    """Position and attitude expressed in an explicit Cartesian reference frame.

    ``frame`` identifies a HydroSIM Cartesian frame such as ``N``, ``B``, ``T``,
    or a future explicitly named local frame. It is not a CRS identifier and it
    does not define a vertical datum.
    """

    model_config = ConfigDict(frozen=True)

    position: Vector3
    attitude: Attitude
    frame: str = Field(min_length=1)

    @field_validator("frame")
    @classmethod
    def frame_must_not_be_blank(cls, value: str) -> str:
        """Reject empty or whitespace-only frame identifiers."""

        normalized = value.strip()
        if not normalized:
            raise ValueError("frame must not be blank")
        return normalized

    def is_close(
        self,
        other: "Pose",
        *,
        position_atol: float = 1e-9,
        attitude_atol: float = 1e-12,
    ) -> bool:
        """Compare two poses while requiring the same explicit reference frame."""

        return (
            self.frame == other.frame
            and self.position.is_close(other.position, atol=position_atol)
            and self.attitude.is_close(other.attitude, atol=attitude_atol)
        )

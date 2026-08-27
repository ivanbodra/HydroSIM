"""Deterministic terrain primitives and exact ray intersections for HydroSIM.

The initial geometry prototype uses infinite planes only. Coordinates are Cartesian
and follow the owning HydroSIM frame; in the common local NED frame, +Z is down.
Ray directions do not need to be unit length: they are normalized internally so
``slant_range`` is always the Euclidean distance from origin to intersection.
"""

from __future__ import annotations

from math import isfinite, sqrt

from pydantic import BaseModel, ConfigDict, FiniteFloat

from .models import Vector3

_EPS = 1e-12


class RayIntersection(BaseModel):
    """Result of intersecting a forward ray with terrain."""

    model_config = ConfigDict(frozen=True)

    point: Vector3 | None
    slant_range: FiniteFloat | None
    valid: bool


class PlaneTerrain(BaseModel):
    """Infinite plane defined by one point and a non-zero normal vector."""

    model_config = ConfigDict(frozen=True)

    point: Vector3
    normal: Vector3

    def model_post_init(self, __context: object) -> None:
        if _norm(self.normal) <= _EPS:
            raise ValueError("plane normal must be non-zero")

    def intersect_ray(self, origin: Vector3, direction: Vector3) -> RayIntersection:
        """Return the forward intersection of ``origin + t * direction`` with the plane.

        ``direction`` is normalized internally. Rays parallel to the plane, or whose
        mathematical plane intersection lies behind the ray origin, return
        ``valid=False`` with no point or range.
        """

        direction_unit = _unit(direction)
        denominator = _dot(self.normal, direction_unit)
        if abs(denominator) <= _EPS:
            return RayIntersection(point=None, slant_range=None, valid=False)

        origin_to_plane = Vector3(
            x=self.point.x - origin.x,
            y=self.point.y - origin.y,
            z=self.point.z - origin.z,
        )
        distance = _dot(self.normal, origin_to_plane) / denominator
        if distance < 0.0:
            return RayIntersection(point=None, slant_range=None, valid=False)

        intersection = Vector3(
            x=origin.x + distance * direction_unit.x,
            y=origin.y + distance * direction_unit.y,
            z=origin.z + distance * direction_unit.z,
        )
        return RayIntersection(point=intersection, slant_range=distance, valid=True)


class FlatTerrain(PlaneTerrain):
    """Horizontal infinite bottom at constant Cartesian ``z``.

    In HydroSIM local NED use, ``depth`` is positive down and therefore equals the
    plane's Z coordinate.
    """

    def __init__(self, *, depth: float) -> None:
        if not isfinite(depth):
            raise ValueError("depth must be finite")
        super().__init__(
            point=Vector3(x=0.0, y=0.0, z=depth),
            normal=Vector3(x=0.0, y=0.0, z=1.0),
        )

    @property
    def depth(self) -> float:
        """Return the constant Z/depth of the flat terrain."""

        return float(self.point.z)


def _dot(a: Vector3, b: Vector3) -> float:
    return float(a.x * b.x + a.y * b.y + a.z * b.z)


def _norm(vector: Vector3) -> float:
    return sqrt(_dot(vector, vector))


def _unit(vector: Vector3) -> Vector3:
    length = _norm(vector)
    if length <= _EPS:
        raise ValueError("ray direction must be non-zero")
    return Vector3(x=vector.x / length, y=vector.y / length, z=vector.z / length)

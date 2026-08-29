"""Physical transducer-array geometry for HydroSIM.

This module represents the physical placement, size, and fixed installation
orientation of transducer elements. It deliberately does not implement
beamforming weights, phase steering, acoustic frequency, wavelength, or
beam-pattern physics. Those belong to downstream models.

Array-local coordinates follow the transducer/sensor Cartesian convention:
+X longitudinal/forward, +Y transverse/starboard, +Z down. A centred regular
layout places the geometric centre of the element grid at the array origin.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, PositiveInt, model_validator

from .models import Attitude, Vector3
from .rotations import rotate_vector, rotation_matrix_from_rpy


class ArrayElement(BaseModel):
    """One physical element in a regular transducer array.

    ``position`` is the element-centre position in the array-local frame.
    Element dimensions are physical face dimensions in metres.
    """

    model_config = ConfigDict(frozen=True)

    index_x: int = Field(ge=0)
    index_y: int = Field(ge=0)
    position: Vector3
    longitudinal_size: FiniteFloat = Field(gt=0.0)
    transverse_size: FiniteFloat = Field(gt=0.0)


class TransducerArray(BaseModel):
    """Regular 1D or rectangular 2D physical transducer array.

    A 1D array is represented by setting one element count to one. Spacing on
    an axis with a single element may be zero because no inter-element spacing
    exists on that axis. For axes with more than one element, spacing must be
    strictly positive.

    ``orientation`` defines the fixed array-to-sensor rotation ``R_SA`` using
    HydroSIM RPY conventions. Therefore a vector expressed in array frame ``A``
    is expressed in the containing sensor frame ``S`` as

        v_S = R_SA @ v_A

    and the inverse component transform is

        v_A = R_SA.T @ v_S.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    role: Literal["tx", "rx", "txrx"] = "txrx"
    n_x: PositiveInt
    n_y: PositiveInt
    d_x: FiniteFloat = Field(ge=0.0)
    d_y: FiniteFloat = Field(ge=0.0)
    element_longitudinal_size: FiniteFloat = Field(gt=0.0)
    element_transverse_size: FiniteFloat = Field(gt=0.0)
    origin_convention: Literal["center"] = "center"
    orientation: Attitude = Attitude(roll=0.0, pitch=0.0, yaw=0.0)

    @model_validator(mode="after")
    def validate_spacing(self) -> "TransducerArray":
        """Require positive spacing on axes containing multiple elements."""

        if self.n_x > 1 and self.d_x <= 0.0:
            raise ValueError("d_x must be > 0 when n_x > 1")
        if self.n_y > 1 and self.d_y <= 0.0:
            raise ValueError("d_y must be > 0 when n_y > 1")
        return self

    @property
    def aperture_longitudinal(self) -> float:
        """Physical longitudinal extent of the complete array in metres."""

        return (self.n_x - 1) * float(self.d_x) + float(self.element_longitudinal_size)

    @property
    def aperture_transverse(self) -> float:
        """Physical transverse extent of the complete array in metres."""

        return (self.n_y - 1) * float(self.d_y) + float(self.element_transverse_size)

    @property
    def element_count(self) -> int:
        """Total number of physical array elements."""

        return self.n_x * self.n_y

    def elements(self) -> tuple[ArrayElement, ...]:
        """Return deterministic centred array-local element geometry.

        Elements are ordered first by longitudinal index and then by transverse
        index. The element-centre coordinates are symmetric about the origin for
        both odd and even counts.
        """

        x0 = -0.5 * (self.n_x - 1) * float(self.d_x)
        y0 = -0.5 * (self.n_y - 1) * float(self.d_y)

        items: list[ArrayElement] = []
        for ix in range(self.n_x):
            x = x0 + ix * float(self.d_x)
            for iy in range(self.n_y):
                y = y0 + iy * float(self.d_y)
                items.append(
                    ArrayElement(
                        index_x=ix,
                        index_y=iy,
                        position=Vector3(x=x, y=y, z=0.0),
                        longitudinal_size=self.element_longitudinal_size,
                        transverse_size=self.element_transverse_size,
                    )
                )
        return tuple(items)

    def direction_to_sensor_frame(self, direction_array_frame: Vector3) -> Vector3:
        """Express an array-local direction in the containing sensor frame."""

        r_sensor_array = rotation_matrix_from_rpy(self.orientation)
        return rotate_vector(r_sensor_array, direction_array_frame)

    def direction_from_sensor_frame(self, direction_sensor_frame: Vector3) -> Vector3:
        """Express a sensor-frame direction in this array's local frame."""

        r_sensor_array = rotation_matrix_from_rpy(self.orientation)
        return rotate_vector(r_sensor_array.T, direction_sensor_frame)

    def element_positions_sensor_frame(self) -> tuple[Vector3, ...]:
        """Return element-centre positions rotated into the sensor frame."""

        return tuple(self.direction_to_sensor_frame(element.position) for element in self.elements())

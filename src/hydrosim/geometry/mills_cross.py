"""Explicit Mills-Cross transducer geometry for HydroSIM.

Mills Cross is represented here as one specific installation geometry built from
otherwise generic ``TransducerArray`` objects.  The model does not make Mills
Cross a requirement for MBES or for two-way beam-pattern composition.

The defining geometric constraint used by this first reference model is that the
principal axes of the transmit and receive linear apertures are orthogonal when
expressed in their common containing sensor frame.
"""

from __future__ import annotations

from math import isclose

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .arrays import TransducerArray
from .models import Attitude, Vector3


def _principal_axis_array_frame(array: TransducerArray) -> Vector3:
    """Return the unit principal axis of a strictly linear array."""

    if array.n_x > 1 and array.n_y == 1:
        return Vector3(x=1.0, y=0.0, z=0.0)
    if array.n_y > 1 and array.n_x == 1:
        return Vector3(x=0.0, y=1.0, z=0.0)
    raise ValueError("Mills-Cross reference geometry requires strictly linear TX and RX arrays")


def principal_axis_sensor_frame(array: TransducerArray) -> Vector3:
    """Return a linear array's principal aperture axis in the common sensor frame."""

    return array.direction_to_sensor_frame(_principal_axis_array_frame(array))


def _dot(a: Vector3, b: Vector3) -> float:
    return a.x * b.x + a.y * b.y + a.z * b.z


class MillsCrossConfiguration(BaseModel):
    """Validated pair of orthogonal TX and RX linear apertures.

    Both arrays retain their own local frames and installation orientations.  The
    Mills-Cross constraint is evaluated only after each principal aperture axis is
    transformed into the common containing sensor frame.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(default="mills_cross", min_length=1)
    transmit_array: TransducerArray
    receive_array: TransducerArray
    orthogonality_tolerance: float = Field(default=1e-10, gt=0.0)

    @model_validator(mode="after")
    def validate_mills_cross_geometry(self) -> "MillsCrossConfiguration":
        if self.transmit_array.role not in {"tx", "txrx"}:
            raise ValueError("transmit_array role must be 'tx' or 'txrx'")
        if self.receive_array.role not in {"rx", "txrx"}:
            raise ValueError("receive_array role must be 'rx' or 'txrx'")

        tx_axis = principal_axis_sensor_frame(self.transmit_array)
        rx_axis = principal_axis_sensor_frame(self.receive_array)
        if not isclose(_dot(tx_axis, rx_axis), 0.0, abs_tol=self.orthogonality_tolerance):
            raise ValueError("Mills-Cross TX and RX principal aperture axes must be orthogonal")
        return self

    @property
    def transmit_axis_sensor_frame(self) -> Vector3:
        return principal_axis_sensor_frame(self.transmit_array)

    @property
    def receive_axis_sensor_frame(self) -> Vector3:
        return principal_axis_sensor_frame(self.receive_array)


def make_reference_mills_cross(
    *,
    transmit_count: int,
    receive_count: int,
    transmit_spacing: float,
    receive_spacing: float,
    transmit_element_longitudinal_size: float,
    transmit_element_transverse_size: float,
    receive_element_longitudinal_size: float,
    receive_element_transverse_size: float,
    name: str = "reference_mills_cross",
) -> MillsCrossConfiguration:
    """Construct a simple common-frame Mills-Cross reference installation.

    The TX linear aperture is longitudinal (+X in sensor frame), producing the
    narrow transmit dimension along-track.  The RX linear aperture is transverse
    (+Y in sensor frame), producing the narrow receive dimension across-track.

    This is a generic didactic reference, not a vendor-specific transducer model.
    """

    tx = TransducerArray(
        name=f"{name}_tx",
        role="tx",
        n_x=transmit_count,
        n_y=1,
        d_x=transmit_spacing,
        d_y=0.0,
        element_longitudinal_size=transmit_element_longitudinal_size,
        element_transverse_size=transmit_element_transverse_size,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )
    rx = TransducerArray(
        name=f"{name}_rx",
        role="rx",
        n_x=1,
        n_y=receive_count,
        d_x=0.0,
        d_y=receive_spacing,
        element_longitudinal_size=receive_element_longitudinal_size,
        element_transverse_size=receive_element_transverse_size,
        orientation=Attitude(roll=0.0, pitch=0.0, yaw=0.0),
    )
    return MillsCrossConfiguration(name=name, transmit_array=tx, receive_array=rx)

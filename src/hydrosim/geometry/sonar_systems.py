"""Vendor-neutral sonar-system geometry adapters for D7.

The models in this module compose existing HydroSIM array, beam, lever-arm and
rotation primitives. They preserve system/head/sector identity without adding
vendor timing, power, frequency sequencing, overlap suppression, or new acoustic
physics.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

from .arrays import TransducerArray
from .beams import BeamRay, IdealFan, generate_ideal_fan
from .models import Attitude, Vector3
from .rotations import rotate_vector, rotation_matrix_from_rpy


class SBESGeometry(BaseModel):
    """One-array, one-centreline baseline SBES geometry."""

    model_config = ConfigDict(frozen=True)

    array: TransducerArray
    centre_ray: BeamRay

    @model_validator(mode="after")
    def _validate_single_nadir(self) -> "SBESGeometry":
        if abs(float(self.centre_ray.definition.across_track_angle)) > 1e-15:
            raise ValueError("SBES centre ray must use zero steering")
        if self.centre_ray.definition.array_name != self.array.name:
            raise ValueError("SBES centre ray must belong to the configured array")
        return self


def make_sbes_geometry(array: TransducerArray) -> SBESGeometry:
    """Compose the canonical one-centreline SBES geometry from an existing array."""

    fan = generate_ideal_fan(array, beam_count=1, total_swath_angle=0.0, role="rx")
    return SBESGeometry(array=array, centre_ray=fan.beams[0])


class TxSectorGeometry(BaseModel):
    """Explicit transmit-sector identity, orientation and angular support."""

    model_config = ConfigDict(frozen=True)

    sector_id: str = Field(min_length=1)
    sector_index: int = Field(ge=0)
    system_id: str = Field(min_length=1)
    head_id: str = Field(min_length=1)
    array_id: str = Field(min_length=1)
    centre_along_track_angle_rad: FiniteFloat = 0.0
    centre_across_track_angle_rad: FiniteFloat = 0.0
    along_track_min_rad: FiniteFloat
    along_track_max_rad: FiniteFloat
    across_track_min_rad: FiniteFloat
    across_track_max_rad: FiniteFloat
    presentation_order: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _validate_support(self) -> "TxSectorGeometry":
        if float(self.along_track_max_rad) < float(self.along_track_min_rad):
            raise ValueError("along-track maximum must be >= minimum")
        if float(self.across_track_max_rad) < float(self.across_track_min_rad):
            raise ValueError("across-track maximum must be >= minimum")
        if not (
            float(self.along_track_min_rad)
            <= float(self.centre_along_track_angle_rad)
            <= float(self.along_track_max_rad)
        ):
            raise ValueError("sector along-track centre must lie inside its support")
        if not (
            float(self.across_track_min_rad)
            <= float(self.centre_across_track_angle_rad)
            <= float(self.across_track_max_rad)
        ):
            raise ValueError("sector across-track centre must lie inside its support")
        return self


class TxSectorSetGeometry(BaseModel):
    """One configured set of explicit TX sectors for a head/system."""

    model_config = ConfigDict(frozen=True)

    sectors: tuple[TxSectorGeometry, ...]

    @model_validator(mode="after")
    def _validate_identity(self) -> "TxSectorSetGeometry":
        if not self.sectors:
            raise ValueError("TX sector set must contain at least one sector")
        ids = [sector.sector_id for sector in self.sectors]
        indices = [sector.sector_index for sector in self.sectors]
        if len(ids) != len(set(ids)):
            raise ValueError("TX sector ids must be unique")
        if len(indices) != len(set(indices)):
            raise ValueError("TX sector indices must be unique")
        return self

    @property
    def coverage_supports(self) -> tuple[tuple[float, float, float, float], ...]:
        """Return the configured sector-support union as individual rectangles.

        Keeping each support separate preserves gaps/overlap instead of replacing
        the union with one contradictory bounding interval.
        """

        return tuple(
            (
                float(sector.along_track_min_rad),
                float(sector.along_track_max_rad),
                float(sector.across_track_min_rad),
                float(sector.across_track_max_rad),
            )
            for sector in self.sectors
        )


class SonarHeadGeometry(BaseModel):
    """One rigidly installed sonar head relative to a common reference frame."""

    model_config = ConfigDict(frozen=True)

    system_id: str = Field(min_length=1)
    head_id: str = Field(min_length=1)
    lever_arm_ref_to_head: Vector3
    fixed_orientation: Attitude
    receive_array: TransducerArray
    receive_fan: IdealFan

    @model_validator(mode="after")
    def _validate_array_fan(self) -> "SonarHeadGeometry":
        if self.receive_fan.array_name != self.receive_array.name:
            raise ValueError("head receive fan must belong to its receive array")
        return self

    @property
    def fan_directions_reference_frame(self) -> tuple[Vector3, ...]:
        rotation = rotation_matrix_from_rpy(self.fixed_orientation)
        return tuple(
            rotate_vector(rotation, beam.direction_sensor_frame)
            for beam in self.receive_fan.beams
        )


def make_sonar_head_geometry(
    *,
    system_id: str,
    head_id: str,
    lever_arm_ref_to_head: Vector3,
    fixed_orientation: Attitude,
    receive_array: TransducerArray,
    beam_count: int,
    total_swath_angle_rad: float,
) -> SonarHeadGeometry:
    """Compose one head while keeping fixed installation separate from vessel attitude."""

    fan = generate_ideal_fan(
        receive_array,
        beam_count=beam_count,
        total_swath_angle=total_swath_angle_rad,
        role="rx",
    )
    return SonarHeadGeometry(
        system_id=system_id,
        head_id=head_id,
        lever_arm_ref_to_head=lever_arm_ref_to_head,
        fixed_orientation=fixed_orientation,
        receive_array=receive_array,
        receive_fan=fan,
    )


class DualHeadGeometry(BaseModel):
    """Two distinct rigid heads whose combined coverage is a derived union."""

    model_config = ConfigDict(frozen=True)

    system_id: str = Field(min_length=1)
    heads: tuple[SonarHeadGeometry, SonarHeadGeometry]

    @model_validator(mode="after")
    def _validate_heads(self) -> "DualHeadGeometry":
        first, second = self.heads
        if first.head_id == second.head_id:
            raise ValueError("dual-head geometry requires distinct head ids")
        if first.system_id != self.system_id or second.system_id != self.system_id:
            raise ValueError("both heads must belong to the containing system")
        return self

    @property
    def combined_coverage_directions_reference_frame(self) -> tuple[Vector3, ...]:
        """Return the derived union of individual head ray directions.

        Duplicate/overlapping directions are intentionally retained; vendor-specific
        overlap suppression is outside the D7 geometry contract.
        """

        return tuple(
            direction
            for head in self.heads
            for direction in head.fan_directions_reference_frame
        )

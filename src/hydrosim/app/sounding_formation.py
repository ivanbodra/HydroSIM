"""Application state for the Sounding Formation / Detection Chain lesson.

This module does not implement new acoustic or sounding physics. It assembles
outputs from the existing acquisition, detection, beam, pose, and sounding
pipelines into one ordered didactic state that later presentation layers can
step through without duplicating scientific calculations.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from hydrosim.acquisition.bottom_detection import BottomDetection
from hydrosim.acquisition.models import AcquisitionPing
from hydrosim.geometry.beams import BeamRay
from hydrosim.geometry.models import Pose
from hydrosim.geometry.soundings import SoundingComparison, SoundingState


class SoundingFormationStage(StrEnum):
    """Canonical stage order for the first sounding-formation experience."""

    TRANSMIT = "transmit"
    PROPAGATION = "propagation"
    SEABED_INTERACTION = "seabed-interaction"
    RECEIVE = "receive"
    DETECTION = "bottom-detection"
    TWTT_RANGE = "twtt-range"
    BEAM_ANGLE = "beam-angle"
    POSE_ASSOCIATION = "pose-association"
    RECONSTRUCTION = "reconstruction"
    TRUTH_OBSERVED = "truth-observed"


STAGE_ORDER: tuple[SoundingFormationStage, ...] = tuple(SoundingFormationStage)


class D8ObservationAssociation(BaseModel):
    """Stable identity of one detected acoustic observation.

    The key follows the canonical D8 contract: ping index, parent receive-beam
    index, and per-beam detection index. It intentionally carries identity only;
    the measured quantities remain on :class:`BottomDetection`.
    """

    model_config = ConfigDict(frozen=True)

    ping_index: int
    beam_index: int
    detection_index: int


class D8ConfiguredState(BaseModel):
    """Configured inputs currently available to the D8 reconstruction adapter.

    ``processing_pose`` and ``processing_beam`` are configuration/processing
    references. They are not acoustic observations. Additional configured state
    (for example sound-speed processing state) can be added by composition when
    the owning scientific model exposes it; this type does not invent it.
    """

    model_config = ConfigDict(frozen=True)

    processing_pose: Pose
    processing_beam: BeamRay


class D8ObservationState(BaseModel):
    """Typed Truth / Observed / Configured / Derived boundary for D8.

    ``observation`` is the measured BottomDetection tuple. ``configured_state``
    contains the processing geometry currently available to the lesson.
    ``reconstructed_sounding`` is the existing configured-geometry reconstruction
    from :class:`SoundingComparison`; its explicit basis records that the current
    geometry helper still uses the Truth-derived slant range and is therefore a
    deterministic Derived/reference reconstruction, not yet a fully
    observation-driven Cartesian sounding.
    """

    model_config = ConfigDict(frozen=True)

    truth_sounding: SoundingState
    observation: BottomDetection
    association: D8ObservationAssociation
    configured_state: D8ConfiguredState
    reconstructed_sounding: SoundingState
    reconstruction_basis: Literal["configured_geometry_reference"] = "configured_geometry_reference"

    @model_validator(mode="after")
    def association_must_match_observation(self) -> "D8ObservationState":
        parent = self.observation.parent_beam_index
        if parent is None:
            raise ValueError("D8 observation requires parent_beam_index for stable association")
        if self.association.beam_index != parent:
            raise ValueError("association beam_index must match observation parent_beam_index")
        if self.association.detection_index != self.observation.detection_index:
            raise ValueError("association detection_index must match observation detection_index")
        return self


class SoundingFormationSnapshot(BaseModel):
    """One assembled sounding chain using existing HydroSIM scientific outputs."""

    model_config = ConfigDict(frozen=True)

    ping: AcquisitionPing
    beam: BeamRay
    detection: BottomDetection
    associated_pose: Pose
    sounding: SoundingComparison
    active_stage: SoundingFormationStage = SoundingFormationStage.TRANSMIT

    @model_validator(mode="after")
    def scientific_outputs_must_refer_to_the_same_beam(self) -> "SoundingFormationSnapshot":
        """Reject accidental assembly of outputs belonging to different beams."""

        beam_index = self.beam.definition.index
        if self.sounding.beam_index != beam_index:
            raise ValueError("sounding beam_index must match the assembled beam")
        if self.detection.parent_beam_index is not None and self.detection.parent_beam_index != beam_index:
            raise ValueError("detection parent_beam_index must match the assembled beam")
        return self

    @property
    def stage_index(self) -> int:
        return STAGE_ORDER.index(self.active_stage)

    @property
    def twtt_seconds(self) -> float:
        return float(self.detection.twtt_seconds)

    @property
    def detected_angle_rad(self) -> float | None:
        value = self.detection.detected_across_track_angle_rad
        return None if value is None else float(value)

    @property
    def truth_sounding(self) -> SoundingState:
        return self.sounding.true

    @property
    def reconstructed_sounding(self) -> SoundingState:
        """Return the deterministic Derived/reference reconstruction.

        The existing geometry helper names this branch ``configured``. Per the
        D8 scientific-state contract, the resulting Cartesian point is a Derived
        reconstruction from configured inputs and must not be labelled as an
        Observed sounding.
        """

        return self.sounding.configured

    @property
    def observation_state(self) -> D8ObservationState:
        """Expose the reusable D8 scientific-state composition.

        A stable observation association requires ``parent_beam_index`` on the
        BottomDetection. The application adapter fails explicitly rather than
        manufacturing a beam identity from presentation context.
        """

        parent = self.detection.parent_beam_index
        if parent is None:
            raise ValueError("D8 observation requires parent_beam_index for stable association")
        return D8ObservationState(
            truth_sounding=self.truth_sounding,
            observation=self.detection,
            association=D8ObservationAssociation(
                ping_index=self.ping.ping_index,
                beam_index=parent,
                detection_index=self.detection.detection_index,
            ),
            configured_state=D8ConfiguredState(
                processing_pose=self.associated_pose,
                processing_beam=self.beam,
            ),
            reconstructed_sounding=self.reconstructed_sounding,
        )

    def at_stage(self, stage: SoundingFormationStage) -> "SoundingFormationSnapshot":
        """Return the same scientific state focused on another didactic stage."""

        return self.model_copy(update={"active_stage": stage})

    def next_stage(self) -> "SoundingFormationSnapshot":
        """Advance one stage, saturating at the final Truth/Observed comparison."""

        index = min(self.stage_index + 1, len(STAGE_ORDER) - 1)
        return self.at_stage(STAGE_ORDER[index])

    def previous_stage(self) -> "SoundingFormationSnapshot":
        """Move one stage backward, saturating at transmit."""

        index = max(self.stage_index - 1, 0)
        return self.at_stage(STAGE_ORDER[index])

    def reset(self) -> "SoundingFormationSnapshot":
        return self.at_stage(SoundingFormationStage.TRANSMIT)

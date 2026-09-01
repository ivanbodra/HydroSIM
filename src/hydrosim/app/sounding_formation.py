"""Application state for the Sounding Formation / Detection Chain lesson.

This module does not implement new acoustic or sounding physics. It assembles
outputs from the existing acquisition, detection, beam, pose, and sounding
pipelines into one ordered didactic state that later presentation layers can
step through without duplicating scientific calculations.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from hydrosim.acquisition.bottom_detection import BottomDetection
from hydrosim.acquisition.models import AcquisitionPing
from hydrosim.geometry.beams import BeamRay
from hydrosim.geometry.models import Pose
from hydrosim.geometry.soundings import SoundingComparison


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


class SoundingFormationSnapshot(BaseModel):
    """One assembled sounding chain using existing HydroSIM scientific outputs."""

    model_config = ConfigDict(frozen=True)

    ping: AcquisitionPing
    beam: BeamRay
    detection: BottomDetection
    associated_pose: Pose
    sounding: SoundingComparison
    active_stage: SoundingFormationStage = SoundingFormationStage.TRANSMIT

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
    def truth_sounding(self):
        return self.sounding.true

    @property
    def observed_sounding(self):
        """Configured/reconstructed state used as the first Observed proxy.

        The existing geometric sounding core calls this state ``configured``.
        This adapter deliberately aliases it for the lesson rather than changing
        the scientific-state object or recomputing a sounding.
        """

        return self.sounding.configured

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

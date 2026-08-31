"""Pedagogical baseline/current comparison for the Didactic Explorer Signal lesson.

This module is presentation-oriented. ``baseline`` and ``current`` are teaching states,
not HydroSIM scientific states such as truth, observed, configured, estimated, or derived.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SignalLessonSnapshot:
    """Small immutable teaching snapshot of the visible Signal controls."""

    duration_seconds: float
    lfm_bandwidth_hz: float

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0.0:
            raise ValueError("duration_seconds must be positive")
        if self.lfm_bandwidth_hz <= 0.0:
            raise ValueError("lfm_bandwidth_hz must be positive")

    @property
    def time_bandwidth_product(self) -> float:
        """Return the dimensionless time-bandwidth product used in the lesson readout."""

        return self.duration_seconds * self.lfm_bandwidth_hz

    @property
    def reciprocal_bandwidth_seconds(self) -> float:
        """Return the reciprocal-bandwidth time scale used in the lesson readout."""

        return 1.0 / self.lfm_bandwidth_hz


@dataclass(frozen=True)
class SignalLessonComparison:
    """Compare a frozen pedagogical baseline with the current visible control state."""

    baseline: SignalLessonSnapshot
    current: SignalLessonSnapshot

    @property
    def duration_change_seconds(self) -> float:
        return self.current.duration_seconds - self.baseline.duration_seconds

    @property
    def bandwidth_change_hz(self) -> float:
        return self.current.lfm_bandwidth_hz - self.baseline.lfm_bandwidth_hz

    @property
    def time_bandwidth_change(self) -> float:
        return self.current.time_bandwidth_product - self.baseline.time_bandwidth_product

    @property
    def reciprocal_bandwidth_change_seconds(self) -> float:
        return (
            self.current.reciprocal_bandwidth_seconds
            - self.baseline.reciprocal_bandwidth_seconds
        )

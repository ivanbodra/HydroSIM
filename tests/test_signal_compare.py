import pytest

from hydrosim.app.signal_compare import SignalLessonComparison, SignalLessonSnapshot


def test_signal_lesson_snapshot_exposes_teaching_readouts():
    snapshot = SignalLessonSnapshot(duration_seconds=1e-3, lfm_bandwidth_hz=100e3)

    assert snapshot.time_bandwidth_product == pytest.approx(100.0)
    assert snapshot.reciprocal_bandwidth_seconds == pytest.approx(10e-6)


def test_signal_lesson_comparison_reports_current_minus_baseline():
    baseline = SignalLessonSnapshot(duration_seconds=1e-3, lfm_bandwidth_hz=100e3)
    current = SignalLessonSnapshot(duration_seconds=2e-3, lfm_bandwidth_hz=200e3)
    comparison = SignalLessonComparison(baseline=baseline, current=current)

    assert comparison.duration_change_seconds == pytest.approx(1e-3)
    assert comparison.bandwidth_change_hz == pytest.approx(100e3)
    assert comparison.time_bandwidth_change == pytest.approx(300.0)
    assert comparison.reciprocal_bandwidth_change_seconds == pytest.approx(-5e-6)


def test_signal_lesson_snapshot_rejects_nonphysical_visible_controls():
    with pytest.raises(ValueError):
        SignalLessonSnapshot(duration_seconds=0.0, lfm_bandwidth_hz=100e3)

    with pytest.raises(ValueError):
        SignalLessonSnapshot(duration_seconds=1e-3, lfm_bandwidth_hz=0.0)


def test_baseline_current_names_are_not_scientific_state_aliases():
    source = __import__("hydrosim.app.signal_compare", fromlist=["__doc__"]).__doc__ or ""

    assert "teaching states" in source
    assert "truth" in source
    assert "observed" in source

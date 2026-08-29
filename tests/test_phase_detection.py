import numpy as np
import pytest

from hydrosim.acquisition import detect_bottom_from_phase_ramp, differential_phase


def _synthetic_split_aperture(sample_rate: float, count: int, zero_time: float, slope: float):
    t = np.arange(count, dtype=float) / sample_rate
    dphi = slope * (t - zero_time)
    a = np.exp(0.5j * dphi)
    b = np.exp(-0.5j * dphi)
    return a, b


def test_differential_phase_recovers_a_minus_b_phase() -> None:
    a = np.array([1.0 + 0.0j, 1.0j])
    b = np.array([1.0 + 0.0j, 1.0 + 0.0j])
    phase = differential_phase(a, b)
    assert phase[0] == pytest.approx(0.0)
    assert phase[1] == pytest.approx(np.pi / 2.0)


def test_phase_ramp_detector_recovers_subsample_zero_crossing() -> None:
    sample_rate = 100_000.0
    zero_time = 0.012345
    a, b = _synthetic_split_aperture(sample_rate, 2000, zero_time, slope=2000.0)

    result = detect_bottom_from_phase_ramp(
        a,
        b,
        sample_rate_hz=sample_rate,
        search_start_sample=1200,
        search_end_sample=1270,
        tx_delay_seconds=0.001,
        parent_beam_index=12,
        steering_across_track_angle_rad=0.3,
        fit_half_width_samples=3,
    )

    assert result.detection.detection_method == "phase_zero_crossing"
    assert result.detection.parent_beam_index == 12
    assert result.detection.arrival_offset_seconds == pytest.approx(zero_time, abs=1e-9)
    assert result.detection.twtt_seconds == pytest.approx(zero_time - 0.001, abs=1e-9)
    assert result.detection.detected_across_track_angle_rad == pytest.approx(0.3)
    assert result.fit.rms_residual_rad == pytest.approx(0.0, abs=1e-10)
    assert result.fit.slope_rad_per_second == pytest.approx(2000.0, rel=1e-10)


def test_phase_detector_rejects_window_without_zero_crossing() -> None:
    sample_rate = 10_000.0
    a, b = _synthetic_split_aperture(sample_rate, 500, zero_time=0.030, slope=100.0)
    with pytest.raises(ValueError, match="no differential-phase zero crossing"):
        detect_bottom_from_phase_ramp(
            a,
            b,
            sample_rate_hz=sample_rate,
            search_start_sample=10,
            search_end_sample=100,
        )

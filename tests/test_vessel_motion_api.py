import pytest

from hydrosim.app.vessel_motion_api import (
    D12AngularHarmonicRequest,
    D12HeaveHarmonicRequest,
    D12VesselMotionRequest,
    prepare_d12_vessel_motion_response,
)


def test_vessel_motion_samples_canonical_pose_and_positive_up_heave():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            heading_deg=90.0,
            speed_mps=2.0,
            start_north_m=10.0,
            start_east_m=20.0,
            start_down_m=5.0,
            duration_seconds=4.0,
            sample_count=5,
            roll=D12AngularHarmonicRequest(amplitude_deg=10.0, period_seconds=4.0),
            pitch=D12AngularHarmonicRequest(amplitude_deg=4.0, period_seconds=4.0),
            yaw_deviation=D12AngularHarmonicRequest(amplitude_deg=6.0, period_seconds=4.0),
            heave=D12HeaveHarmonicRequest(amplitude_m=2.0, period_seconds=4.0),
        )
    )

    quarter = response.samples[1]
    assert quarter.time_seconds == pytest.approx(1.0)
    assert quarter.north_m == pytest.approx(10.0)
    assert quarter.east_m == pytest.approx(22.0)
    assert quarter.roll_deg == pytest.approx(10.0)
    assert quarter.pitch_deg == pytest.approx(4.0)
    assert quarter.yaw_deviation_deg == pytest.approx(6.0)
    assert quarter.heading_deg == pytest.approx(96.0)
    assert quarter.heave_up_m == pytest.approx(2.0)
    assert quarter.down_m == pytest.approx(3.0)
    assert response.metadata["frame"] == "N (North-East-Down)"


def test_vessel_motion_phase_is_converted_only_in_application_adapter():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            duration_seconds=2.0,
            sample_count=3,
            roll=D12AngularHarmonicRequest(
                amplitude_deg=8.0,
                period_seconds=10.0,
                phase_deg=90.0,
            ),
            heave=D12HeaveHarmonicRequest(
                amplitude_m=1.5,
                period_seconds=10.0,
                phase_deg=90.0,
            ),
        )
    )

    first = response.samples[0]
    assert first.roll_deg == pytest.approx(8.0)
    assert first.heave_up_m == pytest.approx(1.5)
    assert first.down_m == pytest.approx(-1.5)


def test_vessel_motion_contract_rejects_invalid_sampling_and_periods():
    with pytest.raises(ValueError):
        D12VesselMotionRequest(sample_count=1)

    with pytest.raises(ValueError):
        D12AngularHarmonicRequest(period_seconds=0.0)

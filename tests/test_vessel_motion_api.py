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
            terrain_depth_m=40.0,
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
            terrain_depth_m=30.0,
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


def test_d12_zero_motion_returns_identical_reference_and_moved_geometry():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            terrain_depth_m=20.0,
            half_swath_angle_deg=45.0,
            duration_seconds=1.0,
            sample_count=2,
        )
    )

    consequence = response.consequences[0]
    assert [beam.beam for beam in consequence.beams] == ["port", "nadir", "starboard"]
    for beam in consequence.beams:
        assert beam.reference_intersection == beam.moved_intersection
        assert beam.displacement is not None
        assert beam.displacement.north_m == pytest.approx(0.0)
        assert beam.displacement.east_m == pytest.approx(0.0)
        assert beam.displacement.down_m == pytest.approx(0.0)

    assert consequence.swath.reference_width_m == pytest.approx(40.0)
    assert consequence.swath.moved_width_m == pytest.approx(40.0)
    assert consequence.swath.width_change_m == pytest.approx(0.0)


def test_d12_pitch_moves_nadir_intersection_using_canonical_rigid_transform():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            terrain_depth_m=30.0,
            duration_seconds=1.0,
            sample_count=2,
            pitch=D12AngularHarmonicRequest(
                amplitude_deg=10.0,
                period_seconds=4.0,
                phase_deg=90.0,
            ),
        )
    )

    nadir = response.consequences[0].beams[1]
    assert nadir.beam == "nadir"
    assert nadir.displacement is not None
    assert abs(nadir.displacement.north_m) > 1.0
    assert nadir.displacement.east_m == pytest.approx(0.0, abs=1e-12)
    assert nadir.displacement.down_m == pytest.approx(0.0, abs=1e-12)


def test_d12_positive_heave_preserves_bottom_plane_but_changes_edge_intersections():
    response = prepare_d12_vessel_motion_response(
        D12VesselMotionRequest(
            terrain_depth_m=30.0,
            half_swath_angle_deg=45.0,
            duration_seconds=1.0,
            sample_count=2,
            heave=D12HeaveHarmonicRequest(
                amplitude_m=2.0,
                period_seconds=4.0,
                phase_deg=90.0,
            ),
        )
    )

    consequence = response.consequences[0]
    nadir = consequence.beams[1]
    assert nadir.displacement is not None
    assert nadir.displacement.north_m == pytest.approx(0.0)
    assert nadir.displacement.east_m == pytest.approx(0.0)
    assert nadir.displacement.down_m == pytest.approx(0.0)
    assert consequence.swath.reference_width_m == pytest.approx(60.0)
    assert consequence.swath.moved_width_m == pytest.approx(64.0)
    assert consequence.swath.width_change_m == pytest.approx(4.0)


def test_vessel_motion_contract_rejects_invalid_sampling_periods_and_swath():
    with pytest.raises(ValueError):
        D12VesselMotionRequest(sample_count=1)

    with pytest.raises(ValueError):
        D12AngularHarmonicRequest(period_seconds=0.0)

    with pytest.raises(ValueError):
        D12VesselMotionRequest(half_swath_angle_deg=90.0)

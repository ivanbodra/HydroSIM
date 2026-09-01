from __future__ import annotations

from math import radians

import pytest

from hydrosim.geometry import (
    Attitude,
    DualHeadGeometry,
    TransducerArray,
    TxSectorGeometry,
    TxSectorSetGeometry,
    Vector3,
    make_sbes_geometry,
    make_sonar_head_geometry,
)


def _array(name: str) -> TransducerArray:
    return TransducerArray(
        name=name,
        role="txrx",
        n_x=1,
        n_y=1,
        d_x=0.0,
        d_y=0.0,
        element_longitudinal_size=0.02,
        element_transverse_size=0.02,
    )


def test_sbes_has_exactly_one_zero_steering_centreline() -> None:
    sbes = make_sbes_geometry(_array("sbes"))
    assert sbes.centre_ray.definition.across_track_angle == pytest.approx(0.0)
    assert sbes.centre_ray.definition.array_name == "sbes"


def test_tx_sector_preserves_identity_and_individual_coverage_supports() -> None:
    first = TxSectorGeometry(
        sector_id="port",
        sector_index=0,
        system_id="mbes",
        head_id="head",
        array_id="tx",
        centre_along_track_angle_rad=0.0,
        centre_across_track_angle_rad=-0.2,
        along_track_min_rad=-0.05,
        along_track_max_rad=0.05,
        across_track_min_rad=-0.4,
        across_track_max_rad=0.0,
    )
    second = first.model_copy(
        update={
            "sector_id": "starboard",
            "sector_index": 1,
            "centre_across_track_angle_rad": 0.2,
            "across_track_min_rad": 0.0,
            "across_track_max_rad": 0.4,
        }
    )
    sectors = TxSectorSetGeometry(sectors=(first, second))
    assert len(sectors.coverage_supports) == 2
    assert sectors.coverage_supports[0][2:] == pytest.approx((-0.4, 0.0))
    assert sectors.coverage_supports[1][2:] == pytest.approx((0.0, 0.4))


def test_dual_head_preserves_identity_and_derived_union() -> None:
    port = make_sonar_head_geometry(
        system_id="dual",
        head_id="port",
        lever_arm_ref_to_head=Vector3(x=0.0, y=-0.5, z=0.0),
        fixed_orientation=Attitude.from_degrees(roll=-15.0, pitch=0.0, yaw=0.0),
        receive_array=_array("port_rx"),
        beam_count=3,
        total_swath_angle_rad=radians(60.0),
    )
    starboard = make_sonar_head_geometry(
        system_id="dual",
        head_id="starboard",
        lever_arm_ref_to_head=Vector3(x=0.0, y=0.5, z=0.0),
        fixed_orientation=Attitude.from_degrees(roll=15.0, pitch=0.0, yaw=0.0),
        receive_array=_array("starboard_rx"),
        beam_count=3,
        total_swath_angle_rad=radians(60.0),
    )
    dual = DualHeadGeometry(system_id="dual", heads=(port, starboard))
    assert port.head_id != starboard.head_id
    assert port.lever_arm_ref_to_head.y == pytest.approx(-0.5)
    assert starboard.lever_arm_ref_to_head.y == pytest.approx(0.5)
    assert len(dual.combined_coverage_directions_reference_frame) == 6


def test_dual_head_rejects_duplicate_head_ids() -> None:
    head = make_sonar_head_geometry(
        system_id="dual",
        head_id="same",
        lever_arm_ref_to_head=Vector3(x=0.0, y=0.0, z=0.0),
        fixed_orientation=Attitude.from_degrees(roll=0.0, pitch=0.0, yaw=0.0),
        receive_array=_array("rx"),
        beam_count=1,
        total_swath_angle_rad=0.0,
    )
    with pytest.raises(ValueError, match="distinct head ids"):
        DualHeadGeometry(system_id="dual", heads=(head, head))

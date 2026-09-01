import pytest

from hydrosim.app.survey_vessel_configuration import (
    SurveyVesselConfiguration,
    default_survey_vessel_configuration,
    prepare_survey_vessel_configuration_snapshot,
)
from hydrosim.geometry.models import Vector3


def test_default_survey_vessel_configuration_is_deterministic():
    first = default_survey_vessel_configuration()
    second = default_survey_vessel_configuration()

    assert first == second
    assert first.vrp_pose.frame == "N"
    assert first.static_draft_m == pytest.approx(2.2)


def test_snapshot_reuses_existing_vertical_reference_adapter():
    configuration = default_survey_vessel_configuration()
    snapshot = prepare_survey_vessel_configuration_snapshot(configuration)

    assert snapshot.configuration == configuration
    assert snapshot.vertical_reference.vessel_vrp_pose == configuration.vrp_pose
    assert snapshot.vertical_reference.transducer_position.z == pytest.approx(2.1)
    assert snapshot.vertical_reference.keel_z_from_vrp_m == pytest.approx(2.9)


def test_sensor_installation_change_propagates_through_shared_geometry():
    base = default_survey_vessel_configuration()
    changed = SurveyVesselConfiguration(
        **{
            **base.model_dump(),
            "lever_arm_vrp_to_sonar": Vector3(x=2.0, y=-1.0, z=2.5),
        }
    )

    snapshot = prepare_survey_vessel_configuration_snapshot(changed)

    assert snapshot.vertical_reference.transducer_position.x == pytest.approx(2.0)
    assert snapshot.vertical_reference.transducer_position.y == pytest.approx(-1.0)
    assert snapshot.vertical_reference.transducer_position.z == pytest.approx(2.5)


def test_water_level_remains_separate_from_vessel_geometry():
    base = default_survey_vessel_configuration()
    changed = base.model_copy(update={"water_level_m_relative_to_datum": 1.4})

    before = prepare_survey_vessel_configuration_snapshot(base)
    after = prepare_survey_vessel_configuration_snapshot(changed)

    assert after.vertical_reference.transducer_position == before.vertical_reference.transducer_position
    assert after.vertical_reference.keel_z_from_vrp_m == before.vertical_reference.keel_z_from_vrp_m
    assert after.vertical_reference.water_level_m_relative_to_datum == pytest.approx(1.4)

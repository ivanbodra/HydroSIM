from pathlib import Path

from hydrosim.product.structure import find_submodule


def test_survey_vessel_configuration_matches_canonical_s1_inventory():
    submodule = find_submodule("vessel-configuration")

    assert submodule.name == "Vessel Configuration"
    assert tuple(item.id for item in submodule.items) == (
        "vrp",
        "gnss-imu",
        "sonar-installation",
        "waterline-draft",
        "save-load-reset",
    )


def test_survey_vessel_state_reuses_existing_vessel_reference_adapter():
    source = Path("src/hydrosim/app/survey_vessel_configuration.py").read_text(encoding="utf-8")

    assert "VesselVerticalReferenceConfiguration" in source
    assert "prepare_vessel_vertical_reference_snapshot" in source
    assert "lever_arm_vrp_to_gnss" in source
    assert "lever_arm_vrp_to_imu" in source
    assert "lever_arm_vrp_to_sonar" in source
    assert "static_draft_m" in source
    assert "water_level_m_relative_to_datum" in source

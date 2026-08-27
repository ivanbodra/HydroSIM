from pathlib import Path

import pytest

from hydrosim.scenarios import load_roll_offset_scenario, run_roll_offset_scenario


SCENARIO_PATH = Path(__file__).resolve().parents[2] / "scenarios" / "roll_offset_demo.yaml"


def test_roll_offset_scenario_loads_from_yaml() -> None:
    config = load_roll_offset_scenario(SCENARIO_PATH)

    assert config.scenario.id == "geometry.roll_offset_demo"
    assert config.random_seed == 1001
    assert config.environment.terrain.depth_m == pytest.approx(30.0)
    assert config.sonar.number_of_beams == 128
    assert config.sonar.swath_angle_deg == pytest.approx(120.0)
    assert config.truth.transducer_alignment.roll_deg == pytest.approx(0.5)
    assert config.configured.transducer_alignment.roll_deg == pytest.approx(0.0)


def test_roll_offset_result_is_reproducible() -> None:
    config = load_roll_offset_scenario(SCENARIO_PATH)

    first = run_roll_offset_scenario(config)
    second = run_roll_offset_scenario(config)

    assert first == second
    assert first.random_seed == 1001
    assert len(first.soundings) == 128


def test_outer_beam_has_nonzero_roll_residual() -> None:
    result = run_roll_offset_scenario(load_roll_offset_scenario(SCENARIO_PATH))

    outer = result.soundings[0]
    assert outer.horizontal_error > 0.0
    assert abs(outer.vertical_error) > 0.0
    assert outer.error_magnitude > 0.0


def test_roll_residual_varies_across_the_swath() -> None:
    result = run_roll_offset_scenario(load_roll_offset_scenario(SCENARIO_PATH))

    outer = result.soundings[0]
    near_center = result.soundings[len(result.soundings) // 2]

    assert abs(outer.vertical_error) > abs(near_center.vertical_error)
    assert outer.error_magnitude != pytest.approx(near_center.error_magnitude)


def test_zero_alignment_difference_collapses_residuals() -> None:
    config = load_roll_offset_scenario(SCENARIO_PATH)
    zero_error_config = config.model_copy(update={"configured": config.truth})

    result = run_roll_offset_scenario(zero_error_config)

    for sounding in result.soundings:
        assert sounding.horizontal_error == pytest.approx(0.0, abs=1e-12)
        assert sounding.vertical_error == pytest.approx(0.0, abs=1e-12)
        assert sounding.error_magnitude == pytest.approx(0.0, abs=1e-12)


def test_summary_reports_across_swath_statistics() -> None:
    result = run_roll_offset_scenario(load_roll_offset_scenario(SCENARIO_PATH))

    assert result.summary.beam_count == 128
    assert result.summary.max_horizontal_error > 0.0
    assert result.summary.max_abs_vertical_error > 0.0
    assert result.summary.rms_horizontal_error > 0.0
    assert result.summary.rms_vertical_error > 0.0

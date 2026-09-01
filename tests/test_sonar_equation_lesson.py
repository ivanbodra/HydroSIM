import pytest

from hydrosim.app.sonar_equation_lesson import (
    SonarEquationLessonControls,
    default_sonar_equation_lesson_snapshot,
    prepare_sonar_equation_lesson_snapshot,
)
from hydrosim.sonar_equation.backscatter import AreaBackscatterInput
from hydrosim.sonar_equation.d3_adapter import D3SonarEquationInput, evaluate_d3_sonar_equation


def test_lesson_snapshot_matches_canonical_scientific_adapter():
    controls = SonarEquationLessonControls()
    snapshot = prepare_sonar_equation_lesson_snapshot(controls)
    expected = evaluate_d3_sonar_equation(
        D3SonarEquationInput(
            frequency_hz=controls.frequency_hz,
            source_level_db_re_1upa_at_1m=controls.source_level_db_re_1upa_at_1m,
            noise_level_db_re_1upa=controls.noise_level_db_re_1upa,
            outbound_path_length_m=controls.range_m,
            inbound_path_length_m=controls.range_m,
            backscatter=AreaBackscatterInput(
                scattering_strength_db_per_m2=controls.scattering_strength_db_per_m2,
                contributing_area_m2=controls.contributing_area_m2,
                frequency_hz=controls.frequency_hz,
            ),
            tx_relative_beam_gain_db=controls.tx_relative_beam_gain_db,
            rx_relative_beam_gain_db=controls.rx_relative_beam_gain_db,
        )
    )

    assert snapshot.result == expected
    assert snapshot.transmission_loss_db == pytest.approx(expected.two_way_transmission_loss_db)


def test_source_level_change_has_direct_one_for_one_received_level_and_snr_consequence():
    baseline = default_sonar_equation_lesson_snapshot()
    louder = prepare_sonar_equation_lesson_snapshot(
        baseline.controls.model_copy(update={"source_level_db_re_1upa_at_1m": 230.0})
    )

    assert louder.received_level_db_re_1upa - baseline.received_level_db_re_1upa == pytest.approx(10.0)
    assert louder.snr_db - baseline.snr_db == pytest.approx(10.0)


def test_range_increase_raises_transmission_loss_and_reduces_snr():
    near = default_sonar_equation_lesson_snapshot()
    far = prepare_sonar_equation_lesson_snapshot(near.controls.model_copy(update={"range_m": 100.0}))

    assert far.transmission_loss_db > near.transmission_loss_db
    assert far.snr_db < near.snr_db


def test_frequency_change_updates_referenced_absorption_and_loss():
    baseline = default_sonar_equation_lesson_snapshot()
    higher_frequency = prepare_sonar_equation_lesson_snapshot(
        baseline.controls.model_copy(update={"frequency_hz": 400_000.0})
    )

    assert higher_frequency.result.absorption_db_per_km != pytest.approx(
        baseline.result.absorption_db_per_km
    )
    assert higher_frequency.transmission_loss_db != pytest.approx(baseline.transmission_loss_db)


def test_contribution_breakdown_preserves_canonical_signs_and_reset_state():
    snapshot = default_sonar_equation_lesson_snapshot()
    contributions = {item.key: float(item.value_db) for item in snapshot.contributions}

    assert contributions["source-level"] > 0.0
    assert contributions["outbound-tl"] < 0.0
    assert contributions["inbound-tl"] < 0.0
    assert contributions["noise"] < 0.0
    assert snapshot.controls == SonarEquationLessonControls()

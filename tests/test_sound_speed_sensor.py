import pytest

from hydrosim.acquisition.sound_speed_sensor import (
    SoundSpeedSensorAtTransducer,
    measure_sound_speed_at_transducer,
)


def test_ideal_sensor_reports_true_local_sound_speed() -> None:
    measurement = measure_sound_speed_at_transducer(true_local_sound_speed_mps=1497.3)
    assert measurement.measured_sound_speed_mps == pytest.approx(1497.3)
    assert measurement.sensor_bias_mps == pytest.approx(0.0)


def test_sensor_bias_changes_measurement_available_to_sonar() -> None:
    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=1497.3,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=2.0),
    )
    assert measurement.measured_sound_speed_mps == pytest.approx(1499.3)


def test_measurement_does_not_expose_simulation_truth() -> None:
    measurement = measure_sound_speed_at_transducer(true_local_sound_speed_mps=1497.3)
    assert not hasattr(measurement, "true_local_sound_speed_mps")


def test_nonpositive_truth_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        measure_sound_speed_at_transducer(true_local_sound_speed_mps=0.0)

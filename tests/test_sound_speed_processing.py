import pytest

from hydrosim.acquisition.sound_speed_processing import (
    SoundSpeedAtTransducerUse,
    use_manual_sound_speed_at_transducer,
    use_measured_sound_speed_at_transducer,
)
from hydrosim.acquisition.sound_speed_sensor import (
    SoundSpeedSensorAtTransducer,
    measure_sound_speed_at_transducer,
)


def test_sensor_measurement_becomes_explicit_sonar_use_state() -> None:
    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=1495.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=2.0),
    )
    used = use_measured_sound_speed_at_transducer(measurement)
    assert isinstance(used, SoundSpeedAtTransducerUse)
    assert used.sound_speed_mps == pytest.approx(1497.0)
    assert used.source == "sensor_measurement"
    assert not hasattr(used, "true_local_sound_speed_mps")


def test_manual_value_has_distinct_provenance() -> None:
    used = use_manual_sound_speed_at_transducer(1502.0)
    assert used.sound_speed_mps == pytest.approx(1502.0)
    assert used.source == "manual"

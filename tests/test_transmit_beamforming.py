from math import radians

import pytest

from hydrosim.acquisition.sound_speed_processing import (
    use_manual_sound_speed_at_transducer,
    use_measured_sound_speed_at_transducer,
)
from hydrosim.acquisition.sound_speed_sensor import (
    SoundSpeedSensorAtTransducer,
    measure_sound_speed_at_transducer,
)
from hydrosim.acquisition.transmit_beamforming import ideal_transmit_steering
from hydrosim.acquisition.transmit_sectors import TransmitSector
from hydrosim.geometry import TransducerArray


def _tx_array() -> TransducerArray:
    return TransducerArray(
        name="tx_array",
        role="tx",
        n_x=5,
        n_y=1,
        d_x=0.1,
        d_y=0.0,
        element_longitudinal_size=0.05,
        element_transverse_size=0.05,
    )


def _sector(angle_rad: float) -> TransmitSector:
    return TransmitSector(
        sector_index=0,
        name="sector_0",
        steering_along_track_angle_rad=angle_rad,
    )


def test_tx_steering_uses_sensor_derived_processing_state_without_truth() -> None:
    measurement = measure_sound_speed_at_transducer(
        true_local_sound_speed_mps=1497.0,
        sensor=SoundSpeedSensorAtTransducer(bias_mps=3.0),
    )
    used = use_measured_sound_speed_at_transducer(measurement)
    law = ideal_transmit_steering(
        transmit_array=_tx_array(),
        sector=_sector(radians(20.0)),
        sound_speed_at_transducer=used,
    )

    assert law.sound_speed_at_transducer.sound_speed_mps == pytest.approx(1500.0)
    assert law.sound_speed_at_transducer.source == "sensor_measurement"
    assert not hasattr(law.sound_speed_at_transducer, "true_local_sound_speed_mps")
    assert min(float(item.hardware_delay_seconds) for item in law.element_delays) == pytest.approx(0.0)


def test_manual_sound_speed_is_explicitly_distinct_from_sensor_measurement() -> None:
    used = use_manual_sound_speed_at_transducer(1480.0)
    law = ideal_transmit_steering(
        transmit_array=_tx_array(),
        sector=_sector(radians(-15.0)),
        sound_speed_at_transducer=used,
    )
    assert law.sound_speed_at_transducer.sound_speed_mps == pytest.approx(1480.0)
    assert law.sound_speed_at_transducer.source == "manual"


def test_off_normal_tx_steering_has_nonuniform_element_delays() -> None:
    law = ideal_transmit_steering(
        transmit_array=_tx_array(),
        sector=_sector(radians(30.0)),
        sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1500.0),
    )
    delays = [float(item.hardware_delay_seconds) for item in law.element_delays]
    assert delays[0] < delays[-1]
    assert delays[-1] > 0.0


def test_nadir_tx_steering_has_equal_element_delays() -> None:
    law = ideal_transmit_steering(
        transmit_array=_tx_array(),
        sector=_sector(0.0),
        sound_speed_at_transducer=use_manual_sound_speed_at_transducer(1500.0),
    )
    assert all(float(item.hardware_delay_seconds) == pytest.approx(0.0) for item in law.element_delays)

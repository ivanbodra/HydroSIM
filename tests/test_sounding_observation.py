import pytest

from hydrosim.acquisition import (
    BottomDetection,
    acoustic_observation_from_detection,
    interpret_observation_constant_sound_speed,
)


def test_detection_becomes_measurement_space_observation() -> None:
    detection = BottomDetection(
        parent_beam_index=7,
        detection_index=2,
        detection_method="phase_zero_crossing",
        arrival_offset_seconds=0.201,
        tx_delay_seconds=0.001,
        twtt_seconds=0.200,
        detected_across_track_angle_rad=0.3,
        quality=0.95,
    )

    observation = acoustic_observation_from_detection(detection)

    assert observation.parent_beam_index == 7
    assert observation.detection_index == 2
    assert observation.detection_method == "phase_zero_crossing"
    assert observation.twtt_seconds == pytest.approx(0.200)
    assert observation.detected_across_track_angle_rad == pytest.approx(0.3)
    assert observation.quality == pytest.approx(0.95)


def test_constant_sound_speed_interpretation_is_explicit_reciprocal_reference() -> None:
    detection = BottomDetection(
        detection_method="amplitude_peak",
        arrival_offset_seconds=0.200,
        tx_delay_seconds=0.0,
        twtt_seconds=0.200,
    )
    observation = acoustic_observation_from_detection(detection)

    interpreted = interpret_observation_constant_sound_speed(
        observation,
        sound_speed_mps=1500.0,
    )

    assert interpreted.two_way_acoustic_path_length_m == pytest.approx(300.0)
    assert interpreted.reciprocal_one_way_range_m == pytest.approx(150.0)
    assert interpreted.propagation_assumption == "stationary_reciprocal_constant_sound_speed"


def test_constant_sound_speed_interpretation_rejects_nonpositive_speed() -> None:
    detection = BottomDetection(
        detection_method="amplitude_peak",
        arrival_offset_seconds=0.1,
        tx_delay_seconds=0.0,
        twtt_seconds=0.1,
    )
    observation = acoustic_observation_from_detection(detection)

    with pytest.raises(ValueError, match="sound_speed_mps must be positive"):
        interpret_observation_constant_sound_speed(observation, sound_speed_mps=0.0)

import math

import pytest

from hydrosim.sonar_equation import AreaBackscatterInput, area_backscatter_term


def test_area_backscatter_term_uses_explicit_scattering_strength_and_area() -> None:
    result = area_backscatter_term(
        AreaBackscatterInput(
            scattering_strength_db_per_m2=-30.0,
            contributing_area_m2=100.0,
        )
    )
    assert result.area_gain_db == pytest.approx(20.0)
    assert result.backscatter_strength_db == pytest.approx(-10.0)


def test_frequency_and_grazing_angle_are_context_not_hidden_model_inputs() -> None:
    a = area_backscatter_term(
        AreaBackscatterInput(
            scattering_strength_db_per_m2=-25.0,
            contributing_area_m2=10.0,
            frequency_hz=100_000.0,
            grazing_angle_rad=math.radians(20.0),
        )
    )
    b = area_backscatter_term(
        AreaBackscatterInput(
            scattering_strength_db_per_m2=-25.0,
            contributing_area_m2=10.0,
            frequency_hz=400_000.0,
            grazing_angle_rad=math.radians(60.0),
        )
    )
    assert a.backscatter_strength_db == pytest.approx(b.backscatter_strength_db)
    assert a.frequency_hz != b.frequency_hz
    assert a.grazing_angle_rad != b.grazing_angle_rad

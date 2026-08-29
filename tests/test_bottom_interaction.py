import math

import pytest

from hydrosim.acquisition import (
    PointTargetStrength,
    SeafloorAreaBackscatter,
    evaluate_bottom_interaction,
    evaluate_point_target_strength,
    evaluate_seafloor_area_backscatter,
)


def test_point_target_strength_converts_db_to_pressure_amplitude() -> None:
    response = evaluate_point_target_strength(PointTargetStrength(target_strength_db=-20.0))
    assert response.interaction_kind == "point_target"
    assert response.effective_backscatter_strength_db == pytest.approx(-20.0)
    assert response.amplitude_ratio == pytest.approx(0.1)


def test_seafloor_scattering_integrates_explicit_area() -> None:
    response = evaluate_seafloor_area_backscatter(
        SeafloorAreaBackscatter(
            scattering_strength_db_per_m2=-30.0,
            insonified_area_m2=100.0,
            incidence_angle_from_normal_rad=0.4,
        )
    )
    # -30 dB/m^2 + 10 log10(100 m^2) = -10 dB for the patch.
    assert response.interaction_kind == "seafloor_area"
    assert response.effective_backscatter_strength_db == pytest.approx(-10.0)
    assert response.amplitude_ratio == pytest.approx(10.0 ** (-10.0 / 20.0))
    assert response.insonified_area_m2 == pytest.approx(100.0)
    assert response.incidence_angle_from_normal_rad == pytest.approx(0.4)


def test_incidence_angle_is_metadata_not_hidden_angular_law() -> None:
    near_normal = SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=-25.0,
        insonified_area_m2=4.0,
        incidence_angle_from_normal_rad=0.1,
    )
    oblique = SeafloorAreaBackscatter(
        scattering_strength_db_per_m2=-25.0,
        insonified_area_m2=4.0,
        incidence_angle_from_normal_rad=1.0,
    )
    a = evaluate_bottom_interaction(near_normal)
    b = evaluate_bottom_interaction(oblique)
    assert a.amplitude_ratio == pytest.approx(b.amplitude_ratio)


def test_seafloor_incidence_angle_is_bounded_to_physical_downward_hemisphere() -> None:
    with pytest.raises(ValueError):
        SeafloorAreaBackscatter(
            scattering_strength_db_per_m2=-20.0,
            insonified_area_m2=1.0,
            incidence_angle_from_normal_rad=math.pi,
        )

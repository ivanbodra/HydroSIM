import math

import pytest

from hydrosim.acquisition import (
    PropagationLossModel,
    one_way_transmission_loss,
    reciprocal_transmission_loss,
)


def test_spherical_spreading_matches_20_log10_range_ratio() -> None:
    model = PropagationLossModel(absorption_db_per_km=0.0)
    loss = one_way_transmission_loss(path_length_m=10.0, model=model)

    assert loss.spreading_loss_db == pytest.approx(20.0)
    assert loss.absorption_loss_db == pytest.approx(0.0)
    assert loss.total_loss_db == pytest.approx(20.0)
    assert loss.amplitude_ratio == pytest.approx(0.1)


def test_absorption_adds_linearly_in_db() -> None:
    model = PropagationLossModel(absorption_db_per_km=2.0)
    loss = one_way_transmission_loss(path_length_m=500.0, model=model)

    expected_spreading = 20.0 * math.log10(500.0)
    assert loss.spreading_loss_db == pytest.approx(expected_spreading)
    assert loss.absorption_loss_db == pytest.approx(1.0)
    assert loss.total_loss_db == pytest.approx(expected_spreading + 1.0)


def test_reciprocal_loss_doubles_db_and_squares_amplitude_ratio() -> None:
    model = PropagationLossModel(absorption_db_per_km=1.0)
    loss = reciprocal_transmission_loss(one_way_path_length_m=100.0, model=model)

    assert loss.two_way_total_loss_db == pytest.approx(2.0 * loss.one_way.total_loss_db)
    assert loss.two_way_amplitude_ratio == pytest.approx(loss.one_way.amplitude_ratio**2)

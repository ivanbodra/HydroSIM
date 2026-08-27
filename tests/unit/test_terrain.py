from math import sqrt

import pytest

from hydrosim.geometry import FlatTerrain, PlaneTerrain, Vector3


def test_flat_terrain_nadir_intersection() -> None:
    terrain = FlatTerrain(depth=100.0)
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=10.0),
        direction=Vector3(x=0.0, y=0.0, z=1.0),
    )

    assert result.valid
    assert result.point is not None
    assert result.point.is_close(Vector3(x=0.0, y=0.0, z=100.0))
    assert result.slant_range == pytest.approx(90.0)


def test_flat_terrain_45_degree_intersection() -> None:
    terrain = FlatTerrain(depth=100.0)
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=0.0, y=1.0, z=1.0),
    )

    assert result.valid
    assert result.point is not None
    assert result.point.is_close(Vector3(x=0.0, y=100.0, z=100.0), atol=1e-9)
    assert result.slant_range == pytest.approx(100.0 * sqrt(2.0))


def test_ray_pointing_away_has_no_intersection() -> None:
    terrain = FlatTerrain(depth=100.0)
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=0.0, y=0.0, z=-1.0),
    )

    assert not result.valid
    assert result.point is None
    assert result.slant_range is None


def test_parallel_ray_has_no_intersection() -> None:
    terrain = FlatTerrain(depth=100.0)
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=1.0, y=0.0, z=0.0),
    )

    assert not result.valid


def test_sloping_plane_known_vertical_solution() -> None:
    # Plane z = 100 + 0.1*y, represented by normal (0, -0.1, 1).
    terrain = PlaneTerrain(
        point=Vector3(x=0.0, y=0.0, z=100.0),
        normal=Vector3(x=0.0, y=-0.1, z=1.0),
    )
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=50.0, z=0.0),
        direction=Vector3(x=0.0, y=0.0, z=1.0),
    )

    assert result.valid
    assert result.point is not None
    assert result.point.is_close(Vector3(x=0.0, y=50.0, z=105.0))
    assert result.slant_range == pytest.approx(105.0)


def test_sloping_plane_known_oblique_solution() -> None:
    # Same plane z = 100 + 0.1*y. Ray has y=z before normalization.
    # At intersection y=z and z=100+0.1y => z=100/0.9.
    terrain = PlaneTerrain(
        point=Vector3(x=0.0, y=0.0, z=100.0),
        normal=Vector3(x=0.0, y=-0.1, z=1.0),
    )
    expected = 100.0 / 0.9
    result = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=0.0, y=1.0, z=1.0),
    )

    assert result.valid
    assert result.point is not None
    assert result.point.is_close(Vector3(x=0.0, y=expected, z=expected), atol=1e-9)
    assert result.slant_range == pytest.approx(expected * sqrt(2.0))


def test_direction_magnitude_does_not_change_slant_range() -> None:
    terrain = FlatTerrain(depth=50.0)
    unit = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=0.0, y=0.0, z=1.0),
    )
    scaled = terrain.intersect_ray(
        origin=Vector3(x=0.0, y=0.0, z=0.0),
        direction=Vector3(x=0.0, y=0.0, z=20.0),
    )

    assert unit.slant_range == pytest.approx(scaled.slant_range)


def test_zero_direction_is_rejected() -> None:
    terrain = FlatTerrain(depth=50.0)

    with pytest.raises(ValueError, match="direction"):
        terrain.intersect_ray(
            origin=Vector3(x=0.0, y=0.0, z=0.0),
            direction=Vector3(x=0.0, y=0.0, z=0.0),
        )


def test_zero_plane_normal_is_rejected() -> None:
    with pytest.raises(ValueError, match="normal"):
        PlaneTerrain(
            point=Vector3(x=0.0, y=0.0, z=100.0),
            normal=Vector3(x=0.0, y=0.0, z=0.0),
        )

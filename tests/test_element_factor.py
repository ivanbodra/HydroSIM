from math import isclose, sqrt

from hydrosim.acquisition import rectangular_element_factor
from hydrosim.geometry import ArrayElement, Vector3


def _element(*, longitudinal: float, transverse: float) -> ArrayElement:
    return ArrayElement(
        index_x=0,
        index_y=0,
        position=Vector3(x=0.0, y=0.0, z=0.0),
        longitudinal_size=longitudinal,
        transverse_size=transverse,
    )


def test_boresight_factor_is_unity():
    result = rectangular_element_factor(
        element=_element(longitudinal=0.01, transverse=0.02),
        direction_array_frame=Vector3(x=0.0, y=0.0, z=1.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.longitudinal_factor, 1.0, abs_tol=1e-15)
    assert isclose(result.transverse_factor, 1.0, abs_tol=1e-15)
    assert isclose(result.amplitude, 1.0, abs_tol=1e-15)
    assert isclose(result.power, 1.0, abs_tol=1e-15)


def test_one_wavelength_element_has_first_null_at_ninety_degrees():
    # lambda = c/f = 0.01 m. For a=lambda, ka/2 = pi, so the first null
    # occurs when u_x = sin(theta) = 1, i.e. at 90 degrees in the XZ plane.
    result = rectangular_element_factor(
        element=_element(longitudinal=0.01, transverse=0.001),
        direction_array_frame=Vector3(x=1.0, y=0.0, z=0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert isclose(result.amplitude, 0.0, abs_tol=1e-12)


def test_half_wavelength_element_is_broad_at_ninety_degrees():
    # a=lambda/2 gives sinc(pi/2)=2/pi at 90 degrees.
    result = rectangular_element_factor(
        element=_element(longitudinal=0.005, transverse=0.001),
        direction_array_frame=Vector3(x=1.0, y=0.0, z=0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    expected = 2.0 / 3.141592653589793
    assert isclose(result.amplitude, expected, rel_tol=1e-12)
    assert isclose(result.power, expected * expected, rel_tol=1e-12)


def test_rectangular_element_separates_longitudinal_and_transverse_directivity():
    # At lambda=0.01 m, choose a=lambda and b=lambda/2. A 45-degree direction
    # in the XY plane therefore samples different sinc arguments on each axis.
    inv_sqrt2 = 1.0 / sqrt(2.0)
    result = rectangular_element_factor(
        element=_element(longitudinal=0.01, transverse=0.005),
        direction_array_frame=Vector3(x=inv_sqrt2, y=inv_sqrt2, z=0.0),
        frequency_hz=150_000.0,
        sound_speed_mps=1500.0,
    )

    assert result.longitudinal_factor < result.transverse_factor
    assert 0.0 < result.amplitude < 1.0

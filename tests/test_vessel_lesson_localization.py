from hydrosim.app.localization import Localizer


def test_vessel_lesson_copy_is_available_in_both_supported_locales() -> None:
    keys = (
        "vessel.title",
        "vessel.question",
        "vessel.vrp",
        "vessel.gnss",
        "vessel.imu",
        "vessel.transducer",
        "vessel.waterline",
        "vessel.water_level",
        "vessel.transducer_depth",
        "vessel.observation",
        "vessel.boundary",
        "vessel.not_shown",
    )

    for locale in ("en", "pt-BR"):
        localizer = Localizer(locale)
        for key in keys:
            assert localizer.text(key)


def test_vessel_boundary_copy_keeps_reference_systems_separate() -> None:
    en = Localizer("en")
    pt = Localizer("pt-BR")

    assert "no datum-to-VRP relationship" in en.text("vessel.boundary")
    assert "nenhuma relação datum–VRP" in pt.text("vessel.boundary")

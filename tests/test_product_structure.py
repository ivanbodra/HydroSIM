from hydrosim.product import HYDROSIM_PRODUCT, find_submodule


def test_product_has_three_top_level_modules() -> None:
    assert [module.id for module in HYDROSIM_PRODUCT] == [
        "didactic-explorer",
        "patch-test",
        "survey-simulator",
    ]


def test_all_intended_submodules_exist() -> None:
    counts = {module.id: len(module.submodules) for module in HYDROSIM_PRODUCT}
    assert counts == {
        "didactic-explorer": 8,
        "patch-test": 5,
        "survey-simulator": 10,
    }


def test_module_submodule_and_item_ids_are_unique_in_scope() -> None:
    module_ids = [module.id for module in HYDROSIM_PRODUCT]
    assert len(module_ids) == len(set(module_ids))

    submodule_ids = [submodule.id for module in HYDROSIM_PRODUCT for submodule in module.submodules]
    assert len(submodule_ids) == len(set(submodule_ids))

    for module in HYDROSIM_PRODUCT:
        for submodule in module.submodules:
            item_ids = [item.id for item in submodule.items]
            assert item_ids
            assert len(item_ids) == len(set(item_ids)), submodule.id


def test_scientific_dependencies_are_explicit() -> None:
    infrastructure_only = {
        "reset",
        "adjustment",
        "estimated",
        "truth-estimated",
        "run-reset-check",
        "bias",
        "biases",
        "displacement",
        "estimate",
        "solutions",
        "corrected",
        "before-after",
        "new-scenario",
        "report",
        "summary-reset",
    }
    for module in HYDROSIM_PRODUCT:
        for submodule in module.submodules:
            for item in submodule.items:
                if item.id in infrastructure_only:
                    continue
                assert item.bindings or item.required_capability, (
                    module.id,
                    submodule.id,
                    item.id,
                )


def test_known_scientific_bindings_are_preserved() -> None:
    motion = find_submodule("motion")
    roll = next(item for item in motion.items if item.id == "roll")
    assert any(binding.path == "hydrosim.app.motion_lesson.MotionLessonControls" for binding in roll.bindings)

    vessel = find_submodule("vessel-sensors-vertical-references")
    water_level = next(item for item in vessel.items if item.id == "water-level")
    assert any(binding.path == "hydrosim.app.vessel_vertical_reference" for binding in water_level.bindings)

    patch_roll = find_submodule("roll-calibration")
    scenario = next(item for item in patch_roll.items if item.id == "scenario")
    assert any(binding.path == "hydrosim.scenarios.roll_offset" for binding in scenario.bindings)

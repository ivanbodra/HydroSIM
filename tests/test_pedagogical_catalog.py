from hydrosim.app.pedagogical_catalog import (
    PEDAGOGICAL_EXPERIENCES,
    experience_by_id,
    experiences_for,
)


def test_catalog_exposes_exact_31_experiences():
    assert len(PEDAGOGICAL_EXPERIENCES) == 31
    assert len(experiences_for("didactic")) == 18
    assert len(experiences_for("patch-test")) == 6
    assert len(experiences_for("acquisition")) == 7


def test_catalog_ids_are_unique_and_follow_new_generation_structure():
    ids = [item.id for item in PEDAGOGICAL_EXPERIENCES]
    assert len(ids) == len(set(ids))
    assert ids[:18] == [f"PED-D{index}" for index in range(1, 19)]
    assert ids[18:24] == [f"P{index}" for index in range(1, 7)]
    assert ids[24:] == [f"A{index}" for index in range(1, 8)]


def test_only_independently_instantiable_lessons_are_available():
    available = {item.id for item in PEDAGOGICAL_EXPERIENCES if item.availability == "available"}
    assert available == {"PED-D2", "PED-D3", "PED-D8", "PED-D12", "PED-D15"}
    assert all(experience_by_id(item).page_builder for item in available)


def test_all_experiences_have_bilingual_learner_names():
    for item in PEDAGOGICAL_EXPERIENCES:
        assert item.name("en")
        assert item.name("pt-BR")
        assert item.name_en != item.name_pt_br or item.id in {"P6", "A4", "A6"}

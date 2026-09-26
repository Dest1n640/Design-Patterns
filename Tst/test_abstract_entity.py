"""Юнит-тесты для Src.Core.abstract_entity.abstract_model."""
from Src.Core.abstract_entity import abstract_model


class _abstract_entity(abstract_model):
    """Заглушка-наследник для тестирования abstract_model."""
    pass


def test_id_is_not_empty_constructor_generated_on_creation():
    """При создании сущности id сразу не пустой."""
    entity = _abstract_entity()
    assert entity.id is not None
    assert entity.id != ""


def test_ids_are_different_constructor_two_instances_get_different_id():
    """Два новых экземпляра получают разные id."""
    entity1 = _abstract_entity()
    entity2 = _abstract_entity()
    assert entity1.id != entity2.id


def test_entities_are_not_equal_eq_two_instances_with_different_id_are_not_equal():
    """Сущности с разным id не считаются равными."""
    entity1 = _abstract_entity()
    entity2 = _abstract_entity()
    assert entity1 != entity2

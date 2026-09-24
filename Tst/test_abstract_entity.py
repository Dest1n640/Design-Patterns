"""Юнит-тесты для Src.Core.abstract_entity.abstract_model."""
from Src.Core.abstract_entity import abstract_model


class _abstract_entity(abstract_model):
    """Заглушка-наследник для тестирования abstract_model."""
    pass


def test_IdIsNotEmpty_Constructor_GeneratedOnCreation():
    """При создании сущности id сразу не пустой."""
    entity = _abstract_entity()
    assert entity.id is not None
    assert entity.id != ""


def test_IdsAreDifferent_Constructor_TwoInstancesGetDifferentId():
    """Два новых экземпляра получают разные id."""
    entity1 = _abstract_entity()
    entity2 = _abstract_entity()
    assert entity1.id != entity2.id


def test_EntitiesAreNotEqual_Eq_TwoInstancesWithDifferentIdAreNotEqual():
    """Сущности с разным id не считаются равными."""
    entity1 = _abstract_entity()
    entity2 = _abstract_entity()
    assert entity1 != entity2

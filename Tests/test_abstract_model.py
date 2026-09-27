"""Юнит-тесты для Src.Core.abstract_model.AbstractModel."""

from Src.Core.abstract_model import AbstractModel


class _AbstractModelStub(AbstractModel):
    """Заглушка-наследник для тестирования AbstractModel."""


def test_abstract_model__constructor__id_is_not_empty():
    """При создании сущности id сразу не пустой."""
    entity = _AbstractModelStub()
    assert entity.id is not None
    assert entity.id != ""


def test_abstract_model__constructor__ids_are_different_across_instances():
    """Два новых экземпляра получают разные id."""
    entity1 = _AbstractModelStub()
    entity2 = _AbstractModelStub()
    assert entity1.id != entity2.id


def test_abstract_model__eq__different_id_instances_are_not_equal():
    """Сущности с разным id не считаются равными."""
    entity1 = _AbstractModelStub()
    entity2 = _AbstractModelStub()
    assert entity1 != entity2

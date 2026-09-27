"""Юнит-тесты для Src.models.warehouse_model.warehouse_model."""
import pytest

from Src.models.warehouse_model import warehouse_model
from Src.models.premises_model import premises_model
from Src.models.restaurant_model import restaurant_model
from Src.models.production_shop_model import production_shop_model
from Src.Core.exception import validation_exception


def test_valid_warehouse_created_constructor_restaurant_owner_accepted():
    """Валидное создание склада с владельцем-рестораном сохраняет все поля."""
    premises = premises_model("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    owner = restaurant_model("Ромашка на Тверской")
    warehouse = warehouse_model("Основной склад", premises, owner)
    assert warehouse.premises is premises
    assert warehouse.warehouse_owner is owner


def test_valid_warehouse_created_constructor_production_shop_owner_accepted():
    """Валидное создание склада с владельцем-производственным цехом сохраняет все поля."""
    premises = premises_model("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    owner = production_shop_model("Центральный цех")
    warehouse = warehouse_model("Цеховой склад", premises, owner)
    assert warehouse.premises is premises
    assert warehouse.warehouse_owner is owner


def test_validation_exception_constructor_invalid_premises_raises():
    """Помещение, не являющееся premises_model, вызывает исключение валидации."""
    owner = restaurant_model("Ромашка на Тверской")
    with pytest.raises(validation_exception):
        warehouse_model("Основной склад", "не помещение", owner)


def test_validation_exception_constructor_invalid_owner_raises():
    """Владелец, не являющийся рестораном или цехом, вызывает исключение валидации."""
    premises = premises_model("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    with pytest.raises(validation_exception):
        warehouse_model("Основной склад", premises, "не владелец")

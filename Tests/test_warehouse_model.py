"""Юнит-тесты для Src.Models.warehouse_model.WarehouseModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.warehouse_model import WarehouseModel


def test_warehouse_model__constructor__restaurant_owner_accepted():
    """Валидное создание склада с владельцем-рестораном сохраняет все поля."""
    premises = PremisesModel("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    owner = RestaurantModel("Ромашка на Тверской")
    warehouse = WarehouseModel("Основной склад", premises, owner)
    assert warehouse.premises is premises
    assert warehouse.warehouse_owner is owner


def test_warehouse_model__constructor__production_shop_owner_accepted():
    """Валидное создание склада с владельцем-цехом сохраняет все поля."""
    premises = PremisesModel("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    owner = ProductionShopModel("Центральный цех")
    warehouse = WarehouseModel("Цеховой склад", premises, owner)
    assert warehouse.premises is premises
    assert warehouse.warehouse_owner is owner


def test_warehouse_model__constructor__invalid_premises_raises():
    """Помещение, не являющееся PremisesModel, вызывает исключение валидации."""
    owner = RestaurantModel("Ромашка на Тверской")
    with pytest.raises(ValidationException):
        WarehouseModel("Основной склад", "не помещение", owner)


def test_warehouse_model__constructor__invalid_owner_raises():
    """Владелец, не являющийся рестораном или цехом, вызывает исключение валидации."""
    premises = PremisesModel("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)
    with pytest.raises(ValidationException):
        WarehouseModel("Основной склад", premises, "не владелец")

"""Юнит-тесты для Src.Models.warehouse_model.WarehouseModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.warehouse_model import WarehouseModel


def _build_premises():
    """Строит валидное помещение склада."""
    return PremisesModel.create("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)


@pytest.mark.parametrize(
    "owner", [RestaurantModel.create("Ромашка"), ProductionShopModel.create("Цех")]
)
def test_warehouse_model__create__restaurant_or_shop_owner_is_accepted(owner):
    """Владельцем склада может быть ресторан или производственный цех."""
    # Подготовка
    premises = _build_premises()

    # Действия
    warehouse = WarehouseModel.create("Склад", premises, owner)

    # Проверки
    assert warehouse.warehouse_owner is owner


def test_warehouse_model__create__other_owner_type_raises():
    """Владелец, не являющийся рестораном или цехом, вызывает исключение валидации."""
    # Подготовка
    premises = _build_premises()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        WarehouseModel.create("Склад", premises, "не владелец")

    # Проверки
    assert isinstance(exc_info.value, ValidationException)

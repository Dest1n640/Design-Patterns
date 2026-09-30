"""Юнит-тесты для Src.Models.warehouse_model.WarehouseModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.premises_model import PremisesModel
from Src.Models.production_shop_model import ProductionShopModel
from Src.Models.restaurant_model import RestaurantModel
from Src.Models.warehouse_model import WarehouseModel


def _build_premises():
    """Строит валидное помещение склада."""
    return PremisesModel("Помещение склада", "г. Москва, ул. Ленина, 1", 50.0)


@pytest.mark.parametrize(
    "owner", [RestaurantModel("Ромашка"), ProductionShopModel("Цех")]
)
def test_warehouse_model__constructor__restaurant_or_shop_owner_is_accepted(owner):
    """Владельцем склада может быть ресторан или производственный цех."""
    WarehouseModel("Склад", _build_premises(), owner)


def test_warehouse_model__constructor__other_owner_type_raises():
    """Владелец, не являющийся рестораном или цехом, вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        WarehouseModel("Склад", _build_premises(), "не владелец")

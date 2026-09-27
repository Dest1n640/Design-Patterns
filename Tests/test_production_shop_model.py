"""Юнит-тесты для Src.Models.production_shop_model.ProductionShopModel."""

from Src.Models.production_shop_model import ProductionShopModel


def test_production_shop_model__constructor__name_is_set():
    """Валидное создание цеха сохраняет переданное имя (смоук-тест)."""
    shop = ProductionShopModel("Центральный цех")
    assert shop.name == "Центральный цех"

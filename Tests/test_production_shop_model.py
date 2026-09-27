"""Юнит-тесты для Src.models.production_shop_model.production_shop_model."""
from Src.models.production_shop_model import production_shop_model


def test_valid_production_shop_created_constructor_name_is_set():
    """Валидное создание производственного цеха сохраняет переданное имя (смоук-тест)."""
    shop = production_shop_model("Центральный цех")
    assert shop.name == "Центральный цех"

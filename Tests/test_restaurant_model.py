"""Юнит-тесты для Src.Models.restaurant_model.restaurant_model."""
from Src.Models.restaurant_model import restaurant_model


def test_valid_restaurant_created_constructor_name_is_set():
    """Валидное создание ресторана сохраняет переданное имя (смоук-тест)."""
    restaurant = restaurant_model("Ромашка на Тверской")
    assert restaurant.name == "Ромашка на Тверской"

"""Юнит-тесты для Src.models.restaurant_model.restaurant_model."""
from Src.models.restaurant_model import restaurant_model


def test_ValidRestaurantCreated_Constructor_NameIsSet():
    """Валидное создание ресторана сохраняет переданное имя (смоук-тест)."""
    restaurant = restaurant_model("Ромашка на Тверской")
    assert restaurant.name == "Ромашка на Тверской"

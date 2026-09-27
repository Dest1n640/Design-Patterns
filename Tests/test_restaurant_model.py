"""Юнит-тесты для Src.Models.restaurant_model.RestaurantModel."""

from Src.Models.restaurant_model import RestaurantModel


def test_restaurant_model__constructor__name_is_set():
    """Валидное создание ресторана сохраняет переданное имя (смоук-тест)."""
    restaurant = RestaurantModel("Ромашка на Тверской")
    assert restaurant.name == "Ромашка на Тверской"

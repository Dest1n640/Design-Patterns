from typing import Self

from Src.Core.named_model import NamedModel


class RestaurantModel(NamedModel):
    """Класс ресторана — точки сети."""

    @classmethod
    def create_default_restaurants(cls) -> list[Self]:
        """Фабричный метод: создаёт рестораны сети."""
        return [cls("Ромашка Центральный"), cls("Ромашка Северный")]

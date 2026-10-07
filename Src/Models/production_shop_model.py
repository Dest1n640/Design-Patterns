from typing import Self

from Src.Core.named_model import NamedModel


class ProductionShopModel(NamedModel):
    """Класс производственного цеха."""

    @classmethod
    def create_default_production_shops(cls) -> list[Self]:
        """Фабричный метод: создаёт производственный цех."""
        return [cls("Производственный цех")]

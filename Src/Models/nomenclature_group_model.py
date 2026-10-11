from typing import Self

from Src.Core.named_model import NamedModel


class NomenclatureGroupModel(NamedModel):
    """Класс группы номенклатуры — классификатора номенклатуры."""

    @classmethod
    def create_default_groups(cls) -> list[Self]:
        """Фабричный метод: создаёт группы номенклатуры."""
        names = ["Бакалея", "Молочные продукты", "Овощи", "Полуфабрикаты", "Блюда"]
        return [cls(name) for name in names]

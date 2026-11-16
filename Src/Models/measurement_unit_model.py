from typing import Self

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation


class MeasurementUnitModel(NamedModel):
    """Класс единицы измерения номенклатуры."""

    _BASE_UNIT_ERROR = "Базовая единица измерения указана некорректно"

    def __init__(self) -> None:
        """Инициализирует единицу измерения без заполненных обязательных полей."""
        super().__init__()
        self.__coefficient: int | float | None = None
        self.__base_unit: Self | None = None

    @classmethod
    def create(
        cls, name: str, coefficient: int | float, base_unit: Self | None = None
    ) -> Self:
        """Создаёт единицу измерения с проверенными полями и базовой единицей."""
        model = cls()
        model.name = name
        model.base_unit = base_unit
        model.coefficient = coefficient
        model.validate()
        return model

    @property
    def coefficient(self):
        """Возвращает коэффициент пересчёта в базовую единицу измерения."""
        return self.__coefficient

    @property
    def base_unit(self):
        """Возвращает базовую единицу измерения."""
        return self.__base_unit

    @coefficient.setter
    def coefficient(self, new_coefficient: int | float):
        """Устанавливает коэффициент пересчёта в базовую единицу измерения."""
        coefficient = Validation.validate_positive_number(
            new_coefficient, "coefficient"
        )
        if (
            self.__coefficient is not None
            and self.__base_unit is None
            and coefficient != 1
        ):
            raise ValidationException("base_unit", self._BASE_UNIT_ERROR)
        self.__coefficient = coefficient

    @base_unit.setter
    def base_unit(self, new_base_unit: Self | None):
        """Устанавливает базовую единицу измерения."""
        self.__base_unit = self._validate_base_unit(new_base_unit)

    @property
    def base_coefficient(self) -> int | float:
        """Возвращает итоговый коэффициент пересчёта в корневую базовую единицу."""
        if self.base_unit is None:
            return self.coefficient
        return self.coefficient * self.base_unit.base_coefficient

    def _validate_base_unit(self, value: Self | None) -> Self | None:
        """Проверяет базовую единицу с учётом заданного коэффициента."""
        if value is None:
            if self.__coefficient is not None and self.__coefficient != 1:
                raise ValidationException("base_unit", self._BASE_UNIT_ERROR)
            return None
        return Validation.validate_instance(
            value, MeasurementUnitModel, "base_unit", self._BASE_UNIT_ERROR
        )

    @classmethod
    def create_gram(cls) -> Self:
        """Фабричный метод: создаёт грамм."""
        return cls.create("грамм", 1)

    @classmethod
    def create_kilogram(cls, gram: Self | None = None) -> Self:
        """Фабричный метод: создаёт килограмм, кратный грамму."""
        return cls.create("килограмм", 1000, gram or cls.create_gram())

    @classmethod
    def create_milliliter(cls) -> Self:
        """Фабричный метод: создаёт миллилитр."""
        return cls.create("миллилитр", 1)

    @classmethod
    def create_liter(cls, milliliter: Self | None = None) -> Self:
        """Фабричный метод: создаёт литр, кратный миллилитру."""
        return cls.create("литр", 1000, milliliter or cls.create_milliliter())

    @classmethod
    def create_piece(cls) -> Self:
        """Фабричный метод: создаёт штуку."""
        return cls.create("штука", 1)

    @classmethod
    def create_default_units(cls) -> list[Self]:
        """Фабричный метод: создаёт базовые единицы измерения и кратные им."""
        gram = cls.create_gram()
        milliliter = cls.create_milliliter()
        return [
            gram,
            cls.create_kilogram(gram),
            milliliter,
            cls.create_liter(milliliter),
            cls.create_piece(),
        ]

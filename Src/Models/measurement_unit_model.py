from typing import Self

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel


class MeasurementUnitModel(NamedModel):
    """Класс единицы измерения номенклатуры."""

    def __init__(
        self, name: str, coefficient: int | float, base_unit: Self | None = None
    ):
        """Конструктор единицы измерения."""
        super().__init__(name)
        if not isinstance(coefficient, int | float) or coefficient <= 0:
            raise ValidationException("coefficient", "Коэффицент указан некорректно")
        self.__coefficient = coefficient
        if base_unit is None and coefficient != 1:
            raise ValidationException(
                "base_unit", "Базовая единица измерения указана некорректно"
            )
        self.__base_unit = base_unit

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
        if not isinstance(new_coefficient, int | float) or new_coefficient <= 0:
            raise ValidationException("coefficient", "Коэффицент указан некорректно")
        self.__coefficient = new_coefficient

    @base_unit.setter
    def base_unit(self, new_base_unit: Self | None):
        """Устанавливает базовую единицу измерения."""
        if (
            not isinstance(new_base_unit, MeasurementUnitModel)
            and new_base_unit is None
            and self.__coefficient != 1
        ):
            raise ValidationException(
                "base_unit", "Базовая единица измерения указана некорректно"
            )
        self.__base_unit = new_base_unit

    @property
    def base_coefficient(self) -> int | float:
        """Возвращает итоговый коэффициент пересчёта в корневую базовую единицу."""
        if self.base_unit is None:
            return self.coefficient
        return self.coefficient * self.base_unit.base_coefficient

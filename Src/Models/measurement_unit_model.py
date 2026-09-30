from typing import Self

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation


class MeasurementUnitModel(NamedModel):
    """Класс единицы измерения номенклатуры."""

    _BASE_UNIT_ERROR = "Базовая единица измерения указана некорректно"

    def __init__(
        self, name: str, coefficient: int | float, base_unit: Self | None = None
    ):
        """Конструктор единицы измерения."""
        super().__init__(name)
        self.__coefficient = Validation.validate_positive_number(
            coefficient, "coefficient"
        )
        self.__base_unit = self._validate_base_unit(base_unit)

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
        self.__coefficient = Validation.validate_positive_number(
            new_coefficient, "coefficient"
        )

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
        """Проверяет базовую единицу: None допустим только при коэффициенте 1."""
        if value is None:
            if self.__coefficient != 1:
                raise ValidationException("base_unit", self._BASE_UNIT_ERROR)
            return None
        return Validation.validate_instance(
            value, MeasurementUnitModel, "base_unit", self._BASE_UNIT_ERROR
        )

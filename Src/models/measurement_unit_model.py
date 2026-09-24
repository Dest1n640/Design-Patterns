from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception
from typing import Self

class measurement_unit_model(named_entity):
    """Класс единицы измерения номенклатуры"""

    def __init__(self, name: str, coefficient: int | float, base_unit: Self | None = None):
        """
        Конструктор единицы измерения.

        :name: наименование единицы (например, "кг")
        :coefficient: во сколько раз эта единица больше base_unit
        :base_unit: базовая единица измерения; None — единица сама себе база
        """
        super().__init__(name)
        if not isinstance(coefficient, int | float) or coefficient <= 0:
          raise validation_exception("coefficient", "Коэффицент указан некорректно")
        self.__coefficient = coefficient
        if base_unit is None and coefficient != 1:
           raise validation_exception("base_unit", "Базовая единица измерения указана некорректно")
        self.__base_unit = base_unit

    @property
    def coefficient(self):
        """Возвращает коэффициент пересчёта в базовую единицу измерения"""
        return self.__coefficient

    @property
    def base_unit(self):
        """Возвращает базовую единицу измерения"""
        return self.__base_unit

    @coefficient.setter
    def coefficient(self, new_coefficient: int | float):
        """
        Устанавливает коэффициент пересчёта в базовую единицу измерения

        :new_coefficient: новый коэффициент пересчёта
        """
        if not isinstance(new_coefficient, int | float) or new_coefficient <= 0:
            raise validation_exception("coefficient", "Коэффицент указан некорректно")
        self.__coefficient = new_coefficient

    @base_unit.setter
    def base_unit(self, new_base_unit: Self | None):
        """
        Устанавливает базовую единицу измерения

        :new_base_unit: новая базовая единица измерения; None — единица сама себе база
        """
        if new_base_unit is None and self.__coefficient != 1:
            raise validation_exception("base_unit", "Базовая единица измерения указана некорректно")
        self.__base_unit = new_base_unit

    @property
    def base_coefficient(self) -> int | float:
        """
        Возвращает итоговый коэффициент пересчёта в самую глубокую
        (корневую) базовую единицу измерения — поднимается по цепочке
        base_unit рекурсивно и перемножает коэффициенты по пути.
        """
        if self.base_unit is None:
            return self.coefficient
        return self.coefficient * self.base_unit.base_coefficient

from Src.Core.named_entity import named_entity
from typing import Self

class measurement_unit_model(named_entity):

    def __init__(self, name: str, coefficient: int | float, base_unit: Self | None = None):
        """
        Конструктор единицы измерения.

        :name: наименование единицы (например, "кг")
        :coefficient: во сколько раз эта единица больше base_unit
        :base_unit: базовая единица измерения; None — единица сама себе база
        """
        super.__init__(name)
        if isinstance(coefficient, int | float) and coefficient > 0:
          self.__coefficient = coefficient
        if base_unit is None and base_unit != 1:
           raise ValueError
        self.__base_unit = base_unit

    @property
    def coefficient(self):
        return self.__coefficient

    @property
    def base_unit(self):
        return self.__base_unit

    @coefficient.setter
    def coefficient(self, new_coefficient: int | float):
        if isinstance(new_coefficient, int | float) and new_coefficient > 0:
            self.__coefficient = new_coefficient

    @property
    def base_unit(self):
        return self.__base_unit

    @base_unit.setter
    def base_unit(self, new_base_unit: Self | None):
        if new_base_unit is None and new_base_unit != 1:
            raise ValueError
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

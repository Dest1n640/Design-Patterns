from typing import Self

from Src.Core.named_model import NamedModel
from Src.Core.position_type import PositionType
from Src.Core.validation import Validation
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel


class NomenclatureModel(NamedModel):
    """Класс номенклатуры — единицы учёта товара, сырья, полуфабриката или блюда."""

    _NAME_MAX_LENGTH = 50
    _FULL_NAME_MAX_LENGTH = 255

    def __init__(
        self,
        name: str,
        full_name: str,
        group: NomenclatureGroupModel,
        measurement_unit: MeasurementUnitModel,
        position_type: PositionType,
    ):
        """Конструктор номенклатуры."""
        super().__init__(name)
        self.full_name = full_name
        self.group = group
        self.measurement_unit = measurement_unit
        self.position_type = position_type

    @property
    def full_name(self):
        """Возвращает полное наименование номенклатурной позиции."""
        return self.__full_name

    @property
    def group(self):
        """Возвращает группу номенклатуры."""
        return self.__group

    @property
    def measurement_unit(self):
        """Возвращает единицу измерения позиции."""
        return self.__measurement_unit

    @property
    def position_type(self):
        """Возвращает тип позиции."""
        return self.__position_type

    @full_name.setter
    def full_name(self, new_full_name: str):
        """Устанавливает полное наименование номенклатурной позиции."""
        self.__full_name = Validation.validate_string(
            new_full_name, "full_name", max_length=self._FULL_NAME_MAX_LENGTH
        )

    @group.setter
    def group(self, new_group: NomenclatureGroupModel):
        """Устанавливает группу номенклатуры."""
        self.__group = Validation.validate_instance(
            new_group,
            NomenclatureGroupModel,
            "group",
            "Группа номенклатуры указана некорректно",
        )

    @measurement_unit.setter
    def measurement_unit(self, new_measurement_unit: MeasurementUnitModel):
        """Устанавливает единицу измерения позиции."""
        self.__measurement_unit = Validation.validate_instance(
            new_measurement_unit,
            MeasurementUnitModel,
            "measurement_unit",
            "Единица измерения указана некорректно",
        )

    @position_type.setter
    def position_type(self, new_position_type: PositionType):
        """Устанавливает тип позиции."""
        self.__position_type = Validation.validate_instance(
            new_position_type,
            PositionType,
            "position_type",
            "Тип позиции указан некорректно",
        )

    def _validate_name(self, value: str) -> str:
        """Проверяет наименование: непустая строка, максимум 50 символов."""
        return Validation.validate_string(
            value, "name", max_length=self._NAME_MAX_LENGTH
        )

    @classmethod
    def create_margherita_nomenclature(
        cls,
        groups: dict[str, NomenclatureGroupModel],
        units: dict[str, MeasurementUnitModel],
    ) -> list[Self]:
        """Фабричный метод: создаёт номенклатуру «Пиццы Маргарита» из справочников."""
        return [
            cls(
                "Мука пшеничная",
                "Мука пшеничная высшего сорта",
                groups["Бакалея"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Дрожжи сухие",
                "Дрожжи хлебопекарные сухие",
                groups["Бакалея"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Соль",
                "Соль поваренная пищевая",
                groups["Бакалея"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Масло оливковое",
                "Масло оливковое Extra Virgin",
                groups["Бакалея"],
                units["миллилитр"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Сыр Моцарелла",
                "Сыр Моцарелла для пиццы 45%",
                groups["Молочные продукты"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Томаты",
                "Томаты свежие",
                groups["Овощи"],
                units["килограмм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Базилик",
                "Базилик зелёный свежий",
                groups["Овощи"],
                units["грамм"],
                PositionType.RAW_MATERIAL,
            ),
            cls(
                "Тесто для пиццы",
                "Тесто дрожжевое для пиццы",
                groups["Полуфабрикаты"],
                units["килограмм"],
                PositionType.SEMI_FINISHED,
            ),
            cls(
                "Пицца Маргарита",
                "Пицца Маргарита 30 см",
                groups["Блюда"],
                units["штука"],
                PositionType.DISH,
            ),
        ]

from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel
from Src.Core.position_type import PositionType
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
        self._validate_full_name(full_name)
        self.__full_name = full_name
        self._validate_group(group)
        self.__group = group
        self._validate_measurement_unit(measurement_unit)
        self.__measurement_unit = measurement_unit
        self._validate_position_type(position_type)
        self.__position_type = position_type

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
        self._validate_full_name(new_full_name)
        self.__full_name = new_full_name

    @group.setter
    def group(self, new_group: NomenclatureGroupModel):
        """Устанавливает группу номенклатуры."""
        self._validate_group(new_group)
        self.__group = new_group

    @measurement_unit.setter
    def measurement_unit(self, new_measurement_unit: MeasurementUnitModel):
        """Устанавливает единицу измерения позиции."""
        self._validate_measurement_unit(new_measurement_unit)
        self.__measurement_unit = new_measurement_unit

    @position_type.setter
    def position_type(self, new_position_type: PositionType):
        """Устанавливает тип позиции."""
        self._validate_position_type(new_position_type)
        self.__position_type = new_position_type

    def _validate_name(self, value: str) -> None:
        """Проверка обычного наименования: базовая проверка + максимум 50 символов."""
        super()._validate_name(value)
        if len(value) > self._NAME_MAX_LENGTH:
            raise ValidationException(
                "name", f"Имя длиннее {self._NAME_MAX_LENGTH} символов"
            )

    def _validate_full_name(self, value: str) -> None:
        """Проверка полного наименования: непустая строка, максимум 255 символов."""
        if value is None or not isinstance(value, str) or len(value) == 0:
            raise ValidationException(
                "full_name", "Полное наименование не должно быть пустым"
            )
        if len(value) > self._FULL_NAME_MAX_LENGTH:
            raise ValidationException(
                "full_name",
                f"Полное наименование длиннее {self._FULL_NAME_MAX_LENGTH} символов",
            )

    def _validate_group(self, value: NomenclatureGroupModel) -> None:
        """Проверка группы: должна быть экземпляром NomenclatureGroupModel."""
        if not isinstance(value, NomenclatureGroupModel):
            raise ValidationException(
                "group", "Группа номенклатуры указана некорректно"
            )

    def _validate_measurement_unit(self, value: MeasurementUnitModel) -> None:
        """Проверка единицы измерения: должна быть экземпляром MeasurementUnitModel."""
        if not isinstance(value, MeasurementUnitModel):
            raise ValidationException(
                "measurement_unit", "Единица измерения указана некорректно"
            )

    def _validate_position_type(self, value: PositionType) -> None:
        """Проверка типа позиции: должен быть значением перечисления PositionType."""
        if not isinstance(value, PositionType):
            raise ValidationException("position_type", "Тип позиции указан некорректно")

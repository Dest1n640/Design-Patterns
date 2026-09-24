from Src.Core.named_entity import named_entity
from Src.Core.position_type import position_type
from Src.models.nomenclature_group_model import nomenclature_group_model
from Src.models.measurement_unit_model import measurement_unit_model
from Src.Core.exception import validation_exception

class nomenclature_model(named_entity):
  """Класс номенклатуры — единицы учёта товара, сырья, полуфабриката или блюда"""
  _NAME_MAX_LENGTH = 50
  _FULL_NAME_MAX_LENGTH = 255

  def __init__(self, name: str, full_name: str, group: nomenclature_group_model, measurement_unit: measurement_unit_model, position_type: position_type):
      """
      Конструктор номенклатуры

      :full_name: полное наименование номенклатурной позиции
      :group: группа номенклатуры
      :measurement_unit: единица измерения позиции
      :position_type: тип позиции (сырьё/товар/полуфабрикат/блюдо)
      """
      super().__init__(name)
      self._validate_full_name(full_name)
      self.__full_name = full_name
      self.__group = group
      self.__measurement_unit = measurement_unit
      self.__position_type = position_type

  @property
  def full_name(self):
      """Возвращает полное наименование номенклатурной позиции"""
      return self.__full_name

  @property
  def group(self):
      """Возвращает группу номенклатуры"""
      return self.__group

  @property
  def measurement_unit(self):
      """Возвращает единицу измерения позиции"""
      return self.__measurement_unit

  @property
  def position_type(self):
      """Возвращает тип позиции"""
      return self.__position_type

  @full_name.setter
  def full_name(self, new_full_name: str):
      """
      Устанавливает полное наименование номенклатурной позиции

      :new_full_name: новое полное наименование
      """
      self._validate_full_name(new_full_name)
      self.__full_name = new_full_name

  @group.setter
  def group(self, new_group: nomenclature_group_model):
      """
      Устанавливает группу номенклатуры

      :new_group: новая группа номенклатуры
      """
      self.__group = new_group

  @measurement_unit.setter
  def measurement_unit(self, new_measurement_unit: measurement_unit_model):
      """
      Устанавливает единицу измерения позиции

      :new_measurement_unit: новая единица измерения
      """
      self.__measurement_unit = new_measurement_unit

  @position_type.setter
  def position_type(self, new_position_type: position_type):
      """
      Устанавливает тип позиции

      :new_position_type: новый тип позиции
      """
      self.__position_type = new_position_type

  def _validate_name(self, value: str) -> None:
      """Проверка обычного наименования: базовая проверка + максимум 50 символов."""
      super()._validate_name(value)
      if len(value) > self._NAME_MAX_LENGTH:
          raise validation_exception("name", f"Имя длиннее {self._NAME_MAX_LENGTH} символов")

  def _validate_full_name(self, value: str) -> None:
      """Проверка полного наименования: непустая строка, максимум 255 символов."""
      if value is None or not isinstance(value, str) or len(value) == 0:
          raise validation_exception("full_name", "Полное наименование не должно быть пустым")
      if len(value) > self._FULL_NAME_MAX_LENGTH:
          raise validation_exception("full_name", f"Полное наименование длиннее {self._FULL_NAME_MAX_LENGTH} символов")

from Src.Core.named_entity import named_entity
from Src.Core.position_type import position_type
from Src.models.nomenclature_group_model import nomenclature_group_model
from Src.models.measurement_unit import measurement_unit_model
from Src.Core.exception import arguments_exception

class nomenclature_model(named_entity):
  def __init__(self, full_name: str, group: nomenclature_group_model, measurement_unit: measurement_unit_model, position_type: position_type):
      super().__init__("Номенклатура")
      self.full_name = self._validate_name(full_name)
      self.group = group
      self.measurement_unit = measurement_unit
      self.position_type = position_type

      self._NAME_MAX_LENGTH = 255

  @property
  def full_name(self):
      return self.full_name

  @property
  def group(self):
      return self.group

  @property
  def measurement_unit(self):
      return self.measurement_unit

  @property 
  def position_type(self):
      return self.position_type

  @full_name.setter
  def full_name(self, new_full_name: str):
      self._validate_name(new_full_name)
      self.full_name = new_full_name

  @group.setter
  def group(self, new_group: nomenclature_group_model):
      self.group = new_group

  @measurement_unit.setter
  def measurement_unit(self, new_measurement_unit: measurement_unit_model):
      self.measurement_unit = new_measurement_unit

  @position_type.setter
  def position_type(self, new_position_type: position_type):
      self.position_type = new_position_type

  def _validate_name(self, value: str) -> None:
      super()._validate_name(value)
      if len(value) > self._NAME_MAX_LENGTH:
          raise arguments_exception("name", f"Имя длиннее {self._NAME_MAX_LENGTH} символов")

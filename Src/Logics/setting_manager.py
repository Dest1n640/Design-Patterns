from Src.Core.abstract_manager import AbstractManager
from Src.Core.exception import ApplicationException
from Src.Models.settings_model import SettingModel
import json


class SettingsManager(AbstractManager):
  __default_file_name : str = "settings.json"
  __setting: SettingModel = SettingModel()

  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(SettingsManager, cls).__new__(cls)
    return cls.instance

  def load(self, file_name = ""):
    inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
    self._validate_load()
    try:
      with open(inner_file_name, "r") as file:
        self.data = json.load (file)
        self.is_loaded = self.convert()
    except Exception as ex:
      raise ApplicationException("Ошибка в прочтении и обработке файла")
      

  def settings(self) -> SettingModel:
    return self.__setting

  def _validate_load(self):
    pass

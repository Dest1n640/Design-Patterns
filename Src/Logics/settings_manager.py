from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.validation import Validation
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Models.settings_model import SettingsModel


class SettingsManager(AbstractManager):
    """Класс менеджера настроек — singleton, читает настройки из json-файла."""

    _DEFAULT_FILE_NAME = "settings.json"
    _instance = None

    def __new__(cls) -> Self:
        """Возвращает единственный экземпляр менеджера настроек."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Конструктор: состояние создаётся один раз для единственного экземпляра."""
        if hasattr(self, "_settings"):
            return
        super().__init__()
        self._settings = SettingsModel()

    @property
    def settings(self) -> SettingsModel:
        """Возвращает модель настроек."""
        return self._settings

    def load(self) -> bool:
        """Восстанавливает модель настроек через общую фабрику десериализации."""
        data = Validation.validate_instance(
            self._data, dict, "settings", "Настройки должны быть json-объектом"
        )
        settings = DeserializeFactory().convert(data)
        self._settings = Validation.validate_instance(
            settings, SettingsModel, "settings", "Ожидается модель настроек"
        )
        return True

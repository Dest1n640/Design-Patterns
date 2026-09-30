import json
from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.exception import ApplicationException
from Src.Core.validation import Validation
from Src.Models.organization_model import OrganizationModel
from Src.Models.settings_model import SettingModel


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
        if hasattr(self, "_setting"):
            return
        super().__init__()
        self._setting = SettingModel()

    @property
    def settings(self) -> SettingModel:
        """Возвращает модель настроек."""
        return self._setting

    def load(self, file_name: str = "") -> None:
        """Читает json-файл настроек (по умолчанию settings.json) и преобразует его."""
        self._is_loaded = False
        self._file_name = Validation.validate_string(
            file_name if file_name.strip() else self._DEFAULT_FILE_NAME, "file_name"
        )
        try:
            with open(self._file_name, encoding="utf-8") as file:
                self._data = json.load(file)
        except (OSError, ValueError) as ex:
            raise ApplicationException(
                f"Не удалось прочитать файл настроек '{self._file_name}'"
            ) from ex
        self._is_loaded = self.convert()

    def convert(self) -> bool:
        """Собирает модель настроек из раздела company загруженных данных."""
        data = Validation.validate_instance(
            self._data, dict, "settings", "Настройки должны быть json-объектом"
        )
        company = Validation.validate_instance(
            data.get("company"),
            dict,
            "company",
            "Раздел company отсутствует или некорректен",
        )

        setting = SettingModel()
        setting.organization = OrganizationModel(
            company.get("name"),
            company.get("inn"),
            company.get("bic"),
            company.get("curr_account"),
            company.get("legal_form"),
        )
        setting.boss_name = company.get("boss_name")
        setting.account_name = company.get("account_name")

        self._setting = setting
        return True

from typing import Self

from Src.Core.abstract_manager import AbstractManager
from Src.Core.validation import Validation
from Src.Models.organization_model import OrganizationModel
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

    def convert(self) -> bool:
        """Собирает модель настроек из раздела company и флага first_start."""
        data = Validation.validate_instance(
            self._data, dict, "settings", "Настройки должны быть json-объектом"
        )
        company = Validation.validate_instance(
            data.get("company"),
            dict,
            "company",
            "Раздел company отсутствует или некорректен",
        )

        settings = SettingsModel()
        settings.organization = OrganizationModel(
            company.get("name"),
            company.get("inn"),
            company.get("bic"),
            company.get("curr_account"),
            company.get("legal_form"),
        )
        settings.boss_name = company.get("boss_name")
        settings.accountant_name = company.get("accountant_name")
        settings.first_start = data.get("first_start")

        self._settings = settings
        return True

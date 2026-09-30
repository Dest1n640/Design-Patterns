from Src.Core.abstract_model import AbstractModel
from Src.Core.validation import Validation
from Src.Models.organization_model import OrganizationModel


class SettingModel(AbstractModel):
    """Класс модели настроек приложения."""

    def __init__(self) -> None:
        """Конструктор пустой модели: значения появятся после загрузки настроек."""
        super().__init__()
        self.__organization: OrganizationModel | None = None
        self.__boss_name = ""
        self.__account_name = ""

    @property
    def organization(self) -> OrganizationModel | None:
        """Возвращает организацию; None, пока настройки не загружены."""
        return self.__organization

    @property
    def boss_name(self) -> str:
        """Возвращает ФИО руководителя организации."""
        return self.__boss_name

    @property
    def account_name(self) -> str:
        """Возвращает наименование счёта организации."""
        return self.__account_name

    @organization.setter
    def organization(self, value: OrganizationModel) -> None:
        """Устанавливает организацию."""
        self.__organization = Validation.validate_instance(
            value, OrganizationModel, "organization", "Организация указана некорректно"
        )

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        """Устанавливает ФИО руководителя организации."""
        self.__boss_name = Validation.validate_string(value, "boss_name")

    @account_name.setter
    def account_name(self, value: str) -> None:
        """Устанавливает наименование счёта организации."""
        self.__account_name = Validation.validate_string(value, "account_name")

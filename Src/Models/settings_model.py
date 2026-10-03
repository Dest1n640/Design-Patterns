from Src.Core.abstract_model import AbstractModel
from Src.Core.validation import Validation
from Src.Models.organization_model import OrganizationModel


class SettingsModel(AbstractModel):
    """Класс модели настроек приложения."""

    def __init__(self) -> None:
        """Конструктор пустой модели: значения появятся после загрузки настроек."""
        super().__init__()
        self.__organization: OrganizationModel | None = None
        self.__boss_name = ""
        self.__accountant_name = ""
        self.__first_start = False

    @property
    def organization(self) -> OrganizationModel | None:
        """Возвращает организацию; None, пока настройки не загружены."""
        return self.__organization

    @property
    def boss_name(self) -> str:
        """Возвращает ФИО руководителя организации."""
        return self.__boss_name

    @property
    def accountant_name(self) -> str:
        """Возвращает ФИО главного бухгалтера организации."""
        return self.__accountant_name

    @property
    def first_start(self) -> bool:
        """Возвращает признак первого запуска приложения."""
        return self.__first_start

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

    @accountant_name.setter
    def accountant_name(self, value: str) -> None:
        """Устанавливает ФИО главного бухгалтера организации."""
        self.__accountant_name = Validation.validate_string(value, "accountant_name")

    @first_start.setter
    def first_start(self, value: bool) -> None:
        """Устанавливает признак первого запуска приложения."""
        self.__first_start = Validation.validate_instance(
            value, bool, "first_start", "Признак первого запуска должен быть bool"
        )

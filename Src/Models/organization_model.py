from typing import Self

from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation


class OrganizationModel(NamedModel):
    """Класс сущности - организация."""

    def __init__(self) -> None:
        """Инициализирует организацию без заполненных реквизитов."""
        super().__init__()
        self.__inn = ""
        self.__bic = ""
        self.__curr_account = ""
        self.__legal_form = ""

    @classmethod
    def create(
        cls, name: str, inn: str, bic: str, curr_account: str, legal_form: str
    ) -> Self:
        """Создаёт организацию с проверенным именем и реквизитами."""
        model = cls()
        model.name = name
        model.inn = inn
        model.bic = bic
        model.curr_account = curr_account
        model.legal_form = legal_form
        model.validate()
        return model

    @property
    def inn(self) -> str:
        """Возвращает ИНН организации."""
        return self.__inn

    @property
    def bic(self) -> str:
        """Возвращает БИК организации."""
        return self.__bic

    @property
    def curr_account(self) -> str:
        """Возвращает расчётный счёт организации."""
        return self.__curr_account

    @property
    def legal_form(self) -> str:
        """Возвращает организационно-правовую форму организации."""
        return self.__legal_form

    @inn.setter
    def inn(self, new_inn: str) -> None:
        """Устанавливает ИНН организации: ровно 10 цифр."""
        self.__inn = Validation.validate_digits(
            new_inn, "inn", min_length=10, max_length=10
        )

    @bic.setter
    def bic(self, new_bic: str) -> None:
        """Устанавливает БИК организации: ровно 9 цифр."""
        self.__bic = Validation.validate_digits(
            new_bic, "bic", min_length=9, max_length=9
        )

    @curr_account.setter
    def curr_account(self, new_curr_account: str) -> None:
        """Устанавливает расчётный счёт организации: ровно 20 цифр."""
        self.__curr_account = Validation.validate_digits(
            new_curr_account, "curr_account", min_length=20, max_length=20
        )

    @legal_form.setter
    def legal_form(self, new_legal_form: str) -> None:
        """Устанавливает организационно-правовую форму организации."""
        self.__legal_form = Validation.validate_string(new_legal_form, "legal_form")

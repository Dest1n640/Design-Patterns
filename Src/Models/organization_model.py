from Src.Core.exception import ValidationException
from Src.Core.named_model import NamedModel


class OrganizationModel(NamedModel):
    """Класс сущности - организация."""

    def __init__(self, inn: str, bic: str, curr_account: str, legal_form: str):
        """Конструктор с присвоением имени ООО Ромашка."""
        super().__init__("Ромашка")
        self._validate_inn(inn)
        self.inn = inn
        self._validate_bic(bic)
        self.bic = bic
        self._validate_curr_account(curr_account)
        self.curr_account = curr_account
        self._validate_legal_form(legal_form)
        self.legal_form = legal_form

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
        """Устанавливает ИНН организации."""
        self._validate_inn(new_inn)
        self.__inn = new_inn

    @bic.setter
    def bic(self, new_bic: str) -> None:
        """Устанавливает БИК организации."""
        self._validate_bic(new_bic)
        self.__bic = new_bic

    @curr_account.setter
    def curr_account(self, new_curr_account: str) -> None:
        """Устанавливает расчётный счёт организации."""
        self._validate_curr_account(new_curr_account)
        self.__curr_account = new_curr_account

    @legal_form.setter
    def legal_form(self, new_legal_form: str) -> None:
        """Устанавливает организационно-правовую форму организации."""
        self._validate_legal_form(new_legal_form)
        self.__legal_form = new_legal_form

    def _validate_inn(self, value: str) -> None:
        """Проверка ИНН: строка ровно из 10 цифр."""
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValidationException("inn", "ИНН должен состоять ровно из 10 цифр")

    def _validate_bic(self, value: str) -> None:
        """Проверка БИК: строка ровно из 9 цифр."""
        if not isinstance(value, str) or not value.isdigit() or len(value) != 9:
            raise ValidationException("bic", "БИК должен состоять ровно из 9 цифр")

    def _validate_curr_account(self, value: str) -> None:
        """Проверка расчётного счёта: строка ровно из 20 цифр."""
        if not isinstance(value, str) or not value.isdigit() or len(value) != 20:
            raise ValidationException(
                "curr_account", "Расчётный счёт должен состоять ровно из 20 цифр"
            )

    def _validate_legal_form(self, value: str) -> None:
        """Проверка организационно-правовой формы: непустая строка."""
        if value is None or not isinstance(value, str) or len(value) == 0:
            raise ValidationException(
                "legal_form", "Организационно-правовая форма не должна быть пустой"
            )

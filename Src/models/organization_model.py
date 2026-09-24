from Src.Core.named_entity import named_entity
from Src.Core.exception import validation_exception


class organization_model(named_entity):
    """Класс сущности - организация"""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Реализация singleton для класса"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, INN: str, BIC: str, curr_account: str, legal_form: str):
      """Констуктор с присваением именни ООО Ромашка"""
      if self._initialized:
          raise validation_exception("organization", "Организация уже создана, повторное создание недопустимо")
      super().__init__("Ромашка")
      self.INN = INN
      self.BIC = BIC
      self.curr_account = curr_account
      self.legal_form = legal_form
      self._initialized = True

    @property
    def INN(self) -> str:
        """Возвращает ИНН организации"""
        return self.__INN

    @property
    def BIC(self) -> str:
        """Возвращает БИК организации"""
        return self.__BIC

    @property
    def curr_account(self) -> str:
        """Возвращает расчётный счёт организации"""
        return self.__curr_account

    @property
    def legal_form(self) -> str:
        """Возвращает организационно-правовую форму организации"""
        return self.__legal_form

    @INN.setter
    def INN(self, new_INN: str) -> None:
        """
        Устанавливает ИНН организации

        :new_INN: новый ИНН
        """
        self._validate_INN(new_INN)
        self.__INN = new_INN

    @BIC.setter
    def BIC(self, new_BIC: str) -> None:
        """
        Устанавливает БИК организации

        :new_BIC: новый БИК
        """
        self._validate_BIC(new_BIC)
        self.__BIC = new_BIC

    @curr_account.setter
    def curr_account(self, new_curr_account: str) -> None:
        """
        Устанавливает расчётный счёт организации

        :new_curr_account: новый расчётный счёт
        """
        self._validate_curr_account(new_curr_account)
        self.__curr_account = new_curr_account

    @legal_form.setter
    def legal_form(self, new_legal_form: str) -> None:
        """
        Устанавливает организационно-правовую форму организации

        :new_legal_form: новая организационно-правовая форма
        """
        self._validate_legal_form(new_legal_form)
        self.__legal_form = new_legal_form

    def _validate_INN(self, value: str) -> None:
        """
        Проверка ИНН: строка ровно из 10 цифр

        :value: проверяемый ИНН
        """
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise validation_exception("INN", "ИНН должен состоять ровно из 10 цифр")

    def _validate_BIC(self, value: str) -> None:
        """
        Проверка БИК: строка ровно из 9 цифр

        :value: проверяемый БИК
        """
        if not isinstance(value, str) or not value.isdigit() or len(value) != 9:
            raise validation_exception("BIC", "БИК должен состоять ровно из 9 цифр")

    def _validate_curr_account(self, value: str) -> None:
        """
        Проверка расчётного счёта: строка ровно из 20 цифр

        :value: проверяемый расчётный счёт
        """
        if not isinstance(value, str) or not value.isdigit() or len(value) != 20:
            raise validation_exception("curr_account", "Расчётный счёт должен состоять ровно из 20 цифр")

    def _validate_legal_form(self, value: str) -> None:
        """
        Проверка организационно-правовой формы: непустая строка

        :value: проверяемая организационно-правовая форма
        """
        if value is None or not isinstance(value, str) or len(value) == 0:
            raise validation_exception("legal_form", "Организационно-правовая форма не должна быть пустой")


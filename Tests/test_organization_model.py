"""Юнит-тесты для Src.Models.organization_model.OrganizationModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.organization_model import OrganizationModel


def test_organization_model__constructor__valid_fields_are_set():
    """Валидное создание организации сохраняет все переданные поля."""
    org = OrganizationModel("1234567890", "123456789", "12345678901234567890", "ООО")
    assert org.inn == "1234567890"
    assert org.bic == "123456789"
    assert org.curr_account == "12345678901234567890"
    assert org.legal_form == "ООО"


def test_organization_model__constructor__invalid_inn_raises_validation_exception():
    """Невалидный ИНН (не 10 цифр) вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        OrganizationModel("123", "123456789", "12345678901234567890", "ООО")


def test_organization_model__constructor__invalid_bic_raises_validation_exception():
    """Невалидный БИК (не 9 цифр) вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        OrganizationModel("1234567890", "123", "12345678901234567890", "ООО")


def test_organization_model__constructor__invalid_curr_account_raises():
    """Невалидный расчётный счёт (не 20 цифр) вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        OrganizationModel("1234567890", "123456789", "123", "ООО")


def test_organization_model__constructor__empty_legal_form_raises():
    """Пустая организационно-правовая форма вызывает исключение валидации."""
    with pytest.raises(ValidationException):
        OrganizationModel("1234567890", "123456789", "12345678901234567890", "")


def test_organization_model__constructor__second_call_with_new_data_does_not_raise():
    """Организация больше не Singleton — повторный вызов с другими данными не ошибка."""
    OrganizationModel("1234567890", "123456789", "12345678901234567890", "ООО")
    OrganizationModel("0987654321", "987654321", "09876543210987654321", "АО")


def test_organization_model__constructor__two_calls_are_independent_instances():
    """Два вызова конструктора возвращают разные независимые объекты."""
    org1 = OrganizationModel("1234567890", "123456789", "12345678901234567890", "ООО")
    org2 = OrganizationModel("1234567890", "123456789", "12345678901234567890", "ООО")
    assert org1 is not org2
    assert org1 != org2


def test_organization_model__field_mutation__does_not_affect_other_instance():
    """Изменение поля одного экземпляра организации не влияет на другой экземпляр."""
    org1 = OrganizationModel("1234567890", "123456789", "12345678901234567890", "ООО")
    org2 = OrganizationModel("0987654321", "987654321", "09876543210987654321", "АО")
    org1.legal_form = "ИП"
    assert org1.legal_form == "ИП"
    assert org2.legal_form == "АО"

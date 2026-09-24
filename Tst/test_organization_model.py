"""Юнит-тесты для Src.models.organization_model.organization_model."""
import pytest

from Src.models.organization_model import organization_model
from Src.Core.exception import validation_exception


@pytest.fixture(autouse=True)
def reset_organization_singleton():
    """Сбрасывает состояние Singleton organization_model до и после каждого теста."""
    organization_model._instance = None
    organization_model._initialized = False
    yield
    organization_model._instance = None
    organization_model._initialized = False


def test_ValidOrganizationCreated_Constructor_AllFieldsAreSet():
    """Валидное создание организации сохраняет все переданные поля."""
    org = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    assert org.INN == "1234567890"
    assert org.BIC == "123456789"
    assert org.curr_account == "12345678901234567890"
    assert org.legal_form == "ООО"


def test_ValidationException_Constructor_InvalidINNRaises():
    """Невалидный ИНН (не 10 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("123", "123456789", "12345678901234567890", "ООО")


def test_ValidationException_Constructor_InvalidBICRaises():
    """Невалидный БИК (не 9 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123", "12345678901234567890", "ООО")


def test_ValidationException_Constructor_InvalidCurrAccountRaises():
    """Невалидный расчётный счёт (не 20 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123456789", "123", "ООО")


def test_ValidationException_Constructor_EmptyLegalFormRaises():
    """Пустая организационно-правовая форма вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123456789", "12345678901234567890", "")


def test_SameInstanceReturned_New_RepeatedCallReturnsSameObject():
    """Повторный вызов __new__ (механизм Singleton) возвращает тот же объект."""
    org1 = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    org2 = organization_model.__new__(organization_model)
    assert org1 is org2


def test_ValidationException_Constructor_RepeatedCallWithDifferentDataRaises():
    """Повторный вызов конструктора с другими данными вызывает исключение."""
    organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    with pytest.raises(validation_exception):
        organization_model("0987654321", "987654321", "09876543210987654321", "АО")

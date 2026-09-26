"""Юнит-тесты для Src.models.organization_model.organization_model."""
import pytest

from Src.models.organization_model import organization_model
from Src.Core.exception import validation_exception


def test_valid_organization_created_constructor_all_fields_are_set():
    """Валидное создание организации сохраняет все переданные поля."""
    org = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    assert org.INN == "1234567890"
    assert org.BIC == "123456789"
    assert org.curr_account == "12345678901234567890"
    assert org.legal_form == "ООО"


def test_validation_exception_constructor_invalid_inn_raises():
    """Невалидный ИНН (не 10 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("123", "123456789", "12345678901234567890", "ООО")


def test_validation_exception_constructor_invalid_bic_raises():
    """Невалидный БИК (не 9 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123", "12345678901234567890", "ООО")


def test_validation_exception_constructor_invalid_curr_account_raises():
    """Невалидный расчётный счёт (не 20 цифр) вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123456789", "123", "ООО")


def test_validation_exception_constructor_empty_legal_form_raises():
    """Пустая организационно-правовая форма вызывает исключение валидации."""
    with pytest.raises(validation_exception):
        organization_model("1234567890", "123456789", "12345678901234567890", "")


def test_multiple_instances_allowed_constructor_second_call_with_different_data_does_not_raise():
    """Организация больше не Singleton: повторный вызов конструктора с другими данными не бросает исключение."""
    organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    organization_model("0987654321", "987654321", "09876543210987654321", "АО")


def test_independent_objects_returned_constructor_two_calls_produce_different_instances():
    """Два вызова конструктора возвращают разные независимые объекты, а не один и тот же."""
    org1 = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    org2 = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    assert org1 is not org2
    assert org1 != org2


def test_fields_are_isolated_constructor_mutating_one_instance_does_not_affect_another():
    """Изменение поля одного экземпляра организации не влияет на другой экземпляр."""
    org1 = organization_model("1234567890", "123456789", "12345678901234567890", "ООО")
    org2 = organization_model("0987654321", "987654321", "09876543210987654321", "АО")
    org1.legal_form = "ИП"
    assert org1.legal_form == "ИП"
    assert org2.legal_form == "АО"

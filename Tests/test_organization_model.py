"""Юнит-тесты для Src.Models.organization_model.OrganizationModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.organization_model import OrganizationModel


def _build_organization(
    name="Ромашка",
    inn="1234567890",
    bic="123456789",
    curr_account="12345678901234567890",
    legal_form="ООО",
):
    """Строит организацию с валидными реквизитами, переопределяя переданные."""
    return OrganizationModel(name, inn, bic, curr_account, legal_form)


def test_organization_model__constructor__name_is_taken_from_argument():
    """Имя организации берётся из аргумента конструктора, а не зашито в класс."""
    # Подготовка
    name = "Лютик"

    # Действия
    organization = _build_organization(name=name)

    # Проверки
    assert organization.name == name


def test_organization_model__constructor__invalid_name_raises():
    """Пустое имя организации вызывает исключение валидации."""
    # Подготовка
    name = ""

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        _build_organization(name=name)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize(
    ("field", "length"), [("inn", 10), ("bic", 9), ("curr_account", 20)]
)
def test_organization_model__constructor__exact_digits_length_is_accepted(
    field, length
):
    """ИНН, БИК и расчётный счёт допустимы при своей длине (10, 9, 20 цифр)."""
    # Подготовка
    value = "1" * length

    # Действия
    organization = _build_organization(**{field: value})

    # Проверки
    assert getattr(organization, field) == value


@pytest.mark.parametrize(
    ("field", "length"), [("inn", 10), ("bic", 9), ("curr_account", 20)]
)
@pytest.mark.parametrize("delta", [-1, 1])
def test_organization_model__constructor__digits_length_off_by_one_raises(
    field, length, delta
):
    """ИНН, БИК и расчётный счёт на одну цифру короче или длиннее вызывают ошибку."""
    # Подготовка
    value = "1" * (length + delta)

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        _build_organization(**{field: value})

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_organization_model__field_mutation__does_not_affect_other_instance():
    """Изменение поля одного экземпляра организации не влияет на другой экземпляр."""
    # Подготовка
    org1 = _build_organization(legal_form="ООО")
    org2 = _build_organization(legal_form="АО")

    # Действия
    org1.legal_form = "ИП"

    # Проверки
    assert org2.legal_form == "АО"

"""Юнит-тесты для Src.Models.settings_model.SettingModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.organization_model import OrganizationModel
from Src.Models.settings_model import SettingModel


def _build_organization():
    """Строит валидную организацию."""
    return OrganizationModel(
        "Ромашка", "7701234567", "044525225", "40702810000000000001", "ООО"
    )


def test_setting_model__constructor__fields_are_empty():
    """Новая модель настроек не содержит организации и пустые строки в именах."""
    setting = SettingModel()
    assert setting.organization is None
    assert setting.boss_name == ""
    assert setting.account_name == ""


def test_setting_model__valid_fields__all_fields_are_set():
    """Валидные значения сохраняются в модели, строки очищаются от пробелов."""
    organization = _build_organization()
    setting = SettingModel()
    setting.organization = organization
    setting.boss_name = "  Иванов И. И.  "
    setting.account_name = "Основной счёт"

    assert setting.organization is organization
    assert setting.boss_name == "Иванов И. И."
    assert setting.account_name == "Основной счёт"


def test_setting_model__organization_not_organization_model__raises():
    """Организация другого типа вызывает исключение валидации."""
    setting = SettingModel()
    with pytest.raises(ValidationException):
        setting.organization = "не организация"


@pytest.mark.parametrize("field", ["boss_name", "account_name"])
@pytest.mark.parametrize("value", ["", "   ", None, 123])
def test_setting_model__invalid_string_field__raises(field, value):
    """Пустое значение или не строка в текстовых полях вызывает исключение валидации."""
    setting = SettingModel()
    with pytest.raises(ValidationException):
        setattr(setting, field, value)


def test_setting_model__two_instances__ids_differ():
    """Разные модели настроек имеют разные идентификаторы и не равны."""
    assert SettingModel() != SettingModel()

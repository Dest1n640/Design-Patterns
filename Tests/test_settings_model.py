"""Юнит-тесты для Src.Models.settings_model.SettingsModel."""

import pytest

from Src.Core.exception import ValidationException
from Src.Models.organization_model import OrganizationModel
from Src.Models.settings_model import SettingsModel


def _build_organization():
    """Строит валидную организацию."""
    return OrganizationModel(
        "Ромашка", "7701234567", "044525225", "40702810000000000001", "ООО"
    )


def test_settings_model__constructor__fields_are_empty():
    """Новая модель настроек пустая, признак первого запуска выключен."""
    settings = SettingsModel()
    assert settings.organization is None
    assert settings.boss_name == ""
    assert settings.accountant_name == ""
    assert settings.first_start is False


def test_settings_model__valid_fields__all_fields_are_set():
    """Валидные значения сохраняются в модели, строки очищаются от пробелов."""
    organization = _build_organization()
    settings = SettingsModel()
    settings.organization = organization
    settings.boss_name = "  Иванов И. И.  "
    settings.accountant_name = "Петрова М. С."
    settings.first_start = True

    assert settings.organization is organization
    assert settings.boss_name == "Иванов И. И."
    assert settings.accountant_name == "Петрова М. С."
    assert settings.first_start is True


def test_settings_model__organization_not_organization_model__raises():
    """Организация другого типа вызывает исключение валидации."""
    settings = SettingsModel()
    with pytest.raises(ValidationException):
        settings.organization = "не организация"


@pytest.mark.parametrize("field", ["boss_name", "accountant_name"])
def test_settings_model__invalid_string_field__raises(field):
    """Не строка в текстовых полях вызывает исключение валидации."""
    settings = SettingsModel()
    with pytest.raises(ValidationException):
        setattr(settings, field, None)


def test_settings_model__first_start_not_bool__raises():
    """Признак первого запуска не типа bool вызывает исключение валидации."""
    settings = SettingsModel()
    with pytest.raises(ValidationException):
        settings.first_start = "true"

"""Юнит-тесты для Src.Logics.settings_manager.SettingsManager."""

import json
from pathlib import Path

import pytest

from Src.Core.exception import ApplicationException, ValidationException
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager


def _write_json(directory: Path, data: object) -> str:
    """Записывает данные во временный json-файл и возвращает путь к нему."""
    path = directory / "settings.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _build_loaded_manager() -> SettingsManager:
    """Возвращает менеджер настроек, загруженный из файла по умолчанию."""
    manager = SettingsManager()
    manager.read()
    return manager


def test_settings_manager__read_default_file__does_not_raise():
    """Загрузка настроек из файла по умолчанию проходит без исключений."""
    # Подготовка
    manager = SettingsManager()

    # Действия
    manager.read()

    # Проверки
    assert manager.is_loaded


def test_settings_manager__read_default_file__settings_not_empty():
    """После загрузки модель настроек заполнена организацией."""
    # Подготовка
    manager = SettingsManager()

    # Действия
    manager.read()

    # Проверки
    assert manager.settings is not None
    assert manager.settings.organization is not None


def test_settings_manager__two_instances__same_object():
    """Повторное создание менеджера возвращает тот же экземпляр (singleton)."""
    # Подготовка
    first = SettingsManager()

    # Действия
    second = SettingsManager()

    # Проверки
    assert first is second


def test_settings_manager__read_default_file__is_loaded_true():
    """После успешной загрузки признак is_loaded равен True."""
    # Подготовка
    manager = SettingsManager()

    # Действия
    manager.read()

    # Проверки
    assert manager.is_loaded


def test_settings_manager__two_instances__share_settings():
    """Настройки, загруженные через один экземпляр, видны через другой."""
    # Подготовка
    manager = _build_loaded_manager()

    # Действия
    settings = SettingsManager().settings

    # Проверки
    assert settings is manager.settings


def test_settings_manager__read_default_file__organization_matches_json(
    settings_data,
):
    """Реквизиты организации совпадают с разделом organization в settings.json."""
    # Подготовка
    expected = settings_data["organization"]

    # Действия
    organization = _build_loaded_manager().settings.organization

    # Проверки
    assert organization.name == expected["name"]
    assert organization.inn == expected["inn"]
    assert organization.bic == expected["bic"]
    assert organization.curr_account == expected["curr_account"]
    assert organization.legal_form == expected["legal_form"]


def test_settings_manager__read_default_file__names_match_json(settings_data):
    """ФИО руководителя и главного бухгалтера совпадают с settings.json."""
    # Подготовка
    expected = settings_data

    # Действия
    settings = _build_loaded_manager().settings

    # Проверки
    assert settings.boss_name == expected["boss_name"]
    assert settings.accountant_name == expected["accountant_name"]


def test_settings_manager__read_default_file__first_start_matches_json(
    settings_data,
):
    """Признак первого запуска совпадает с settings.json."""
    # Подготовка
    expected = settings_data["first_start"]

    # Действия
    settings = _build_loaded_manager().settings

    # Проверки
    assert settings.first_start is expected


def test_settings_manager__read_default_file__response_format_matches_json(
    settings_data,
):
    """Формат ответа совпадает с settings.json."""
    # Подготовка
    expected = settings_data["response_format"]

    # Действия
    settings = _build_loaded_manager().settings

    # Проверки
    assert settings.response_format.value == expected


def test_settings_manager__read_unknown_response_format__raises_validation_exception(
    settings_data, tmp_path
):
    """Неизвестный формат ответа вызывает исключение валидации."""
    # Подготовка
    settings_data["response_format"] = "pdf"
    file_name = _write_json(tmp_path, settings_data)
    manager = SettingsManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(file_name)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_settings_manager__read_without_organization__raises_validation_exception(
    settings_data, tmp_path
):
    """Файл настроек без раздела organization вызывает исключение валидации."""
    # Подготовка
    settings_data.pop("organization")
    file_name = _write_json(tmp_path, settings_data)
    manager = SettingsManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(file_name)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_settings_manager__read_not_object__raises_validation_exception(tmp_path):
    """Файл, в котором лежит не json-объект, вызывает исключение валидации."""
    # Подготовка
    file_name = _write_json(tmp_path, [1, 2, 3])
    manager = SettingsManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(file_name)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_settings_manager__read_non_string_file_name__raises_validation_exception():
    """Имя файла не строкой вызывает исключение валидации."""
    # Подготовка
    manager = SettingsManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(None)

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


def test_settings_manager__read_missing_file__raises_application_exception(
    tmp_path,
):
    """Отсутствующий файл вызывает исключение приложения."""
    # Подготовка
    file_name = str(tmp_path / "missing.json")
    manager = SettingsManager()

    # Действия
    with pytest.raises(ApplicationException) as exc_info:
        manager.read(file_name)

    # Проверки
    assert type(exc_info.value) is ApplicationException


def test_settings_manager__read_broken_json__raises_application_exception(tmp_path):
    """Файл с синтаксической ошибкой json вызывает исключение приложения."""
    # Подготовка
    path = tmp_path / "broken.json"
    path.write_text("{не json", encoding="utf-8")
    manager = SettingsManager()

    # Действия
    with pytest.raises(ApplicationException) as exc_info:
        manager.read(str(path))

    # Проверки
    assert type(exc_info.value) is ApplicationException


def test_settings_manager__read_invalid_after_success__keeps_previous_settings(
    settings_data, tmp_path
):
    """Неудачная загрузка не сбрасывает is_loaded и настройки прошлой загрузки."""
    # Подготовка
    manager = _build_loaded_manager()
    settings = manager.settings
    settings_data["organization"]["inn"] = "abc"
    file_name = _write_json(tmp_path, settings_data)

    # Действия
    with pytest.raises(ValidationException):
        manager.read(file_name)

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings


def test_settings_manager__read_from_other_directory__reads_default_file(
    tmp_path, monkeypatch
):
    """Файл по умолчанию ищется от корня проекта, а не от текущего каталога."""
    # Подготовка
    monkeypatch.chdir(tmp_path)
    manager = SettingsManager()

    # Действия
    manager.read()

    # Проверки
    assert manager.is_loaded


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        (None, "boss_name", None),
        (None, "accountant_name", " "),
        (None, "first_start", "true"),
        (None, "first_start", None),
        (None, "response_format", None),
        (None, "response_format", []),
        (None, "response_format", {}),
    ],
)
def test_settings_manager__invalid_property__previous_settings_kept(
    settings_data, tmp_path, section, field, value
):
    """Ошибка свойства при общей десериализации сохраняет прежние настройки."""
    # Подготовка
    manager = _build_loaded_manager()
    original = manager.settings
    target = settings_data[section] if section else settings_data
    target[field] = value
    file_name = _write_json(tmp_path, settings_data)

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(file_name)

    # Проверки
    assert exc_info.value.field == field
    assert manager.settings is original
    assert manager.is_loaded


def test_settings_manager__serialized_settings__all_fields_and_ids_restored(tmp_path):
    """Полный результат сериализации настроек загружается без изменения структуры."""
    # Подготовка
    manager = _build_loaded_manager()
    source = SerializeFactory().convert(manager.settings)
    source["id"] = "settings-config"
    source["organization"]["id"] = "organization-config"
    file_name = _write_json(tmp_path, source)

    # Действия
    manager.read(file_name)

    # Проверки
    assert SerializeFactory().convert(manager.settings) == source


@pytest.mark.parametrize("field", ["boss_name", "accountant_name", "response_format"])
def test_settings_manager__required_field_missing__previous_settings_kept(
    settings_data, tmp_path, field
):
    """Отсутствующее обязательное поле отклоняется без замены настроек."""
    # Подготовка
    manager = _build_loaded_manager()
    original = manager.settings
    del settings_data[field]
    file_name = _write_json(tmp_path, settings_data)

    # Действия
    with pytest.raises(ValidationException) as error:
        manager.read(file_name)

    # Проверки
    assert error.value.field == field
    assert manager.settings is original


@pytest.mark.parametrize("case", ["missing_type", "wrong_model", "missing_nested_type"])
def test_settings_manager__invalid_model_tags__previous_settings_kept(
    settings_data, tmp_path, case
):
    """Неверные метки типов отклоняются без замены ранее загруженных настроек."""
    # Подготовка
    manager = _build_loaded_manager()
    original = manager.settings
    if case == "missing_type":
        del settings_data["type"]
    elif case == "wrong_model":
        settings_data = settings_data["organization"]
    else:
        del settings_data["organization"]["type"]
    file_name = _write_json(tmp_path, settings_data)

    # Действия
    with pytest.raises(ValidationException):
        manager.read(file_name)

    # Проверки
    assert manager.settings is original
    assert manager.is_loaded

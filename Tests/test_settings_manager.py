"""Юнит-тесты для Src.Logics.settings_manager.SettingsManager."""

import json
from pathlib import Path

import pytest

from Src.Core.exception import ApplicationException, ValidationException
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
    """Реквизиты организации совпадают с разделом company в settings.json."""
    # Подготовка
    company = settings_data["company"]

    # Действия
    organization = _build_loaded_manager().settings.organization

    # Проверки
    assert organization.name == company["name"]
    assert organization.inn == company["inn"]
    assert organization.bic == company["bic"]
    assert organization.curr_account == company["curr_account"]
    assert organization.legal_form == company["legal_form"]


def test_settings_manager__read_default_file__names_match_json(settings_data):
    """ФИО руководителя и главного бухгалтера совпадают с settings.json."""
    # Подготовка
    company = settings_data["company"]

    # Действия
    settings = _build_loaded_manager().settings

    # Проверки
    assert settings.boss_name == company["boss_name"]
    assert settings.accountant_name == company["accountant_name"]


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


def test_settings_manager__read_without_company__raises_validation_exception(
    settings_data, tmp_path
):
    """Файл настроек без раздела company вызывает исключение валидации."""
    # Подготовка
    settings_data.pop("company")
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
    settings_data["company"]["inn"] = "abc"
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
